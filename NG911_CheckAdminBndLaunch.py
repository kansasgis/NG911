#-------------------------------------------------------------------------------
# Name:        NG911_CheckAdminBndLaunch
# Purpose:     Launches script to check NG911 administrative boundaries
#
# Author:      kristen
#
# Created:     25/11/2014
#-------------------------------------------------------------------------------

def main():
    from arcpy import GetParameterAsText, Exists
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

    #create check list
    checkList = [checkValuesAgainstDomain,checkFeatureLocations]

    #set object parameters
    checkType = "admin"
    currentPathSettings.gdbPath = gdb
    currentPathSettings.domainsFolderPath = domainsFolder

    adminList = ["AuthoritativeBoundary", "CountyBoundary", "MunicipalBoundary", "ESZ", "PSAP"]
    fcList = []
    for admin in adminList:
        path = join(gdb, admin)
        if Exists(path):
            fcList.append(path)

    currentPathSettings.fcList = fcList
    currentPathSettings.checkList = checkList

    #launch the data check
    main_check(checkType, currentPathSettings)

if __name__ == '__main__':
    main()
