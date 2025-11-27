# SmartSaha/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from SmartSaha.services import SimpleAIClient


class AgriAssistantViewSet(viewsets.ViewSet):
    """
    ViewSet complet pour l'assistant agronome
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ai_client = SimpleAIClient()

    def create(self, request):
        """
        POST /api/assistant/ - Pose une question (méthode principale)
        """
        question = request.data.get('question', '').strip()

        if not question:
            return Response(
                {'error': 'Le champ "question" est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Paramètres optionnels
        max_tokens = request.data.get('max_tokens', 1000)
        temperature = request.data.get('temperature', 0.7)

        try:
            reponse = self.ai_client.ask(question)

            return Response({
                'id': f"chat_{int(timezone.now().timestamp())}",
                'question': question,
                'reponse': reponse,
                'timestamp': timezone.now().isoformat(),
                'metadata': {
                    'max_tokens': max_tokens,
                    'temperature': temperature
                }
            })

        except Exception as e:
            return Response({
                'error': f'Erreur du service IA: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """
        GET /api/assistant/ - Informations sur le service
        """
        return Response({
            'service': 'Assistant Agronome Expert Madagascar',
            'version': '1.0',
            'description': 'Service IA pour conseils agricoles adaptés à Madagascar',
            'endpoints': {
                'POST /': 'Poser une question',
                'GET /status/': 'Statut du service',
                'GET /history/': 'Historique (à implémenter)'
            },
            'timestamp': timezone.now().isoformat()
        })

    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        GET /api/assistant/status/ - Statut du service
        """
        return Response({
            'status': 'operational',
            'timestamp': timezone.now().isoformat(),
            'models_available': len(self.ai_client.models)
        })

    @action(detail=False, methods=['post'])
    def batch_ask(self, request):
        """
        POST /api/assistant/batch_ask/ - Questions multiples
        """
        questions = request.data.get('questions', [])

        if not isinstance(questions, list) or len(questions) == 0:
            return Response(
                {'error': 'Le champ "questions" doit être une liste non vide'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(questions) > 5:
            return Response(
                {'error': 'Maximum 5 questions par requête'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reponses = []
        for question in questions:
            if isinstance(question, str) and question.strip():
                try:
                    reponse = self.ai_client.ask(question.strip())
                    reponses.append({
                        'question': question,
                        'reponse': reponse,
                        'status': 'success'
                    })
                except Exception as e:
                    reponses.append({
                        'question': question,
                        'reponse': None,
                        'status': 'error',
                        'error': str(e)
                    })

        return Response({
            'batch_id': f"batch_{int(timezone.now().timestamp())}",
            'results': reponses,
            'timestamp': timezone.now().isoformat()
        })


from SmartSaha.services import RobustGeminiClient
class GeminiAssistantViewSet(viewsets.ViewSet):
    """
    ViewSet pour l'assistant agronome avec Gemini
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ai_client = RobustGeminiClient()

    def create(self, request):
        """
        POST /api/gemini-assistant/ - Pose une question à Gemini
        """
        question = request.data.get('question', '').strip()

        if not question:
            return Response(
                {'error': 'Le champ "question" est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            reponse = self.ai_client.ask(question)

            return Response({
                'success': True,
                'question': question,
                'reponse': reponse,
                'timestamp': timezone.now().isoformat()
            })

        except Exception as e:
            return Response({
                'error': f'Erreur du service: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """
        GET /api/gemini-assistant/ - Informations sur le service
        """
        available_models = self.ai_client.get_available_models()

        return Response({
            'service': 'Assistant Agronome Gemini',
            'provider': 'Google Gemini',
            'available_models': available_models,
            'timestamp': timezone.now().isoformat()
        })

    @action(detail=False, methods=['get'])
    def models(self, request):
        """
        GET /api/gemini-assistant/models/ - Liste les modèles disponibles
        """
        available_models = self.ai_client.get_available_models()
        return Response({
            'available_models': available_models,
            'total': len(available_models)
        })


from SmartSaha.services import MistralAgentClient


class MistralAssistantViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    """
    ViewSet public pour Mistral - Sans authentification
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.agent_client = MistralAgentClient()
        except Exception as e:
            self.agent_client = None
            self.error_message = f"Client non disponible: {str(e)}"

    def create(self, request):
        """
        POST /api/mistral-assistant/ - Pose une question (public)
        """
        question = request.data.get('question', '').strip()

        if not question:
            return Response(
                {'error': 'Le champ "question" est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérification si le client est disponible
        if not self.agent_client:
            return Response({
                'success': False,
                'question': question,
                'reponse': self.error_message if hasattr(self,
                                                         'error_message') else "Service temporairement indisponible",
                'fallback': True,
                'timestamp': timezone.now().isoformat()
            })

        try:
            reponse = self.agent_client.ask(question)

            return Response({
                'success': True,
                'question': question,
                'reponse': reponse,
                'timestamp': timezone.now().isoformat()
            })

        except Exception as e:
            # Fallback avec réponse basique
            fallback_response = self._get_fallback_response(question)
            return Response({
                'success': False,
                'question': question,
                'reponse': fallback_response,
                'error': str(e),
                'fallback': True,
                'timestamp': timezone.now().isoformat()
            })

    def list(self, request):
        """
        GET /api/mistral-assistant/ - Info du service (public)
        """
        service_status = "actif" if self.agent_client and self.agent_client.mistral_available else "inactif"

        return Response({
            'service': 'Assistant Agronome Mistral',
            'provider': 'Mistral AI',
            'status': service_status,
            'authentication': 'aucune requise',
            'usage': 'POST avec {"question": "votre question"}',
            'timestamp': timezone.now().isoformat()
        })

    def _get_fallback_response(self, question):
        """Réponses de fallback quand l'API ne marche pas"""
        fallback_responses = {
            "riz": "À Madagascar, plantez le riz en novembre-décembre pour la saison des pluies. Rendement moyen: 2-4 tonnes/ha.",
            "maïs": "Maïs: plantation octobre-novembre. Cycle 90-120 jours. Rendement: 1.5-3 tonnes/ha.",
            "manioc": "Manioc: tolérant aux sols pauvres. Plantation toute l'année en zone humide. Rendement: 10-20 tonnes/ha.",
            "haricot": "Haricot: fixe l'azote. Plantation en début de saison pluies. Bonne rotation avec céréales.",
            "pomme de terre": "Pomme de terre: altitude >1000m. Plantation août-septembre. Rendement: 15-25 tonnes/ha."
        }

        # Cherche des mots-clés dans la question
        question_lower = question.lower()
        for key, response in fallback_responses.items():
            if key in question_lower:
                return f"⚠️ Mode basique - {response}"

        return "⚠️ Service IA temporairement indisponible. Question reçue: " + question[:100] + "..."
