#-------------------------------------------------------------------------------
# Name:        Validation_CheckAll
# Purpose:     Check all validation scripts
#
# Author:      kristen
#
# Created:     20/10/2015
#-------------------------------------------------------------------------------
from NG911_Config import getGDBObject, currentPathSettings
from NG911_DataCheck import sanityCheck, userMessage
from arcpy import Exists, GetParameterAsText
from os.path import basename
from Conversion_ZipNG911Geodatabase import createNG911Zip

def validateAllPrep(gdb, domain, esbList, ESZ, template10, zipFlag, zipPath):

    if template10 == 'true':
        version = "10"
    else:
        version = "11"

    gdbObject = getGDBObject(gdb)
    fcList = [gdbObject.AddressPoints, gdbObject.AuthoritativeBoundary, gdbObject.RoadAlias, gdbObject.RoadCenterline]

    if Exists(gdbObject.MunicipalBoundary):
        fcList.append(gdbObject.MunicipalBoundary)

    #create esb name list
    esb = []
    esbPath = []

    for e in esbList:
        e = e.replace("'", "")
        esbPath.append(e)
        e1 = basename(e)
        esb.append(e1)

    #set up currentPathSettings
    currentPathSettings.gdbPath = gdb
    currentPathSettings.domainsFolderPath = domain
    currentPathSettings.esbList = esb
    currentPathSettings.fcList = fcList + esbPath
    currentPathSettings.gdbVersion = version
    currentPathSettings.ESZ = ESZ

    #run sanity checks
    sanity = 0
    sanity = sanityCheck(currentPathSettings)

    if sanity == 1 and zipFlag == "true":
        createNG911Zip(gdb, zipPath)

    if sanity == 0 and zipFlag == "true":
        userMessage("Several issues with the data need to be addressed prior to submission. Data will not be zipped.")

def main():
    gdb = GetParameterAsText(0)
    domain = GetParameterAsText(1)
    esbList = GetParameterAsText(2).split(";")
    ESZ = GetParameterAsText(3)
    template10 = GetParameterAsText(4)

    validateAllPrep(gdb, domain, esbList, ESZ, template10, "false", "")

if __name__ == '__main__':
    main()
