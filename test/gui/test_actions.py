import unittest

from PyQt5.QtCore import Qt

from dimensions_selector.core import Dimension
from dimensions_selector.gui.actions import DimensionValuesModel

from dimensions_selector.test.utils import add_layer


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
        self.assertEqual(model.data(model.index(0, 0), Qt.ItemDataRole), "A")


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
        self.assertEqual(model.data(model.index(0, 0), Qt.ItemDataRole), 1)
