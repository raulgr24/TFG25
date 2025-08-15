import qgis.core as qgis
from qgis.utils import iface
from PyQt5.QtCore import QVariant
import json
import numpy as np
import csv
import os
from pathlib import Path
import pandas as pd
import warnings
from colorama import Fore
# Initialize the QGIS resources at the beginning of the scrip https://docs.qgis.org/3.40/en/docs/pyqgis_developer_cookbook/intro.html#using-pyqgis-in-standalone-scripts
# Supply path to qgis install location
qgis.QgsApplication.setPrefixPath("C:/Program Files/QGIS 3.40.7", True)

qgs = qgis.QgsApplication([], False)
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
project = qgis.QgsProject.instance()
if project:
    project.read("./tfg_project.qgz")
    names = [layer.name() for layer in project.mapLayers().values()]
else:
    print("No project")
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
    df.to_csv("output/"+file+".csv", index=False, na_rep="", quoting=csv.QUOTE_MINIMAL)

def results_dict_to_csv(dict, file):
    df0=pd.DataFrame(columns=["Nucleo","POB"]) # type: ignore
    for orig in list(project.mapLayersByName(origin)[0].getFeatures()):
        df0.loc[len(df0)]= [orig["CDTNUCLEO"],orig['POB']]
    index = "Nucleo"
    df = pd.DataFrame.from_dict(dict, orient = "index")
    df.index.name = index
    df = df.reset_index()
    print(df[index])
    num_cols = df.columns.drop(index)
    df[num_cols] = df[num_cols].replace(r'^\s*$',pd.NA, regex =True)
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors = 'coerce')
    df[num_cols] = df[num_cols].astype("Int64")
    new_cols = ["hospt3","hospt2","bomberos","csmental","juzgados"]
    for col in new_cols:

        df[f"mean_dis_{col}"]= df[[c for c in df.columns if f"dis_{col}" in c]].mean(axis=1)
        df[f"mean_dur_{col}"]= df[[c for c in df.columns if f"dur_{col}" in c]].mean(axis=1)
    
    df = df.reindex(sorted(df.columns), axis=1)
    df[index] = df[index].astype("string").str.zfill(7)

    df["mean_dis_all"] = df[[c for c in df.columns if f"mean_dis_" in c]].mean(axis=1)
    df["mean_dur_all"] = df[[c for c in df.columns if f"mean_dur_" in c]].mean(axis=1)
    df = pd.merge(df,df0,on='Nucleo',how='inner')
    for col in df.columns:
        if "mean" in col:
            df[f"weigh_{col}"] = df[col]*df["POB"]
    df.to_csv(f"output/{file}.csv", index = False, na_rep="", quoting = csv.QUOTE_MINIMAL)


# Suprimir warnings de deprecación de QgsField (no hay alternativa en esta versión)
warnings.filterwarnings("ignore", message="QgsField.*is deprecated", category=DeprecationWarning)

def merge_layer_with_dict(layer_name, data_dict, join_field, output_name, save_as_file=True, output_dir="Datos nuevos", verbose = False):
    """
    Función modular para fusionar una capa QGIS con un diccionario de datos.
    
    Args:
        layer_name (str): Nombre de la capa QGIS existente
        data_dict (dict): Diccionario con datos a fusionar {key: {col1: val1, col2: val2, ...}}
        join_field (str): Nombre del campo en la capa QGIS para hacer la unión
        output_name (str): Nombre para la capa/archivo resultante
        save_as_file (bool): Si True, guarda como .gpkg; si False, crea capa en memoria
        output_dir (str): Directorio donde guardar el archivo (solo si save_as_file=True)
    
    Returns:
        QgsVectorLayer: Nueva capa creada, o None si hay error
    """
    
    try:
        # 1. BUSCAR SI LA CAPA EXISTE
        if verbose:
            print(f"{Fore.YELLOW}Buscando capa: '{layer_name}'")
        layers = project.mapLayersByName(layer_name)
        if not layers:
            available_layers = [layer.name() for layer in project.mapLayers().values()]
            print(f"{Fore.RED} Capa '{layer_name}' no existe en el proyecto.")
            print(f"Capas del proyecto: {available_layers}")
            return None
        
        source_layer = layers[0]
        print(f"{Fore.GREEN}Capa encontrada: {source_layer.name()} ({source_layer.featureCount()} features)")
        
        # 2. Comprobar si el campo por el que se va a hacer el merge existe
        field_names = source_layer.fields().names()
        if join_field not in field_names:
            print(f"{Fore.RED}Campo '{join_field}' no encontrado en la capa.")
            print(f"Campos disponibles: {field_names}")
            return None
        if verbose: 
            print(f"{Fore.GREEN}Campo de unión encontrado: '{join_field}'")
        
        # 3. Procesar diccionario de datos
        if not data_dict:
            print("{Fore.RED}El diccionario de datos está vacío")
            return None
        
        if verbose:
            print(f"{Fore.GREEN}Diccionario procesado: {len(data_dict)} registros")
        
        # Convertir diccionario a DataFrame para mejor manejo
        df = pd.DataFrame.from_dict(data_dict, orient="index")
        df.index.name = join_field
        print(df)
        return merge_layer_with_dataframe(
            source_layer = source_layer,
            dataframe = df,
            join_field = join_field,
            output_name = output_name
        )
        
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error en el proceso: {e}")
        import traceback
        traceback.print_exc()
        return None


