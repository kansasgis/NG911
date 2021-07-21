#-------------------------------------------------------------------------------
# Name:        Conversion_PopulateAP_GEOMSAG
# Purpose:     Auto-populates GEOMSAG 2.1 address point field
#
# Author:      kristen
#
# Created:     10/10/2017
# Copyright:   (c) kristen 2017
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, DisableEditorTracking_management, 
                   EnableEditorTracking_management, Exists, AddMessage)
from NG911_arcpy_shortcuts import CalcWithWC, fieldExists, hasRecords
from NG911_GDB_Objects import getFCObject, getGDBObject


def main():
    gdb = GetParameterAsText(0)
    
    gdb_obj = getGDBObject(gdb)

    ap = gdb_obj.AddressPoints

    # make sure the file exists and has records
    if Exists(ap) and hasRecords(ap):
        a_obj = getFCObject(ap)

        # disable editor tracking
        DisableEditorTracking_management(ap, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")

        # set up the queries with the desired result
        wc_list = [["%s = 'N'" % a_obj.SUBMIT, '"N"'],
                   ["%s = 'NO_MATCH' and %s = 'Y'" % (a_obj.RCLMATCH, a_obj.SUBMIT), '"Y"'],
                   ["%s <> 'NO_MATCH' and %s = 'Y'" % (a_obj.RCLMATCH, a_obj.SUBMIT), '"N"']]

        # loop through & calculate the fields
        for wc_pair in wc_list:
            wc = wc_pair[0]
            val = wc_pair[1]

            # make sure the field exists
            if fieldExists(ap, a_obj.GEOMSAG):
                CalcWithWC(ap, a_obj.GEOMSAG, val, wc)

            else:
                AddMessage("Address Point file does not have %s field. Please double-check your geodatabase version." % a_obj.GEOMSAG)
                print("Address Point file does not have %s field. Please double-check your geodatabase version." % a_obj.GEOMSAG)

        # reenable editor tracking
        EnableEditorTracking_management(ap, "", "", a_obj.UPDATEBY, a_obj.L_UPDATE, "NO_ADD_FIELDS", "UTC")

    else:
        AddMessage("Address point file does not exist or does not have records. Please check " + ap)
        print("Address point file does not exist or does not have records. Please check " + ap)


if __name__ == '__main__':
    main()
