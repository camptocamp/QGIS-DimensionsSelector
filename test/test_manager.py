# coding=utf-8

import os
import tempfile
import unittest
from unittest.mock import patch, Mock
from qgis.core import QgsApplication, QgsProject, QgsVectorLayer
from qgis.PyQt.QtCore import QEvent
from qgis.utils import iface
from dimensions_selector.core import Dimension, LayerDimension, DimensionsManager
from dimensions_selector.test import data_folder


def add_layer(filename, layername):
    path = os.path.join(data_folder, filename)
    layer = QgsVectorLayer(path, layername, 'ogr')
    if not layer.isValid():
        raise Exception('Invalid layer: {}'.format(path))
    QgsProject.instance().addMapLayer(layer)
    return layer


class DimensionsManagerTest(unittest.TestCase):

    def setUp(self):
        """Runs before each test."""
        self.manager = None

        self.layer1 = add_layer('point.shp', 'layer1')
        self.layer2 = add_layer('point.shp', 'layer2')
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
        layer1 = project.mapLayersByName('layer1')[0]
        layer2 = project.mapLayersByName('layer2')[0]

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
        dimensions.append(Dimension('column', 'A,B,C,D', True, 'A'))
        self.manager.set_dimensions(dimensions)

        for layer in (self.layer1, self.layer2):
            layer_dimensions = self.manager.layer_dimensions(layer)
            layer_dimensions.append(
                LayerDimension(layer, 'column', 'column', True)
            )
            self.manager.set_layer_dimensions(layer, layer_dimensions)

        self.manager.set_active(True)

        self._assert_initial_dimensions_state()

    def _assert_initial_dimensions_state(self):
        self.assertTrue(self.manager.active())

        self.assertEqual('( "column" = \'A\' )', self.layer1.subsetString())
        self.assertEqual(4, self.layer1.featureCount())

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
        path = os.path.join(data_folder, 'project.qgs')

        self._init_manager()

        '''
        self._init_dimensions()
        QgsProject.instance().setFileName( path )
        QgsProject.instance().write()

        self.manager.clear()
        QgsProject.instance().clear()
        '''

        QgsProject.instance().read(path)
        self.manager.read()

        self.layer1 = QgsProject.instance().mapLayersByName('layer1')[0]
        self.layer2 = QgsProject.instance().mapLayersByName('layer2')[0]

        self.assertTrue(self.manager.active())
        self.assertEqual('( "column" = \'A\' )', self.layer1.subsetString())
        self.assertEqual(4, self.layer1.featureCount())

        self.assertEqual('( "row" = \'1\' ) AND ( "column" = \'A\' )', self.layer2.subsetString())
        self.assertEqual(1, self.layer2.featureCount())


if __name__ == "__main__":
    suite = unittest.makeSuite(DimensionsManagerTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
