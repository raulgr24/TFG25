from urllib import response
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
import requests
import asyncio
import httpx
import file_creator_nuevo as fc

with open("api.txt") as f:
    API_KEY = f.read()
PATH = "jsons/"
MAX_CONCURRENT_REQUESTS = 50  # Límite de concurrencia
URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "routes.duration,routes.distanceMeters"
}
modes = [
    "drive",
    "transit"
         ]
hours_true = [datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month,  datetime.datetime.now().day, 8,30)+datetime.timedelta(days=2)
        ,datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month,  datetime.datetime.now().day, 11)+datetime.timedelta(days=2)
         ]
hours = [datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month,  datetime.datetime.now().day, 8,30)+datetime.timedelta(days=1)
        ,datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month,  datetime.datetime.now().day, 11)+datetime.timedelta(days=1)
         ]
gmaps =googlemaps.Client(key=API_KEY)
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

def request_diff_jsons():
    pathlist = Path("jsons/").glob('**/*.json')
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
        out ="results/"+path.stem+"_c_n.json"
        with open(out,'w') as outfile:
            json.dump(result, outfile, indent=4)
            
        result = gmaps.distance_matrix(origins,
                                    destinations,
                                    mode='transit',
                                    transit_mode="bus",
                                    departure_time=datetime.datetime(2025,6,19,8)) # HORA PUNTA EN BUS
        out ="results/"+path.stem+"_b_p.json"
        with open(out,'w') as outfile:
            json.dump(result, outfile, indent=4)
            
        result = gmaps.distance_matrix(origins,
                                    destinations,
                                    mode='transit',
                                    transit_mode="bus",
                                    departure_time=datetime.datetime(2025,6,19,11)) # HORA DE MENOS TRAFICO EN BUS
        out ="results/"+path.stem+"_b_n.json"
        with open(out,'w') as outfile:
            json.dump(result, outfile, indent=4)

def request_same_json(preserve=False):
    path = Path("output/closest_destinations_cords.json")
    pathstr = str(path)
    with open(pathstr, 'rb') as file:
        json_file = json.load(file)
    if preserve:
        with open("output/full_API_results.json", 'rb') as file:
            full_result = json.load(file)
    else:
        full_result = {}
    for origin in json_file:
        if not preserve:
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
                        out = f"results/{origin}_{mode}_{transit_mode}_{hour.strftime('%H')}.json"
                        full_result[origin][f"{mode}_{transit_mode}_{hour.strftime('%H')}"] = result
                        with open(out, 'w') as outfile:
                            json.dump(result, outfile, indent=4)
                else:
                    result = gmaps.distance_matrix(origins,
                                                    destinations,
                                                    mode=mode,
                                                    departure_time=hour)
                    out = f"results/{origin}_{mode}_{hour.strftime('%H')}.json"
                    full_result[origin][f"{mode}_{hour.strftime('%H')}"] = result
                    with open(out, 'w') as outfile:
                        json.dump(result, outfile, indent=4)
    return full_result

def element_count(combinations = 0):
    c1 = 0
    c2 = 0
    c3 = 0
    path = Path("output/closest_destinations_cords.json")
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

def request_routes(preserve=False):
    path = Path("output/closest_destinations_cords.json")
    pathstr = str(path)

    # Parámetros para todas las consultas (no cambian entre consultas  )
    url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "originIndex,destinationIndex,duration,distanceMeters,condition"
            }
    
    with open(pathstr, 'rb') as file:
        json_file = json.load(file)
    if preserve:
        with open("output/full_API_results.json", 'rb') as file:
            full_result = json.load(file)
    else:
        full_result = {}
    for origin in json_file:
        if not preserve:
            full_result[origin] = {}
        origins = (json_file[origin]["cords"][0],json_file[origin]["cords"][1])
        destinations = []
        for item in json_file[origin]["destinations"]:
            if item:
                if isinstance(item[0], list):
                    destinations.extend(item)
                else:
                    destinations.append(item)
        for hour in hours:
            for mode in modes:
                body = {}
                body["origins"] = [
                        {"waypoint": {"location": {"latLng": {"latitude": origins[0], "longitude": origins[1]}}}}  # Madrid
                    ]
                dests = []
                for destination in destinations:
                    dests.append({"waypoint": {"location": {"latLng": {"latitude": destination[0], "longitude": destination[1]}}}})
                body["destinations"] = dests
                body["travelMode"] = mode.upper()
                body["departureTime"] = hour.strftime("%Y-%m-%dT%H:%M:%SZ")
                body["routingPreference"] = "TRAFFIC_AWARE" if mode == "drive" else "TRAFFIC_UNAWARE"
                response = requests.post(url, headers=headers, data=json.dumps(body))
                full_result[origin][f"{mode}_{(hour + datetime.timedelta(hours=2)).strftime('%H:%M')}"] = response.json()
                print(full_result)
                return 1
                break
                
            
            
    return full_result

