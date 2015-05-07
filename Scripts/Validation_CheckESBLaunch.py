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
    from os.path import join, basename

    from NG911_DataCheck import main_check, userMessage, Exists
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
    template10 = GetParameterAsText(6)

    #create esb list
    esb = []
    fcList = []

    for e in esbList:
        e = e.replace("'", "")
        fcList.append(e)
        e1 = basename(e)
        esb.append(e1)

    #create check list
    checkList = [checkValuesAgainstDomain,checkFeatureLocations,checkUniqueIDs]

    #set object parameters
    checkType = "ESB"
    currentPathSettings.gdbPath = gdb
    currentPathSettings.domainsFolderPath = domainsFolder
    currentPathSettings.fcList = fcList
    currentPathSettings.esbList = esb
    currentPathSettings.checkList = checkList

    if template10 == 'true':
        currentPathSettings.gdbVersion = "10"
    else:
        currentPathSettings.gdbVersion = "11"

    #launch the data check
    main_check(checkType, currentPathSettings)

if __name__ == '__main__':
    main()
