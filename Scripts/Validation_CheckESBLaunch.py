#-------------------------------------------------------------------------------
# Name:        NG911_CheckESBLaunch
# Purpose:     Launches script to check NG911 emergency services boundaries
#
# Author:      kristen
#
# Created:     25/11/2014
# Copyright:   (c) kristen 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def main():
    from arcpy import GetParameterAsText
    from NG911_DataCheck import main_check
    from NG911_GDB_Objects import NG911_Session

    #get parameters
    gdb = GetParameterAsText(0)
    checkValuesAgainstDomain = GetParameterAsText(1)
    checkFeatureLocations = GetParameterAsText(2)
    checkUniqueIDs = GetParameterAsText(3)

    #create check list
    checkList = [checkValuesAgainstDomain,checkFeatureLocations,checkUniqueIDs]

    session_object = NG911_Session(gdb)
    fcList = session_object.gdbObject.esbList
    session_object.gdbObject.fcList = fcList

    #set object parameters
    checkType = "ESB"
    session_object.checkList = checkList

    #launch the data check
    main_check(checkType, session_object)

if __name__ == '__main__':
    main()
