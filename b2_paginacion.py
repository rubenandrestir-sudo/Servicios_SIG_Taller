"""
Ejercicio B2 - APIs y JSON: paginación de un FeatureServer de ArcGIS
1. Recupera TODAS las veredas de Boyacá paginando con resultOffset.
2. Imprime cuántos municipios distintos aparecen.
3. Repite con resultRecordCount = 500 y compara vueltas y total.

Uso:  python b2_paginacion.py
"""
import requests

URL = (
    "https://services6.arcgis.com/Ex2fmFOuTOHRZtML/ArcGIS/rest/services/"
    "Veredas_Boyaca_2024/FeatureServer/0/query"
)
BASE = {
    "where": "1=1",
    "outFields": "NOMB_MPIO,NOMBRE_VER",
    "outSR": "4326",
    "f": "geojson",
}


def descargar_todo(bloque):
    """Pagina el servicio en bloques de `bloque` registros.
    Devuelve (features, numero_de_vueltas)."""
    features, offset, vueltas = [], 0, 0
    while True:
        p = {**BASE, "resultOffset": offset, "resultRecordCount": bloque}
        r = requests.get(URL, params=p, timeout=30)
        r.raise_for_status()
        datos = r.json()
        if "error" in datos:                      # ArcGIS responde 200 con error
            raise RuntimeError(datos["error"])
        nuevos = datos.get("features", [])
        vueltas += 1
        features += nuevos
        print(f"  vuelta {vueltas} | offset {offset}: +{len(nuevos)} (total {len(features)})")
        if len(nuevos) < bloque:                  # último bloque
            break
        offset += bloque
    return features, vueltas


# ---------------------------------------------------------------------------
# 1 y 2. Bloques de 1000
# ---------------------------------------------------------------------------
print("=" * 60)
print("Paginación con resultRecordCount = 1000")
print("=" * 60)
features, vueltas = descargar_todo(1000)
print("TOTAL:", len(features))
municipios = {f["properties"]["NOMB_MPIO"] for f in features}
print("Municipios distintos:", len(municipios))
print("Vueltas del bucle:", vueltas)

# ---------------------------------------------------------------------------
# 3. Bloques de 500
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("Paginación con resultRecordCount = 500")
print("=" * 60)
features_500, vueltas_500 = descargar_todo(500)
print("TOTAL:", len(features_500))
print("Vueltas del bucle:", vueltas_500)

print("\n" + "=" * 60)
print("Comparación")
print("=" * 60)
print(f"Bloque 1000 -> {len(features)} registros en {vueltas} vueltas")
print(f"Bloque  500 -> {len(features_500)} registros en {vueltas_500} vueltas")
print("¿Mismo total?", len(features) == len(features_500))
