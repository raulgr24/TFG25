import pandas as pd
import googlemaps
from itertools import tee
import pickle
import json
import urllib.parse as urlp
from pathlib import Path
import datetime
import file_creator_nuevo as fc
import os

API_KEY = "***REMOVED***"
PATH = "C:/Users/raulc/Desktop/2025/TFG/jsons/"
modes = ["driving", "transit"]
transit_modes = ["bus", "subway", "train"]
hours = [datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month,  datetime.datetime.now().day, 8)+datetime.timedelta(days=1),
         datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month,  datetime.datetime.now().day, 12)+datetime.timedelta(days=1),
         datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month,  datetime.datetime.now().day, 16)+datetime.timedelta(days=1)]
gmaps =googlemaps.Client(key=API_KEY)
# pathlist = Path(PATH+"Adaro.json")
# json_paths = [
#     Path(PATH+"Adaro.json"),
#     Path(PATH+"Ajalvir.json")
#               ]




def request_diff_jsons():
    pathlist = Path("C:/Users/raulc/Desktop/2025/TFG/jsons/").glob('**/*.json')
    json_paths = list(pathlist)
    for path in json_paths:
        pathstr = str(path)
        with open(pathstr, 'rb') as file:
            nucleo = json.load(file)
        origins = (nucleo["origins"][0]["lat"],nucleo["origins"][0]["lng"])
        destinations = []
        for destination in  nucleo["destinations"]:
            destinations.append((destination["lat"],destination["lng"]))
            
        result = gmaps.distance_matrix(origins,
                                    destinations,
                                    mode='driving',
                                    departure_time=datetime.datetime(2025,6,19,8)) # HORA PUNTA EN COCHE
        out ="C:/Users/raulc/Desktop/2025/TFG/results/"+path.stem+"_c_p.json"
        with open(out,'w') as outfile:
            json.dump(result, outfile, indent=4)
            
        result = gmaps.distance_matrix(origins,
                                    destinations,
                                    mode='driving',
                                    departure_time=datetime.datetime(2025,6,19,11)) # HORA DE MENOS TRAFICO EN COCHE
        out ="C:/Users/raulc/Desktop/2025/TFG/results/"+path.stem+"_c_n.json"
        with open(out,'w') as outfile:
            json.dump(result, outfile, indent=4)
            
        result = gmaps.distance_matrix(origins,
                                    destinations,
                                    mode='transit',
                                    transit_mode="bus",
                                    departure_time=datetime.datetime(2025,6,19,8)) # HORA PUNTA EN BUS
        out ="C:/Users/raulc/Desktop/2025/TFG/results/"+path.stem+"_b_p.json"
        with open(out,'w') as outfile:
            json.dump(result, outfile, indent=4)
            
        result = gmaps.distance_matrix(origins,
                                    destinations,
                                    mode='transit',
                                    transit_mode="bus",
                                    departure_time=datetime.datetime(2025,6,19,11)) # HORA DE MENOS TRAFICO EN BUS
        out ="C:/Users/raulc/Desktop/2025/TFG/results/"+path.stem+"_b_n.json"
        with open(out,'w') as outfile:
            json.dump(result, outfile, indent=4)


def request_same_json():
    path = Path("C:/Users/raulc/Desktop/TFG25/output/closest_destinations_cords.json")
    pathstr = str(path)
    full_result = {}
    with open(pathstr, 'rb') as file:
        json_file = json.load(file)
        for origin in json_file:
            full_result[origin] = {}
            origins = (json_file[origin]["cords"][0],json_file[origin]["cords"][1])
            destinations = []
            for item in json_file[origin]["destinations"]:
                if item:
                    if isinstance(item[0], list):
                        destinations.extend(item)
                    else:
                        destinations.append(item)
            for mode in modes:
                for hour in hours:
                    if mode == "transit":
                        for transit_mode in transit_modes:
                            result = gmaps.distance_matrix(origins,
                                                           destinations,
                                                           mode=mode,
                                                           transit_mode=transit_mode,
                                                           departure_time=hour)
                            out = f"C:/Users/raulc/Desktop/TFG25/results/{path.stem}_{mode}_{transit_mode}_{hour.strftime('%H')}.json"
                            full_result[origin][f"{path.stem}_{mode}_{transit_mode}_{hour.strftime('%H')}"] = result
                            with open(out, 'w') as outfile:
                                json.dump(result, outfile, indent=4)
                    else:
                        result = gmaps.distance_matrix(origins,
                                                       destinations,
                                                       mode=mode,
                                                       departure_time=hour)
                        out = f"C:/Users/raulc/Desktop/TFG25/results/{path.stem}_{mode}_{hour.strftime('%H')}.json"
                        full_result[origin][f"{path.stem}_{mode}_{hour.strftime('%H')}"] = result
                        with open(out, 'w') as outfile:
                            json.dump(result, outfile, indent=4)
    return full_result

def element_count(combinations = 0):
    c1 = 0
    c2 = 0
    c3 = 0
    path = Path("C:/Users/raulc/Desktop/TFG25/output/closest_destinations_cords.json")
    pathstr = str(path)
    with open(pathstr, 'rb') as file:
        json_file = json.load(file)
        for origin in json_file:
            c1 +=1
            for item in json_file[origin]["destinations"]:
                if item:
                    if isinstance(item[0], list):
                        c2 += len(item)
                    else:
                        c2 += 1
        for mode in modes:
                for hour in hours:
                    if mode == "transit":
                        for transit_mode in transit_modes:
                            c3 +=1
                    else:
                        c3+=1
    c3 -=combinations
    elements = c2*c3
    print(f"Número de orígenes: {c1}, Número de pares origen-destinos: {c2}, Combinaciones posibles de parámetros: {c3}")
    print(f"Total combinaciones: ({c2}*{c3}) = {elements}")
    
    price = 0
    print("10000 son gratis")
    if elements>10000:
        if elements>100000:
            price += (elements-100000)/1000*4
            price += 90000/1000*10
        else:
            price += (elements-10000)/1000*5
    print(f"Precio total: {price} $")

    return(c1, c2, c3)
element_count()
element_count(2)
element_count(4)
element_count(6)
element_count(8)


# fc.dict_to_json(request_same_json(), 'full_API_results')

# with open("C:/Users/raulc/Desktop/2025/TFG/jsons/Base Aérea.json", 'rb') as file:
#     nucleo = json.load(file)
# origins = (nucleo["origins"][0]["lat"],nucleo["origins"][0]["lng"])
# destinations = []
# for destination in  nucleo["destinations"]:
#     destinations.append((destination["lat"],destination["lng"]))
# print(gmaps.distance_matrix(origins,destinations, mode='driving'))

