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
from os.path import join
from time import strftime

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
    addy_pt_name_table_full = join(gdb, "AP_Road_Names_Full")
    addy_pt_name_table = join(gdb, "AP_Road_Names")

    #remove any existing resources
    existsList = [road_name_table, addy_pt_name_table, addy_pt_name_table_full]

    for thingy in existsList:
        if Exists(thingy):
            Delete_management(thingy)

    #get list of road labels
    rd_lyr = "rd_lyr"
    userMessage("Preparing road names...")
    MakeFeatureLayer_management(roads, rd_lyr)
    Dissolve_management(rd_lyr, road_name_table, [rc_obj.LABEL])
    CalculateField_management(road_name_table, rc_obj.LABEL, "!" + rc_obj.LABEL + "!.upper()","PYTHON")

    #create list of road names from address points
    #copy rows to a table and add a field
    userMessage("Preparing address point road names...")
    CopyFeatures_management(addressPoints, addy_pt_name_table_full)
    AddField_management(addy_pt_name_table_full, "ROAD_" + rc_obj.LABEL, "TEXT", "", "", 100)

    #calculate the road label in the address points
    road_label_fields = rc_obj.LABEL_FIELDS
    road_label_fields.remove("LABEL")
    road_label_fields.insert(0, "ROAD_" + rc_obj.LABEL)

    edit = Editor(gdb)
    edit.startEditing(False, False)

    #run update cursor
    with UpdateCursor(addy_pt_name_table_full, road_label_fields) as rows:
        for row in rows:
            field_count = len(road_label_fields)
            start_int = 1
            label = ""

            #loop through the fields to see what's null & skip it
            while start_int < field_count:
                if row[start_int] is not None:
                    if row[start_int] not in ("", " "):
                        label = label + " " + str(row[start_int])
                start_int = start_int + 1

            row[0] = label.strip()
            rows.updateRow(row)

    edit.stopEditing(True)


    #clean up all labels
    trim_expression = '" ".join(!' + rc_obj.LABEL + '!.split())'
    CalculateField_management(addy_pt_name_table_full, rc_obj.LABEL, trim_expression, "PYTHON_9.3")


    #run a dissolve on the address points
    ap_lyr1 = "ap_lyr1"
    MakeFeatureLayer_management(addy_pt_name_table_full, ap_lyr1)
    Dissolve_management(ap_lyr1, addy_pt_name_table, ["ROAD_" + rc_obj.LABEL])

    #clean up intermediate data
    Delete_management(addy_pt_name_table_full)

    #join address point road names to the road labels
    rnt = "rnt"
    apnt = "apnt"
    MakeTableView_management(road_name_table, rnt)
    MakeTableView_management(addy_pt_name_table, apnt)

    AddJoin_management(rnt, rc_obj.LABEL, apnt, "ROAD_" + rc_obj.LABEL)

    #report which road labels don't have a match in address points
    wc = "AP_Road_Names.ROAD_LABEL is null"
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
        with SearchCursor(rnt, ("Road_Names.LABEL"), wc) as r_rows:
            for r in r_rows:
                report = "Notice: " + r[0] + " is a road name and not an address point road name."
                val = (today, report, filename, "", "")
                values.append(val)

    #remove join
    RemoveJoin_management(rnt)

    #join road labels to the address point road names
    AddJoin_management(apnt, "ROAD_" + rc_obj.LABEL, rnt, rc_obj.LABEL)

    #report which address point road names don't have a match in road labels
    wc1 = "Road_Names.LABEL is null"
    SelectLayerByAttribute_management(apnt, "NEW_SELECTION", wc1)

    b = getFastCount(apnt)

    #loop through unmatching records if necessary and report issues
    if b > 0:
        filename = "AddressPoints"
        userMessage(str(b) + " records were in address point road labels and not in road labels")
        with SearchCursor(apnt, ("AP_Road_Names.ROAD_LABEL"), wc1) as a_rows:
            for a_row in a_rows:
                report = "Notice: " + a_row[0] + " is an address point road name and not a road name."
                val = (today, report, filename, "", "")
                values.append(val)

    #remove join
    RemoveJoin_management(apnt)

    #report final issues
    if values != []:
        RecordResults(recordType, values, gdb)

if __name__ == '__main__':
    main()
