from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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

        # On passe tout à DeepSeekClient
        answer = deepseek.ask(
            question=question,
            parcel_uuid=parcel_id,
            user_modules=user_modules
        )

        return Response({
            "answer": answer,
            "meta": {
                "question_type": question_type,
                "parcel_id": parcel_id,
                "crop_name": crop_name,
                "modules": user_modules
            }
        }, status=status.HTTP_200_OK)
