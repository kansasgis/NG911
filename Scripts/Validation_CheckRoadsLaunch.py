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
        from NG911_Config import currentPathSettings # currentPathSettings should have all the path information available. ## import esb, gdb, folder
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
    template10 = GetParameterAsText(7)

    #create check list
    checkList = [checkValuesAgainstDomain,checkFeatureLocations,checkRoadFrequency,checkUniqueIDs,checkCutbacks]

    roadFile = join(gdb, "RoadCenterline")
    aliasFile = join(gdb, "RoadAlias")

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
