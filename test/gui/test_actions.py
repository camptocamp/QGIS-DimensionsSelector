import unittest

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox

from dimensions_selector.core import Dimension
from dimensions_selector.gui.actions import DimensionValuesModel, DimensionSelectorAction

from test.utils import add_layer


class DimensionValuesModelWithOptionsTest(unittest.TestCase):

    def model(self):
        return DimensionValuesModel(
            Dimension(
                name="column",
                options="A,B,C,D",
                current_value="A",
            )
        )

    def test_columnCount(self):
        model = self.model()
        self.assertEqual(model.columnCount(), 1)

    def test_rowCount(self):
        model = self.model()
        self.assertEqual(model.rowCount(), 4)

    def test_data(self):
        model = self.model()
        self.assertEqual(model.data(model.index(0, 0), Qt.DisplayRole), "A")
        self.assertEqual(model.data(model.index(0, 0), Qt.EditRole), "A")


class DimensionValuesModelWithTableTest(unittest.TestCase):

    def model(self):
        rows = add_layer('rows.geojson', 'rows')

        return DimensionValuesModel(
            Dimension(
                name="column",
                table=rows,
                value_field="id",
                label_field="name",
                current_value=1,
            )
        )

    def test_columnCount(self):
        model = self.model()
        self.assertEqual(model.columnCount(), 1)

    def test_rowCount(self):
        model = self.model()
        self.assertEqual(model.rowCount(), 4)

    def test_data(self):
        model = self.model()
        self.assertEqual(model.data(model.index(0, 0), Qt.DisplayRole), "first")
        self.assertEqual(model.data(model.index(0, 0), Qt.EditRole), 1)


class DimensionSelectorActionWithOptionsTest(unittest.TestCase):

    def action(self):
        self._dimension = Dimension(
            name="column",
            options="A,B,C,D",
            current_value="A",
        )

        return DimensionSelectorAction(
            self._dimension
        )

    def test_createWidget(self):
        action = self.action()
        widget = action.createWidget(None)
        assert isinstance(widget, QComboBox)

    def test_onSelectionChanged(self):
        action = self.action()

        mock = unittest.mock.Mock()
        action.valueChanged.connect(mock)

        widget = action.createWidget(None)
        widget.setCurrentText("B")

        assert self._dimension.current_value == "B"

        assert mock.called_once_with()


class DimensionSelectorActionWithTableTest(unittest.TestCase):

    def action(self):
        rows = add_layer('rows.geojson', 'rows')

        self._dimension = Dimension(
            name="row",
            table=rows,
            value_field="id",
            label_field="name",
            current_value=1,
        )

        return DimensionSelectorAction(
            self._dimension
        )

    def test_createWidget(self):
        action = self.action()
        widget = action.createWidget(None)
        assert isinstance(widget, QComboBox)

    def test_onSelectionChanged(self):
        action = self.action()

        mock = unittest.mock.Mock()
        action.valueChanged.connect(mock)

        widget = action.createWidget(None)
        widget.setCurrentText("second")

        assert self._dimension.current_value == 2

        assert mock.called_once_with()
