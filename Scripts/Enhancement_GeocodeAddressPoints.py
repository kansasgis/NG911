#-------------------------------------------------------------------------------
# Name:        Enhancement_GeocodeAddressPoints
# Purpose:     Geocodes address points against road centerline
#
# Author:      kristen
#
# Created:     26/07/2016, Edited 10/28/2016, Edited 12/13/2016, edited 5/12/2017
# Copyright:   (c) kristen 2016
#-------------------------------------------------------------------------------
from arcpy import GetParameterAsText, Exists, Copy_management
from MSAG_DBComparison import launch_compare, prep_roads_for_comparison
from NG911_GDB_Objects import getDefault20NG911AddressObject, getDefault20NG911RoadCenterlineObject
from os.path import join

def main():
    gdb = GetParameterAsText(0)
    addy_fc = join(gdb, "NG911", "AddressPoints")
    addy_object = getDefault20NG911AddressObject()
    rd_object = getDefault20NG911RoadCenterlineObject()
    addy_field_list = rd_object.LABEL_FIELDS

    # create output results
    output_table = join(gdb, "AddressPt_GC_Results")
    if not Exists(output_table):
        Copy_management(addy_fc, output_table)

    launch_compare(gdb, output_table, addy_object.HNO, addy_object.MSAGCO, addy_field_list)

##    geocodeAddressPoints(gdb)

if __name__ == '__main__':
    main()
