#-------------------------------------------------------------------------------
# Name:        NG911_CheckUniqueIDs
# Purpose:     Launches script to check NG911 unique identifiers
#
# Author:      kristen
#
# Created:     28/04/2015
# Copyright:   (c) kristen 2015
#-------------------------------------------------------------------------------

def main():
    from arcpy import GetParameterAsText

    from NG911_DataCheck import main_check
    from os.path import basename

    try:
        from NG911_Config import currentPathSettings # currentPathSettings should have all the path information available. ## import esb, gdb, folder
    except:
        userMessage( "Copy config file into command line")

    #get parameters
    gdb = GetParameterAsText(0)
    esbList = GetParameterAsText(1).split(";")

    #create esb list
    esb = []

    for e in esbList:
        e = e.replace("'", "")
        e1 = basename(e)
        esb.append(e1)

    #set object parameters
    checkType = "UniqueID"
    currentPathSettings.gdbPath = gdb
    currentPathSettings.esbList = esb

    #launch the data check
    main_check(checkType, currentPathSettings)

if __name__ == '__main__':
    main()