def merge_layer_with_dataframe(source_layer, dataframe, join_field, output_name, save_as_file=True, output_dir="Datos nuevos", verbose=True):
    """
    Función optimizada para fusionar capa QGIS con DataFrame.
    
    Args:
        source_layer: Capa QGIS existente
        dataframe (pd.DataFrame): DataFrame con datos a fusionar
        join_field (str): Campo en la capa QGIS para hacer la unión
        output_name (str): Nombre para la capa/archivo resultante
        save_as_file (bool): Si True, guarda como .gpkg; si False, crea capa en memoria
        output_dir (str): Directorio donde guardar el archivo
        verbose (bool): Mostrar información detallada 
    Returns:
        QgsVectorLayer: Nueva capa creada
    """
    df = dataframe # Trabajar con copia para no modificar original
    
    # Limpiar y convertir datos numéricos
    for col in df.columns:
        # Intentar convertir a numérico, mantener como string si falla
        df[col] = pd.to_numeric(df[col],errors='coerce')
        # Limpiar espacios en blanco para strings
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace('', pd.NA)
    
    if verbose: 
        print(f"Columnas a añadir:")
        for col_index, col in enumerate(list(df.columns)):
            print(f"  {col_index}\t{col}")
    
    # Crear nueva capa con estructura expandida
    crs = source_layer.crs()
    geom_type = source_layer.wkbType()
    
    new_layer = qgis.QgsVectorLayer(
        f"{qgis.QgsWkbTypes.displayString(geom_type)}?crs={crs.authid()}", 
        output_name, 
        "memory"
    )
    
    # Añadir campos originales
    original_fields = []
    for field in source_layer.fields():
        original_fields.append(field)
    
    new_layer.dataProvider().addAttributes(original_fields)
    
    # Añadir campos del DataFrame
    new_fields = []
    for col in df.columns:
        field_name = str(col)
        
        # Crear campo copiando estructura de un campo existente
        if source_layer.fields().count() > 0:
            template_field = source_layer.fields().at(0)
            
            # Determinar tipo según dtype del DataFrame
            if df[col].dtype in ['int64', 'int32', 'Int64']:
                # Buscar plantilla entero
                int_template = None
                for existing_field in source_layer.fields():
                    if existing_field.type() == QVariant.Int:
                        int_template = existing_field
                        break
                
                new_field = qgis.QgsField(int_template if int_template else template_field)
                new_field.setName(field_name)
                    
            elif df[col].dtype in ['float64', 'float32', 'Float64']:
                # Buscar plantilla float
                float_template = None
                for existing_field in source_layer.fields():
                    if existing_field.type() in [QVariant.Double, QVariant.Int]:
                        float_template = existing_field
                        break
                
                new_field = qgis.QgsField(float_template if float_template else template_field)
                new_field.setName(field_name)
                    
            else:
                # Para strings
                string_template = None
                for existing_field in source_layer.fields():
                    if existing_field.type() == QVariant.String:
                        string_template = existing_field
                        break
                
                new_field = qgis.QgsField(string_template if string_template else template_field)
                new_field.setName(field_name)
            
            new_fields.append(new_field)
    
    # Añadir todos los campos nuevos
    if new_fields:
        new_layer.dataProvider().addAttributes(new_fields)
    
    new_layer.updateFields()
    
    # Crear diccionario de búsqueda desde DataFrame
    # Si el DataFrame tiene índice con el join_field, usarlo
    if df.index.name == join_field:
        data_lookup = df.to_dict('index')
    else:
        # Si join_field es una columna, usar esa columna como índice
        if join_field in df.columns:
            data_lookup = df.set_index(join_field).to_dict('index')
        else:
            print(f"{Fore.RED}Campo '{join_field}' no encontrado en DataFrame")
            return None
    
    # Procesar features y fusionar datos
    features_to_add = []
    matched_count = 0
    missing_data = []
    
    for original_feature in source_layer.getFeatures():
        # Obtener valor del campo de unión
        join_value = str(original_feature[join_field])
        # Crear nueva feature
        new_feature = qgis.QgsFeature()
        new_feature.setGeometry(original_feature.geometry())
        # Copiar atributos originales
        attributes = []
        for field in source_layer.fields():
            attributes.append(original_feature[field.name()])
        
        # Añadir datos del DataFrame si existen
        if join_value in data_lookup:
            row_data = data_lookup[join_value]
            for col in df.columns:
                if col != join_field:  # No duplicar el campo de unión
                    value = row_data.get(col, None)
                    # Convertir NaN/None apropiadamente
                    if pd.isna(value):
                        attributes.append(None)
                    else:
                        attributes.append(value)
            matched_count += 1
        else:
            # Añadir valores nulos para columnas del DataFrame
            for col in df.columns:
                if col != join_field:
                    attributes.append(None)
            missing_data.append(join_value)
        new_feature.setAttributes(attributes)
        features_to_add.append(new_feature)
    
    # Añadir features a la nueva capa
    new_layer.dataProvider().addFeatures(features_to_add)
    new_layer.updateExtents()
    # Guardar o añadir según configuración
    final_layer = None
    if save_as_file:
        # Guardar como archivo
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_path = os.path.join(output_dir, f"{output_name}.gpkg")
        transform_context = qgis.QgsCoordinateTransformContext()
        options = qgis.QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GPKG"
        options.fileEncoding = "UTF-8"
        options.layerName = output_name
        
        error = qgis.QgsVectorFileWriter.writeAsVectorFormatV3(
            new_layer, 
            output_path, 
            transform_context, 
            options
        )
        
        if error[0] == qgis.QgsVectorFileWriter.NoError:
            # Cargar archivo guardado
            final_layer = qgis.QgsVectorLayer(output_path, output_name, "ogr")
            if final_layer.isValid():
                qgis.QgsProject.instance().addMapLayer(final_layer)
                if verbose:
                    print(f"{Fore.GREEN}Archivo guardado: {output_path}")
            else:
                print(f"{Fore.RED}Error cargando archivo: {output_path}")
                return None
        else:
            print(f"{Fore.RED}Error guardando archivo (código {error[0]}): {error[1]}")
            return None
    else:
        # Mantener en memoria
        if new_layer.isValid():
            qgis.QgsProject.instance().addMapLayer(new_layer)
            final_layer = new_layer
        else:
            print(f"{Fore.RED}La capa en memoria no es válida")
            return None
    
    # Actualizar interfaz
    if final_layer and hasattr(iface, 'mapCanvas'):
        iface.mapCanvas().setExtent(final_layer.extent())
        iface.mapCanvas().refresh()
        final_layer.triggerRepaint()
    
    # Resumen
    if verbose:
        print(f"{Fore.LIGHTGREEN_EX}Proceso completado")
        print(f"{Fore.CYAN}Features totales: {len(features_to_add)}")
        print(f"{Fore.CYAN}Features con datos fusionados: {matched_count}")
        
        if missing_data:
            print(f"{Fore.LIGHTYELLOW_EX}Features sin datos del diccionario: {len(missing_data)}")
            if len(missing_data) <= 10:
                print(f"   Sin datos: {missing_data}")
            else:
                print(f"   Primeros 10 sin datos: {missing_data[:10]}...")
    
    # Guardar proyecto permanentemente
    if final_layer and final_layer.isValid():
        project.write()
        if verbose:
            print(f"{Fore.LIGHTGREEN_EX}Capa '{output_name}' añadida permanentemente al proyecto")
    
    return final_layer    
