# -*- #################
# ---------------------------------------------------------------------------
# Script for assigning a unique identifier to a field in an Esri feature class
# Author:  Sherry Massey, Dickinson County GIS
# Created: May 14, 2014
# Subject to Creative Commons Attribution-ShareAlike 4.0 International Public License
# ---------------------------------------------------------------------------

# Import arcpy module
from arcpy import (GetParameterAsText, MakeTableView_management, 
                   CalculateField_management, Delete_management)

def main():

    # Set the parameters and variables
    FC = GetParameterAsText(0)
    
    Field_Name = GetParameterAsText(1)
    
    
    # The expression below is formatted for use in file geodatabases
    # If it will be used in personal or SDE geodatabases, CHAR_LENGTH should be changed to LEN
    # and the placeholder {0} will need to be surrounded by brackets or double quotes
    # depending on your system
    
    Expression = "{0} is NULL or CHAR_LENGTH({0}) = 0".format(Field_Name)
    
    Layer ="temp_lyr"
    
    
    # Make a temp table
    MakeTableView_management(FC, Layer, Expression)
    
    # Calculate the value of the Unique ID field for the selected records
    # ID value is based on system time in seconds since the new epoch converted to a string and concatenated with record's ObjectID
    code_block = """def uniqueID():
        x = '%d' % time.time()
        str(x)
        return x"""
    CalculateField_management(Layer, Field_Name, "uniqueID() + str(!OBJECTID!)", "PYTHON", code_block)

    # clean up
    Delete_management(Layer)

if __name__ == '__main__':
    main()

