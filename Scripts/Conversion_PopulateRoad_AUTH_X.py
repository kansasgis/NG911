#-------------------------------------------------------------------------------
# Name:        Conversion_PopulateRoadAUTHFields
# Purpose:     Auto-populates AUTH 2.1 road fields
#
# Author:      kristen
#
# Created:     10/10/2017
# Copyright:   (c) kristen 2017
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, Statistics_analysis, Delete_management,
                DisableEditorTracking_management, EnableEditorTracking_management, 
                Exists, AddMessage)
from arcpy.da import SearchCursor
from NG911_GDB_Objects import getFCObject, getGDBObject
from NG911_arcpy_shortcuts import CalcWithWC, hasRecords, fieldExists
from os.path import join

def main():
    gdb = GetParameterAsText(0)
    
    gdb_obj = getGDBObject(gdb)

    rc = gdb_obj.RoadCenterline
    rc_obj = getFCObject(rc)

    if Exists(rc) and hasRecords(rc):

        # get the most-frequently used county name
        freq_table = join("in_memory", "CountyStat")
        countyField = rc_obj.COUNTY_L
        Statistics_analysis(rc, freq_table, [[countyField, "COUNT"]], countyField)

        # get the county with the greatest count
        popVal = ""
        count = 0
        with SearchCursor(freq_table, (countyField, "COUNT_" + countyField)) as rows:
            for row in rows:
                if row[1] > count:
                    count = row[1]
                    popVal = row[0]

        DisableEditorTracking_management(rc, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")

        # make sure all records being populated are for submission
        for side in [rc_obj.COUNTY_L, rc_obj.COUNTY_R]:
            countyWC = side + " = '" + popVal + "' AND " + rc_obj.SUBMIT + " = 'Y'"

            # define the field to be populated
            field = "AUTH" + side[-2:]

            # make sure the field exists
            if fieldExists(rc, field):

                # calculate the field
                CalcWithWC(rc, field, '"Y"', countyWC)

            else:
                AddMessage("Road Centerline file does not have " + field + " field. Please double-check your geodatabase version.")
                print("Road Centerline file does not have " + field + " field. Please double-check your geodatabase version.")

        # clean up
        Delete_management(freq_table)

        # start editor tracking again
        EnableEditorTracking_management(rc, "", "", rc_obj.UPDATEBY, rc_obj.L_UPDATE, "NO_ADD_FIELDS", "UTC")

    else:
        AddMessage("Road centerline file does not exist or does not have records. Please check " + gdb)
        print("Road centerline file does not exist or does not have records. Please check " + gdb)

if __name__ == '__main__':
    main()
