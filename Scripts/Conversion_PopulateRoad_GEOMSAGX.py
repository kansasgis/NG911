#-------------------------------------------------------------------------------
# Name:        Conversion_PopulateRoad_GEOMSAGX
# Purpose:     Auto-populates AUTH 2.1 road fields
#
# Author:      kristen
#
# Created:     10/10/2017
# Copyright:   (c) kristen 2017
#-------------------------------------------------------------------------------
from arcpy import (CalculateField_management, MakeFeatureLayer_management, GetParameterAsText, Delete_management,
            DisableEditorTracking_management, EnableEditorTracking_management, Exists, AddMessage, AddError)
from NG911_GDB_Objects import getFCObject
from os.path import join
from NG911_arcpy_shortcuts import CalcWithWC, hasRecords, fieldExists, getFastCount

def userMessage(msg):
    AddMessage(msg)
    print(msg)

def main():
    gdb = GetParameterAsText(0)

    rc = join(gdb, "NG911", "RoadCenterline")
    rc_obj = getFCObject(rc)

    success = 0

    # make sure the file exists and has records
    if Exists(rc) and hasRecords(rc):

        check_auth_wc = "AUTH_L is null or AUTH_R is null"
        auth = "auth"
        MakeFeatureLayer_management(rc, auth, check_auth_wc)
        if getFastCount(auth) > 0:
            AddError("One or more AUTH_L or AUTH_R field values is null. No AUTH_L or AUTH_R fields can be null. Please fix those before running this tool.")
            print("One or more AUTH_L or AUTH_R field values is null. No AUTH_L or AUTH_R fields can be null. Please fix those before running this tool.")

        else:

            # disable editor tracking
            DisableEditorTracking_management(rc, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")

            # make sure all records being populated are for submission
            for side in [rc_obj.GEOMSAGL, rc_obj.GEOMSAGR]:
                x = side[-1]

                if fieldExists(rc, side):
                    # populate GEOMSAGX based on parity
                    # if side of road is ZERO parity, GEOMSAGX = "N"
                    parityWC = "PARITY_" + x + " = 'Z' AND " + rc_obj.SUBMIT + " = 'Y'"
                    bigNo = '"N"'
                    CalcWithWC(rc, side, bigNo, parityWC)

                    # populate GEOMSAGX based on AUTH_X
                    # if auth_X = N, GEOMSAGX = "N"
                    authWC = "AUTH_" + x + " = 'N' AND " + rc_obj.SUBMIT + " = 'Y'"
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
            EnableEditorTracking_management(rc, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")

    else:
        userMessage("Road Centerline file does not exist or does not have records. Please check " + rc)

    if success == 1:
        userMessage("Road centerline GEOMSAGX fields have been calculated. Please examine the values in areas that might need attention.")

if __name__ == '__main__':
    main()
