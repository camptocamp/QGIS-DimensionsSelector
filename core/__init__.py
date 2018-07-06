# -*- coding: utf-8 -*-

import json
from qgis.core import QgsProject
from qgis.utils import iface
from qgis.PyQt.QtCore import QObject, pyqtSignal


class Dimension():

    def __init__(self, name, options, active, current_value):
        self.name = name
        self.options = options
        self.active = active
        self.current_value = current_value

    def toDict(self):
        return self.__dict__

    @classmethod
    def fromDict(cls, dict_):
        return cls(**dict_)

    def copy(self):
        return Dimension.fromDict(self.toDict())


class LayerDimension():

    def __init__(self, layer, name, field, active):
        self.layer = layer
        self.name = name
        self.field = field
        self.active = active

    def toDict(self):
        dict_ = self.__dict__.copy()
        dict_.pop('layer')
        return dict_

    @classmethod
    def fromDict(cls, layer, dict_):
        return cls(layer, **dict_)

    def copy(self):
        return LayerDimension.fromDict(self.layer, self.toDict())


class DimensionsManager(QObject):

    configurationChanged = pyqtSignal()

    def __init__(self, scope, parent=None):
        super().__init__(parent)
        self.scope = scope
        self._active = False
        self._dimensions = []
        self.read()

        iface.newProjectCreated.connect(self.clear)
        iface.projectRead.connect(self.read)
        QgsProject.instance().writeProject.connect(self.write)
        QgsProject.instance().projectSaved.connect(self.saved)

    def clear(self):
        self._dimensions = []
        self._active = False
        self.configurationChanged.emit()

    def read(self):
        self._dimensions = []
        str, ok = QgsProject.instance().readEntry(self.scope, 'dimensions')
        if ok and str:
            for dict_ in json.loads(str):
                self._dimensions.append(Dimension.fromDict(dict_))

        active, ok = QgsProject.instance().readBoolEntry(self.scope, 'dimensions')
        if ok:
            self.set_active(active)

        self.configurationChanged.emit()

    def write(self, doc):
        self.restore_subset_strings()
        QgsProject.instance().writeEntry(self.scope, 'active', self.active())
        QgsProject.instance().writeEntry(self.scope, 'dimensions', json.dumps([d.toDict() for d in self._dimensions]))

    def saved(self):
        self.refresh_filters()

    def active(self):
        return self._active

    def set_active(self, value):
        if self._active == False and value == True:
            self.backup_subset_strings()
        self._active = value
        self.refresh_filters()

    def backup_subset_strings(self):
        for layer in QgsProject.instance().mapLayers().values():
            layer.setCustomProperty('{}/subsetString_backup'.format(self.scope), layer.subsetString())

    def restore_subset_strings(self):
        for layer in QgsProject.instance().mapLayers().values():
            sql = layer.customProperty('{}/subsetString_backup'.format(self.scope), None)
            if sql is not None:
                layer.setSubsetString(sql)

    def dimensions(self):
        return self._dimensions

    def set_dimensions(self, dimensions):
        self._dimensions = dimensions

    def layer_dimensions(self, layer):
        dimensions = []
        str = layer.customProperty(self.scope, None)
        if str:
            for dict_ in json.loads(str):
                dimensions.append(LayerDimension.fromDict(layer, dict_))
        return dimensions

    def set_layer_dimensions(self, layer, dimensions):
        layer.setCustomProperty(self.scope, json.dumps([d.toDict() for d in dimensions]))

    def refresh_filters(self):
        self.restore_subset_strings()
        if not self._active:
            return
        for layer in QgsProject.instance().mapLayers().values():
            try:
                self._apply_layer_filter(layer)
            except Exception as e:
                print(e)
                continue

    def _apply_layer_filter(self, layer):
        clauses = []
        layer_dimensions = self.layer_dimensions(layer)
        for layer_dimension in self.layer_dimensions(layer):
            if not layer_dimension.active:
                continue
            for dimension in self._dimensions:
                if dimension.name == layer_dimension.name:
                    clauses.append('"{}" = \'{}\''.format(
                        layer_dimension.field,
                        dimension.current_value))
        if len(clauses) == 0:
            return
        if layer.subsetString():
            sql = '( {} ) AND ( {} )'.format(
                layer.subsetString(),
                ') AND ('.join(clauses)
            )
        else:
            sql = '( {} )'.format(
                ') AND ('.join(clauses)
            )
        if not layer.setSubsetString( sql ):
            raise Exception( "Layer {} does not support subset string: {}".format(layer.name(), sql) )
