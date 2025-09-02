# server.py - Servidor Flask adaptado para carpeta "Datos nuevos"
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import geopandas as gpd
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Ruta actualizada a tu carpeta de datos
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parent / "Datos nuevos"  # ← Cambiado aquí

@app.route('/')
def index():
    """Servir el visor HTML"""
    return send_from_directory('.', 'index.html')

@app.route('/api/municipios')
def get_municipios():
    """Convertir y servir municipios como GeoJSON"""
    try:
        # Leer GeoPackage desde "Datos nuevos"
        gdf = gpd.read_file(DATA_PATH / "municipios.geojson")
        
        # Convertir a WGS84 si es necesario
        gdf = gdf.to_crs('EPSG:4326')
        #gdf = gdf.to_crs('EPSG:4326')
        
        # Convertir a GeoJSON
        geojson = json.loads(gdf.to_json())
        
        return jsonify(geojson)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/centroides')
def get_centroides():
    """Convertir y servir centroides como GeoJSON"""
    try:
        # Leer GeoPackage desde "Datos nuevos"
        gdf = gpd.read_file(DATA_PATH / "centroides.geojson")
        
        # Convertir a WGS84 si es necesario
        if gdf.crs and gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs('EPSG:4326')
        
        # Convertir a GeoJSON
        geojson = json.loads(gdf.to_json())
        
        return jsonify(geojson)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/metadata')
def get_metadata():
    """Servir metadatos DCAT desde Datos nuevos"""
    try:
        with open(DATA_PATH / "metadata.jsonld", 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        return jsonify(metadata)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Servir archivos estáticos desde "Datos nuevos"
@app.route('/Datos nuevos/<path:filename>')
def serve_data_files(filename):
    """Servir archivos desde la carpeta Datos nuevos"""
    return send_from_directory('Datos nuevos', filename)

if __name__ == '__main__':
    print("🚀 Servidor iniciado en http://localhost:5000")
    print(f"📁 Leyendo datos desde: {DATA_PATH.absolute()}")
    print("📊 Endpoints disponibles:")
    print("   - GET /api/municipios")
    print("   - GET /api/centroides")
    print("   - GET /api/metadata")
    
    # Verificar que la carpeta existe
    if not DATA_PATH.exists():
        print(f"⚠️  AVISO: La carpeta '{DATA_PATH}' no existe!")
    else:
        files = list(DATA_PATH.glob("*.geojson"))
        print(f"✅ Encontrados {len(files)} archivos geojson")
    
    app.run(debug=True, use_reloader = False , port=5000)
