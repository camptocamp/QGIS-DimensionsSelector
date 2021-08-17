.. Dimensions Selector QGIS plugi'sn documentation master file, created by
   sphinx-quickstart on Sun Feb 12 17:11:03 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Dimensions Selector QGIS plugin's documentation
===============================================

Configuration
-------------

Add a dimension
...............

* Click on the **Add** button next to dimensions table.
* Set the **Name** value to the name of the field you want to use as a dimension, for example: "floor".

Configure dimension values, using a static list of values or using a table
..........................................................................

If you want to enter a static list of choices:

* Set the **Choices** value to a commas separated list of possible values for the dimension, for example: "value1,value2,value3,value4".

If you want to use a table of choices:

* Select the source table in **Table** column.
* Select appropriated fields in columns **Value field** and **Label field**.

Configure the layers where this dimension whould apply
......................................................

* Select the new dimension row in dimensions table.
* Click populate to fillout the layers table (all layer with a "floor" field).

Validate your configuration
...........................

* Click OK.

Note that you still need to save you QGIS project.

Usage
-----

In "Dimensions selector" toolbar:

* Toggle filtering.
* Select one dimension value in the dropdown list to filter all layers simultaneously.
