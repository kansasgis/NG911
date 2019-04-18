#-------------------------------------------------------------------------------
# Name:        MSAG_CheckTNList
# Purpose:     Check a county's TN list against MSAG communities in the NG911 Address Point and Road Centerline files
#
# Author:      kristen
#
# Created:     03/09/2015
#-------------------------------------------------------------------------------
from arcpy import (Delete_management, AddField_management,
            CalculateField_management, GetParameterAsText, Exists, 
            CreateTable_management, CreateFileGDB_management,
            MakeTableView_management, DisableEditorTracking_management,
            EnableEditorTracking_management)
from arcpy.da import InsertCursor, UpdateCursor
from NG911_DataCheck import userMessage, getFieldDomain
from os.path import join, dirname, basename, exists, realpath
from os import mkdir
from NG911_GDB_Objects import getFCObject, getTNObject
from NG911_arcpy_shortcuts import getFastCount, fieldExists
from MSAG_DBComparison import launch_compare


def prepXLS(tnxls, gdb):
    import xlrd

    userMessage("Converting spreadsheet to geodatabase table...")
    #create gdb table
    tn_object = getTNObject(gdb)
    outTable = tn_object.TN_List
    tn_gdb = tn_object.tn_gdb
    LocatorFolder = tn_object.LocatorFolder

    #get the correct address point object
    address_points = join(gdb, "NG911", "AddressPoints")
    a_obj = getFCObject(address_points)

    if not exists(LocatorFolder):
        mkdir(LocatorFolder)

    if not Exists(tn_gdb):
        CreateFileGDB_management(dirname(tn_gdb), basename(tn_gdb))

    if Exists(outTable):
        Delete_management(outTable)

    tname = basename(outTable)
    CreateTable_management(tn_gdb, tname)

    #add fields
    fields = (a_obj.HNO, a_obj.HNS, a_obj.PRD, a_obj.RD, a_obj.MUNI, a_obj.STATE,"NPA","NXX","PHONELINE","SERVICECLASS")

    colIDlist = (17,18,20,21,22,24,2,3,4,7)

    #add fields
    for field in fields:
        AddField_management(outTable, field, "TEXT", "", "", 50)

    #read xls spreadsheet
    xl_workbook = xlrd.open_workbook(tnxls)
    xl_sheet = xl_workbook.sheet_by_index(0)

    #start at row 1 (maybe? depends on indexing, skip the headers is the goal)
    rowIdx = 1
    endRow = xl_sheet.nrows

    userMessage("This takes a while. It's a great time to take a 10 minute walk or refresh your favorite beverage.")

    #loop through info rows
    while rowIdx < endRow:
        if str(rowIdx)[-3:] == "000":
            userMessage("Converted " + str(rowIdx) + " spreadsheet records so far...")

        if rowIdx == endRow/2:
            userMessage("Have you backed up your GIS data with DASC recently? Email dasc@kgs.ku.edu for more info!")

        #create list to hold info
        rowToInsertList = []
        #look at just the fields I want to import
        for colID in colIDlist:
            cellval = xl_sheet.cell(rowIdx,colID).value
            rowToInsertList.append(cellval)

        #see if the service class is 8 or V. if it is, skip adding that row
        if rowToInsertList[-1] not in ["8", "V"]:

            #convert list of info to a tuple
            rowToInsert = tuple(rowToInsertList)

            #create insert cursor
            i = InsertCursor(outTable,fields)
            #insert the row of info
            i.insertRow(rowToInsert)
            #clean up
            del i, rowToInsert, rowToInsertList
        rowIdx = rowIdx + 1

    # split out RD into RD, STS, & POD
    postRoadFields = [a_obj.STS, a_obj.POD]

    for prf in postRoadFields:
        AddField_management(outTable, prf, "TEXT", "", "", 4)

    postRoadFields.append("RD")

    folder = join(dirname(dirname(realpath(__file__))), "Domains")

    streetSuffixDict = getFieldDomain("STS", folder).keys()
    postDirectionalDict = getFieldDomain("POD", folder).keys()

    with UpdateCursor(outTable, postRoadFields) as rows:
        for row in rows:

            # split the road name by spaces
            fullNameList = row[2].split()

            # try to skip things that are OLD HIGHWAY/HWY
            strikes = 0
            if "OLD" in fullNameList:
                strikes += 2
            if "HWY" in fullNameList:
                strikes += 1
            if "HIGHWAY" in fullNameList:
                strikes += 1

            # if it has less than three strikes, keep processing the split
            if strikes < 3:

                # set up an iteration to loop through the road name parts
                i = 1
                rd =[fullNameList[0]]
                while i < len(fullNameList):
                    # check to see if the road part is really a street suffix or post directional
                    if fullNameList[i] not in streetSuffixDict and fullNameList[i] not in postDirectionalDict:
                        rd.append(fullNameList[i])

                    # if it's a street suffix...
                    elif fullNameList[i] in streetSuffixDict:

                        # see if it's the last part of the street name or in the middle
                        if i < (len(fullNameList) - 1):
                            # if it's in the middle and the last part is also a street suffix...

                            if fullNameList[i + 1] in streetSuffixDict:
                                # include the middle street suffix as part of the road name
                                rd.append(fullNameList[i])
                            elif fullNameList[0] in ["COUNTY", "STATE", "US", "KS"]:
                                rd.append(fullNameList[i])
                            else:
                                # if not, set it as the street suffix since the last part is probable
                                # a post directional
                                row[0] = fullNameList[i]
                        else:
                            # if it's really the last part, set as the street suffix
                            row[0] = fullNameList[i]

                    # if it's a post directional
                    elif fullNameList[i] in postDirectionalDict:
                        # check for various components that indicate it's not actually a post directional
                        if fullNameList[0] not in ("AVENUE", "ROAD", "HIGHWAY", "HWY", "CR", "AVE", "COUNTY", "STATE"):
                            row[1] = fullNameList[i]
                        else:
                            rd.append(fullNameList[i])
                    i += 1

            # things with OLD HIGHWAY/HWY will leave the RD field as is for comparison purposes

                    row[2] = " ".join(rd)
                    rows.updateRow(row)

    userMessage("Conversion to geodatabase table successful. " + str(endRow-1) + " rows converted. VOIP and test rows were not converted.")


