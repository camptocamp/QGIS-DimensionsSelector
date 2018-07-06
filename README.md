# Dimensions Selector QGIS Plugin

QGIS Plugin which adds a toolbar to QGIS for filtering features upon multiple layers on a common field (floor, year, project, ...).

## Configuration

Open the "Plugin" / "Dimensions Selector" / "Settings" dialog.

Click the "Add" button to create a new dimension, give it a name and a list of values separated by ",".

Click the "Populate" button, it will affect the dimension to each layer having a field with the same name as the dimension.

After acceptation of the settings dialog, a new combox will appear in the "Dimensions Selector" toolbar.

## Limitations

Filtering is applied on layers using the "Provider feature filter".

When the plugin is activated, a backup of current filter is saved in the layer properties, and the filter is altered in view of the current selected dimensions values.

When the plugin is deactivated, unloaded or during project saving, origin filter which was saved in properties is restored.

If you want to change the original filter of one layer, deactivate the plugin, change the filter and reactivate the plugin.
