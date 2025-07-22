#ANTES DE EJECUTAR ABRE "C:/Program Files/QGIS 3.38.3/OSGeo4W.bat", LUEGO ABRE VSC
from qgis.core import *
import json
import pickle

# Initialize the QGIS resources at the beginning of the scrip https://docs.qgis.org/3.40/en/docs/pyqgis_developer_cookbook/intro.html#using-pyqgis-in-standalone-scripts
# Supply path to qgis install location
QgsApplication.setPrefixPath("C:/Program Files/QGIS 3.40.7", True)

# Create a reference to the QgsApplication.  Setting the
# second argument to False disables the GUI.
qgs = QgsApplication([], False)
qgs.initQgis()

project = QgsProject.instance()
names = [layer.name() for layer in project.mapLayers().values()]
print(names)
root = project.layerTreeRoot().children()
print(root)
project.read("C:/Users/raulc/Desktop/2025/TFG/tfg_project.qgz")

o = "Centroides"
o_layer = project.mapLayersByName(o)[0]

d= "Carreteras con codigo"
d_layer = project.mapLayersByName(d)
output = "Centroides en carretera"

def snap_by_attribute():
    o_feat = o_layer.getFeatures()
    for feature in o_feat:
        
    print(o_layer.getFeatures()[0])
    
    
snap_by_attribute()