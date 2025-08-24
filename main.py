from file_creator import *
from google_request import *
import colorama

get_closest_cords = False
get_requests = False
get_pens = True
get_stats = True

def pens():
    """
    Lee routes_API_results_dump.json ,
    guarda los resultados limpios en HOLAAAA.json ,
    guarda las penalizaciones en pen_json_prueba.json
    aplica las penalizaciones
    """
    clean_results_dict = readable_results("routes_API_results_dump")
    dict_to_json(clean_results_dict,"requests_clean")
    dict_to_json(get_penalization("Centroides final","Centroides bus"),"penalizations")
    dict_to_json(apply_penalization("requests_clean","penalizations"),"requests_clean_post_penalizations")

def get_closest():
        closest_destinations_cords(origin,destinations)

def merge_results():
    results_dict = json_to_dict("requests_clean")
    merge_layer_with_dict(
            layer_name="Centroides bus",
            data_dict=results_dict,
            join_field="CDTNUCLEO", 
            output_name="Centroides_stats_2",
            save_as_file=True,
            output_dir="output",
            verbose = True
        )
    print("CAPA DE CENTROIDES HECHA")
    mun_df = municipios_stats("Centroides_stats","Municipios corregidos")
    merge_layer_with_dataframe(
            source_layer = project.mapLayersByName("Municipios corregidos")[0],
            dataframe = mun_df,
            join_field = "CMUN",
            output_name = "Municipios_stats_2"
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
