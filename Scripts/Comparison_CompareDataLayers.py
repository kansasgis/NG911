#-------------------------------------------------------------------------------
# Name:        Comparison_CompareDataLayers
# Purpose:     Find edits in layers based on their unique ID fields
#
# Author:      kristen
#
# Created:     13/05/2016
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, AddJoin_management, MakeTableView_management,
            Exists, ListFields, CopyFeatures_management, Delete_management,
            MakeFeatureLayer_management, CalculateField_management, AddField_management,
            Describe, AddIndex_management, DeleteField_management, RemoveJoin_management,
            Exists, CreateTable_management)
from arcpy.da import SearchCursor, InsertCursor
from os.path import join, basename, dirname
from NG911_DataCheck import userMessage
from NG911_arcpy_shortcuts import ListFieldNames, MakeLayer, fieldExists, indexExists, getFastCount
import NG911_GDB_Objects
from time import strftime

a_obj = NG911_GDB_Objects.getDefaultNG911AddressObject()
rc_obj = NG911_GDB_Objects.getDefaultNG911RoadCenterlineObject()
esb_obj = NG911_GDB_Objects.getDefaultNG911ESBObject()
ab_obj = NG911_GDB_Objects.getDefaultNG911AuthoritativeBoundaryObject()
ra_obj = NG911_GDB_Objects.getDefaultNG911RoadAliasObject()
cb_obj = NG911_GDB_Objects.getDefaultNG911CountyBoundaryObject()
mb_obj = NG911_GDB_Objects.getDefaultNG911MunicipalBoundaryObject()
esz_obj = NG911_GDB_Objects.getDefaultNG911ESZObject()
psap_obj = NG911_GDB_Objects.getDefaultNG911ESBObject()

layer_obj_dict = {"ADDRESSPOINTS": a_obj, "ROADCENTERLINE": rc_obj, "ESB": esb_obj, "AUTHORITATIVEBOUNDARY": ab_obj, "ROADALIAS": ra_obj, "COUNTYBOUNDARY": cb_obj,
                     "MUNICIPALBOUNDARY":mb_obj, "ESZ": esz_obj, "PSAP": esb_obj}

