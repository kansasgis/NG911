#-------------------------------------------------------------------------------
# Name:        Validation_CheckAll
# Purpose:     Check all validation scripts
#
# Author:      kristen
#
# Created:     20/10/2015
#-------------------------------------------------------------------------------
from NG911_DataCheck import sanityCheck, userMessage
from arcpy import GetParameterAsText, Exists
from Conversion_ZipNG911Geodatabase import createNG911Zip
from NG911_GDB_Objects import NG911_Session
from os.path import basename
from NG911_arcpy_shortcuts import hasRecords

def validateAllPrep(gdb, zipFlag, zipPath):

    #get session object
    session_object = NG911_Session(gdb)

    #make sure all existing layers are checked
    fcPossList = session_object.gdbObject.fcList

    fcList = []
    for fc in fcPossList:
        if Exists(fc):
            if hasRecords(fc):
                fcList.append(fc)
            else:
                userMessage(basename(fc) + " has no records and will not be checked.")

    session_object.gdbObject.fcList = fcList

    #run sanity checks
    sanity = 0
    sanity = sanityCheck(session_object)

    if sanity == 1 and zipFlag == "true":
        createNG911Zip(gdb, zipPath)

    if sanity == 0 and zipFlag == "true":
        userMessage("Several issues with the data need to be addressed prior to submission. Data will not be zipped.")

def main():
    import time

    startTime = time.time()
    gdb = GetParameterAsText(0)
    validateAllPrep(gdb, "false", "")
    endTime = time.time()
    print("Running time was %g minutes\n" % round(((endTime - startTime)/60.0),1))

if __name__ == '__main__':
    main()
