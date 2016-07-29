#-------------------------------------------------------------------------------
# Name:        Enhancement_GeocodeAddressPoints
# Purpose:     Geocodes address points against road centerline
#
# Author:      kristen
#
# Created:     26/07/2016
# Copyright:   (c) kristen 2016
#-------------------------------------------------------------------------------
from arcpy import GetParameterAsText
from NG911_DataCheck import geocodeAddressPoints

def main():
    gdb = GetParameterAsText(0)

    geocodeAddressPoints(gdb)

if __name__ == '__main__':
    main()
