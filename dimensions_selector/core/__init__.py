# -*- coding: utf-8 -*-

import json
from qgis.core import QgsProject
from qgis.utils import iface
from qgis.PyQt.QtCore import QObject, pyqtSignal


class Dimension():

    def __init__(self, name="", options="", table=None, value_field="", label_field="", active=True, current_value=""):
        self.name = name
        self.options = options
        self.table = table
        self.value_field = value_field
        self.label_field = label_field
        self.active = active
        self.current_value = current_value

    def toDict(self):
        dict_ = self.__dict__.copy()
        if self.table is not None:
            dict_["table"] = self.table.id()
        return dict_

    @classmethod
    def fromDict(cls, dict_):
        dict_ = dict_.copy()
        table_id = dict_.get("table", None)
        if table_id is not None:
            dict_["table"] = QgsProject.instance().mapLayer(table_id)
        return cls(**dict_)

    def copy(self):
        return Dimension.fromDict(self.toDict())

    def getOptions(self):
        """
        Returns options as tuple(value, label).
        """
        if self.table is None:
            return [(v, v) for v in self.options.split(",")]
        else:
            options = []
            for f in self.table.getFeatures():
                options.append(
                    (
                        f.attribute(self.value_field),
                        f.attribute(self.label_field),
                    )
                )
            return options  # sorted(options, key=lambda o, o[1])


class LayerDimension():

    def __init__(self, layer=None, name="", field="", active=True):
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
        self.set_active(False)
        self.configurationChanged.emit()

    def read(self):
        self._dimensions = []
        str_value, ok = QgsProject.instance().readEntry(self.scope, 'dimensions')
        if ok and str_value:
            for dict_ in json.loads(str_value):
                self._dimensions.append(Dimension.fromDict(dict_))

        active, ok = QgsProject.instance().readBoolEntry(self.scope, 'active')
        if ok:
            self.set_active(active)

        self.configurationChanged.emit()

        self.refresh_filters()

    def write(self, doc):  # pylint: disable=unused-argument
        self.restore_subset_strings()
        QgsProject.instance().writeEntry(self.scope, 'active', self.active())
        QgsProject.instance().writeEntry(
            self.scope,
            'dimensions',
            json.dumps([d.toDict() for d in self._dimensions]),
        )

    def saved(self):
        self.refresh_filters()

    def active(self):
        return self._active

    def set_active(self, value):
        value = bool(value)
        if self._active == value:
            return
        if not self._active:
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
        str_value = layer.customProperty(self.scope, None)
        if str_value:
            for dict_ in json.loads(str_value):
                dimensions.append(LayerDimension.fromDict(layer, dict_))
        return dimensions

    def set_layer_dimensions(self, layer, dimensions):
        layer.setCustomProperty(self.scope, json.dumps([d.toDict() for d in dimensions]))

    def refresh_filters(self):
        self.restore_subset_strings()
        if not self._active:
            return
        for layer in QgsProject.instance().mapLayers().values():
            self._apply_layer_filter(layer)

    def _apply_layer_filter(self, layer):
        clauses = []
        for layer_dimension in self.layer_dimensions(layer):
            if not layer_dimension.active:
                continue
            for dimension in self._dimensions:
                if dimension.name == layer_dimension.name:
                    clauses.append('"{}" = \'{}\''.format(
                        layer_dimension.field,
                        dimension.current_value))
        if not clauses:
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
        if not layer.setSubsetString(sql):
            raise Exception("Layer {} does not support subset string: {}".format(layer.name(), sql))
