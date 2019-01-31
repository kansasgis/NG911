#-------------------------------------------------------------------------------
# Name:        Enhancement_CheckRoadESN_Launch
# Purpose:     Launches script to check ESN values of NG911 road centerlines
#
# Author:      kristen
#
# Created:     November 16, 2018
#-------------------------------------------------------------------------------

def main():
    from arcpy import GetParameterAsText
    from NG911_DataCheck import checkRoadESN
    from NG911_GDB_Objects import NG911_Session

    #get parameters
    gdb = GetParameterAsText(0)
    session_object = NG911_Session(gdb)

    #launch the data check
    checkRoadESN(session_object)

if __name__ == '__main__':
    main()
