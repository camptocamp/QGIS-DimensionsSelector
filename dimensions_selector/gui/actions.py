# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import Qt, pyqtSignal, QAbstractTableModel, QModelIndex
from qgis.PyQt.QtWidgets import QComboBox, QWidgetAction


class DimensionValuesModel(QAbstractTableModel):

    def __init__(self, dimension, parent=None):
        super().__init__(parent)
        self._items = dimension.getOptions()

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return 1

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        try:
            return len(self._items)
        except TypeError:
            return 0

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._items[index.row()][1]
        if role == Qt.ItemDataRole.EditRole:
            return self._items[index.row()][0]


class DimensionSelectorAction(QWidgetAction):

    valueChanged = pyqtSignal()

    def __init__(self, dimension, parent=None):
        super().__init__(parent)
        self._dimension = dimension
        self._model = DimensionValuesModel(dimension)

    def createWidget(self, parent):
        widget = QComboBox(parent)
        widget.setModel(self._model)
        index = widget.findData(
            self._dimension.current_value, role=Qt.ItemDataRole.EditRole
        )
        widget.setCurrentIndex(index)
        widget.currentIndexChanged.connect(self.onSelectionChange)
        return widget

    def onSelectionChange(self, index):
        self._dimension.current_value = self.sender().currentData(
            Qt.ItemDataRole.EditRole
        )
        self.valueChanged.emit()
