#-------------------------------------------------------------------------------
# Name:        Conversion_PopulateRoad_GEOMSAGX
# Purpose:     Auto-populates AUTH 2.1 road fields
#
# Author:      kristen
#
# Created:     10/10/2017
# Copyright:   (c) kristen 2017
#-------------------------------------------------------------------------------
from arcpy import (MakeFeatureLayer_management, GetParameterAsText, 
            DisableEditorTracking_management, EnableEditorTracking_management, 
            Exists, AddMessage, AddError)
from NG911_GDB_Objects import getFCObject, getGDBObject
from NG911_arcpy_shortcuts import CalcWithWC, hasRecords, fieldExists, getFastCount

def userMessage(msg):
    AddMessage(msg)
    print(msg)

def main():
    gdb = GetParameterAsText(0)

    gdb_obj = getGDBObject(gdb)
    rc = gdb_obj.RoadCenterline
    rc_obj = getFCObject(rc)

    success = 0

    # make sure the file exists and has records
    if Exists(rc) and hasRecords(rc):

        check_auth_wc = "%s is null or %s is null" % (rc_obj.AUTH_L, rc_obj.AUTH_R)
        auth = "auth"
        MakeFeatureLayer_management(rc, auth, check_auth_wc)
        if getFastCount(auth) > 0:
            msg = "One or more %s or %s field values is null. No %s or %s fields can be null. Please fix those before running this tool." % (rc_obj.AUTH_L, rc_obj.AUTH_R, rc_obj.AUTH_L, rc_obj.AUTH_R)
            AddError(msg)
            print(msg)

        else:

            # disable editor tracking
            DisableEditorTracking_management(rc, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")

            # make sure all records being populated are for submission
            for side in [rc_obj.GEOMSAGL, rc_obj.GEOMSAGR]:
                x = side[-1]

                if fieldExists(rc, side):
                    # populate GEOMSAGX based on parity
                    # if side of road is ZERO parity, GEOMSAGX = "N"
                    parityWC = rc_obj.PARITY_L[0:-1] + x + " = 'Z' AND " + rc_obj.SUBMIT + " = 'Y'"
                    bigNo = '"N"'
                    CalcWithWC(rc, side, bigNo, parityWC)

                    # populate GEOMSAGX based on AUTH_X
                    # if auth_X = N, GEOMSAGX = "N"
                    authWC = rc_obj.AUTH_L[0:-1] + x + " = 'N' AND " + rc_obj.SUBMIT + " = 'Y'"
                    CalcWithWC(rc, side, bigNo, authWC)

                    # populate all remaining records as "Y"
                    geomsagWC = side + " is null or " + side + " = ''"
                    yes = '"Y"'
                    CalcWithWC(rc, side, yes, geomsagWC)

                    userMessage("Completed calculating " + side)

                    success = 1

                else:
                    userMessage("Road centerline file does not have " + side + " field. Please double-check your geodatabase version.")

            # reenable editor tracking
            EnableEditorTracking_management(rc, "", "", rc_obj.UPDATEBY, rc_obj.L_UPDATE, "NO_ADD_FIELDS", "UTC")

    else:
        userMessage("Road Centerline file does not exist or does not have records. Please check " + rc)

    if success == 1:
        userMessage("Road centerline GEOMSAGX fields have been calculated. Please examine the values in areas that might need attention.")

if __name__ == '__main__':
    main()
