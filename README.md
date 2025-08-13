# Archivos y carpetas importantes
- tfg_project.qgz --> Proyecto QGIS
- datos-bruto/ --> Carpeta con datos recién obtenidos de nomecalles
- datos-nuevo/ --> Carpeta con datos procesados
- Memoria.docx --> Memoria del TFG
- file_creator_nuevo.py --> Scripts de creación, lectura y modificación de archivos
- google_request.py --> Scripts de requuests a la Routes API de Google
- output/ --> Carpeta de archivos generados

# Partes a cambiar
- file_creator_nuevo.py --> Línea 12 --> qgis.QgsApplication.setPrefixPath("C:/Program Files/QGIS 3.40.7", True)
    Cambiar el Path a donde esté instalado QGIS.
