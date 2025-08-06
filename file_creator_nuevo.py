from qgis.core import *
import json
import numpy as np
import csv
import os
from pathlib import Path
import pandas as pd

# Initialize the QGIS resources at the beginning of the scrip https://docs.qgis.org/3.40/en/docs/pyqgis_developer_cookbook/intro.html#using-pyqgis-in-standalone-scripts
# Supply path to qgis install location
QgsApplication.setPrefixPath("C:/Program Files/QGIS 3.40.7", True)

qgs = QgsApplication([], False)
qgs.initQgis()
identifiers={
    "Centroides bus":"CDTNUCLEO",
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
# Orígenes y destinos
origin = 'Centroides bus'
destinations = ['Hospitales grupo 3',
                'Hospitales grupo 2',
                'Bomberos',
                'Juzgados',
                'Salud mental']

def json_to_dict(filename):
    """
    Abre el JSON y lo devuelve como diccionario
    """
    with open("output/"+filename+".json","r") as file:
        data = json.load(file) 
    return data

def dict_to_json(data, filename):
    """ 
    Toma un diccionario data y lo guarda en "output/<filename>.json"
    Input:
        data: diccionario
        filename: String del archivo en el que se quiere guardar
    Output: None
    """
    output = os.path.dirname("output/"+filename+".json")
    os.makedirs(output, exist_ok=True)
    with open("output/"+filename+".json","w") as f:
        json.dump(data,f,indent=4)

def json_to_csv(file):
    """ 
    Deprecado
     """
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

def dict_to_csv(dict, file):
    """
    Usa pandas para guardar diccionario como csv
    """
    df = pd.DataFrame.from_dict(dict,orient = "index")
    df.to_csv("output/"+file+".csv")

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

def average_distance(distance_dict):
    """ 
    !Deprecada!
    Toma todas las distancias y hace la media """
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

def closest_destinations_features(origin, destinations):
    """ 
    Lee el proyecto QGIS y devuelve diccionario con todos los orígenes y sus destinos más cercanos
    """
    closest = {}
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

def closest_destinations_cords_nuevo(origin, destinations):
    """
    Lee el proyecto QGIS y devuelve un diccionario
    Para cada origen guarda sus coordenadas y las coordenadas de los destinos más cercanos
    """
    closest = {}
    origin_layer = project.mapLayersByName(origin)[0]
    origin_features = list(origin_layer.getFeatures())
    destination_layers = [project.mapLayersByName(dest)[0] for dest in destinations]
    destination_features = [list(layer.getFeatures()) for layer in destination_layers]

    crs_src = origin_layer.crs()
    crs_dest = QgsCoordinateReferenceSystem("EPSG:4326")
    transform = QgsCoordinateTransform(crs_src, crs_dest, QgsProject.instance())
    for origin_feat in origin_features:
        origin_id = origin_feat[identifiers[origin_layer.name()]]
        origin_point = origin_feat.geometry().asPoint()
        origin_ll = transform.transform(origin_point)
        origin_cords = [origin_ll.y(),origin_ll.x()]
        # origin_cords = (origin_feat["lat"],origin_feat["lng"])
        closest[origin_id]={"cords":origin_cords, "destinations":[]}
        # closest_feats = []
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
                added = [[transform.transform(f.geometry().asPoint()).y(),
                          transform.transform(f.geometry().asPoint()).x()] 
                        for f in filtered_dest_feats]
                closest[origin_id]["destinations"].append(added)
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
            pt = transform.transform(min_feat.geometry().asPoint())
            closest[origin_id]["destinations"].append([pt.y(), pt.x()])
            # closest[origin_id]["destinations"].append([min_feat["lat"],min_feat["lng"]] if min_feat else None)
        # closest[origin_id]["destinations"] = closest_feats
    return closest

def closest_destinations_cords(origin, destinations):
    """
    Lee el proyecto QGIS y devuelve un diccionario
    Para cada origen guarda sus coordenadas y las coordenadas de los destinos más cercanos
    """
    closest = {}
    origin_layer = project.mapLayersByName(origin)[0]
    origin_features = list(origin_layer.getFeatures())
    destination_layers = [project.mapLayersByName(dest)[0] for dest in destinations]
    destination_features = [list(layer.getFeatures()) for layer in destination_layers]

    for origin_feat in origin_features:
        origin_id = origin_feat[identifiers[origin_layer.name()]]
        origin_cords = (origin_feat["lat"],origin_feat["lng"])
        closest[origin_id]={"cords":origin_cords, "destinations":[]}
        # closest_feats = []
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
                added = [[f["lat"],f["lng"]] for f in filtered_dest_feats]
                closest[origin_id]["destinations"].append(added)
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
            closest[origin_id]["destinations"].append([min_feat["lat"],min_feat["lng"]] if min_feat else None)
        # closest[origin_id]["destinations"] = closest_feats
    return closest

def get_hospital_num():
    """ 
    Abre closest_destinations.json
    Devuelve JSON con cantidad de hospitales de grupo 3 y hospitales de grupo 2
    """
    path = Path("C:/Users/raulc/Desktop/TFG25/output/closest_destinations.json")
    with open(path, 'r') as file:
        data = json.load(file)
    output = {}
    for key,value in data.items():
        output[key]=(len(value[0]),len(value[1]))
    return output
        
def json_to_csv_results(file):
    """
    Deprecado (creo)
    """
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

def readable_results(file, mode  = "distance"):
    """
    Toma el json de resultados de las consultas y lo devuelve en un formato más legible
    mode = 'distance'/'duration'
    """
    data = json_to_dict(file)
    output = {}
    for origin_name, all_destinations in data.items():
        result_per_origin = {}
        for dest_index,destination in enumerate(all_destinations):
            for mode_hour, info in destination.items():
                print(info)
                if mode == "distance":
                    result_per_origin[f"dest_{str(dest_index)}_{mode_hour}"] = info["routes"][0]["distanceMeters"] if info else None
                else:
                    result_per_origin["dest"+str(dest_index)+mode_hour] =int(info["routes"][0]["duration"][:-1])
        output[origin_name]=result_per_origin
    return output
            
def get_empty_results(file):
    """
    Devuelve diccionario con los origenes que todavía tienen resultados mal dados y el número de resultados vacíos
    """
    results = readable_results("routes_API_results_dump")
    o = {k: sum(1 for val in v.values() if val == None) for k,v in results.items()}
    o = {k: v for k,v in o.items() if v!=0}
    return o

def get_penalization(old, new):
    old_layer = project.mapLayersByName(old)[0]
    old_features = list(old_layer.getFeatures())
    new_layer = project.mapLayersByName(new)[0]
    new_features = list(new_layer.getFeatures())

    penalizations = {}

    for old_feature in old_features:
        for new_feature in new_features:
            if old_feature["CDTNUCLEO"]==new_feature["CDTNUCLEO"]:
                dist = QgsDistanceArea().measureLine(
                    old_feature.geometry().centroid().asPoint(),
                    new_feature.geometry().centroid().asPoint()
                )
                if dist>0:
                    penalizations[old_feature["CDTNUCLEO"]] = dist
                    continue
    
    return penalizations