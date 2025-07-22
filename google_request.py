import pandas as pd
import googlemaps
from itertools import tee
import pickle
import json
import urllib.parse as urlp
from pathlib import Path
import datetime
import os

API_KEY = "***REMOVED***"
PATH = "C:/Users/raulc/Desktop/2025/TFG/jsons/"

# pathlist = Path(PATH+"Adaro.json")
# json_paths = [
#     Path(PATH+"Adaro.json"),
#     Path(PATH+"Ajalvir.json")
#               ]

pathlist = Path("C:/Users/raulc/Desktop/2025/TFG/jsons/").glob('**/*.json')
json_paths = list(pathlist)
gmaps =googlemaps.Client(key=API_KEY)

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

# with open("C:/Users/raulc/Desktop/2025/TFG/jsons/Base Aérea.json", 'rb') as file:
#     nucleo = json.load(file)
# origins = (nucleo["origins"][0]["lat"],nucleo["origins"][0]["lng"])
# destinations = []
# for destination in  nucleo["destinations"]:
#     destinations.append((destination["lat"],destination["lng"]))
# print(gmaps.distance_matrix(origins,destinations, mode='driving'))

