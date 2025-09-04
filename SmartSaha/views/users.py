# SmartSaha/views/user_viewset.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from SmartSaha.serializers import UserSerializer, UserSignupSerializer, UserLoginSerializer
from SmartSaha.models import User

def send_test_email():
    send_mail(
        subject="Test Django avec Zoho",
        message="Ceci est un mail de test envoyé depuis Django avec Zoho Mail.",
        from_email=None,  # par défaut prend DEFAULT_FROM_EMAIL
        recipient_list=["test@gmail.com"],
        fail_silently=False,
    )
class UserViewSet(viewsets.ModelViewSet):
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
            return Response({"error": "Email required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Générer token et uid
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        reset_link = f"http://localhost:8000/api/reset-password/{uid}/{token}/"

        # Envoi mail (à remplacer par ton backend mail)
        send_mail(
            subject="Password Reset",
            message=f"Click here to reset your password: {reset_link}",
            from_email=None,  # utilisera DEFAULT_FROM_EMAIL si défini
            recipient_list=[user.email],
            fail_silently=False,
        )

        send_mail(
            subject="Test Django avec Zoho",
            message="Ceci est un mail de test envoyé depuis Django avec Zoho Mail.",
            from_email=None,  # par défaut prend DEFAULT_FROM_EMAIL
            recipient_list=["destinataire@example.com"],
            fail_silently=False,
        )

        return Response({"message": "Password reset link sent"}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    permission_classes = []  # public

    def post(self, request, uidb64, token):
        # Décoder l'UID de l'utilisateur
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier le token
        if not token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        # Récupérer le nouveau mot de passe depuis la requête POST
        new_password = request.data.get("new_password")
        if not new_password:
            return Response({"error": "Password required"}, status=status.HTTP_400_BAD_REQUEST)

        # Mettre à jour le mot de passe
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)