#-------------------------------------------------------------------------------
# Name:        MSAG_GeocodeTNList_Prepped
# Purpose:     Geocode a TN list where the full address has already been caclulated
#
# Author:      kristen
#
# Created:     01/08/2016
#-------------------------------------------------------------------------------
from MSAG_CheckTNList import createLocators, geocodeTable
from arcpy import (GetParameterAsText, GeocodeAddresses_geocoding,
        ExcelToTable_conversion, Exists, Delete_management)
from NG911_Config import getGDBObject
from NG911_GDB_Objects import getTNObject
from os.path import join, dirname, basename
from NG911_DataCheck import userMessage
from time import strftime

def main():

    gdb = GetParameterAsText(0)
    xls = GetParameterAsText(1)
    field = GetParameterAsText(2)
    gdb_object = getGDBObject(gdb)

    #create locators
    createLocators(gdb_object)

    #export xls to gdb table
    tn_object = getTNObject(gdb)
    outTable = tn_object.TN_List
    if Exists(outTable):
        Delete_management(outTable)
    ExcelToTable_conversion(dirname(xls), outTable, basename(xls).replace("$", ""))

    #geocode addresses
    geocodeTable(gdb, field)

if __name__ == '__main__':
    main()
