#-------------------------------------------------------------------------------
# Name:        Submission_CheckAllAndZip
# Purpose:     Runs all data checks and zips geodatabase if it passes
#
# Author:      kristen
#
# Created:     20/10/2015
#-------------------------------------------------------------------------------
from Validation_CheckAll import validateAllPrep
from NG911_DataCheck import userMessage
from arcpy import GetParameterAsText

def main():
    gdb = GetParameterAsText(0)
    domain = GetParameterAsText(1)
    esbList = GetParameterAsText(2).split(";")
    ESZ = GetParameterAsText(3)
    template10 = GetParameterAsText(4)
    zipOutput = GetParameterAsText(5)

    if zipOutput[-3:] != "zip":
        userMessage("Output zip file is not valid. Please try again.")

    else:
        validateAllPrep(gdb, domain, esbList, ESZ, template10, "true", zipOutput)

if __name__ == '__main__':
    main()
