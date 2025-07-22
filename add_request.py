from pathlib import Path
import pickle
import json
from collections import defaultdict
import numpy as np
import pandas as pd


destinations = ['hospitales_das_grupo_coords_3','hospitales_das_grupo_coords_2','bomberos_coords','juzgados','saludmental']

PATH = "C:/Users/raulc/Desktop/2025/TFG"
pickles_folder_path = PATH+"/pickles"
pickles_pathlist = list(Path(pickles_folder_path).glob('**/*.pkl'))

results_folder_path = PATH+"/results"
results_pathlist = list(Path(results_folder_path).glob('**/*.json'))

cords_name_path = pickles_folder_path+"/cords_name.pkl" #cordenadas-nombre
with open(cords_name_path, 'rb') as file:
    cords_name = pickle.load(file)
    # print(cords_name)

missing_path = pickles_folder_path+"/missing.pkl" #cordenadas-destino que le falta
with open(missing_path, 'rb') as file:
    missing = pickle.load(file)
    # print(missing)

pairs_path = pickles_folder_path+"/pairs.pkl" #cordenadas-[cordenadas_destinos]
with open(pairs_path, 'rb') as file:
    pairs = pickle.load(file)
    # print(pairs)

relations_path = pickles_folder_path+"/relations.pkl" #nombres-tipo de destino-nombres de destinos
with open(relations_path, 'rb') as file:
    relations = pickle.load(file)

final_results = {}
for path in results_pathlist:
    pathstr = str(path)
    origin = path.stem[:-4]
    args = path.stem[-4:]
    with open(pathstr,'rb') as file:
        results = json.load(file)["rows"][0]["elements"]
        if origin not in final_results.keys():
            final_results[origin] = {}
        for key in destinations:
            if relations[origin][key] == None:
                results.insert(destinations.index(key),None)
        for i in range(len(results)):
            if results[i] == None:
                if destinations[i] not in final_results[origin].keys():
                        final_results[origin][destinations[i]] = {}
                final_results[origin][destinations[i]]["name"] = "NINGUNO"
                final_results[origin][destinations[i]]["distance"+args]=None
                final_results[origin][destinations[i]]["duration"+args]=None
            else:
                if results[i]["status"] == "ZERO_RESULTS":
                    print("AAAAAAAAAAA")
                    print(origin)
                    if destinations[i] not in final_results[origin].keys():
                        final_results[origin][destinations[i]] = {}
                    final_results[origin][destinations[i]]["name"] = relations[origin][destinations[i]]
                    final_results[origin][destinations[i]]["distance"+args]=None
                    final_results[origin][destinations[i]]["duration"+args]=None
                else:
                    if destinations[i] not in final_results[origin].keys():
                        final_results[origin][destinations[i]] = {}
                    final_results[origin][destinations[i]]["name"] = relations[origin][destinations[i]]
                    final_results[origin][destinations[i]]["distance"+args]=results[i]["distance"]["value"]
                    final_results[origin][destinations[i]]["duration"+args]=results[i]["duration"]["value"]
        
clean_version = [["NOMBRE","HOSPITAL3","DIST_HOSPITAL3","DURACION_HOSPITAL3","HOSPITAL2","DIST_HOSPITAL2","DURACION_HOSPITAL2","BOMBEROS","DIST_BOMBEROS","DURACION_BOMBEROS","JUZGADOS","DIST_JUZGADOS","DURACION_JUZGADOS","SALUDMENTAL","DIST_SALUDMENTAL","DURACION_SALUDMENTAL"]]
for key in final_results.keys():
    hospital_3_name = final_results[key]["hospitales_das_grupo_coords_3"]["name"]
    hospital_3_dists = []
    hospital_3_durations = []
    for medio in ["b","c"]:
        for hora in ["p","n"]:
            if final_results[key]["hospitales_das_grupo_coords_3"]["distance_"+medio+"_"+hora] is not None:
                hospital_3_dists.append(final_results[key]["hospitales_das_grupo_coords_3"]["distance_"+medio+"_"+hora])
                hospital_3_durations.append(final_results[key]["hospitales_das_grupo_coords_3"]["duration_"+medio+"_"+hora])
    hospital_3_dist = np.mean(hospital_3_dists)
    hospital_3_duration = np.mean(hospital_3_durations)
    
    hospital_2_name = final_results[key]["hospitales_das_grupo_coords_2"]["name"]
    hospital_2_dists = []
    hospital_2_durations = []
    for medio in ["b","c"]:
        for hora in ["p","n"]:
            if final_results[key]["hospitales_das_grupo_coords_2"]["distance_"+medio+"_"+hora] is not None:
                hospital_2_dists.append(final_results[key]["hospitales_das_grupo_coords_2"]["distance_"+medio+"_"+hora])
                hospital_2_durations.append(final_results[key]["hospitales_das_grupo_coords_2"]["duration_"+medio+"_"+hora])
    hospital_2_dist = np.mean(hospital_2_dists)
    hospital_2_duration = np.mean(hospital_2_durations)    
    
    bomberos_name = final_results[key]["bomberos_coords"]["name"]
    bomberos_dists = []
    bomberos_durations = []
    for medio in ["b","c"]:
        for hora in ["p","n"]:
            if final_results[key]["bomberos_coords"]["distance_"+medio+"_"+hora] is not None:
                bomberos_dists.append(final_results[key]["bomberos_coords"]["distance_"+medio+"_"+hora])
                bomberos_durations.append(final_results[key]["bomberos_coords"]["duration_"+medio+"_"+hora])
    bomberos_dist = np.mean(bomberos_dists)
    bomberos_duration = np.mean(bomberos_durations)    

    juzgados_name = final_results[key]["juzgados"]["name"]
    juzgados_dists = []
    juzgados_durations = []
    for medio in ["b","c"]:
        for hora in ["p","n"]:
            if final_results[key]["juzgados"]["distance_"+medio+"_"+hora] is not None:
                juzgados_dists.append(final_results[key]["juzgados"]["distance_"+medio+"_"+hora])
                juzgados_durations.append(final_results[key]["juzgados"]["duration_"+medio+"_"+hora])
    juzgados_dist = np.mean(juzgados_dists)
    juzgados_duration = np.mean(juzgados_durations)    

    saludmental_name = final_results[key]["saludmental"]["name"]
    saludmental_dists = []
    saludmental_durations = []
    for medio in ["b","c"]:
        for hora in ["p","n"]:
            if final_results[key]["saludmental"]["distance_"+medio+"_"+hora] is not None:
                saludmental_dists.append(final_results[key]["saludmental"]["distance_"+medio+"_"+hora])
                saludmental_durations.append(final_results[key]["saludmental"]["duration_"+medio+"_"+hora])
    saludmental_dist = np.mean(saludmental_dists)
    saludmental_duration = np.mean(saludmental_durations)     
    
    clean_version.append([int(key),hospital_3_name,hospital_3_dist,hospital_3_duration,hospital_2_name,hospital_2_dist,hospital_2_duration,bomberos_name,bomberos_dist,bomberos_duration,juzgados_name,juzgados_dist,juzgados_duration,saludmental_name,saludmental_dist,saludmental_duration])
    
header = clean_version[0]
rows = clean_version[1:]

# Crear el DataFrame correctamente
df = pd.DataFrame(rows, columns=header)
print(df.dtypes)
df.to_csv("out.csv",index=False)

# for path in results_pathlist:
#     path.stem
#     pathstr = str(path)
    # print(path.stem)
    # with open(pathstr, 'rb') as file:
    #     result = json.load(file)
    # print(pkl)
