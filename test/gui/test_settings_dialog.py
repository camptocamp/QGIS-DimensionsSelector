# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = "info@camptocamp.com"
__date__ = "2018-07-05"
__copyright__ = "Copyright 2018, Camptocamp"

import unittest

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialogButtonBox, QDialog

from dimensions_selector.core import Dimension, DimensionsManager, LayerDimension
from dimensions_selector.gui.settings_dialog import (
    DimensionsTableModel,
    LayerDimensionsTableModel,
    LayerDelegate,
    FieldDelegate,
    SettingsDialog,
)
from test.utils import add_layer


class DimensionsTableModelTest(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.rows = add_layer("rows.geojson", "rows")
        self.dimensions = [
            Dimension(name="column", options="A,B,C,D", current_value="A"),
            Dimension(
                name="row",
                table=self.rows,
                value_field="id",
                label_field="name",
                current_value=1,
            ),
        ]

    def test_items(self):
        model = DimensionsTableModel(list(self.dimensions))
        self.assertEqual(model.items(), self.dimensions)

    def test_addItem(self):
        model = DimensionsTableModel([])
        for dimension in self.dimensions:
            model.addItem(dimension)
        self.assertEqual(model.items(), self.dimensions)

    def test_removeRows(self):
        model = DimensionsTableModel(list(self.dimensions))
        model.removeRows(0, 1)
        self.assertEqual(model.items(), [self.dimensions[1]])

    def test_columnIndex(self):
        model = DimensionsTableModel(list(self.dimensions))
        self.assertEqual(model.columnIndex("name"), 0)
        self.assertEqual(model.columnIndex("options"), 1)
        self.assertEqual(model.columnIndex("table"), 2)
        self.assertEqual(model.columnIndex("value_field"), 3)
        self.assertEqual(model.columnIndex("label_field"), 4)
        self.assertEqual(model.columnIndex("active"), 5)

    def test_columnCount(self):
        model = DimensionsTableModel(list(self.dimensions))
        self.assertEqual(model.columnCount(), 6)

    def test_rowCount(self):
        model = DimensionsTableModel(list(self.dimensions))
        self.assertEqual(model.rowCount(), 2)

    def test_headerData(self):
        model = DimensionsTableModel(list(self.dimensions))

        self.assertEqual(model.headerData(0, Qt.Orientation.Horizontal), "Name")
        self.assertEqual(model.headerData(1, Qt.Orientation.Horizontal), "Choices")
        self.assertEqual(model.headerData(2, Qt.Orientation.Horizontal), "Table")
        self.assertEqual(model.headerData(3, Qt.Orientation.Horizontal), "Value field")
        self.assertEqual(model.headerData(4, Qt.Orientation.Horizontal), "Label field")
        self.assertEqual(model.headerData(5, Qt.Orientation.Horizontal), "Active")

        self.assertEqual(model.headerData(0, Qt.Orientation.Vertical), "0")
        self.assertEqual(model.headerData(1, Qt.Orientation.Vertical), "1")

    def test_flags(self):
        model = DimensionsTableModel(list(self.dimensions))
        for column in range(5):
            self.assertEqual(
                model.flags(model.index(0, column)),
                Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEditable
                | Qt.ItemFlag.ItemIsEnabled,
            )
        self.assertEqual(
            model.flags(model.index(0, 5)),
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsUserCheckable,
        )

    def test_data(self):
        model = DimensionsTableModel(list(self.dimensions))
        self.assertEqual(
            model.data(model.index(0, 0), Qt.ItemDataRole.DisplayRole), "column"
        )
        self.assertEqual(
            model.data(model.index(0, 0), Qt.ItemDataRole.EditRole), "column"
        )
        self.assertEqual(
            model.data(model.index(0, 1), Qt.ItemDataRole.DisplayRole), "A,B,C,D"
        )
        self.assertEqual(
            model.data(model.index(0, 1), Qt.ItemDataRole.EditRole), "A,B,C,D"
        )
        self.assertEqual(
            model.data(model.index(0, 5), Qt.ItemDataRole.CheckStateRole),
            Qt.CheckState.Checked,
        )

        self.assertEqual(
            model.data(model.index(1, 0), Qt.ItemDataRole.DisplayRole), "row"
        )
        self.assertEqual(model.data(model.index(1, 0), Qt.ItemDataRole.EditRole), "row")
        self.assertEqual(
            model.data(model.index(1, 2), Qt.ItemDataRole.DisplayRole), "rows"
        )
        self.assertEqual(
            model.data(model.index(1, 2), Qt.ItemDataRole.EditRole), self.rows
        )
        self.assertEqual(
            model.data(model.index(1, 3), Qt.ItemDataRole.DisplayRole), "id"
        )
        self.assertEqual(model.data(model.index(1, 3), Qt.ItemDataRole.EditRole), "id")
        self.assertEqual(
            model.data(model.index(1, 4), Qt.ItemDataRole.DisplayRole), "name"
        )
        self.assertEqual(
            model.data(model.index(1, 4), Qt.ItemDataRole.EditRole), "name"
        )
        self.assertEqual(
            model.data(model.index(1, 5), Qt.ItemDataRole.CheckStateRole),
            Qt.CheckState.Checked,
        )

    def test_setData(self):
        dimensions = list(self.dimensions)
        model = DimensionsTableModel(dimensions)

        # Choices based dimension
        model.setData(model.index(0, 0), "new_name0", Qt.ItemDataRole.EditRole)
        self.assertEqual(dimensions[0].name, "new_name0")

        model.setData(model.index(0, 1), "A,B,C,D,E", Qt.ItemDataRole.EditRole)
        self.assertEqual(dimensions[0].options, "A,B,C,D,E")

        model.setData(
            model.index(0, 5), Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole
        )
        self.assertEqual(dimensions[0].active, False)

        # Table based dimension
        model.setData(model.index(1, 0), "new_name1", Qt.ItemDataRole.EditRole)
        self.assertEqual(dimensions[1].name, "new_name1")

        new_rows = add_layer("rows.geojson", "new_rows")
        model.setData(model.index(1, 2), new_rows, Qt.ItemDataRole.EditRole)
        self.assertEqual(dimensions[1].table, new_rows)

        model.setData(model.index(1, 3), "name", Qt.ItemDataRole.EditRole)
        self.assertEqual(dimensions[1].value_field, "name")

        model.setData(model.index(1, 4), "id", Qt.ItemDataRole.EditRole)
        self.assertEqual(dimensions[1].label_field, "id")

        model.setData(
            model.index(1, 5), Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole
        )
        self.assertEqual(dimensions[1].active, False)


class LayerDimensionsTableModelTest(unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.layer1 = add_layer("layer.geojson", "layer1")
        self.layer2 = add_layer("layer.geojson", "layer2")

        self.layer_dimensions = [
            LayerDimension(
                layer=self.layer1, name="column", field="column", active=True
            ),
            LayerDimension(layer=self.layer2, name="row", field="row", active=True),
        ]

    def test_items(self):
        model = LayerDimensionsTableModel(list(self.layer_dimensions))
        self.assertEqual(model.items(), self.layer_dimensions)

    def test_addItem(self):
        model = LayerDimensionsTableModel([])
        for layer_dimension in self.layer_dimensions:
            model.addItem(layer_dimension)
        self.assertEqual(model.items(), self.layer_dimensions)

    def test_removeRows(self):
        model = LayerDimensionsTableModel(list(self.layer_dimensions))
        model.removeRows(0, 1)
        self.assertEqual(model.items(), [self.layer_dimensions[1]])

    def test_columnIndex(self):
        model = LayerDimensionsTableModel(list(self.layer_dimensions))
        self.assertEqual(model.columnIndex("layer"), 0)
        self.assertEqual(model.columnIndex("name"), 1)
        self.assertEqual(model.columnIndex("field"), 2)
        self.assertEqual(model.columnIndex("active"), 3)

    def test_columnCount(self):
        model = LayerDimensionsTableModel(list(self.layer_dimensions))
        self.assertEqual(model.columnCount(), 4)

    def test_rowCount(self):
        model = LayerDimensionsTableModel(list(self.layer_dimensions))
        self.assertEqual(model.rowCount(), 2)

    def test_headerData(self):
        model = LayerDimensionsTableModel(list(self.layer_dimensions))

        self.assertEqual(model.headerData(0, Qt.Orientation.Horizontal), "Layer")
        self.assertEqual(model.headerData(1, Qt.Orientation.Horizontal), "Name")
        self.assertEqual(model.headerData(2, Qt.Orientation.Horizontal), "Field")
        self.assertEqual(model.headerData(3, Qt.Orientation.Horizontal), "Active")

        self.assertEqual(model.headerData(0, Qt.Orientation.Vertical), "0")
        self.assertEqual(model.headerData(1, Qt.Orientation.Vertical), "1")

    def test_flags(self):
        model = LayerDimensionsTableModel(list(self.layer_dimensions))
        for column in range(3):
            self.assertEqual(
                model.flags(model.index(0, column)),
                Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEditable
                | Qt.ItemFlag.ItemIsEnabled,
            )
        self.assertEqual(
            model.flags(model.index(0, 3)),
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsUserCheckable,
        )

    def test_data(self):
        model = LayerDimensionsTableModel(list(self.layer_dimensions))
        self.assertEqual(
            model.data(model.index(0, 0), Qt.ItemDataRole.DisplayRole), "layer1"
        )
        self.assertEqual(
            model.data(model.index(0, 0), Qt.ItemDataRole.EditRole), self.layer1
        )
        self.assertEqual(
            model.data(model.index(0, 1), Qt.ItemDataRole.DisplayRole), "column"
        )
        self.assertEqual(
            model.data(model.index(0, 1), Qt.ItemDataRole.EditRole), "column"
        )
        self.assertEqual(
            model.data(model.index(0, 2), Qt.ItemDataRole.DisplayRole), "column"
        )
        self.assertEqual(
            model.data(model.index(0, 2), Qt.ItemDataRole.EditRole), "column"
        )
        self.assertEqual(
            model.data(model.index(0, 3), Qt.ItemDataRole.CheckStateRole),
            Qt.CheckState.Checked,
        )

        self.assertEqual(
            model.data(model.index(1, 0), Qt.ItemDataRole.DisplayRole), "layer2"
        )
        self.assertEqual(
            model.data(model.index(1, 0), Qt.ItemDataRole.EditRole), self.layer2
        )
        self.assertEqual(
            model.data(model.index(1, 1), Qt.ItemDataRole.DisplayRole), "row"
        )
        self.assertEqual(model.data(model.index(1, 1), Qt.ItemDataRole.EditRole), "row")
        self.assertEqual(
            model.data(model.index(1, 2), Qt.ItemDataRole.DisplayRole), "row"
        )
        self.assertEqual(model.data(model.index(1, 2), Qt.ItemDataRole.EditRole), "row")
        self.assertEqual(
            model.data(model.index(1, 3), Qt.ItemDataRole.CheckStateRole),
            Qt.CheckState.Checked,
        )

    def test_setData(self):
        dimensions = list(self.layer_dimensions)
        model = LayerDimensionsTableModel(list(self.layer_dimensions))

        model.setData(model.index(0, 0), self.layer2, Qt.ItemDataRole.EditRole)
        self.assertEqual(dimensions[0].layer, self.layer2)

        model.setData(model.index(0, 1), "new_name", Qt.ItemDataRole.EditRole)
        self.assertEqual(dimensions[0].name, "new_name")

        model.setData(model.index(0, 2), "new_field", Qt.ItemDataRole.EditRole)
        self.assertEqual(dimensions[0].field, "new_field")

        model.setData(
            model.index(0, 3), Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole
        )
        self.assertEqual(dimensions[0].active, False)


class LayerDelegateTest(unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.layer1 = add_layer("layer.geojson", "layer1")
        self.layer2 = add_layer("layer.geojson", "layer2")

        self.layer_dimensions = [
            LayerDimension(
                layer=self.layer1, name="column", field="column", active=True
            ),
            LayerDimension(layer=self.layer2, name="row", field="row", active=True),
        ]

    def test_createEditor(self):
        from qgis.core import Qgis
        from qgis.gui import QgsMapLayerComboBox

        delegate = LayerDelegate()
        editor = delegate.createEditor(None, None, None)
        self.assertTrue(isinstance(editor, QgsMapLayerComboBox))
        self.assertEqual(editor.filters(), Qgis.LayerFilter.VectorLayer)

    def test_setEditorData(self):
        model = LayerDimensionsTableModel(list(self.layer_dimensions))
        self.assertEqual(
            model.data(
                model.index(0, 0),
                Qt.ItemDataRole.EditRole,
            ),
            self.layer1,
        )

        delegate = LayerDelegate()
        editor = delegate.createEditor(None, None, None)

        delegate.setEditorData(editor, model.index(0, 0))
        self.assertEqual(editor.currentLayer(), self.layer1)

    def test_setModelData(self):
        model = LayerDimensionsTableModel(list(self.layer_dimensions))
        self.assertEqual(
            model.data(
                model.index(0, 0),
                Qt.ItemDataRole.EditRole,
            ),
            self.layer1,
        )

        delegate = LayerDelegate()
        editor = delegate.createEditor(None, None, None)
        editor.setLayer(self.layer2)

        delegate.setModelData(editor, model, model.index(0, 0))
        self.assertEqual(
            model.data(
                model.index(0, 0),
                Qt.ItemDataRole.EditRole,
            ),
            self.layer2,
        )

    def on_layerChanged(self, layer):
        delegate = LayerDelegate()

        mock = unittest.mock.Mock()
        delegate.commitData.connect(mock)

        editor = delegate.createEditor(None, None, None)
        editor.setLayer(self.layer2)

        mock.assert_called_once_with()


class FieldDelegateTest(unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.layer1 = add_layer("layer.geojson", "layer1")
        self.layer2 = add_layer("layer.geojson", "layer2")

        self.layer_dimensions = [
            LayerDimension(
                layer=self.layer1, name="column", field="column", active=True
            ),
            LayerDimension(layer=self.layer2, name="row", field="row", active=True),
        ]

    def test_createEditor(self):
        from qgis.gui import QgsFieldComboBox

        model = LayerDimensionsTableModel(list(self.layer_dimensions))

        delegate = FieldDelegate(layer_column_index=0)
        editor = delegate.createEditor(None, None, model.index(0, 2))
        self.assertTrue(isinstance(editor, QgsFieldComboBox))
        self.assertEqual(editor.layer(), self.layer1)

    def test_setEditorData(self):
        model = LayerDimensionsTableModel(list(self.layer_dimensions))

        delegate = FieldDelegate(layer_column_index=0)
        editor = delegate.createEditor(None, None, model.index(0, 2))

        delegate.setEditorData(editor, model.index(0, 2))
        self.assertEqual(editor.currentField(), "column")

    def test_setModelData(self):
        model = LayerDimensionsTableModel(list(self.layer_dimensions))

        delegate = FieldDelegate(layer_column_index=0)
        editor = delegate.createEditor(None, None, model.index(0, 2))
        editor.setField("row")

        delegate.setModelData(editor, model, model.index(0, 2))
        self.assertEqual(
            model.data(
                model.index(0, 2),
                Qt.ItemDataRole.EditRole,
            ),
            "row",
        )

    def on_fieldChanged(self, layer):
        model = LayerDimensionsTableModel(list(self.layer_dimensions))

        delegate = FieldDelegate(layer_column_index=0)

        mock = unittest.mock.Mock()
        delegate.commitData.connect(mock)

        editor = delegate.createEditor(None, None, model.index(0, 2))
        editor.setField("row")

        mock.assert_called_once_with()


class SettingsDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        self.rows = add_layer("rows.geojson", "rows")
        self.layer1 = add_layer("layer.geojson", "layer1")
        self.layer2 = add_layer("layer.geojson", "layer2")

        self.manager = DimensionsManager("dimensions_selector")

        self.dimensions = [
            Dimension(name="column", options="A,B,C,D", active=True, current_value="A"),
            Dimension(
                name="row",
                table=self.rows,
                value_field="id",
                label_field="name",
                active=True,
                current_value=1,
            ),
        ]
        self.manager.set_dimensions(list(self.dimensions))

        layer_dimensions = [
            LayerDimension(self.layer1, "column", "column", True),
            LayerDimension(self.layer2, "row", "row", True),
        ]
        self.manager.set_layer_dimensions(self.layer1, [layer_dimensions[0]])
        self.manager.set_layer_dimensions(self.layer2, [layer_dimensions[1]])

        self.manager.set_active(True)

    def dialog(self):
        return SettingsDialog(self.manager, None)

    def tearDown(self):
        """Runs after each test."""
        from qgis.core import QgsApplication, QgsProject
        from qgis.PyQt.QtCore import QEvent

        if self.manager is not None:
            self.manager.deleteLater()
        QgsApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        QgsProject.instance().clear()

    def test_init(self):
        dialog = self.dialog()

        self.assertEqual(len(dialog._dimensions_model.items()), 2)
        self.assertEqual(dialog._dimensions_model.rowCount(), 2)
        self.assertEqual(dialog.dimensionsView.model().rowCount(), 2)

        self.assertEqual(len(dialog._layer_dimensions_model.items()), 2)
        self.assertEqual(dialog._layer_dimensions_model.rowCount(), 2)
        self.assertEqual(dialog.layerDimensionsView.model().rowCount(), 2)

    def test_dialog_ok(self):
        """Test we can click OK."""
        dialog = self.dialog()
        button = dialog.button_box.button(QDialogButtonBox.StandardButton.Ok)
        button.click()
        result = dialog.result()
        self.assertEqual(result, QDialog.DialogCode.Accepted)

    def test_dialog_cancel(self):
        """Test we can click cancel."""
        dialog = self.dialog()
        button = dialog.button_box.button(QDialogButtonBox.StandardButton.Cancel)
        button.click()
        result = dialog.result()
        self.assertEqual(result, QDialog.DialogCode.Rejected)

    def test_selected_dimensions_names(self):
        dialog = self.dialog()
        dialog.dimensionsView.selectRow(0)
        self.assertEqual(dialog.selected_dimensions_names(), ["column"])

    def test_on_dimensionsView_selectionChanged(self):
        from qgis.PyQt.QtCore import QItemSelection, QItemSelectionModel

        dialog = self.dialog()
        dialog.dimensionsView.clearSelection()
        self.assertEqual(
            dialog.layerDimensionsView.model().filterRegularExpression().pattern(), ""
        )
        self.assertEqual(dialog.layerDimensionsView.model().rowCount(), 2)

        dialog.dimensionsView.selectRow(0)
        self.assertEqual(
            dialog.layerDimensionsView.model().filterRegularExpression().pattern(),
            "^(?:column)$",
        )
        self.assertEqual(dialog.layerDimensionsView.model().rowCount(), 1)

        dialog.dimensionsView.selectRow(1)
        self.assertEqual(
            dialog.layerDimensionsView.model().filterRegularExpression().pattern(),
            "^(?:row)$",
        )
        self.assertEqual(dialog.layerDimensionsView.model().rowCount(), 1)

        dialog.dimensionsView.selectionModel().select(
            QItemSelection(
                dialog.dimensionsView.model().index(0, 0),
                dialog.dimensionsView.model().index(1, 5),
            ),
            QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )
        self.assertEqual(
            dialog.layerDimensionsView.model().filterRegularExpression().pattern(),
            "^(?:column|row)$",
        )
        self.assertEqual(dialog.layerDimensionsView.model().rowCount(), 2)

    def test_on_addDimensionButton_clicked(self):
        dialog = self.dialog()
        self.assertEqual(len(dialog._dimensions_model.items()), 2)
        dialog.on_addDimensionButton_clicked()
        self.assertEqual(len(dialog._dimensions_model.items()), 3)

    def test_on_removeDimensionButton_clicked(self):
        dialog = self.dialog()
        self.assertEqual(len(dialog._dimensions_model.items()), 2)
        dialog.dimensionsView.selectRow(0)
        dialog.on_removeDimensionButton_clicked()
        self.assertEqual(len(dialog._dimensions_model.items()), 1)

    def test_on_populateDimensionButton_clicked(self):
        from qgis.PyQt.QtCore import QItemSelection, QItemSelectionModel

        dialog = self.dialog()

        dialog.layerDimensionsView.model().sourceModel().clear()
        dialog.dimensionsView.selectRow(0)
        self.assertEqual(dialog.layerDimensionsView.model().rowCount(), 0)
        dialog.on_populateDimensionButton_clicked()
        self.assertEqual(dialog.layerDimensionsView.model().rowCount(), 2)

        dialog.layerDimensionsView.model().sourceModel().clear()
        dialog.dimensionsView.selectRow(1)
        self.assertEqual(dialog.layerDimensionsView.model().rowCount(), 0)
        dialog.on_populateDimensionButton_clicked()
        self.assertEqual(dialog.layerDimensionsView.model().rowCount(), 2)

        dialog.layerDimensionsView.model().sourceModel().clear()
        dialog.dimensionsView.selectionModel().select(
            QItemSelection(
                dialog.dimensionsView.model().index(0, 0),
                dialog.dimensionsView.model().index(
                    1, dialog._dimensions_model.columnCount() - 1
                ),
            ),
            QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )
        dialog.on_populateDimensionButton_clicked()
        self.assertEqual(dialog.layerDimensionsView.model().rowCount(), 4)

    def test_on_addLayerDimensionButton_clicked(self):
        dialog = self.dialog()
        self.assertEqual(dialog.layerDimensionsView.model().rowCount(), 2)
        dialog.on_addLayerDimensionButton_clicked()
        self.assertEqual(dialog.layerDimensionsView.model().rowCount(), 3)

    def test_on_removeLayerDimensionButton_clicked(self):
        dialog = self.dialog()
        self.assertEqual(dialog.layerDimensionsView.model().rowCount(), 2)
        dialog.layerDimensionsView.selectRow(0)
        dialog.on_removeLayerDimensionButton_clicked()
        self.assertEqual(dialog.layerDimensionsView.model().rowCount(), 1)

    def test_accept(self):
        dialog = self.dialog()

        self.manager.set_layer_dimensions(self.layer1, [])
        self.manager.set_layer_dimensions(self.layer2, [])
        self.manager.set_dimensions([])

        dialog.accept()

        self.assertEqual(len(self.manager.dimensions()), 2)
        self.assertEqual(len(self.manager.layer_dimensions(self.layer1)), 1)
        self.assertEqual(len(self.manager.layer_dimensions(self.layer2)), 1)


if __name__ == "__main__":
    suite = unittest.makeSuite(SettingsDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
