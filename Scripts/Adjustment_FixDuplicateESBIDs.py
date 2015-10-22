#-------------------------------------------------------------------------------
# Name:        Adjustment_FixDuplicateESBIDs
# Purpose:     Fix duplicate ESB ids
#
# Author:      kristen
#
# Created:     21/10/2015
#-------------------------------------------------------------------------------
from arcpy import GetParameterAsText
from NG911_DataFixes import FixDuplicateESBIDs

def main():
    EMSESB = GetParameterAsText(0)
    FireESB = GetParameterAsText(1)
    LawESB = GetParameterAsText(2)

    FixDuplicateESBIDs(FireESB, EMSESB, LawESB)

if __name__ == '__main__':
    main()