def CompareThatData(fc1, fc2, resultsTable, keyword):
    compare = "compare"
    ng911id = "ng911id"

    #Add comparison field
    if not fieldExists(fc1, compare + "1"):
        AddField_management(fc1, compare + "1", "TEXT", "", "", 1000)
    if not fieldExists(fc2, compare + "2"):
        AddField_management(fc2, compare + "2", "TEXT", "", "", 1000)

    #get object of data
    data_obj = layer_obj_dict[keyword]

    #get unique ID
    uniqueID = data_obj.UNIQUEID

    #prep data for attribute comparison
    fields = data_obj.FIELD_MAP
    if "L_UPDATE" in fields:
        fields.remove("L_UPDATE")
    if "UPDATEBY" in fields:
        fields.remove("UPDATEBY")
    exp = 'Replace([' + ('] & [').join(fields) + '], " ", "")'
    CalculateField_management(fc1, compare + "1", exp, "VB")
    CalculateField_management(fc2, compare + "2", exp, "VB")

    #convert to feature layer
    lyr1 = MakeLayer(fc1, "lyr1", "")
    lyr2 = MakeLayer(fc2, "lyr2", "")

    #if needed, add a field index in the unique ID
    if not indexExists(fc1, ng911id):
        AddIndex_management(lyr1, uniqueID, ng911id, "UNIQUE")
    if not indexExists(fc2, ng911id):
        AddIndex_management(lyr2, uniqueID, ng911id, "UNIQUE")

    #join the two layers
    AddJoin_management(lyr1, uniqueID, lyr2, uniqueID)

    #see where they don't match
    wc = basename(fc1) + ".compare1 <> " + basename(fc2) + ".compare2"
    lyr_compare = MakeLayer(lyr1, "lyr", wc)

    #set up list for reporting various edits
    attributeEdits = []
    spatialEdits = []
    in1not2Records = []
    in2not1Records = []

    count = getFastCount(lyr_compare)

    #search for attribute issues
    if count > 0:
        with SearchCursor(lyr_compare, (basename(fc1) + "." + uniqueID)) as rows:
            for row in rows:
                unID = row[0]
                attributeEdits.append(unID)
            del row, rows

    #clean up attribute issue stuff
    #delete joined layer
    Delete_management(lyr_compare)

    #search for spatial differences if possible
    dataType = Describe(fc1).dataType
    if dataType != "Table":
        with SearchCursor(fc1, (uniqueID, "SHAPE@TRUECENTROID")) as sRows:
            for sRow in sRows:
                uniqueID_val = sRow[0]
                geom1 = sRow[1]
                where_clause = uniqueID + " = '" + uniqueID_val + "'"
                with SearchCursor(fc2, ("SHAPE@TRUECENTROID"), where_clause) as moreRows:
                    for mRow in moreRows:
                        geom2 = mRow[0]
                        if geom1 != geom2:
                            spatialEdits.append(uniqueID_val)
            del sRow, sRows

    #search for in 1 not 2 records
    wc1 = basename(fc2) + "." + compare + "2 is null"
    mismatch1 = MakeLayer(lyr1, "m1", wc1)

    count = getFastCount(mismatch1)

    if count > 0:
        with SearchCursor(mismatch1, (basename(fc1) + "." + uniqueID)) as rows:
            for row in rows:
                uniqueID_val = row[0]
                in1not2Records.append(uniqueID_val)
            del row, rows

    #clean up
    Delete_management(mismatch1)

    #remove join
    RemoveJoin_management(lyr1)

    #search for in 2 not 1 records
    AddJoin_management(lyr2, uniqueID, lyr1, uniqueID)
    wc2 = basename(fc1) + "." + compare + "1 is null"
    mismatch2 = MakeLayer(lyr2, "m2", wc2)

    count = getFastCount(mismatch2)

    if count > 0:
        with SearchCursor(mismatch2, (basename(fc2) + "." + uniqueID)) as rows:
            for row in rows:
                uniqueID_val = row[0]
                in2not1Records.append(uniqueID_val)
            del row, rows

    Delete_management(mismatch2)

    #remove join
    RemoveJoin_management(lyr2)

    #clean up
    #delete added fields
    DeleteField_management(fc1, [compare + "1"])
    DeleteField_management(fc2, [compare + "2"])

    #issue reporting
    issueDict = {"Attribute edit": attributeEdits, "Spatial edit": spatialEdits,
    "Record not in " + fc2: in1not2Records, "Record not in " + fc1: in2not1Records}

    if issueDict != {"Attribute edit": [], "Spatial edit": [],
    "Record not in " + fc2: [], "Record not in " + fc1: []}:

        #see if the results table already exists
        if not Exists(resultsTable):
            CreateTable_management(dirname(resultsTable), basename(resultsTable))

        #see if the fields exists
        if not fieldExists(resultsTable, "DateChecked"):
            AddField_management(resultsTable, "DateChecked", "DATE")
        if not fieldExists(resultsTable, "FC1"):
            AddField_management(resultsTable, "FC1", "TEXT", "", "", 150)
        if not fieldExists(resultsTable, "FC2"):
            AddField_management(resultsTable, "FC2", "TEXT", "", "", 150)
        if not fieldExists(resultsTable, "EditResult"):
            AddField_management(resultsTable, "EditResult", "TEXT", "", "", 250)
        if not fieldExists(resultsTable, "FeatureID"):
            AddField_management(resultsTable, "FeatureID", "TEXT", "", "", 30)

        #create result records
        insertFields = ("DateChecked", "FC1", "FC2", "EditResult", "FeatureID")
        today = strftime("%m/%d/%y")

        cursor = InsertCursor(resultsTable, insertFields)

        for message, IDlist in issueDict.iteritems():
            if IDlist != []:
                for id_num in IDlist:
                    cursor.insertRow((today, fc1, fc2, message, id_num))
    else:
        userMessage("No changes were found.")

    Delete_management(lyr1)
    Delete_management(lyr2)

