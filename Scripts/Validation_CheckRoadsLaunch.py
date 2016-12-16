#-------------------------------------------------------------------------------
# Name:        NG911_CheckRoadsLaunch
# Purpose:     Launches script to check NG911 road centerlines
#
# Author:      kristen
#
# Created:     25/11/2014
#-------------------------------------------------------------------------------

def main():
    from arcpy import GetParameterAsText
    from NG911_DataCheck import main_check
    from NG911_GDB_Objects import NG911_Session

    #get parameters
    gdb = GetParameterAsText(0)
    checkValuesAgainstDomain = GetParameterAsText(1)
    checkFeatureLocations = GetParameterAsText(2)
    checkRoadFrequency = GetParameterAsText(3)
    checkUniqueIDs = GetParameterAsText(4)
    checkCutbacks = GetParameterAsText(5)
    checkDirectionality = GetParameterAsText(6)
    checkRoadAliases = GetParameterAsText(7)
    checkAddressRanges = GetParameterAsText(8)

    #create check list
    checkList = [checkValuesAgainstDomain,checkFeatureLocations,checkRoadFrequency,checkUniqueIDs,checkCutbacks,checkDirectionality, checkRoadAliases,
                    checkAddressRanges]

    session_object = NG911_Session(gdb)
    gdbObject = session_object.gdbObject
    roadFile = gdbObject.RoadCenterline
    aliasFile = gdbObject.RoadAlias

    fcList = [roadFile, aliasFile]

    #set object parameters
    checkType = "Roads"
    session_object.gdbObject.fcList = fcList
    session_object.gdbObject.esbList = []
    session_object.checkList = checkList

    #launch the data check
    main_check(checkType, session_object)

if __name__ == '__main__':
    main()
