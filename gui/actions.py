# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, pyqtSignal, QAbstractTableModel, QModelIndex
from PyQt5.QtWidgets import QComboBox, QWidgetAction


class DimensionValuesModel(QAbstractTableModel):

    def __init__(self, dimension, parent=None):
        super().__init__(parent)
        self._items = dimension.options.split(',')

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

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._items[index.row()]


class DimensionSelectorAction(QWidgetAction):

    valueChanged = pyqtSignal()

    def __init__(self, dimension, parent=None):
        super().__init__(parent)
        self._dimension = dimension
        self._model = DimensionValuesModel(dimension)

    def createWidget(self, parent):
        widget = QComboBox(parent)
        widget.setModel(self._model)
        widget.setCurrentText(self._dimension.current_value)
        widget.currentIndexChanged.connect(self.onSelectionChange)
        return widget

    def onSelectionChange(self, index):
        self._dimension.current_value = self.sender().currentText()
        self.valueChanged.emit()
