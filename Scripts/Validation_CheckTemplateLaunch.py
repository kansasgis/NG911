#-------------------------------------------------------------------------------
# Name:        NG911_CheckTemplateLaunch
# Purpose:     Launches script to check NG911 template
#
# Author:      kristen
#
# Created:     24/11/2014
#-------------------------------------------------------------------------------
from NG911_Config import getGDBObject, currentPathSettings
from arcpy import GetParameterAsText, Exists
from os.path import basename
from NG911_DataCheck import main_check, userMessage

def main():

    #get parameters
    gdb = GetParameterAsText(0)
    domainsFolder = GetParameterAsText(1)
    esbList = GetParameterAsText(2).split(";")
    checkLayerList = GetParameterAsText(3)
    checkRequiredFields = GetParameterAsText(4)
    checkRequiredFieldValues = GetParameterAsText(5)
    checkSubmissionNumbers = GetParameterAsText(6)
    findInvalidGeometry = GetParameterAsText(7)
##    template10 = GetParameterAsText(8)

    gdbObject = getGDBObject(gdb)
    #create esb list
    esb = []

    for e in esbList:
        e = e.replace("'", "")
        e1 = basename(e)
        esb.append(e1)

    #create check list
    checkList = [checkLayerList,checkRequiredFields,checkRequiredFieldValues, checkSubmissionNumbers, findInvalidGeometry]

    fcList = [gdbObject.AddressPoints, gdbObject.AuthoritativeBoundary, gdbObject.RoadAlias, gdbObject.RoadCenterline]

    if Exists(gdbObject.MunicipalBoundary):
        fcList.append(gdbObject.MunicipalBoundary)

    #set object parameters
    checkType = "template"
    currentPathSettings.gdbPath = gdb
    currentPathSettings.domainsFolderPath = domainsFolder
    currentPathSettings.esbList = esb
    currentPathSettings.checkList = checkList
    currentPathSettings.fcList = fcList

##    if template10 == 'true':
##        currentPathSettings.gdbVersion = "10"
##    else:
##        currentPathSettings.gdbVersion = "11"

    #launch the data check
    main_check(checkType, currentPathSettings)

if __name__ == '__main__':
    main()
