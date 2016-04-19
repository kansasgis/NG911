#-------------------------------------------------------------------------------
# Name:        NG911_CheckAddressPointsLaunch
# Purpose:     Launches script to check NG911 address points
#
# Author:      kristen
#
# Created:     24/11/2014
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
    geocodeAddressPoints = GetParameterAsText(4)
    checkAddressPointFrequency = GetParameterAsText(5)
    checkUniqueIDs = GetParameterAsText(6)
    checkESZ = GetParameterAsText(7)
    ESZlayer = GetParameterAsText(8)
    template10 = GetParameterAsText(9)

    #create check list
    checkList = [checkValuesAgainstDomain,checkFeatureLocations,geocodeAddressPoints,checkAddressPointFrequency,checkUniqueIDs,checkESZ]

    #set object parameters
    checkType = "AddressPoints"
    gdbObject = getGDBObject(gdb)
    currentPathSettings.gdbPath = gdb
    currentPathSettings.domainsFolderPath = domainsFolder
    currentPathSettings.addressPointsPath = gdbObject.AddressPoints
    currentPathSettings.fcList = [currentPathSettings.addressPointsPath]
    currentPathSettings.esbList = []
    currentPathSettings.checkList = checkList
    currentPathSettings.ESZ = ESZlayer

    if template10 == 'true':
        currentPathSettings.gdbVersion = "10"
    else:
        currentPathSettings.gdbVersion = "11"

    #launch the data check
    main_check(checkType, currentPathSettings)

if __name__ == '__main__':
    main()
