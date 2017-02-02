#-------------------------------------------------------------------------------
# Name:        Validation_CheckOtherLayers
# Purpose:     Launches script to check NG911 other data (like parcels, gates, hydrants, cell sites)
#
# Author:      kristen
#
# Created:     Oct. 20, 2016
#-------------------------------------------------------------------------------

def main():
    from arcpy import GetParameterAsText, Exists
    from os.path import join, basename
    from NG911_DataCheck import main_check, userMessage
    from NG911_GDB_Objects import NG911_Session
    from NG911_arcpy_shortcuts import hasRecords

    #get parameters
    gdb = GetParameterAsText(0)
    checkValuesAgainstDomain = GetParameterAsText(1)
    checkFeatureLocations = GetParameterAsText(2)
    checkUniqueIDs = GetParameterAsText(3)

    #create check list
    checkList = [checkValuesAgainstDomain,checkFeatureLocations,checkUniqueIDs]

    #set object parameters
    checkType = "standard"
    session_object = NG911_Session(gdb)
    NG911_Session.checkList = checkList
    gdbObject = session_object.gdbObject

    otherList = gdbObject.otherLayers
    fcList = []
    for fc in otherList:
        if Exists(fc):
            if hasRecords(fc):
                fcList.append(fc)
            else:
                userMessage(basename(fc) + " has no records and will not be checked.")

    #redo various settings to limit what is checked
    session_object.gdbObject.fcList = fcList
    session_object.checkList = checkList

    #launch the data check
    if len(fcList) > 0:
        main_check(checkType, session_object)
    else:
        userMessage("You do not have any additional layers in the geodatabase to check.")

if __name__ == '__main__':
    main()
