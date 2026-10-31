"""
Ejercicio B1 - Veredas de Boyacá
1. Descarga las veredas de Tunja desde el IDE Boyacá con requests.
2. Cuenta veredas por municipio (top 10) con el paquete completo.
3. Reproyecta a EPSG:9377, calcula área en ha y muestra las 5 más grandes.

Uso:  python b1_veredas.py
Requiere: datos/veredas_boyaca.geojson (paquete completo)
"""
from pathlib import Path

import geopandas as gpd
import requests

RUTA_VEREDAS = Path("datos/veredas_boyaca.geojson")
SALIDAS = Path("salidas")
SALIDAS.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. requests: veredas de Tunja desde el servicio ArcGIS del IDE Boyacá
# ---------------------------------------------------------------------------
print("=" * 60)
print("1. Veredas de Tunja (servicio IDE Boyacá)")
print("=" * 60)

URL = (
    "https://services6.arcgis.com/Ex2fmFOuTOHRZtML/ArcGIS/rest/services/"
    "Veredas_Boyaca_2024/FeatureServer/0/query"
)
params = {
    "where": "NOMB_MPIO = 'TUNJA'",
    "outFields": "NOMB_MPIO,NOMBRE_VER,CODIGO_VER",
    "outSR": "4326",
    "f": "geojson",
}

r = requests.get(URL, params=params, timeout=30)
r.raise_for_status()
tunja_web = gpd.GeoDataFrame.from_features(r.json()["features"], crs=4326)
print(len(tunja_web), "veredas en Tunja")
print(tunja_web[["NOMBRE_VER", "CODIGO_VER"]].head())

# ---------------------------------------------------------------------------
# 2. pandas: veredas por municipio (top 10)
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("2. Top 10 municipios por número de veredas")
print("=" * 60)

gdf = gpd.read_file(RUTA_VEREDAS)
print("Forma:", gdf.shape)

por_municipio = gdf.groupby("NOMB_MPIO").size().sort_values(ascending=False)
print(por_municipio.head(10))

# ---------------------------------------------------------------------------
# 3. geopandas: reproyección y área en hectáreas
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("3. Las 5 veredas más grandes (EPSG:9377)")
print("=" * 60)

gdf_m = gdf.to_crs(9377)                      # CRS en metros
gdf_m["area_ha"] = gdf_m.geometry.area / 10_000   # m² -> ha

top5 = (
    gdf_m[["NOMB_MPIO", "NOMBRE_VER", "area_ha"]]
    .sort_values("area_ha", ascending=False)
    .head(5)
    .round({"area_ha": 2})
)
print(top5.to_string(index=False))

# Guardar resultado
gdf_m.to_file(SALIDAS / "veredas_area.gpkg", driver="GPKG")
print(f"\nGuardado: {SALIDAS / 'veredas_area.gpkg'}")