def municipios_stats(centroides_layer, municipios_layer):
    try:  
        # 1. Cargar las capas
        print(f"{Fore.YELLOW}Buscando capa: '{centroides_layer}'")
        centroides = project.mapLayersByName(centroides_layer)
        if not centroides:
            available_layers = [layer.name() for layer in project.mapLayers().values()]
            print(f"{Fore.RED} Capa '{centroides}' no existe en el proyecto.")
            print(f"Capas del proyecto: {available_layers}")
            return None

        centroides = centroides[0]

        print(f"{Fore.GREEN}Capa encontrada: {centroides.name()} ({centroides.featureCount()} features)")
        print(f"{Fore.YELLOW}Buscando capa: '{municipios_layer}'")
        municipios = project.mapLayersByName(municipios_layer)
        if not municipios:
            available_layers = [layer.name() for layer in project.mapLayers().values()]
            print(f"{Fore.RED} Capa '{municipios}' no existe en el proyecto.")
            print(f"Capas del proyecto: {available_layers}")
            return None
        municipios = municipios[0]

        print(f"{Fore.GREEN}Capa encontrada: {municipios.name()} ({municipios.featureCount()} features)")
        # 2. Comprobar que CMUN está en ambas capas (no debería hacer falta)
        centroides_fields = centroides.fields().names()
        municipios_fields = municipios.fields().names()
        if "CMUN" not in centroides_fields or "CMUN" not in municipios_fields:
            print(f"{Fore.RED}Campo 'CMUN' no encontrado en las capa.")
            print(f"Campos disponibles: 'CMUN'")
            return None
        print(f"{Fore.GREEN}'CMUN en ambas capas'")

        # 3. Sumar todos los valores de cada municipio
        used_cols = [f for f in list(centroides_fields) if f in["CMUN","POB"] or "weigh" in f]
        mun_df = pd.DataFrame(columns= used_cols) # pyright: ignore[reportArgumentType]
        mun_df = mun_df.set_index("CMUN")
        for centroide in centroides.getFeatures():
            valores = {col:centroide[col] for col in used_cols}
            for key, value in valores.items():
                if isinstance(value, QVariant):  # Si es QVariant
                    if value.isNull():
                        valores[key]=0.0
                    else:
                        valores[key] = value.value()
                elif value is None:
                    valores[key] = 0
            if centroide["CMUN"] in mun_df.index:
                for col,valor in valores.items():
                    if col!="CMUN":
                        mun_df.loc[valores["CMUN"],col] += valor
            else:
                mun_df.loc[valores["CMUN"]] = valores
        # 4. Dividir entre la población del municipio
        col_a_dividir = [col for col in mun_df.columns if col not in ["POB","CMUN"]]
        mun_df[col_a_dividir] = mun_df[col_a_dividir].div(mun_df["POB"],axis = 0)
        print("QUE PASAAAA")
        return mun_df       
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Error en el proceso: {e}")
        import traceback
        traceback.print_exc()
        return None
