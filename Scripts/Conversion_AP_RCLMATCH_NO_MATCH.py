#-------------------------------------------------------------------------------
# Name:        Conversion_AP_RCLMATCH_NO_MATCH
# Purpose:     Auto-populates any empty RCLMATCH 2.1 address point records with "NO_MATCH"
#
# Author:      kristen
#
# Created:     10/11/2017
# Copyright:   (c) kristen 2017
#-------------------------------------------------------------------------------
from arcpy import GetParameterAsText, DisableEditorTracking_management, EnableEditorTracking_management, Exists, AddMessage
from NG911_arcpy_shortcuts import CalcWithWC, hasRecords, fieldExists
from NG911_GDB_Objects import getFCObject, getGDBObject

def main():
    gdb = GetParameterAsText(0)
    
    # get objects and values
    gdb_obj = getGDBObject(gdb)
    addy_pt = gdb_obj.AddressPoints
    a_obj = getFCObject(addy_pt)
    rclm = a_obj.RCLMATCH

    # make sure the address point file exists and has records
    if Exists(addy_pt) and hasRecords(addy_pt):

        # disable editor tracking
        DisableEditorTracking_management(addy_pt, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")

        # update RCLMATCH records where empty
        wc = "%s is null or %s in (' ', '')" % (rclm, rclm)
        val = '"NO_MATCH"'
        if fieldExists(addy_pt, rclm):
            CalcWithWC(addy_pt, rclm, val, wc)

        else:
            AddMessage("Address point file does not have %s field. Please double-check your geodatabase version." % rclm)
            print("Address point file does not have %s field. Please double-check your geodatabase version." % rclm)

        # reenable editor tracking
        EnableEditorTracking_management(addy_pt, "", "", a_obj.UPDATEBY, a_obj.L_UPDATE, "NO_ADD_FIELDS", "UTC")

    else:
        AddMessage("Address point file does not exist or does not have records. Please check " + gdb)
        print("Address point file does not exist or does not have records. Please check " + gdb)

if __name__ == '__main__':
    main()
