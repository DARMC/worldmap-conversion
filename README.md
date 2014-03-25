WorldMap Conversion Script
===================

To run this script, set the variable GDB_PATH to a valid geodatabase containing 1 or more feature classes and run ```dump_geodatabase_for_worldmap.py```. Outputs will be created in a new folder in the project directory and will create one shapefile per feature class with a defined projection. Feature classes without a defined projection, cannot be projected to WGS84 and will not be exported.
