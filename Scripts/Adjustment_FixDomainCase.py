#-------------------------------------------------------------------------------
# Name:        Adjustment_FixDomainCase
# Purpose:     Fix domain errors where just the case is wrong
#
# Author:      kristen
#
# Created:     21/10/2015
#-------------------------------------------------------------------------------
from arcpy import GetParameterAsText
from NG911_DataFixes import FixDomainCase

def main():
    gdb = GetParameterAsText(0)
    domainFolder = GetParameterAsText(1)

    FixDomainCase(gdb, domainFolder)

if __name__ == '__main__':
    main()