# Funciones auxiliares
def list_available_layers():
    """Lista todas las capas disponibles en el proyecto QGIS actual"""
    print("Capas disponibles en el proyecto:")
    for i, layer in enumerate(project.mapLayers().values()):
        layer_type = "Vector" if hasattr(layer, 'geometryType') else "Raster"
        feature_count = layer.featureCount() if hasattr(layer, 'featureCount') else "N/A"
        print(f"  {i+1}: '{layer.name()}' ({layer_type}) - {feature_count} features")
    print()


def check_layer_fields(layer_name):
    """Función auxiliar para inspeccionar campos de una capa"""
    try:
        layer = project.mapLayersByName(layer_name)[0]
        print(f"Campos en '{layer_name}':")
        for i, field in enumerate(layer.fields()):
            print(f"  {i}: {field.name()} ({field.typeName()})")
        
        # Mostrar algunos valores de ejemplo
        print("\nEjemplos de valores:")
        for i, feature in enumerate(layer.getFeatures()):
            if i < 3:  # Solo 3 ejemplos
                print(f"  Feature {i}:")
                for field_name in layer.fields().names()[:5]:  # Solo primeros 5 campos
                    print(f"    {field_name}: {feature[field_name]}")
            else:
                break
                
    except Exception as e:
        print(f"Error inspeccionando capa {layer_name}: {e}")


