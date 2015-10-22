#-------------------------------------------------------------------------------
# Name:        Adjustment_CreateGeocodeExceptions
# Purpose:     Create a table of geocoding exceptions so data can be submitted and processed
#
# Author:      kristen
#
# Created:     21/10/2015
#-------------------------------------------------------------------------------
from arcpy import GetParameterAsText
from NG911_DataFixes import CreateGeocodeExceptions

def main():
    gdb = GetParameterAsText(0)
    CreateGeocodeExceptions(gdb)

if __name__ == '__main__':
    main()
