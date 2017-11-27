#-------------------------------------------------------------------------------
# Name:        Adjustment_FixLeadingTrailingSpaces
# Purpose:     Removes leading and trailing spaces from all MSAGCO fields
#
# Author:      kristen
#
# Created:     09/28/2017
#-------------------------------------------------------------------------------
from arcpy import GetParameterAsText
from NG911_DataFixes import FixMSAGCOspaces

def main():
    gdb = GetParameterAsText(0)

    FixMSAGCOspaces(gdb)

if __name__ == '__main__':
    main()
