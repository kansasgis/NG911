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
from NG911_GDB_Objects import getFCObject, getGDBObject


def main():
    gdb = GetParameterAsText(0)
    
    gdb_obj = getGDBObject(gdb)

    ap = gdb_obj.AddressPoints
    rc = gdb_obj.RoadCenterline
    
    a_obj = getFCObject(ap)

    if Exists(ap) and Exists(rc) and hasRecords(ap) and hasRecords(rc):
        geocompare(gdb, "21", "true")

        # calculate any SUBMIT = 'N' as RCLSIDE "N"
        wc_rclside = "%s is null or %s in ('', ' ')" % (a_obj.RCLSIDE, a_obj.RCLSIDE)
        CalcWithWC(ap, a_obj.RCLSIDE, '"N"', wc_rclside)

    else:
        print("Either " + ap + " or " + rc + " either doesn't exist or doesn't have records. Cannot perform populating %s." % a_obj.RCLMATCH)
        AddMessage("Either " + ap + " or " + rc + " either doesn't exist or doesn't have records. Cannot perform populating %s." % a_obj.RCLMATCH)

if __name__ == '__main__':
    main()
