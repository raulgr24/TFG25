#ANTES DE EJECUTAR ABRE "C:/Program Files/QGIS 3.38.3/OSGeo4W.bat", LUEGO ABRE VSC
from qgis.core import *
import json
import pickle

PAIRS_PATH = "C:/Users/raulc/Desktop/2025/TFG/pickles/pairs.pkl"
flags = {
    "need_cords_name" : True,
    "need_neighbour_file": True,
    "need_jsons" : True
}

# Initialize the QGIS resources at the beginning of the scrip https://docs.qgis.org/3.40/en/docs/pyqgis_developer_cookbook/intro.html#using-pyqgis-in-standalone-scripts
# Supply path to qgis install location
QgsApplication.setPrefixPath("C:/Program Files/QGIS 3.40.7", True)

# Create a reference to the QgsApplication.  Setting the
# second argument to False disables the GUI.
qgs = QgsApplication([], False)
qgs.initQgis()
identifiers={
    "centroides_pobl_jud_2":"CDTNUCLEO",
    'hospitales_das_grupo_coords_3':"CODIGO",
    'hospitales_das_grupo_coords_2':"CODIGO",
    "bomberos_coords":"COD_SUCA",
    'juzgados':"fid",
    'saludmental':"COD_SUCA"
}

# Load providers


# Write your code here to load some layers, use processing
# Abrimos el archivo qgz
project = QgsProject.instance()
project.read("C:/Users/raulc/Desktop/2025/TFG/centros_urbanos.qgz")

# Orígenes y destinos
origin = 'centroides_pobl_jud_2'
destinations = ['hospitales_das_grupo_coords_3',
                'hospitales_das_grupo_coords_2',
                'bomberos_coords',
                'juzgados',
                'saludmental']

def get_cords_name():
    points = [origin]+destinations
    cords = {}
    for element in points:
        print(element)
        layer =  project.mapLayersByName(element)[0]
        features=layer.getFeatures()
        for feature in features:
            cords[(feature["lat"],feature["lng"])]=feature[identifiers[element]]
    out = "C:/Users/raulc/Desktop/2025/TFG/pickles/cords_name.pkl"
    with open(out,'wb+') as outfile:
        pickle.dump(cords, outfile)
    return


def get_nearest(project,origin,destinations):
    o_layer =  project.mapLayersByName(origin)[0]
    # Origin --> Destinations dictionary
    relations = {}
    o_features=o_layer.getFeatures()                                        # Cargamos los orígenes
    for o_feat in o_features:
        relations[o_feat[identifiers[origin]]]=dict.fromkeys(destinations)   
    pairs={}
    missing={}
    missing_name = {}
    cords_name = {}
    for i in range(len(destinations)):                                          # Para cada tipo de servicio
        d_layers= project.mapLayersByName(destinations[i])        # Cargamos la capa con los puntos de ese servicio
        d_layer = d_layers[0]                                                   
        o_features=o_layer.getFeatures()                                        # Cargamos los orígenes
        for o_feat in o_features:                                               # Por cada origen
            nearest_dist = 2000000                                              # Valores iniciales de distancia mas cercana altos                                          
            nearest = None                                          
            d_features = d_layer.getFeatures()                                  # Cargamos los destinos
            for d_feat in d_features:
                if o_feat[identifiers[origin]] ==1640501:
                    print(d_feat[identifiers[destinations[i]]])
                    print(d_feat["COD"])
                    print(o_feat["COD"])
                if i in [0,1,4] and d_feat["COD"]!=o_feat["COD"]:
                    continue
                if i==3 and d_feat["PART_JUD"]!=o_feat["PART_JUD"]:
                    continue                                                                                     
                ogeom = o_feat.geometry()  
                dgeom = d_feat.geometry()
                dist = dgeom.distance(ogeom)                            # Calculamos distancia entre los puntos
                if dist<nearest_dist:                                   # Si la distancia es la mas corta para ese origen se guarda
                    nearest = d_feat
                    nearest_dist=dist
            if o_feat[identifiers[origin]] =="1640501":
                print(nearest[identifiers[destinations[i]]])
            if nearest is not None:
                if (o_feat["lat"],o_feat["lng"]) in pairs.keys():
                    pairs[o_feat["lat"],o_feat["lng"]].append((nearest["lat"],nearest["lng"]))
                else:
                    pairs[o_feat["lat"],o_feat["lng"]] = [(nearest["lat"],nearest["lng"])]
                relations[o_feat[identifiers[origin]]][destinations[i]]=nearest[identifiers[destinations[i]]]
            else:
                # print(f"A {o_feat[identifiers[origin]]} LE FALTA {destinations[i]}")
                missing[o_feat["lat"],o_feat["lng"]]=destinations[i]
                missing_name[o_feat[identifiers[origin]]]=destinations[i]
                relations[o_feat[identifiers[origin]]][destinations[i]]=None
    print(relations["1640501"])
    out = PAIRS_PATH
    with open(out,'wb+') as outfile:
        pickle.dump(pairs, outfile)
    out ="C:/Users/raulc/Desktop/2025/TFG/pickles/missing.pkl"
    with open(out,'wb+') as outfile:
        pickle.dump(missing, outfile)
    out ="C:/Users/raulc/Desktop/2025/TFG/pickles/missing_name.pkl"
    with open(out,'wb+') as outfile:
        pickle.dump(missing_name, outfile)
    out ="C:/Users/raulc/Desktop/2025/TFG/pickles/relations.pkl"
    with open(out,'wb+') as outfile:
        pickle.dump(relations, outfile)
    return

def get_jsons():
    with open(PAIRS_PATH, 'rb') as f:
        pairs = pickle.load(f)
    with open("C:/Users/raulc/Desktop/2025/TFG/pickles/cords_name.pkl",'rb') as f:
        cords_name = pickle.load(f)
    # count=1     
    for key in pairs.keys():
        out_dict = {
            "origins":[{"lat":key[0],"lng":key[1]}],
            "destinations":[],
            "travelMode": "DRIVING",
            "unitSystem": 0
        }
        for element in pairs[key]:
            out_dict["destinations"].append({"lat":element[0],"lng":element[1]})
        out ="C:/Users/raulc/Desktop/2025/TFG/jsons/"+cords_name[key]+".json"
        with open(out,'w') as outfile:
            json.dump(out_dict, outfile, indent=4)
        # count+=1
    return

# #    print(f"{key} --> {pairs[key]}")
if flags["need_cords_name"]:
    get_cords_name()
if flags["need_neighbour_file"]:
    get_nearest(project,origin,destinations)
if flags["need_jsons"]:
    get_jsons()


# Finally, exitQgis() is called to remove the
# provider and layer registries from memory
qgs.exitQgis()

