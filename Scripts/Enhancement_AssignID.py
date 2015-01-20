# -*- #################
# ---------------------------------------------------------------------------
# Script for assigning a unique identifier to a field in an Esri feature class
# Author:  Sherry Massey, Dickinson County GIS
# Created: May 14, 2014
# Subject to Creative Commons Attribution-ShareAlike 4.0 International Public License
# Updated 09/22/2014 to test for geodatabase type
# ---------------------------------------------------------------------------

# Import arcpy module
from arcpy import GetParameterAsText, MakeFeatureLayer_management, SelectLayerByAttribute_management, CalculateField_management

# Set the parameters and variables
FC = GetParameterAsText(0)
Field_Name = GetParameterAsText(1)

# The first expression is formatted for use with file geodatabases
# The second is formatted for use with SDE and personal geodatabaser

if ".gdb" in FC :
	Expression = "{0} is NULL or CHAR_LENGTH({0}) = 0".format(Field_Name)
else:
	Expression = "{0} is NULL or LEN([{0}]) = 0".format(Field_Name)

Layer ="temp_lyr"


# Make a temp feature layer
MakeFeatureLayer_management(FC, Layer)

# Select from the feature layer any records with null or blank value in the Unique ID field
SelectLayerByAttribute_management(Layer, "NEW_SELECTION", Expression)

# Calculate the value of the Unique ID field for the selected records
# ID value is based on system time in seconds since the new epoch converted to a string and concatenated with record's ObjectID
CalculateField_management(Layer, Field_Name, "uniqueID() + str(!OBJECTID!)", "PYTHON", "def uniqueID():\\n  x = '%d' % time.time()\\n  str(x)\\n  return x")




