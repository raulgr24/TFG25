# Archivos y carpetas importantes
- tfg_project.qgz --> Proyecto QGIS
- datos-bruto/ --> Carpeta con datos recién obtenidos de nomecalles
- datos-nuevo/ --> Carpeta con datos procesados
- Memoria.docx --> Memoria del TFG
- file_creator_nuevo.py --> Scripts de creación, lectura y modificación de archivos
- google_request.py --> Scripts de requuests a la Routes API de Google
- output/ --> Carpeta de archivos generados

# Partes a cambiar
- Para hacer consultas, crea un "api.txt" en la carpeta general con la clave API.
- file_creator_nuevo.py --> Línea 12 --> qgis.QgsApplication.setPrefixPath("C:/Program Files/QGIS 3.40.7", True)
    Cambiar el Path a donde esté instalado QGIS.
## Creación del entorno
Por alguna razón el paquete qgis.core para python no se puede instalar por pip y se necesitan unas variables de entorno específicas para poder ejecutar con la librería qgis.core en python.
Para eso tengo TFG.bat, que crea las variables de entorno necesarias junto con otras que me permiten abrir el editor y una powershell directa a la carpeta con los archivos.
Es probable que de errores en otros ordenadores, se puede cambiar el archivo para que añada rutas al PATH, en mi caso añado PATH neovim, powershell, etc.

