#-------------------------------------------------------------------------------
# Name:        Conversion_PopulateAP_GEOMSAG
# Purpose:     Auto-populates GEOMSAG 2.1 address point field
#
# Author:      kristen
#
# Created:     10/10/2017
# Copyright:   (c) kristen 2017
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, MakeFeatureLayer_management, CalculateField_management,
    DisableEditorTracking_management, EnableEditorTracking_management, Exists, AddMessage)
from os.path import join
from NG911_arcpy_shortcuts import CalcWithWC, fieldExists, hasRecords


def main():
    gdb = GetParameterAsText(0)

    ap = join(gdb, "NG911", "AddressPoints")

    # make sure the file exists and has records
    if Exists(ap) and hasRecords(ap):

        # disable editor tracking
        DisableEditorTracking_management(ap, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")

        # set up the queries with the desired result
        wc_list = [["SUBMIT = 'N'", '"N"'],
                   ["RCLMATCH = 'NO_MATCH' and SUBMIT = 'Y'", '"Y"'],
                   ["RCLMATCH <> 'NO_MATCH' and SUBMIT = 'Y'", '"N"']]

        # loop through & calculate the fields
        for wc_pair in wc_list:
            wc = wc_pair[0]
            val = wc_pair[1]

            # make sure the field exists
            if fieldExists(ap, "GEOMSAG"):
                CalcWithWC(ap, "GEOMSAG", val, wc)

            else:
                AddMessage("Address Point file does not have GEOMSAG field. Please double-check your geodatabase version.")
                print("Address Point file does not have GEOMSAG field. Please double-check your geodatabase version.")

        # reenable editor tracking
        EnableEditorTracking_management(ap, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")

    else:
        AddMessage("Address point file does not exist or does not have records. Please check " + ap)
        print("Address point file does not exist or does not have records. Please check " + ap)


if __name__ == '__main__':
    main()
