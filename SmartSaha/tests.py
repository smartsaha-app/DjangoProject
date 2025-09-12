#
#
# from openai import OpenAI
#
# api_key = "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"  # remplace par ta clé
# client = OpenAI(
#   base_url="https://openrouter.ai/api/v1",
#   api_key=api_key,
# )
#
# completion = client.chat.completions.create(
#   extra_headers={
#     "HTTP-Referer": "smart-saha.com", # Optional. Site URL for rankings on openrouter.ai.
#     "X-Title": "smart-saha", # Optional. Site title for rankings on openrouter.ai.
#   },
#   model="openai/gpt-4o",
#   messages=[
#     {
#       "role": "user",
#       "content": "What is the meaning of life?"
#     }
#   ]
# )
#
# print(completion.choices[0].message.content)


# Exemple d'utilisation
# from SmartSaha.services import DeepSeekClient
