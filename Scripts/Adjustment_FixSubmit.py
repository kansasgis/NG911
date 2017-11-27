#-------------------------------------------------------------------------------
# Name:        Adjustment_FixSubmit
# Purpose:     Fix SUBMIT field so all blanks or nulls become "Y"
#
# Author:      kristen
#
# Created:     10/23/2017
#-------------------------------------------------------------------------------
from arcpy import GetParameterAsText
from NG911_DataFixes import fixSubmit

def main():
    gdb = GetParameterAsText(0)

    fixSubmit(gdb)

if __name__ == '__main__':
    main()
