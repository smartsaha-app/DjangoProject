Voici un **guide Markdown complet** pour automatiser la mise à jour quotidienne de ton CSV FIRMS sur **Railway ou Render**, sans base de données et avec génération de carte HTML.

---

# Automatisation FIRMS Madagascar sur Railway / Render

## 1️⃣ Pré-requis

* Compte sur **[Railway](https://railway.app)** ou **[Render](https://render.com)**
* Python installé localement pour tester le script
* Dépendances Python :

```bash
pip install pandas requests folium
```

* Script Python prêt (`firms_madagascar_auto.py`) :

  * Télécharge le CSV FIRMS global
  * Filtre Madagascar
  * Met à jour `fires_madagascar.csv` en évitant les doublons
  * Génère la carte HTML `fires_map_madagascar.html`

---

## 2️⃣ Préparer le projet

1. Crée un dossier local :

```
firms_project/
├─ firms_madagascar_auto.py
├─ requirements.txt
```

2. Contenu de `requirements.txt` :

```
pandas
requests
folium
```

3. Teste localement :

```bash
python firms_madagascar_auto.py
```

* Vérifie que `fires_madagascar.csv` et `fires_map_madagascar.html` sont générés correctement.

---

## 3️⃣ Déploiement sur Railway

1. Crée un **nouveau projet Python** sur Railway.

2. Connecte ton **dépôt Git** contenant `firms_project/`.

3. Dans Railway :

   * Ajoute un **Plugin Scheduler** (Jobs)
   * Commande du job :

   ```bash
   python firms_madagascar_auto.py
   ```

   * Fréquence : **Daily** (ex : tous les jours à 08:00)

4. Déploiement : Railway exécutera le script automatiquement tous les jours.

5. Résultat : le CSV et la carte HTML seront mis à jour sur le filesystem de ton projet.

   * Pour rendre la carte accessible publiquement, tu peux ajouter un **Static Site** sur Render ou stocker sur Railway Storage.

---

## 4️⃣ Déploiement sur Render

1. Crée un **Web Service Python** ou un **Background Worker**.

2. Connecte ton dépôt Git.

3. Dans Render :

   * Pour un **Background Worker**, définis :

     * **Command** :

     ```bash
     python firms_madagascar_auto.py
     ```

     * **Environment** : Python 3.x
     * **Auto-deploy** : activé

4. Dans **Cron Job** (Render Scheduler) :

   * Crée un cron job :

     ```
     0 8 * * * python /path/to/firms_madagascar_auto.py
     ```
   * Cela exécutera le script tous les jours à 08h00.

5. Le script générera automatiquement le CSV mis à jour et la carte HTML.

---

## 5️⃣ Conseils pratiques

* **Éviter les doublons** : le script gère déjà les doublons par `(latitude, longitude, acq_date, acq_time, satellite)`.
* **Stockage permanent** : Render et Railway peuvent réinitialiser le filesystem sur chaque déploiement.

  * Solution : stocker `fires_madagascar.csv` et `fires_map_madagascar.html` dans **Railway Storage** ou **Render Persistent Disk**.
* **Logs** : ajoute des `print()` ou `logging` pour vérifier que le script s’exécute correctement chaque jour.

---

Si tu veux, je peux te préparer **le script Python final prêt pour deployment**, incluant :

* Téléchargement CSV FIRMS
* Filtrage Madagascar
* Mise à jour CSV avec gestion des doublons
* Génération automatique de la carte HTML
* Compatible **Railway / Render**

Veux‑tu que je fasse ça ?