def request_routes_v2(preserve=False):
    path = Path("output/closest_destinations_cords_test.json")
    pathstr = str(path)

    # Parámetros para todas las consultas (no cambian entre consultas  )
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters"
            }
    
    with open(pathstr, 'rb') as file:
        json_file = json.load(file)
    if preserve:
        with open("output/full_API_results.json", 'rb') as file:
            full_result = json.load(file)
    else:
        full_result = {}
    for origin in json_file:
        if not preserve:
            full_result[origin] = []
        origin_cords = (json_file[origin]["cords"][0],json_file[origin]["cords"][1])
        destinations = []
        for item in json_file[origin]["destinations"]:
            if item:
                if isinstance(item[0], list):
                    destinations.extend(item)
                else:
                    destinations.append(item)
        for dest_index, destination in enumerate(destinations):
            this_destination = {}
            for mode in modes:
                for hour in hours:
                    body = {}
                    body["origin"] = {"location": {"latLng": {"latitude": origin_cords[0], "longitude": origin_cords[1]}}} # Madrid
                    body["destination"] = {"location": {"latLng": {"latitude": destination[0], "longitude": destination[1]}}}
                    body["travelMode"] = mode.upper()
                    body["departureTime"] = hour.strftime("%Y-%m-%dT%H:%M:%SZ")
                    if mode == "drive":
                        body["routingPreference"] = "TRAFFIC_AWARE"
                    response = requests.post(url, headers=headers, json=body)
                    this_destination[f"{mode}_{(hour + datetime.timedelta(hours=2)).strftime('%H:%M')}"] = response.json()
                    print(origin, dest_index, f"{mode}_{(hour + datetime.timedelta(hours=2)).strftime('%H:%M')}", response.json())
            full_result[origin].append(this_destination)
    return full_result

async def fetch_route(origin_cords, destination, mode, hour, origin_id, dest_index):
    async with semaphore:
        body = {
            "origin": {"location": {"latLng": {"latitude": origin_cords[0], "longitude": origin_cords[1]}}},
            "destination": {"location": {"latLng": {"latitude": destination[0], "longitude": destination[1]}}},
            "travelMode": mode.upper(),
            "departureTime": hour.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        if mode == "drive":
            body["routingPreference"] = "TRAFFIC_AWARE"

        for attempt in range(3):  # Reintenta hasta 3 veces
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    print(f"→ Enviando: {origin_id} → Dest {dest_index} [{mode} {hour.strftime('%H:%M')}]")
                    response = await client.post(URL, headers=HEADERS, json=body)
                    response.raise_for_status()
                    print(f"✓ Recibido: {origin_id} → Dest {dest_index} [{mode} {hour.strftime('%H:%M')}]")
                    return (origin_id, dest_index, mode, hour, response.json())
            except httpx.HTTPStatusError as e:
                print(f"⚠ HTTP {e.response.status_code} en {origin_id}-{dest_index} [{mode}], intento {attempt + 1}")
                await asyncio.sleep(2)
            except Exception as e:
                print(f"⚠ Error general en {origin_id}-{dest_index} [{mode}]: {e}")
                await asyncio.sleep(2)
        return (origin_id, dest_index, mode, hour, {"error": "failed after retries"})

async def request_routes_v2_async(preserve=False):
    path = Path("output/closest_destinations_cords.json")
    with open(path, 'r') as file:
        json_file = json.load(file)

    if preserve:
        with open("output/routes_API_results_dump.json", 'r') as file:
            full_result = json.load(file)
    else:
        full_result = {}

    tasks = []

    for origin in json_file:
        if not preserve:
            full_result[origin] = []

        origin_cords = json_file[origin]["cords"]
        destinations = []
        for item in json_file[origin]["destinations"]:
            if item:
                if isinstance(item[0], list):
                    destinations.extend(item)
                else:
                    destinations.append(item)

        for dest_index, destination in enumerate(destinations):
            for mode in modes:
                for hour_index,hour in enumerate(hours):
                    if preserve:
                        if not full_result[origin][dest_index][f"{mode}_{hours_true[hour_index].strftime("%H:%M")}"]:
                            tasks.append(
                                fetch_route(origin_cords, destination, mode, hour, origin, dest_index)
                            )
                    else:
                        tasks.append(
                            fetch_route(origin_cords, destination, mode, hour, origin, dest_index)
                        )

    results = await asyncio.gather(*tasks)

    # Reconstruir el resultado en estructura original
    for origin_id, dest_index, mode, hour, data in results:
        hour_key = hours_true[hour_index].strftime('%H:%M')
        key = f"{mode}_{hour_key}"

        if len(full_result[origin_id]) <= dest_index:
            full_result[origin_id].extend([{}] * (dest_index - len(full_result[origin_id]) + 1))

        full_result[origin_id][dest_index][key] = data

    return full_result

def specific_request(origin,dest_index,mode,hour=None):
    cords_file = fc.json_to_dict("closest_destinations_cords")
    destinations = []
    for item in cords_file[origin]["destinations"]:
            if item:
                if isinstance(item[0], list):
                    destinations.extend(item)
                else:
                    destinations.append(item)
                    
    origin_cords = cords_file[origin]["cords"]
    destination = destinations[dest_index]


    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters"
            }
    body = {}
    body["origin"] = {"location": {"latLng": {"latitude": origin_cords[0], "longitude": origin_cords[1]}}} # Madrid
    body["destination"] = {"location": {"latLng": {"latitude": destination[0], "longitude": destination[1]}}}
    body["travelMode"] = mode.upper()
    # body["departureTime"] = hour.strftime("%Y-%m-%dT%H:%M:%SZ")
    if mode == "drive":
        body["routingPreference"] = "TRAFFIC_AWARE"
    else:
        body["transitPreferences"]={ "allowedTravelModes": ["BUS","SUBWAY","TRAIN","LIGHT_RAIL","RAIL"]}
    response = requests.post(url, headers=headers, json=body)
    print(response.status_code)
    print(response.text)
    print(origin, dest_index, f"{mode}_{(hour + datetime.timedelta(hours=2)).strftime('%H:%M')}", response.json())
    print(type(response))
    return response

##### FUNCIONES MÁS ESPECÍFICAS
def run_requests_preserve():
    result = asyncio.run(request_routes_v2_async(preserve=True))
    fc.dict_to_json(result, 'routes_API_results_dump')
