# SmartSaha/views/user_viewset.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from SmaartSahaProject import settings
from SmartSaha.mixins.cache_mixins import CacheInvalidationMixin
from SmartSaha.serializers import UserSerializer, UserSignupSerializer, UserLoginSerializer
from SmartSaha.models import User

from google.oauth2 import id_token
from google.auth.transport import requests
import secrets

def send_test_email():
    send_mail(
        subject="Test Django avec Zoho",
        message="Ceci est un mail de test envoyé depuis Django avec Zoho Mail.",
        from_email=None,  # par défaut prend DEFAULT_FROM_EMAIL
        recipient_list=["test@gmail.com"],
        fail_silently=False,
    )
class UserViewSet(CacheInvalidationMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # protégé

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = []  # public

class LoginView(APIView):
    permission_classes = []  # public
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user": {
                "uuid": str(user.uuid),
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }, status=200)

token_generator = PasswordResetTokenGenerator()


class ForgotPasswordView(APIView):
    permission_classes = []  # public

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email requis"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "Si l'email existe, un lien de réinitialisation a été envoyé"},
                status=status.HTTP_200_OK
            )

        # Générer token et uid
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        # ✅ CORRECTION : Utiliser une valeur par défaut si FRONTEND_URL n'existe pas
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        reset_link = f"{frontend_url}/reset-password/{uid}/{token}/"

        # Le reste du code reste identique...
        try:
            send_mail(
                subject="Réinitialisation de votre mot de passe - SmartSaha",
                message=f"""
Bonjour,

Vous avez demandé la réinitialisation de votre mot de passe.

Cliquez sur ce lien pour créer un nouveau mot de passe :
{reset_link}

Ce lien expirera dans 24 heures.

Si vous n'êtes pas à l'origine de cette demande, ignorez simplement cet email.

Cordialement,
L'équipe SmartSaha
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return Response(
                {"message": "Lien de réinitialisation envoyé par email"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print(f"Erreur envoi email: {str(e)}")
            return Response(
                {"error": "Erreur lors de l'envoi de l'email"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ResetPasswordView(APIView):
    permission_classes = []  # public

    def post(self, request, uidb64, token):
        # Décoder l'UID de l'utilisateur
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Lien invalide ou expiré"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier le token
        if not token_generator.check_token(user, token):
            return Response(
                {"error": "Lien invalide ou expiré"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Récupérer le nouveau mot de passe
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not new_password:
            return Response(
                {"error": "Mot de passe requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_password != confirm_password:
            return Response(
                {"error": "Les mots de passe ne correspondent pas"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(new_password) < 8:
            return Response(
                {"error": "Le mot de passe doit contenir au moins 8 caractères"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mettre à jour le mot de passe
        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Mot de passe réinitialisé avec succès"},
            status=status.HTTP_200_OK
        )


# Créez une vue de test
class TestEmailView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            send_mail(
                subject="Test Configuration Email - SmartSaha",
                message="Ceci est un test de configuration email.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["hugueszeus@gmail.com"],  # Remplacez par votre email
                fail_silently=False,
            )
            return Response({"message": "Email de test envoyé"})
        except Exception as e:
            return Response({"error": f"Erreur: {str(e)}"}, status=500)


class GoogleLoginView(APIView):
    permission_classes = []  # public

    GOOGLE_CLIENT_ID = "972113542805-n0fujnh22t4jkejhvda051oml965limf.apps.googleusercontent.com"  # Remplace par ton client ID Google

    def post(self, request, *args, **kwargs):
        token_from_front = request.data.get("token")
        if not token_from_front:
            return Response({"error": "Token missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Vérification du token Google
            idinfo = id_token.verify_oauth2_token(token_from_front, requests.Request(), self.GOOGLE_CLIENT_ID)
            email = idinfo.get("email")
            first_name = idinfo.get("given_name", "")
            last_name = idinfo.get("family_name", "")

            if not email:
                return Response({"error": "Email not provided by Google"}, status=status.HTTP_400_BAD_REQUEST)

            # Crée ou récupère l'utilisateur
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": first_name,
                    "first_name": first_name,
                    "last_name": last_name,
                    "password": secrets.token_urlsafe(16)  # mot de passe aléatoire
                }
            )

            # Générer le token Django REST Framework
            token_obj, _ = Token.objects.get_or_create(user=user)

            return Response({
                "token": token_obj.key,
                "user": {
                    "uuid": str(user.uuid),
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                }
            })

        except ValueError:
            return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)


