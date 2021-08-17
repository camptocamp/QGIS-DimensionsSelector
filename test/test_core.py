# coding=utf-8

import os
import tempfile
import unittest
from unittest.mock import patch, Mock

from qgis.core import QgsApplication, QgsProject
from qgis.PyQt.QtCore import QCoreApplication, QEvent
from qgis.utils import iface

from dimensions_selector.core import Dimension, LayerDimension, DimensionsManager

from test import data_folder
from test.utils import add_layer, init_project


class DimensionTest(unittest.TestCase):
    def setUp(self):
        """Runs before each test."""
        self.rows = add_layer('rows.geojson', 'rows')

    def test_init(self):
        dim = Dimension()
        assert dim.name == ""
        assert dim.options == ""
        assert dim.table == None
        assert dim.active is True

    def test_toDict(self):
        dim = Dimension(
            name="dimension_with_options",
            options="A,B,C,D",
            active=True,
            current_value="",
        )
        assert dim.toDict() == {
            "name": "dimension_with_options",
            "options": "A,B,C,D",
            "table": None,
            "value_field": "",
            "label_field": "",
            "active": True,
            "current_value": "",
        }

        dim = Dimension(
            name="dimension_with_table",
            table=self.rows,
            value_field="id",
            label_field="name",
            active=True,
            current_value=1,
        )
        assert dim.toDict() == {
            "name": "dimension_with_table",
            "options": "",
            "table": self.rows.id(),
            "value_field": "id",
            "label_field": "name",
            "active": True,
            "current_value": 1,
        }

    def test_fromDict(self):
        dim = Dimension.fromDict({
            "name": "dimension_with_options",
            "options": "A,B,C,D",
            "table": None,
            "value_field": "",
            "label_field": "",
            "active": True,
            "current_value": "",
        })
        assert dim.name == "dimension_with_options"
        assert dim.options == "A,B,C,D"
        assert dim.table is None
        assert dim.value_field == ""
        assert dim.label_field == ""
        assert dim.active is True
        assert dim.current_value == ""

        dim = Dimension.fromDict({
            "name": "dimension_with_options",
            "options": "",
            "table": self.rows.id(),
            "value_field": "id",
            "label_field": "name",
            "active": True,
            "current_value": 1,
        })
        assert dim.name == "dimension_with_options"
        assert dim.options == ""
        assert dim.table is self.rows
        assert dim.value_field == "id"
        assert dim.label_field == "name"
        assert dim.active is True
        assert dim.current_value == 1

    def test_copy(self):
        dim = Dimension(
            name="dimension_with_table",
            table=self.rows,
            value_field="id",
            label_field="name",
            active=True,
            current_value=1,
        )
        dim_copy = dim.copy()
        assert dim_copy.name == dim.name
        assert dim_copy.options == dim.options
        assert dim_copy.table is dim.table
        assert dim_copy.value_field == dim.value_field
        assert dim_copy.label_field == dim.label_field
        assert dim_copy.active is dim.active
        assert dim_copy.current_value == dim.current_value

    def test_getOptions(self):
        dim = Dimension(
            name="dimension_with_options",
            options="A,B,C,D",
            active=True,
            current_value="",
        )
        assert dim.getOptions() == [("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")]

        dim = Dimension(
            name="dimension_with_table",
            table=self.rows,
            value_field="id",
            label_field="name",
            active=True,
            current_value=1,
        )
        assert dim.getOptions() == [(1, "first"), (2, "second"), (3, "third"), (4, "fourth")]


class LayerDimensionTest(unittest.TestCase):

    def setUp(self):
        """Runs before each test."""
        self.layer = add_layer('layer.geojson', 'layer1')

    def test_init(self):
        layer_dim = LayerDimension()
        assert layer_dim.layer is None
        assert layer_dim.name == ""
        assert layer_dim.field == ""
        assert layer_dim.active is True

    def test_toDict(self):
        layer_dim = LayerDimension(self.layer, "column", "column", True)
        assert layer_dim.toDict() == {
            "name": "column",
            "field": "column",
            "active": True,
        }

    def test_fromDict(self):
        layer_dim = LayerDimension.fromDict(
            self.layer,
            {
                "name": "column",
                "field": "column",
                "active": True,
            },
        )
        assert layer_dim.layer is self.layer
        assert layer_dim.name == "column"
        assert layer_dim.field == "column"
        assert layer_dim.active is True

    def test_copy(self):
        layer_dim = LayerDimension(self.layer, "column", "column", True)
        layer_dim_copy = layer_dim.copy()
        assert layer_dim_copy.layer is layer_dim.layer
        assert layer_dim_copy.name == layer_dim.name
        assert layer_dim_copy.field == layer_dim.field
        assert layer_dim_copy.active is layer_dim.active


