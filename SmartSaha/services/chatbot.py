# SmartSaha/services/simple_ai_client.py
import os
import httpx
from django.conf import settings
from mistralai import Mistral

BASE_PROMPT = """
Tu es un ingenieur agronome expert à Madagascar.
Reponds toujours de maniere précise, pratique, court et adaptee aux conditions locales :
- Inclue les saisons, sols et pratiques agricoles typiques.
- Ne donne jamais de reponses vagues.
- Si tu ne sais pas, indique clairement que l’information n’est pas disponible.
"""


class SimpleAIClient:
    def __init__(self):
        self.api_key = getattr(settings, "OPENROUTER_API_KEY", None) or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY manquant")

        self.base_url = "https://openrouter.ai/api/v1"
        self.models = [
            "deepseek/deepseek-chat:free",
            "huggingfaceh4/zephyr-7b-beta:free",
            "openchat/openchat-7b:free",
        ]

    def ask(self, question: str):
        """Version ultra-simplifiée - utilise seulement la question de l'utilisateur"""
        full_prompt = f"{BASE_PROMPT}\n\nQuestion: {question}\nRéponse:"

        for model in self.models:
            try:
                print(f"🔄 Essai avec: {model}")

                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://localhost",
                    "X-Title": "SmartSaha"
                }
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": full_prompt}],
                    "max_tokens": 1000
                }

                with httpx.Client(timeout=30.0) as client:
                    response = client.post(
                        f"{self.base_url}/chat/completions",
                        json=payload,
                        headers=headers
                    )

                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ Succès avec {model}")
                        return data["choices"][0]["message"]["content"]
                    else:
                        print(f"❌ {model} échoué: {response.status_code}")
                        continue

            except Exception as e:
                print(f"❌ Erreur avec {model}: {e}")
                continue

        return "Désolé, le service est temporairement indisponible. Réessaie dans quelques minutes."


# SmartSaha/services/robust_gemini_client.py
from google import genai

BASE_PROMPT = """
Tu es un ingenieur agronome expert à Madagascar.
Reponds toujours de maniere précise, pratique, court et adaptee aux conditions locales :
- Inclue les saisons, sols et pratiques agricoles typiques.
- Ne donne jamais de reponses vagues.
- Si tu ne sais pas, indique clairement que l’information n’est pas disponible.
"""


class RobustGeminiClient:
    def __init__(self):
        self.api_key = getattr(settings, "GEMINI_API_KEY", None) or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY manquant")

        self.client = genai.Client(api_key=self.api_key)

        # 🎯 MODÈLES GEMINI QUI EXISTENT VRAIMENT
        self.models = [
            "gemini-2.0-flash-exp",  # Modèle expérimental rapide
            "gemini-1.5-flash-8b",  # Version 8B de Flash
            "gemini-1.5-pro",  # Modèle pro
            "gemini-1.0-pro"  # Modèle de base
        ]

    def ask(self, question: str):
        """Essaie plusieurs modèles Gemini jusqu'à ce qu'un fonctionne"""
        full_prompt = f"{BASE_PROMPT}\n\nQuestion: {question}\nRéponse:"

        for model in self.models:
            try:
                print(f"🔄 Essai Gemini avec: {model}")

                response = self.client.models.generate_content(
                    model=model,
                    contents=full_prompt
                )

                print(f"✅ Succès avec {model}")
                return response.text

            except Exception as e:
                error_msg = str(e)
                print(f"❌ {model} échoué: {error_msg}")

                # Si c'est une erreur 404 (modèle non trouvé), on continue
                if "404" in error_msg or "not found" in error_msg.lower():
                    continue
                # Si c'est une erreur de quota, on continue aussi
                elif "quota" in error_msg.lower() or "429" in error_msg:
                    continue
                else:
                    # Pour d'autres erreurs, on retourne l'erreur
                    return f"Erreur API Gemini ({model}): {error_msg}"

        return "Désolé, aucun modèle Gemini n'est disponible pour le moment."

    def get_available_models(self):
        """Liste les modèles disponibles"""
        try:
            models = self.client.models.list()
            available_models = [model.name for model in models]
            print("📋 Modèles Gemini disponibles:", available_models)
            return available_models
        except Exception as e:
            print(f"❌ Erreur liste modèles: {e}")
            return []




class MistralAgentClient:
    def __init__(self):
        self.api_key = getattr(settings, "MISTRAL_API_KEY", None) or os.getenv("MISTRAL_API_KEY")

        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY manquant")

        try:
            from mistralai import Mistral
            self.mistral_available = True
        except ImportError:
            self.mistral_available = False

    def ask(self, question: str):
        """Client agronome avec modèle officiel"""
        if not self.mistral_available:
            return "Erreur: pip install mistralai"

        try:
            print(f"🔄 Mistral - Question: {question[:50]}...")

            with  Mistral(api_key=self.api_key) as client:
                response = client.chat.complete(
                    model="mistral-small-latest",  # Modèle gratuit et efficace
                    messages=[
                        {
                            "role": "system",
                            "content": "Expert agronome malgache. Réponses courtes, précises, adaptées aux saisons et sols locaux. Pas de généralités."
                        },
                        {
                            "role": "user",
                            "content": question
                        }
                    ],
                    max_tokens=500,  # Réponses courtes
                    temperature=0.3,  # Réponses précises
                    stream=False
                )

            answer = response.choices[0].message.content
            print(f"✅ Réponse reçue: {answer[:50]}...")
            return answer

        except Exception as e:
            print(f"❌ Erreur Mistral: {e}")
            return f"Erreur service: {str(e)}"