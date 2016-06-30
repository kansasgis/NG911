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
    import sys
    from arcpy import GetParameterAsText, AddError
    from os.path import join, basename

    from NG911_DataCheck import main_check, userMessage, Exists, getLayerList
    try:
        from NG911_Config import currentPathSettings # currentPathSettings should have all the path information available. ## import esb, gdb, folder
    except:
        userMessage( "Copy config file into command line")

    #get parameters
    gdb = GetParameterAsText(0)
    domainsFolder = GetParameterAsText(1)
    esbList = GetParameterAsText(2).split(";")
    checkValuesAgainstDomain = GetParameterAsText(3)
    checkFeatureLocations = GetParameterAsText(4)
    checkUniqueIDs = GetParameterAsText(5)
##    template10 = GetParameterAsText(6)

    #create esb list
    esb = []
    fcList = []

    layerList = getLayerList()

    layerFlag = 0

    for e in esbList:
        e = e.replace("'", "")
        for l in ['EMS','FIRE','LAW','PSAP','ESB']:
            if l in e.upper():
                fcList.append(e)
                e1 = basename(e)
                if e1 in layerList:
                    layerFlag = 1
                else:
                    esb.append(e1)

    if layerFlag == 1:
        AddError("Please define PSAP and ESB layers like EMS, fire & law enforcement boundaries. One or more layers you identfied is a different layer type.")
        print("Please define PSAP and ESB layers like EMS, fire & law enforcement boundaries. One or more layers you identfied is a different layer type.")
        sys.exit()

    #create check list
    checkList = [checkValuesAgainstDomain,checkFeatureLocations,checkUniqueIDs]

    #set object parameters
    checkType = "ESB"
    currentPathSettings.gdbPath = gdb
    currentPathSettings.domainsFolderPath = domainsFolder
    currentPathSettings.fcList = fcList
    currentPathSettings.esbList = esb
    currentPathSettings.checkList = checkList

##    if template10 == 'true':
##        currentPathSettings.gdbVersion = "10"
##    else:
##        currentPathSettings.gdbVersion = "11"

    #launch the data check
    main_check(checkType, currentPathSettings)

if __name__ == '__main__':
    main()
