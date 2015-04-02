#-------------------------------------------------------------------------------
# Name:        NG911_CheckTemplateLaunch
# Purpose:     Launches script to check NG911 template
#
# Author:      kristen
#
# Created:     24/11/2014
#-------------------------------------------------------------------------------

def main():
    from arcpy import GetParameterAsText
    from os.path import basename

    from NG911_DataCheck import main_check, userMessage
    try:
        from NG911_Config import currentPathSettings # currentPathSettings should have all the path information available. ## import esb, gdb, folder
    except:
        userMessage( "Copy config file into command line")

    #get parameters
    gdb = GetParameterAsText(0)
    domainsFolder = GetParameterAsText(1)
    esbList = GetParameterAsText(2).split(";")
    checkLayerList = GetParameterAsText(3)
    checkRequiredFields = GetParameterAsText(4)
    checkRequiredFieldValues = GetParameterAsText(5)
    template10 = GetParameterAsText(6)

    #create esb list
    esb = []

    for e in esbList:
        e1 = basename(e)
        esb.append(e1)

    #create check list
    checkList = [checkLayerList,checkRequiredFields,checkRequiredFieldValues]

    #set object parameters
    checkType = "template"
    currentPathSettings.gdbPath = gdb
    currentPathSettings.domainsFolderPath = domainsFolder
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
