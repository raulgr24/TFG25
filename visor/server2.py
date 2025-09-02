# server.py
from pathlib import Path
from flask import Flask, Response, jsonify, send_from_directory
from flask_cors import CORS
import geopandas as gpd
import json

# --- compresión gzip (opcional, pero MUY recomendable) ---
try:
    from flask_compress import Compress
    HAS_COMPRESS = True
except Exception:
    HAS_COMPRESS = False

app = Flask(__name__)
CORS(app)
if HAS_COMPRESS:
    Compress(app)

# ----- Rutas de datos (robustas) -----
BASE_DIR = Path(__file__).resolve().parent          # .../TFG/visor
INDEX_PATH = BASE_DIR / "index.html"
DATA_DIR = BASE_DIR.parent / "Datos nuevos"         # .../TFG/Datos nuevos

# ----- Memoria para servir rápido -----
GEOJSON_TEXT = {}        # {"municipios": <str GeoJSON EPSG:4326>, "centroides": <str ...>}
GEOJSON_TEXT_SIMPLE = {} # idem pero simplificado

def load_layer(layer_name: str, simplify_tolerance: float | None = None) -> str:
    """
    Lee un .geojson del disco, reproyecta a EPSG:4326 y (opcional) simplifica.
    Devuelve texto GeoJSON (str) listo para enviar.
    """
    path = DATA_DIR / f"{layer_name}.geojson"
    if not path.exists():
        # Si prefieres, lanza excepción para detectar el error rápido
        raise FileNotFoundError(f"No existe {path}")

    gdf = gpd.read_file(path)

    # Reproyecta a WGS84 si no está ya
    try:
        gdf = gdf.to_crs("EPSG:4326")
    except Exception:
        # Por si viniera sin crs definido; NO debería ocurrir en geojson bien formado
        if gdf.crs is None:
            # asume que ya está en 4326
            pass
        else:
            raise

    if simplify_tolerance is not None:
        # ~0.0005 ≈ 50 m aprox (en grados); ajusta si quieres
        gdf["geometry"] = gdf.geometry.simplify(tolerance=simplify_tolerance, preserve_topology=True)

    return gdf.to_json()  # str (GeoJSON)

def preload():
    """
    Carga TODO una sola vez al arrancar el servidor.
    Ajusta la tolerancia de simplificación si quieres empezar más agresivo o más fino.
    """
    # Carga “completo”
    GEOJSON_TEXT["municipios"] = load_layer("municipios", simplify_tolerance=None)
    GEOJSON_TEXT["centroides"] = load_layer("centroides", simplify_tolerance=None)

    # Carga “simplificado” (opcional; cambia tolerancia a tu gusto)
    tol = 0.0005  # ≈ 50 m; prueba 0.0003–0.001 según lo que veas en el visor
    GEOJSON_TEXT_SIMPLE["municipios"] = load_layer("municipios", simplify_tolerance=tol)
    # Para puntos no aporta simplificar; lo dejamos igual
    GEOJSON_TEXT_SIMPLE["centroides"] = GEOJSON_TEXT["centroides"]

# --- Llama a la precarga al arrancar el proceso ---
preload()

# ----- Endpoints -----

@app.route('/')
def index():
    """Servir el visor HTML"""
    return send_from_directory('.', 'index.html')
@app.route("/api/municipios")
def api_municipios():
    # Sirve desde memoria (rápido)
    return Response(GEOJSON_TEXT["municipios"], mimetype="application/json", headers={
        "Cache-Control": "public, max-age=3600"
    })

@app.route("/api/centroides")
def api_centroides():
    return Response(GEOJSON_TEXT["centroides"], mimetype="application/json", headers={
        "Cache-Control": "public, max-age=3600"
    })

# Versión simplificada para probar rendimiento en el front:
@app.route("/api/municipios_simple")
def api_municipios_simple():
    return Response(GEOJSON_TEXT_SIMPLE["municipios"], mimetype="application/json", headers={
        "Cache-Control": "public, max-age=3600"
    })

@app.route("/api/health")
def api_health():
    return jsonify({"ok": True})

if __name__ == "__main__":
    # IMPORTANTE: sin reloader para que NO cargue dos veces ni recargue al guardar
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

