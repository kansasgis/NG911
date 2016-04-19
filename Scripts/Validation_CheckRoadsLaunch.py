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
    from os.path import join

    from NG911_DataCheck import main_check, userMessage
    try:
        from NG911_Config import currentPathSettings, getGDBObject # currentPathSettings should have all the path information available. ## import esb, gdb, folder
    except:
        userMessage( "Copy config file into command line")

    #get parameters
    gdb = GetParameterAsText(0)
    domainsFolder = GetParameterAsText(1)
    checkValuesAgainstDomain = GetParameterAsText(2)
    checkFeatureLocations = GetParameterAsText(3)
    checkRoadFrequency = GetParameterAsText(4)
    checkUniqueIDs = GetParameterAsText(5)
    checkCutbacks = GetParameterAsText(6)
    checkDirectionality = GetParameterAsText(7)
    checkRoadAliases = GetParameterAsText(8)
    template10 = GetParameterAsText(9)

    #create check list
    checkList = [checkValuesAgainstDomain,checkFeatureLocations,checkRoadFrequency,checkUniqueIDs,checkCutbacks,checkDirectionality, checkRoadAliases]

    gdbObject = getGDBObject(gdb)
    roadFile = gdbObject.RoadCenterline
    aliasFile = gdbObject.RoadAlias

    fcList = [roadFile, aliasFile]

    #set object parameters
    checkType = "Roads"
    currentPathSettings.gdbPath = gdb
    currentPathSettings.domainsFolderPath = domainsFolder
    currentPathSettings.fcList = fcList
    currentPathSettings.esbList = []
    currentPathSettings.checkList = checkList

    if template10 == 'true':
        currentPathSettings.gdbVersion = "10"
    else:
        currentPathSettings.gdbVersion = "11"

    #launch the data check
    main_check(checkType, currentPathSettings)

if __name__ == '__main__':
    main()
