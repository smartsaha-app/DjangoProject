import requests
import pandas as pd
import folium

# 1️⃣ Télécharger le CSV FIRMS
url = "https://firms.modaps.eosdis.nasa.gov/data/csv/MODIS_C6_1_Global_24h.csv"
r = requests.get(url)
with open("fires_24h.csv", "wb") as f:
    f.write(r.content)
print("CSV téléchargé avec succès")

# 2️⃣ Charger le CSV
df = pd.read_csv("fires_24h.csv")

# 3️⃣ Filtrer pour Madagascar
lat_min, lat_max = -25.0, -12.0
lon_min, lon_max = 43.0, 51.0

df_mada = df[(df['latitude'] >= lat_min) & (df['latitude'] <= lat_max) &
             (df['longitude'] >= lon_min) & (df['longitude'] <= lon_max)]

# Sauvegarder le CSV filtré
df_mada.to_csv("fires_madagascar.csv", index=False)
print(f"{len(df_mada)} points chauds détectés à Madagascar")

# 4️⃣ Générer une carte avec Folium
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

# Sauvegarder la carte
m.save("fires_map_madagascar.html")
print("Carte générée : fires_map_madagascar.html")
