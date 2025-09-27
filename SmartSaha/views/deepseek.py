import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import httpx  # pour gérer les exceptions HTTP de DeepSeek

from SmartSaha.services import DeepSeekClient

deepseek = DeepSeekClient()


class AgronomyAssistantAPIView(APIView):
    def post(self, request):
        question = request.data.get("question")
        question_type = request.data.get("question_type", "general")
        parcel_id = request.data.get("parcel_id")
        crop_name = request.data.get("crop_name")
        user_modules = request.data.get("user_modules", {})

        if not question:
            return Response({"error": "No question provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            answer = deepseek.ask(
                question=question,
                parcel_uuid=parcel_id,
                user_modules=user_modules
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                answer = "Trop de requêtes vers le service IA. Réessaie plus tard."
            else:
                answer = f"Erreur API: {str(e)}"
        except Exception as e:
            answer = f"Erreur inattendue: {str(e)}"

        return Response({
            "answer": answer,
            "meta": {
                "question_type": question_type,
                "parcel_id": parcel_id,
                "crop_name": crop_name,
                "modules": user_modules
            }
        }, status=status.HTTP_200_OK)


@login_required(login_url="login")
def assistant_agronome_page(request):
    """
    Vue qui rend la page HTML avec le formulaire.
    """
    return render(request, "assistant_agronome.html")


@csrf_exempt
@login_required(login_url="login")
def assistant_agronome_api(request):
    """
    Vue qui reçoit la question, appelle le moteur IA et renvoie la réponse JSON.
    """
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Payload JSON invalide"}, status=400)

        question = payload.get("question")
        question_type = payload.get("question_type")
        parcel_id = payload.get("parcel_id")
        crop_name = payload.get("crop_name")
        user_modules = payload.get("user_modules", {})

        if not question or not question_type:
            return JsonResponse({"error": "Champs obligatoires manquants"}, status=400)

        try:
            response = deepseek.ask(
                question=question,
                parcel_uuid=parcel_id,
                user_modules=user_modules
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                response = {"answer": "Trop de requêtes vers le service IA. Réessaie plus tard. Tester le "}
            else:
                response = {"answer": f"Erreur API: {str(e)}"}
        except Exception as e:
            response = {"answer": f"Erreur inattendue: {str(e)}"}

        return JsonResponse(response, safe=False)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
