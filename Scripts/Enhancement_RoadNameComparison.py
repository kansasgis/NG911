#-------------------------------------------------------------------------------
# Name:        Enhancement_RoadNameComparison
# Purpose:     Compares road names against address point road names to check
#               for consistency
#
# Author:      kristen
#
# Created:     12/08/2016
#-------------------------------------------------------------------------------
from arcpy import (Exists, AddJoin_management, RemoveJoin_management,
                    MakeTableView_management, SelectLayerByAttribute_management,
                    GetParameterAsText, CopyRows_management, CalculateField_management,
                    Dissolve_management, AddField_management, CopyFeatures_management,
                    MakeFeatureLayer_management, Delete_management)
from arcpy.da import SearchCursor, Editor, UpdateCursor
from NG911_GDB_Objects import getFCObject, getGDBObject
from NG911_DataCheck import userMessage, RecordResults
from NG911_arcpy_shortcuts import getFastCount, fieldExists
from os.path import join, basename
from time import strftime

def prepLayer(fc, copy_table, unique, rc_obj, gdb):

    #copy features and add field for the parsed label
    CopyFeatures_management(fc, copy_table)
    AddField_management(copy_table, "ROAD_" + rc_obj.LABEL, "TEXT", "", "", 100)

    #calculate the road label
    road_label_fields = rc_obj.LABEL_FIELDS
    if "LABEL" in road_label_fields:
        road_label_fields.remove("LABEL")
        road_label_fields.insert(0, "ROAD_" + rc_obj.LABEL)

    edit = Editor(gdb)
    edit.startEditing(False, False)

    #run update cursor
    with UpdateCursor(copy_table, road_label_fields) as rows:
        for row in rows:
            field_count = len(road_label_fields)
            start_int = 1
            label = ""

            #loop through the fields to see what's null & skip it
            while start_int < field_count:
                if row[start_int] is not None:
                    if row[start_int] not in ("", " "):
                        label = label + "|" + str(row[start_int])
                start_int = start_int + 1

            row[0] = label.strip("|")
            rows.updateRow(row)

    edit.stopEditing(True)

    lyr1 = "lyr1"
    MakeFeatureLayer_management(copy_table, lyr1)
    Dissolve_management(lyr1, unique, ["ROAD_" + rc_obj.LABEL])

    Delete_management(lyr1)

def main():
    gdb = GetParameterAsText(0)
    gdb_object = getGDBObject(gdb)
    addressPoints = gdb_object.AddressPoints
    roads = gdb_object.RoadCenterline

    #get address point and road objects
    a_obj = getFCObject(addressPoints)
    rc_obj = getFCObject(roads)

    #define working layers & tables
    road_name_table = join(gdb, "Road_Names")
    addy_pt_name_table = join(gdb, "AP_Road_Names")
    road_name_unique = join(gdb, "RD_UNIQUE")
    addy_pt_name_unique = join(gdb, "AP_UNIQUE")

    #remove any existing resources
    existsList = [road_name_table, addy_pt_name_table, road_name_unique, addy_pt_name_unique]

    for thingy in existsList:
        if Exists(thingy):
            Delete_management(thingy)

    #prep addresses
    prepLayer(addressPoints, addy_pt_name_table, addy_pt_name_unique, rc_obj, gdb)

    #prep roads
    prepLayer(roads, road_name_table, road_name_unique, rc_obj, gdb)

    #join address point road names to the road labels
    rnt = "rnt"
    apnt = "apnt"
    MakeTableView_management(road_name_unique, rnt)
    MakeTableView_management(addy_pt_name_unique, apnt)

    AddJoin_management(rnt, "ROAD_" + rc_obj.LABEL, apnt, "ROAD_" + rc_obj.LABEL)

    #report which road labels don't have a match in address points
    wc = "AP_UNIQUE.ROAD_LABEL is null"
    SelectLayerByAttribute_management(rnt, "NEW_SELECTION", wc)

    values = []
    filename = ""
    today = strftime("%m/%d/%Y")
    recordType = "fieldValues"

    a = getFastCount(rnt)

    #loop through unmatching records if necessary and report issues
    if a > 0:
        filename = "RoadCenterline"
        userMessage(str(a) + " records were in road labels but not address point road labels")
        with SearchCursor(rnt, ("RD_UNIQUE.ROAD_LABEL"), wc) as r_rows:
            for r in r_rows:
                report = "Notice: " + r[0] + " is a road name and not an address point road name."
                val = (today, report, filename, "", "")
                values.append(val)

    #remove join
    RemoveJoin_management(rnt)

    #join road labels to the address point road names
    AddJoin_management(apnt, "ROAD_" + rc_obj.LABEL, rnt, "ROAD_" + rc_obj.LABEL)

    #report which address point road names don't have a match in road labels
    wc1 = "RD_UNIQUE.ROAD_LABEL is null"
    SelectLayerByAttribute_management(apnt, "NEW_SELECTION", wc1)

    b = getFastCount(apnt)

    #loop through unmatching records if necessary and report issues
    if b > 0:
        filename = "AddressPoints"
        userMessage(str(b) + " records were in address point road labels and not in road labels")
        with SearchCursor(apnt, ("AP_UNIQUE.ROAD_LABEL"), wc1) as a_rows:
            for a_row in a_rows:
                report = "Notice: " + a_row[0] + " is an address point road name and not a road name."
                val = (today, report, filename, "", "")
                values.append(val)

    #remove join
    RemoveJoin_management(apnt)

    #report final issues
    if values != []:
        RecordResults(recordType, values, gdb)
        userMessage("Results are in FieldValuesCheckResults. Tables of unique road names are called RD_UNIQUE and AP_UNIQUE.")
        #if there are issues, leave the unique name tables
        existsList.remove(road_name_unique)
        existsList.remove(addy_pt_name_unique)

    #clean up
    existsList.append(rnt)
    existsList.append(apnt)

    for e in existsList:
        if Exists(e):
            Delete_management(e)

if __name__ == '__main__':
    main()
