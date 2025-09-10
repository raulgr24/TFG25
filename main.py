from file_creator import *
from google_request import *
import colorama

get_closest_cords = False
get_requests = False
get_pens = False
get_stats = True

def pens():
    """
    Lee routes_API_results_dump.json ,
    guarda los resultados limpios en requests_clean.json ,
    guarda las penalizaciones en penalizations.json
    aplica las penalizaciones y las guarda en requests_clean_post_penalizations.json
    """
    clean_results_dict = readable_results("routes_API_results_dump")
    dict_to_json(clean_results_dict,"requests_clean")
    dict_to_json(get_penalization("Centroides final","Centroides bus"),"penalizations")
    dict_to_json(apply_penalization("requests_clean_test","penalizations"),"requests_clean_post_penalizations")

def get_closest():
        closest_destinations_cords(origin,destinations)

def merge_results():
    results_dict = json_to_dict("requests_clean_post_penalizations")
    print("LO QUE PASAMOS A merge_layer_centroides")
    merge_layer_centroides(
            layer_name="Centroides bus",
            data_dict=results_dict,
            join_field="CDTNUCLEO", 
            output_name="Centroides_stats",
            verbose = True
        )
    
    merge_layer_centroides(
            layer_name="Nucleos urbanos > 10 fix",
            data_dict=results_dict,
            join_field="CDTNUCLEO", 
            output_name="Nucleos_stats",
            verbose = True
        )
    print("CAPA DE CENTROIDES HECHA")
    mun_df = municipios_stats("Centroides_stats","Municipios corregidos")
    print(mun_df)
    merge_layer_with_dataframe(
            source_layer = project.mapLayersByName("Municipios corregidos")[0],
            dataframe = mun_df,
            join_field = "CMUN",
            output_name = "Municipios_stats"
        )

if __name__ == "__main__":
    colorama.init(convert=True, strip=False, autoreset=True)
    if get_closest_cords:
        closest_destinations_cords(origin,destinations)
    if get_requests:
        run_requests_preserve()
    if get_pens:
        pens()
    if get_stats:
        merge_results()