class DimensionsManagerTest(unittest.TestCase):

    def setUp(self):
        """Runs before each test."""
        self.manager = None
        init_project()
        self.rows = QgsProject.instance().mapLayersByName('rows')[0]
        self.layer1 = QgsProject.instance().mapLayersByName('layer1')[0]
        self.layer2 = QgsProject.instance().mapLayersByName('layer2')[0]
        self.layer2.setSubsetString('"row" = \'1\'')
        self._assert_setup_state()

    def tearDown(self):
        """Runs after each test."""
        if self.manager is not None:
            self.manager.deleteLater()
        QgsApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        QgsProject.instance().clear()

    def _assert_setup_state(self, project=None):
        if project is None:
            project = QgsProject.instance()
        rows = project.mapLayersByName('rows')[0]
        layer1 = project.mapLayersByName('layer1')[0]
        layer2 = project.mapLayersByName('layer2')[0]

        self.assertEqual(4, rows.featureCount())

        self.assertEqual('', layer1.subsetString())
        self.assertEqual(16, layer1.featureCount())

        self.assertEqual('"row" = \'1\'', layer2.subsetString())
        self.assertEqual(4, layer2.featureCount())

    def _init_manager(self):
        self.manager = DimensionsManager('dimensions_selector', iface.mainWindow())

    def _init_dimensions(self):
        if self.manager is None:
            self._init_manager()

        dimensions = self.manager.dimensions()

        # One dimension with static options
        dimensions.append(
            Dimension(
                name='column',
                options='A,B,C,D',
                active=True,
                current_value='A',
            )
        )

        # One dimension with table
        dimensions.append(
            Dimension(
                name='row',
                table=self.rows,
                value_field="id",
                label_field="name",
                active=True,
                current_value=1,
            )
        )

        self.manager.set_dimensions(dimensions)

        for layer in (self.layer1, self.layer2):
            layer_dimensions = self.manager.layer_dimensions(layer)
            layer_dimensions.append(
                LayerDimension(layer, 'column', 'column', True)
            )
            self.manager.set_layer_dimensions(layer, layer_dimensions)

        for layer in (self.layer1,):
            layer_dimensions = self.manager.layer_dimensions(layer)
            layer_dimensions.append(
                LayerDimension(layer, 'row', 'row', True)
            )
            self.manager.set_layer_dimensions(layer, layer_dimensions)

        self.manager.set_active(True)

        self._assert_initial_dimensions_state()

    def _assert_initial_dimensions_state(self):
        self.assertTrue(self.manager.active())

        self.rows = QgsProject.instance().mapLayersByName('rows')[0]
        self.layer1 = QgsProject.instance().mapLayersByName('layer1')[0]
        self.layer2 = QgsProject.instance().mapLayersByName('layer2')[0]

        dimensions = self.manager.dimensions()
        self.assertEqual(len(dimensions), 2)

        self.assertEqual(dimensions[0].name, "column")
        self.assertEqual(dimensions[0].options, "A,B,C,D")
        self.assertEqual(dimensions[0].active, True)
        self.assertEqual(dimensions[0].current_value, "A")

        self.assertEqual(dimensions[1].name, "row")
        self.assertEqual(dimensions[1].table, self.rows)
        self.assertEqual(dimensions[1].value_field, "id")
        self.assertEqual(dimensions[1].label_field, "name")
        self.assertEqual(dimensions[1].active, True)
        self.assertEqual(dimensions[1].current_value, 1)

        self.assertEqual('( "column" = \'A\') AND ("row" = \'1\' )', self.layer1.subsetString())
        self.assertEqual(1, self.layer1.featureCount())

        self.assertEqual('( "row" = \'1\' ) AND ( "column" = \'A\' )', self.layer2.subsetString())
        self.assertEqual(1, self.layer2.featureCount())

    @patch('dimensions_selector.core.iface.newProjectCreated')
    @patch('dimensions_selector.core.iface.projectRead')
    def test_init(self, projectRead, newProjectCreated):
        self._init_manager()

        newProjectCreated.connect.assert_called_once_with(self.manager.clear)
        projectRead.connect.assert_called_once_with(self.manager.read)

    def test_refresh_filters(self):
        self._init_dimensions()

        self.manager.set_layer_dimensions(self.layer2, [])
        self.manager.refresh_filters()

        self.layer2.setSubsetString('"row" = \'1\'')
        self.assertEqual(4, self.layer2.featureCount())

    def test_deactivate(self):
        self._init_dimensions()

        self.manager.set_active(False)

        self._assert_setup_state()

    def test_clear(self):
        self._init_dimensions()

        on_config_changed = Mock()
        self.manager.configurationChanged.connect(on_config_changed)

        self.manager.clear()

        self.assertEqual(0, len(self.manager.dimensions()))
        self.assertFalse(self.manager.active())
        self._assert_setup_state()
        on_config_changed.test_assert_called_once_with()

    def test_write(self):
        self._init_dimensions()

        with tempfile.TemporaryDirectory() as tmpdirname:
            path = os.path.join(tmpdirname, 'project.qgs')
            QgsProject.instance().setFileName(path)
            QgsProject.instance().write()

            project = QgsProject()
            project.read(path)
            layer1_saved = project.mapLayersByName('layer1')[0]
            layer2_saved = project.mapLayersByName('layer2')[0]
            self.assertEqual('', layer1_saved.subsetString())
            self.assertEqual('"row" = \'1\'', layer2_saved.subsetString())

        self.assertFalse(os.path.exists(path))
        self._assert_initial_dimensions_state()

    def test_read(self):
        self._init_manager()
        self._init_dimensions()
        self.manager.set_active(True)

        # Save as the example project
        path = os.path.join(data_folder, 'project.qgs')
        QgsProject.instance().setFileName(path)
        QgsProject.instance().write()

        # Clear project and manager
        QgsProject.instance().clear()

        QgsProject.instance().read(path)
        self.manager.read()

        self._assert_initial_dimensions_state()


if __name__ == "__main__":
    suite = unittest.makeSuite(DimensionsManagerTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
