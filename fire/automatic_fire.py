import requests
import pandas as pd
import folium
from datetime import datetime
import os

# 1️⃣ Définir les URLs et fichiers
url_csv = "https://firms.modaps.eosdis.nasa.gov/data/csv/MODIS_C6_1_Global_24h.csv"
csv_global = "fires_24h.csv"
csv_mada = "fires_madagascar.csv"
map_html = "fires_map_madagascar.html"

# 2️⃣ Télécharger le CSV FIRMS
try:
    r = requests.get(url_csv)
    r.raise_for_status()
    with open(csv_global, "wb") as f:
        f.write(r.content)
    print(f"[{datetime.now()}] CSV global téléchargé avec succès")
except Exception as e:
    print(f"[{datetime.now()}] Erreur lors du téléchargement : {e}")
    if not os.path.exists(csv_global):
        raise SystemExit("Pas de CSV disponible pour continuer")

# 3️⃣ Charger le CSV
df = pd.read_csv(csv_global)

# 4️⃣ Filtrer pour Madagascar
lat_min, lat_max = -25.0, -12.0
lon_min, lon_max = 43.0, 51.0

df_mada = df[(df['latitude'] >= lat_min) & (df['latitude'] <= lat_max) &
             (df['longitude'] >= lon_min) & (df['longitude'] <= lon_max)]

df_mada.to_csv(csv_mada, index=False)
print(f"[{datetime.now()}] {len(df_mada)} points chauds détectés à Madagascar")

# 5️⃣ Générer la carte interactive
m = folium.Map(location=[-18.77, 46.8], zoom_start=6)

for _, row in df_mada.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=3,
        color='red',
        fill=True,
        fill_opacity=0.7,
        popup=f"Brightness: {row['brightness']}, Date: {row['acq_date']}"
    ).add_to(m)

m.save(map_html)
print(f"[{datetime.now()}] Carte générée : {map_html}")