def LaunchDataCompare(fc1, fc2, resultsTable):
    try:
        userMessage(fc1)
        userMessage(fc2)

        keyword = basename(fc1).upper()
        if "FIRE" in keyword or "EMS" in keyword or "LAW" in keyword:
            keyword = "ESB"
        if "ESZ" in keyword:
            keyword = "ESZ"
        if "PSAP" in keyword:
            keyword = "PSAP"

        GoAheadAndTest = 1

        #make sure the two layers are the same type
        if basename(fc1) != basename(fc2):
            GoAheadAndTest = 0

        #make sure both layers have the same unique ID
        if GoAheadAndTest == 1:
            fields1 = ListFieldNames(fc1)
            fields2 = ListFieldNames(fc2)

            uniqueID = layer_obj_dict[keyword].UNIQUEID
            if uniqueID not in fields1 or uniqueID not in fields2:
                GoAheadAndTest = 2

        if GoAheadAndTest == 1:
            userMessage("Comparing data...")
            CompareThatData(fc1, fc2, resultsTable, keyword)
        elif GoAheadAndTest == 2:
            userMessage("Layers do not have the same unique ID and cannot be compared.")
        elif GoAheadAndTest == 0:
            userMessage("Layers are not the same NG911 type and cannot be comapared.")
    except Exception as e:
        userMessage("Cannot compare " + basename(fc1) + " and " + basename(fc2) + ".")
        userMessage(str(e))

def CompareAllData(gdb1, gdb2, resultsTable):
    from arcpy import ListFeatureClasses, env
    #compare all the data in a geodatabase to another geodatabase

    fds = join(gdb1, "NG911") #gdb1 feature dataset
    env.workspace = fds

    #loop through layers in gdb1
    fcs = ListFeatureClasses()

    layers = layer_obj_dict.keys()

    checkList = {}

    #add the road alias table to the check list
    roadAlias1 = join(gdb1, "RoadAlias")
    roadAlias2 = join(gdb2, "RoadAlias")
    if Exists(roadAlias2) and Exists(roadAlias1):
        if not roadAlias1 in checkList.keys():
            checkList[roadAlias1] = roadAlias2

    #add feature classes to the check list
    for fc in fcs:
        if fc.upper() in layers:
            fcFull1 = join(fds, fc)
            fcFull2 = join(gdb2, "NG911", fc)

            if Exists(fcFull2):
                if not fcFull1 in checkList.keys():
                    checkList[fcFull1] = fcFull2

        else:
            for l in ['EMS','FIRE','LAW','PSAP','ESZ']:
                if l in fc.upper():
                    fcFull1 = join(fds, fc)
                    fcFull2 = join(gdb2, "NG911", fc)

                    if Exists(fcFull2):
                        if not fcFull1 in checkList.keys():
                            checkList[fcFull1] = fcFull2

    #launch the comparison for each active data lyaer
    for fc1, fc2 in checkList.iteritems():
            LaunchDataCompare(fc1, fc2, resultsTable)

    userMessage("Results of the data comparison are in " + resultsTable)

def main():
    item1 = GetParameterAsText(0)
    item2 = GetParameterAsText(1)
    resultsTable = GetParameterAsText(2)

    #handle scripting options so either two feature classes or two geodatabases can be processed
    if Describe(item1).dataType == "FeatureClass":
        LaunchDataCompare(item1, item2, resultsTable)
    elif Describe(item1).dataType == "Workspace":
        CompareAllData(item1, item2, resultsTable)

if __name__ == '__main__':
    main()
