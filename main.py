from file_creator_nuevo import *
from google_request import *

if __name__ == "__main__":
    dict_to_json(get_hospital_score(),"hospital_score")
    
    #dict_to_json(apply_penalization("distance"),"distance_post_penalizations")
    #dict_to_json(apply_penalization("duration"),"duration_post_penalizations")
    # dict_to_json(get_hospital_num(),"hosp_per_origin")
    # distance_dict = readable_results("routes_API_results_dump")
    # dict_to_json(distance_dict,"requests_distance")
    # duration_dict = readable_results("routes_API_results_dump",mode="duration")
    # dict_to_json(distance_dict,"requests_duration")
    # dict_to_csv(distance_dict,"testingtesting")
    #print(closest_destinations_cords_nuevo(origin, destinations))
    # dict_to_json(closest_destinations_cords_nuevo(origin,destinations),"closest_destinations_cords2")
    # run_requests_preserve()
    # specific_request("1350201",0,"transit",hours[0].replace(hour=14))
    # Obtener nucleos con espacios vacíos 
    # dict_to_json(get_empty_results("routes_API_results_dump"),"nucleos_fallidos")
    #print(get_penalization('Centroides final','Centroides bus'))
    #dict_to_json(get_penalization('Centroides final','Centroides bus'),"penalizations")
