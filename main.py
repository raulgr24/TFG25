from file_creator_nuevo import *
from google_request import *
import colorama

show_layers = False
get_centroides_stats = True
get_municipios_stats = True

if __name__ == "__main__":
    colorama.init(convert=True, strip=False, autoreset=True)
    # dict_to_json(get_hospital_score(),"hospital_score")
    #dict_to_json(apply_penalization("distance"),"distance_post_penalizations")
    #dict_to_json(apply_penalization("duration"),"duration_post_penalizations")
    # dict_to_json(get_hospital_num(),"hosp_per_origin")
    results_dict = json_to_dict("requests_clean")
    # results_dict_to_csv(results_dict,"requests_clean")
    # results_dict_to_csv(results_dict,"requests_clean")
    # Primero verifica los campos (opcional)
    # duration_dict = readable_results("routes_API_results_dump",mode="duration")
    # dict_to_json(distance_dict,"requests_duration")
    if show_layers:
        list_available_layers()
    if get_centroides_stats:
        nueva_capa = merge_layer_with_dict(
        layer_name="Centroides bus",
        data_dict=results_dict,
        join_field="CDTNUCLEO", 
        output_name="Centroides_stats",
        save_as_file=True,
        output_dir="output",
        verbose = True
    )
    print("CAPA DE CENTROIDES HECHA")
    if get_municipios_stats:
        mun_df = municipios_stats("Centroides_stats","Municipios corregidos")
        mun_capa = merge_layer_with_dataframe(
            source_layer = project.mapLayersByName("Municipios corregidos")[0],
                dataframe = mun_df,
                join_field = "CMUN",
                output_name = "Municipios_stats"
        )


    # dict_to_csv(distance_dict,"testingtesting")
    #print(closest_destinations_cords_nuevo(origin, destinations))
    # dict_to_json(closest_destinations_cords_nuevo(origin,destinations),"closest_destinations_cords2")
    # run_requests_preserve()
    # specific_request("1350201",0,"transit",hours[0].replace(hour=14))
    # Obtener nucleos con espacios vacíos 
    # dict_to_json(get_empty_results("routes_API_results_dump"),"nucleos_fallidos")
    #print(get_penalization('Centroides final','Centroides bus'))
    #dict_to_json(get_penalization('Centroides final','Centroides bus'),"penalizations")
