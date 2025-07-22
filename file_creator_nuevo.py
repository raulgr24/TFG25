from qgis.core import *
import json
import numpy as np
import csv
import os
from pathlib import Path

# Initialize the QGIS resources at the beginning of the scrip https://docs.qgis.org/3.40/en/docs/pyqgis_developer_cookbook/intro.html#using-pyqgis-in-standalone-scripts
# Supply path to qgis install location
QgsApplication.setPrefixPath("C:/Program Files/QGIS 3.40.7", True)

qgs = QgsApplication([], False)
qgs.initQgis()
identifiers={
    "Centroides final":"CDTNUCLEO",
    'Hospitales grupo 3':"DESCR",
    'Hospitales grupo 2':"DESCR",
    "Bomberos":"ETIQUETA",
    'Juzgados':"BUSCA",
    'Salud mental':"DESCR"
}

# Abrimos el archivo qgz
project = QgsProject.instance()
project.read("C:/Users/raulc/Desktop/TFG25/tfg_project.qgz")
names = [layer.name() for layer in project.mapLayers().values()]
print(names)
# Orígenes y destinos
origin = 'Centroides final'
destinations = ['Hospitales grupo 3',
                'Hospitales grupo 2',
                'Bomberos',
                'Juzgados',
                'Salud mental']

def distance_matrix_filtered(origin, destinations):
    origin_layer = project.mapLayersByName(origin)[0]
    destination_layers = [project.mapLayersByName(dest)[0] for dest in destinations]

    distance_calculator = QgsDistanceArea()
    distance_calculator.setSourceCrs(origin_layer.crs(), QgsProject.instance().transformContext())
    distance_calculator.setEllipsoid('WGS84')

    origin_features = list(origin_layer.getFeatures())
    destination_features = [list(layer.getFeatures()) for layer in destination_layers]

    distances = {}
    for origin_feat in origin_features:
        origin_id = origin_feat[identifiers[origin]]
        row = []
        for i, dest_layer_feats in enumerate(destination_features):
            dest_name = destinations[i]
            filtered_dest_feats = []
            # Filtro
            if dest_name in ["Hospitales grupo 2", "Hospitales grupo 3", "Salud mental"]:
                if 'COD' in origin_feat.fields().names():
                    origin_cod = origin_feat['COD']
                    filtered_dest_feats = [f for f in dest_layer_feats if f['COD'] == origin_cod]
            elif dest_name == "Juzgados":
                if 'PART_JUD' in origin_feat.fields().names():
                    origin_part_jud = origin_feat['PART_JUD']
                    filtered_dest_feats = [f for f in dest_layer_feats if f['PART_JUD'] == origin_part_jud]
            else:
                filtered_dest_feats = dest_layer_feats

            # Calcula la distancia solo con los destinos filtrados
            dest_distances = []
            for dest_feat in filtered_dest_feats:
                dist = distance_calculator.measureLine(
                    origin_feat.geometry().centroid().asPoint(),
                    dest_feat.geometry().centroid().asPoint()
                )
                dest_distances.append(dist)
            row.append(dest_distances)
        distances[origin_id] = row
    return distances

def dict_to_json(data, filename):
    output = os.path.dirname("output/"+filename+".json")
    os.makedirs(output, exist_ok=True)
    with open("output/"+filename+".json","w") as f:
        json.dump(data,f,indent=4)
        
def average_distance(distance_dict):
    mean_distance_matrix = {}
    for origin, dests in distance_dict.items():
        distances = []
        for dest in dests:
            if len(dest)> 0:
                distances.append(np.mean(dest))
            else:
                distances.append(None)
        mean_distance_matrix[origin] = distances
    return mean_distance_matrix

def json_to_csv(file):
    with open("output/"+file+".json", 'r') as f:
        data = json.load(f)
    max_cols = max(len(v) for v in data.values())
    output = os.path.dirname("output/"+file+".csv")
    os.makedirs(output, exist_ok=True)
    with open("output/"+file+".csv", 'w', newline='') as f:
        writer = csv.writer(f)
        header = ['Origen'] + destinations
        writer.writerow(header)
        for key, values in data.items():
            row = [key] + [v if v is not None else '' for v in values] + [''] * (max_cols - len(values))
            writer.writerow(row)

def closest_destinations_features(origin, destinations):
    closest = {}
    print(project.mapLayersByName(origin))
    origin_layer = project.mapLayersByName(origin)[0]
    origin_features = list(origin_layer.getFeatures())
    destination_layers = [project.mapLayersByName(dest)[0] for dest in destinations]
    destination_features = [list(layer.getFeatures()) for layer in destination_layers]

    for origin_feat in origin_features:
        origin_id = origin_feat[identifiers[origin_layer.name()]]
        closest_feats = []
        for i, dest_layer_feats in enumerate(destination_features):
            dest_name = destinations[i]
            filtered_dest_feats = []
            # Filtro
            if dest_name in ["Hospitales grupo 2", "Hospitales grupo 3", "Salud mental"]:
                if 'COD' in origin_feat.fields().names():
                    origin_cod = origin_feat['COD']
                    filtered_dest_feats = [f for f in dest_layer_feats if f['COD'] == origin_cod]
            elif dest_name == "Juzgados":
                if 'PART_JUD' in origin_feat.fields().names():
                    origin_part_jud = origin_feat['PART_JUD']
                    filtered_dest_feats = [f for f in dest_layer_feats if f['PART_JUD'] == origin_part_jud]
            else:
                filtered_dest_feats = dest_layer_feats
                
            if dest_name in ["Hospitales grupo 2", "Hospitales grupo 3"]:
                added = [f[identifiers[dest_name]] for f in filtered_dest_feats]
                closest_feats.append(added)
                continue
            # Busca el destino más cercano (feature)
            min_dist = float('inf')
            min_feat = None
            for dest_feat in filtered_dest_feats:
                dist = QgsDistanceArea().measureLine(
                    origin_feat.geometry().centroid().asPoint(),
                    dest_feat.geometry().centroid().asPoint()
                )
                if dist < min_dist:
                    min_dist = dist
                    min_feat = dest_feat
            # Guardamos sus identificadores
            closest_feats.append(min_feat[identifiers[dest_name]] if min_feat else None)
        closest[origin_id] = closest_feats
    return closest


# Matriz de distancias filtrada
distance_dict = distance_matrix_filtered(origin, destinations)
dict_to_json(distance_dict, 'distance_matrix')

# Distancias medias a cada destino
avg_distance_dict = average_distance(distance_dict)
dict_to_json(avg_distance_dict, 'distance_matrix_average')

# json a csv
json_to_csv('distance_matrix_average')

closest_dict = closest_destinations_features(origin,destinations)
dict_to_json(closest_dict,'closest_destinations')

