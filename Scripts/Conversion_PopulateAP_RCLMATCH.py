#-------------------------------------------------------------------------------
# Name:        Conversion_PopulateAP_RCLMATCH
# Purpose:     Auto-populates RCLMATCH 2.1 address point field
#
# Author:      kristen
#
# Created:     10/10/2017
# Copyright:   (c) kristen 2017
#-------------------------------------------------------------------------------
from Enhancement_GeocodeAddressPoints import geocompare
from arcpy import GetParameterAsText, Exists, AddMessage
from NG911_arcpy_shortcuts import hasRecords, CalcWithWC
from os.path import join

def main():
    gdb = GetParameterAsText(0)

    ap = join(gdb, "NG911", "AddressPoints")
    rc = join(gdb, "NG911", "RoadCenterline")

    if Exists(ap) and Exists(rc) and hasRecords(ap) and hasRecords(rc):
        geocompare(gdb, "21", "true")

        # calculate any SUBMIT = 'N' as RCLSIDE "N"
        wc_rclside = "RCLSIDE is null or RCLSIDE in ('', ' ')"
        CalcWithWC(ap, "RCLSIDE", '"N"', wc_rclside)

    else:
        print("Either " + ap + " or " + rc + " either doesn't exist or doesn't have records. Cannot perform populating RCLMATCH.")
        AddMessage("Either " + ap + " or " + rc + " either doesn't exist or doesn't have records. Cannot perform populating RCLMATCH.")

if __name__ == '__main__':
    main()
