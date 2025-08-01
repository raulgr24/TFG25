from file_creator_nuevo import *
from google_request import *


if __name__ == "__main__":
    # dict_to_json(get_hospital_num(),"hosp_per_origin")
    # distance_dict = readable_results()
    # dict_to_json(distance_dict,"requests_distance")
    # dict_to_csv(distance_dict,"testingtesting")
    specific_request("1350201",0,"transit",hours[0].replace(hour=14))

    # Obtener nucleos con espacios vacíos 
    # dict_to_json(get_empty_results("routes_API_results_dump"),"nucleos_fallidos")