def distance_matrix_filtered(origin, destinations):
    origin_layer = project.mapLayersByName(origin)[0]
    destination_layers = [project.mapLayersByName(dest)[0] for dest in destinations]

    distance_calculator = qgis.QgsDistanceArea()
    distance_calculator.setSourceCrs(origin_layer.crs(), qgis.QgsProject.instance().transformContext())
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
                dist = qgis.QgsDistanceArea().measureLine(
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

def closest_destinations_cords_nuevo(origin: str, destinations: list[str]) -> dict[str,dict[str,list[str]]]:
    """
    Args:
        origin: String --> Origin layer name
        destinations: list[String] --> Destination layer names list
    Returns:
        dict{String: dict{String: list[String]}} --> For each origin, its coords and closest destination's cords
    Lee el proyecto QGIS y devuelve un diccionario
    Para cada origen guarda sus coordenadas y las coordenadas de los destinos más cercanos
    """
    closest = {}
    origin_layer = project.mapLayersByName(origin)[0]
    origin_features = list(origin_layer.getFeatures())
    destination_layers = [project.mapLayersByName(dest)[0] for dest in destinations]
    destination_features = [list(layer.getFeatures()) for layer in destination_layers]

    crs_src = origin_layer.crs()
    crs_dest = qgis.QgsCoordinateReferenceSystem("EPSG:4326")
    transform = qgis.QgsCoordinateTransform(crs_src, crs_dest, qgis.QgsProject.instance())
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
                dist = qgis.QgsDistanceArea().measureLine(
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
    if project:
        origin_layer = project.mapLayersByName(origin)[0]
        origin_features = list(origin_layer.getFeatures())
        destination_layers = [project.mapLayersByName(dest)[0] for dest in destinations]
        destination_features = [list(layer.getFeatures()) for layer in destination_layers]
    else:
        return None
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
                dist = qgis.QgsDistanceArea().measureLine(
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
    origin_hospital = json_to_dict("hosp_per_origin")
    output = {}
    for origin_name, all_destinations in data.items():
        idents = []
        idents.extend(["hospt3_"+str(k) for k in range(1,origin_hospital[origin_name][0]+1)])
        idents.extend(["hospt2_"+str(k) for k in range(1,origin_hospital[origin_name][1]+1)])
        idents.extend(["juzgados","bomberos","csmental"])
        print(origin_name,idents)
        result_per_origin = {}
        for dest_index,destination in enumerate(all_destinations):
            for mode_hour, info in destination.items():
                print(info)
                result_per_origin[f"dis_{idents[dest_index]}_{mode_hour}"] = int(info["routes"][0]["distanceMeters"]) if info else None
                result_per_origin[f"dur_{idents[dest_index]}_{mode_hour}"] =int(info["routes"][0]["duration"][:-1])
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
                dist = qgis.QgsDistanceArea().measureLine(
                    old_feature.geometry().centroid().asPoint(),
                    new_feature.geometry().centroid().asPoint()
                )
                if dist>0:
                    penalizations[old_feature["CDTNUCLEO"]] = dist
                    continue

    return penalizations

def apply_penalization(mode : str):
    penalizations = json_to_dict("penalizations")
    results = json_to_dict("requests_"+mode)
    for centro_key , penalization in penalizations.items():
        for result_key, result in results[centro_key].items():
            if "transit" in result_key:
                if mode == "duration": 
                    results[centro_key][result_key]+=int(penalization/1.4)
                if mode == "distance":
                    results[centro_key][result_key]+=int(penalization*1.5)
    return results

def get_hospital_score():
    hospital_num = json_to_dict("hosp_per_origin")
    scores = {}
    for nucleo_key, nucleo_info in hospital_num.items():
        score = 1*(1.1**nucleo_info[0])
        score = score*(1.05**nucleo_info[1])
        scores[nucleo_key]=score
        #scores[nucleo_key]=1/(nucleo_info[0]*1.4+nucleo_info[1])
    return scores
