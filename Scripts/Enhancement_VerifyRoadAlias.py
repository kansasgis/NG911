#-------------------------------------------------------------------------------
# Name:        Enhancement_VerifyRoadAlias
# Purpose:     See if the road alias values for highways are the approved names
#
# Author:      kristen
#
# Created:     21/12/2015
#-------------------------------------------------------------------------------
from arcpy import GetParameterAsText
from NG911_DataCheck import VerifyRoadAlias

def main():
    gdb = GetParameterAsText(0)
    domainFolder = GetParameterAsText(1)

    VerifyRoadAlias(gdb, domainFolder)

if __name__ == '__main__':
    main()