def AddUniqueIDField(outTable, uniqueIDField):
    if not fieldExists(outTable, uniqueIDField):
        AddField_management(outTable, uniqueIDField, "TEXT", "", "", 50) #KK EDIT: changed from 38 to 50

    wc = uniqueIDField + " is null or " + uniqueIDField + " in ('', ' ')"
    tbl = "tbl"
    MakeTableView_management(outTable, tbl, wc)

    if fieldExists(outTable, "NXX"):
        CalculateField_management(tbl, uniqueIDField, "!NPA! + !NXX! + !PHONELINE!", "PYTHON")
    else:
        CalculateField_management(tbl, uniqueIDField, "uniqueID() + str(!OBJECTID!)", "PYTHON", "def uniqueID():\\n  x = '%d' % time.time()\\n  str(x)\\n  return x")


def geocodeTable(gdb):
    #geocode addresses
    tn_object = getTNObject(gdb)
    tname = tn_object.TN_List
    uniqueFieldID = tn_object.UNIQUEID

    #add unique ID to TN List table
    AddUniqueIDField(tname, uniqueFieldID)

    addy_field_list = ["NAME_COMPARE", "PRD", "RD", "STS", "POD"]
    launch_compare(gdb, tname, "HNO", "MUNI", addy_field_list, True)

    #see if any records did not match
    wc = "MATCH <> 'M'"
    lyr = "lyr"
    MakeTableView_management(tname, lyr, wc)

    rCount = getFastCount(lyr)
    if rCount > 0:
        userMessage("Geocoding complete. " + str(rCount) + " records did not geocode. Processing results...")
        userMessage("Results processed. Please see results in " + tname)
    else:
        userMessage("Geocoding complete. All records geocoded successfully.")

    Delete_management(lyr)

def main():

    tnxls = GetParameterAsText(0)
    gdb = GetParameterAsText(1)

    addy_fc = join(gdb, "NG911", "AddressPoints")
    rd_fc = join(gdb, "NG911", "RoadCenterline")

    # turn off editor tracking
    DisableEditorTracking_management(addy_fc, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")
    DisableEditorTracking_management(rd_fc, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")

    #prep TN list
    prepXLS(tnxls, gdb)

    #geocode addresses
    geocodeTable(gdb)

    # turn editor tracking back on
    EnableEditorTracking_management(addy_fc, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")
    EnableEditorTracking_management(rd_fc, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")


if __name__ == '__main__':
    main()
