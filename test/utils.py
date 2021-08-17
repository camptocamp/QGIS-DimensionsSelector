import os

from qgis.core import QgsProject, QgsVectorLayer

from test import data_folder


def add_layer(filename, layername):
    path = os.path.join(data_folder, filename)
    layer = QgsVectorLayer(path, layername, 'ogr')
    if not layer.isValid():
        raise Exception('Invalid layer: {}'.format(path))
    QgsProject.instance().addMapLayer(layer)
    return layer


def init_project():
    add_layer('rows.geojson', 'rows')
    add_layer('layer.geojson', 'layer1')
    layer2 = add_layer('layer.geojson', 'layer2')
    layer2.setSubsetString('"row" = \'1\'')
