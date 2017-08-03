#-------------------------------------------------------------------------------
# Name:        Enhancement_GeocodeAddressPoints
# Purpose:     Geocodes address points against road centerline
#
# Author:      kristen
#
# Created:     26/07/2016, Edited 10/28/2016, Edited 12/13/2016, edited 5/12/2017
# Copyright:   (c) kristen 2016
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, Exists, Copy_management, DisableEditorTracking_management,
            EnableEditorTracking_management)
from MSAG_DBComparison import launch_compare, prep_roads_for_comparison
from NG911_GDB_Objects import getDefault20NG911AddressObject, getDefault20NG911RoadCenterlineObject
from os.path import join

def main():
    gdb = GetParameterAsText(0)
    addy_fc = join(gdb, "NG911", "AddressPoints")
    rd_fc = join(gdb, "NG911", "RoadCenterline")
    addy_object = getDefault20NG911AddressObject()
    rd_object = getDefault20NG911RoadCenterlineObject()
    addy_field_list = rd_object.LABEL_FIELDS

    # create output results
    output_table = join(gdb, "AddressPt_GC_Results")
    if not Exists(output_table):
        Copy_management(addy_fc, output_table)

    # turn off editor tracking
    DisableEditorTracking_management(addy_fc, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")
    DisableEditorTracking_management(rd_fc, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")

    launch_compare(gdb, output_table, addy_object.HNO, addy_object.MSAGCO, addy_field_list)

    # turn editor tracking back on
    EnableEditorTracking_management(addy_fc, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")
    EnableEditorTracking_management(rd_fc, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")

if __name__ == '__main__':
    main()
