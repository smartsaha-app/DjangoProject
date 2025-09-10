from openai import OpenAI
import os
from django.conf import settings

from SmartSaha.services.context_builder import ContextBuilder

BASE_PROMPT = """
Tu es un ingénieur agronome expert à Madagascar.
Réponds toujours de manière précise, pratique et adaptée aux conditions locales :
- Inclue les saisons, sols et pratiques agricoles typiques.
- Ne donne jamais de réponses vagues.
- Si tu ne sais pas, indique clairement que l’information n’est pas disponible.
"""
class DeepSeekClient:
    def __init__(self):
        api_key = getattr(settings, "OPENROUTER_API_KEY", None)
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY manquant dans les settings / .env")

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = "deepseek/deepseek-r1:free"

    def ask(self, question: str, parcel_uuid: str = None, user_modules: dict = None):
        context_data = ContextBuilder.build_context(parcel_uuid, user_modules)
        full_prompt = f"{BASE_PROMPT}\n\nDonnées locales:\n{context_data}\n\nQuestion: {question}\nRéponse:"
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": full_prompt}]
        )
        return response.choices[0].message.content