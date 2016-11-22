#-------------------------------------------------------------------------------
# Name:        MSAG_CreateLocators
# Purpose:     Create composite locator using MSAG info from address points
#               and road centerlines
#
# Author:      kristen
#
# Created:     01/08/2016
#-------------------------------------------------------------------------------
from MSAG_CheckTNList import createLocators
from arcpy import GetParameterAsText
from NG911_GDB_Objects import getGDBObject

def main():

    gdb = GetParameterAsText(0)
    gdb_object = getGDBObject(gdb)

    createLocators(gdb_object)

if __name__ == '__main__':
    main()
