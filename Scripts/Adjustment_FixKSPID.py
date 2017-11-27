#-------------------------------------------------------------------------------
# Name:        Adjustment_FixKSPID
# Purpose:     Fix dots and dashes in KSPID records
#
# Author:      kristen
#
# Created:     09/28/2017
#-------------------------------------------------------------------------------
from arcpy import GetParameterAsText
from NG911_DataFixes import fixKSPID

def main():
    gdb = GetParameterAsText(0)

    fixKSPID(gdb)

if __name__ == '__main__':
    main()
