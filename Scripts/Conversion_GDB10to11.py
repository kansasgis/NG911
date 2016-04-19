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
        AssignDefaultToField_management, Exists, Copy_management, AddField_management,
        CalculateField_management, ListFields)
    from os.path import join
    from NG911_Config import getGDBObject
    from NG911_GDB_Objects import getDefaultNG911RoadCenterlineObject, getDefaultNG911CountyBoundaryObject, getDefaultNG911RoadAliasObject

    oldgdb = GetParameterAsText(0)
    gdbTemplate = GetParameterAsText(1)

    oldgdb_object = getGDBObject(oldgdb)
    gdbTemplate_object = getGDBObject(gdbTemplate)

    #set road alias table names
    roadAlias10 = oldgdb_object.RoadAlias
    roadAlias11 = gdbTemplate_object.RoadAlias

    #get road alias object
    ra = getDefaultNG911RoadAliasObject()

    #copy over road alias table
    Append_management(roadAlias10, roadAlias11, "NO_TEST")

    #input default value for road alias records
    CalculateField_management(roadAlias11, ra.SUBMIT, '"Y"', "PYTHON_9.3")

    #set up geodatabase workspaces that include the feature dataset
    oldgdb = oldgdb_object.NG911_FeatureDataset
    gdbTemplate = gdbTemplate_object.NG911_FeatureDataset

    env.workspace = oldgdb

    #list feature classes
    fcs = ListFeatureClasses()

    #loop through feature classes
    for fc in fcs:
        #make the names
        fc10 = join(oldgdb, fc)
        fc11 = join(gdbTemplate, fc)

        #migrate other user fields
        fields10 = ListFields(fc10)
        fields11 = ListFields(fc11)

        #make list of field names in 1.1 version
        fList11 = []
        for f11 in fields11:
            fList11.append(f11.name)

        #if the proprietary field doesn't exist, add it
        for field10 in fields10:
            if field10.name not in fList11:
                AddField_management(fc11, field10.name, field10.type, "", "", field10.length)

        #if the feature class already exists, copy over the data
        if Exists(fc11):
            Append_management(fc10, fc11, "NO_TEST")
        else:
            #this means it's most likely an esb layer of some kind
            Copy_management(fc10, fc11)

            #add new fields necessary for the 1.1 template

            if fc <> "CountyBoundary":
                #I'm using fields from the road alias object since they are common in most all layers
                AddField_management(fc11, ra.SUBMIT, "TEXT", "", "", 1, ra.SUBMIT, "", "", "Submit")
                AssignDefaultToField_management(fc11, ra.SUBMIT, "Y")

                AddField_management(fc11, ra.NOTES, "TEXT", "", "", 255)

        #fill in default values
        #SUBMIT for all except county boundary
        if fc <> "CountyBoundary":
            CalculateField_management(fc11, ra.SUBMIT, '"Y"', "PYTHON_9.3")

        #EXCEPTION if it's a road feature
        if fc == 'RoadCenterline':
            rc = getDefaultNG911RoadCenterlineObject()
            CalculateField_management(fc11, rc.EXCEPTION, '"NOT EXCEPTION"', "PYTHON_9.3")
            del rc


if __name__ == '__main__':
    main()
