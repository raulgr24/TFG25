# server.py — robusto: sirve index, precarga GeoJSON y API rápida
from pathlib import Path
from flask import Flask, Response, jsonify, send_file, send_from_directory
from flask_cors import CORS
import geopandas as gpd

# --- compresión opcional (pip install flask-compress) ---
try:
    from flask_compress import Compress
    HAS_COMPRESS = True
except Exception:
    HAS_COMPRESS = False

app = Flask(__name__, static_folder=None)
CORS(app)
if HAS_COMPRESS:
    Compress(app)

# Rutas absolutas
BASE_DIR = Path(__file__).resolve().parent          # .../TFG25/visor
INDEX_PATH = BASE_DIR / "index.html"                # path de index
DATA_DIR  = BASE_DIR.parent / "Datos nuevos"        # path de los datasets

# Memoria (precarga una vez)
GEOJSON_TEXT = {}        # diccionario con las capas
GEOJSON_TEXT_SIMPLE = {} 

def to_wgs84(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if gdf.crs is None:
        return gdf
    if str(gdf.crs).upper() not in ("EPSG:4326", "WGS 84", "WGS84"):
        print("Capa reproyectada")
        return gdf.to_crs("EPSG:4326")
    return gdf

def load_layer(name: str, tol: float | None = None) -> str:
    path = DATA_DIR / f"{name}.geojson"
    if not path.exists():
        raise FileNotFoundError(f"No existe {path}")
    gdf = gpd.read_file(path)
    gdf = to_wgs84(gdf)
    if tol is not None:
        gdf["geometry"] = gdf.geometry.simplify(tol, preserve_topology=True)
    return gdf.to_json()

def preload():
    # Completo
    GEOJSON_TEXT["municipios"] = load_layer("municipios", tol=None)
    GEOJSON_TEXT["centroides"] = load_layer("centroides", tol=None)
    GEOJSON_TEXT["nucleos"] = load_layer("nucleos", tol=None)
    # Simplificado (p.ej. ~50 m; ajusta 0.0003–0.001)
    GEOJSON_TEXT_SIMPLE["municipios"] = load_layer("municipios", tol=0.0005)
    GEOJSON_TEXT_SIMPLE["centroides"] = GEOJSON_TEXT["centroides"]
    GEOJSON_TEXT_SIMPLE["nucleos"] = GEOJSON_TEXT["nucleos"]
# Precarga al iniciar el proceso
preload()

# ---------- HTML ----------
@app.route("/")
def root():
    return send_file(INDEX_PATH)

# # Si tienes assets (css/js/img) en visor/assets/, expónlos así:
# @app.route("/assets/<path:filename>")
# def assets(filename):
#     return send_from_directory(BASE_DIR / "assets", filename)

# ---------- API ----------
@app.route("/api/health")
def api_health():
    return jsonify({"ok": True})

@app.route("/api/municipios")
def api_municipios():
    return Response(GEOJSON_TEXT["municipios"], mimetype="application/json",
                    headers={"Cache-Control": "public, max-age=3600"})

@app.route("/api/nucleos")
def api_nucleos():
    return Response(GEOJSON_TEXT["nucleos"], mimetype="application/json",
                    headers={"Cache-Control": "public, max-age=3600"})

@app.route("/api/centroides")
def api_centroides():
    return Response(GEOJSON_TEXT["centroides"], mimetype="application/json",
                    headers={"Cache-Control": "public, max-age=3600"})

@app.route("/api/municipios_simple")
def api_municipios_simple():
    return Response(GEOJSON_TEXT_SIMPLE["municipios"], mimetype="application/json",
                    headers={"Cache-Control": "public, max-age=3600"})

# (Opcional) servir ficheros crudos sin espacios en la ruta:
@app.route("/data/<path:filename>")
def data_files(filename):
    return send_from_directory(DATA_DIR, filename)

if __name__ == "__main__":
    print("🚀 http://localhost:5000")
    print(f"📁 Datos: {DATA_DIR}")
    print("🔎 /api/health, /api/municipios, /api/centroides, /api/municipios_simple, /api/nucleos")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
