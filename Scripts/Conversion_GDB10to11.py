#-------------------------------------------------------------------------------
# Name:        Conversion_GDB1.0to1.1
# Purpose:     Migrates a county's 1.0 GDB to the new and fancy 1.1 template
#
# Author:      kristen
#
# Created:     01/04/2015
# Copyright:   (c) Kristen Jordan 2015
#-------------------------------------------------------------------------------

def main():
    from arcpy import (GetParameterAsText, env, Append_management, ListFeatureClasses,
        AssignDefaultToField_management, Exists, Copy_management, AddField_management, CalculateField_management)
    from os.path import join

    oldgdb = GetParameterAsText(0)
    gdbTemplate = GetParameterAsText(1)

    #set road alias table names
    roadAlias10 = join(oldgdb, "RoadAlias")
    roadAlias11 = join(gdbTemplate, "RoadAlias")

    #copy over road alias table
    Append_management(roadAlias10, roadAlias11, "NO_TEST")

    #input default value for road alias records
    CalculateField_management(roadAlias11, "SUBMIT", '"Y"', "PYTHON_9.3")

    #set up geodatabase workspaces that include the feature dataset
    oldgdb = join(oldgdb, "NG911")
    gdbTemplate = join(gdbTemplate, "NG911")

    env.workspace = oldgdb

    #list feature classes
    fcs = ListFeatureClasses()

    #loop through feature classes
    for fc in fcs:
        #make the names
        fc10 = join(oldgdb, fc)
        fc11 = join(gdbTemplate, fc)

        #if the feature class already exists, copy over the data
        if Exists(fc11):
            Append_management(fc10, fc11, "NO_TEST")
        else:
            #this means it's most likely an esb layer of some kind
            Copy_management(fc10, fc11)

            #add new fields necessary for the 1.1 template
            if fc <> "CountyBoundary":
                AddField_management(fc11, "SUBMIT", "TEXT", "", "", 1, "SUBMIT", "", "", "Submit")
                AssignDefaultToField_management(fc11, "SUBMIT", "Y")

                AddField_management(fc11, "NOTES", "TEXT", "", "", 255)

        #fill in default values
        #SUBMIT for all except county boundary
        if fc <> "CountyBoundary":
            CalculateField_management(fc11, "SUBMIT", '"Y"', "PYTHON_9.3")

        #EXCEPTION if it's a road feature
        if fc == 'RoadCenterline':
            CalculateField_management(fc11, "EXCEPTION", '"NOT EXCEPTION"', "PYTHON_9.3")

if __name__ == '__main__':
    main()
