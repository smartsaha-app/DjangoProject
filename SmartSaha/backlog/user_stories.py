# agriculture/backlog/user_stories.py
USER_STORIES = {
    "SPRINT_1": [
        {
            "id": "US-001",
            "title": "Affichage Météo Parcelle",
            "description": "En tant qu'agriculteur, je veux voir la météo actuelle de ma parcelle",
            "acceptance_criteria": [
                "Doit afficher température, humidité, précipitations",
                "Doit montrer les conditions actuelles",
                "Doit être accessible via API REST"
            ],
            "story_points": 3,
            "priority": "HIGH"
        },
        {
            "id": "US-002",
            "title": "Stockage Données Météo",
            "description": "En tant que système, je dois stocker les données météo via API",
            "acceptance_criteria": [
                "Doit sauvegarder les données JSON complètes",
                "Doit extraire les métadonnées importantes",
                "Doit gérer les erreurs d'API"
            ],
            "story_points": 5,
            "priority": "HIGH"
        }
    ],
    "SPRINT_2": [
        {
            "id": "US-003",
            "title": "Alertes Météo Agricoles",
            "description": "En tant qu'agriculteur, je veux recevoir des alertes météo critiques",
            "acceptance_criteria": [
                "Doit détecter pluies intenses (>20mm)",
                "Doit alerter risques gel (<5°C)",
                "Doit signaler sécheresse (0mm pluie + >30°C)"
            ],
            "story_points": 8,
            "priority": "MEDIUM"
        }
    ]
}