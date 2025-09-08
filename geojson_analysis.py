import folium
import geopandas as gpd

# Cargar GeoJSON
gdf = gpd.read_file('Datos nuevos/centroides.geojson')

# Crear mapa
m = folium.Map(location=[40.4, -3.7], zoom_start=8)
folium.GeoJson(gdf).add_to(m)
m.save('mapa.html')
