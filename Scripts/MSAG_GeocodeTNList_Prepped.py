#-------------------------------------------------------------------------------
# Name:        MSAG_GeocodeTNList_Prepped
# Purpose:     Geocode a TN list where the full address has already been caclulated
#
# Author:      kristen
#
# Created:     01/08/2016
#-------------------------------------------------------------------------------
from arcpy import (Delete_management, AddField_management,
            GetParameterAsText, Exists, CreateTable_management,
            CreateFileGDB_management, DisableEditorTracking_management,
            EnableEditorTracking_management)
from arcpy.da import InsertCursor, UpdateCursor
from NG911_DataCheck import userMessage, getFieldDomain
from os.path import join, dirname, basename, exists, realpath
from os import mkdir
from NG911_GDB_Objects import getFCObject, getTNObject
from MSAG_CheckTNList import geocodeTable

def prepXLS(tnxls_sheet, gdb, xls_fields):
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
    fields = (a_obj.HNO, a_obj.HNS, a_obj.PRD, a_obj.RD, a_obj.STS, a_obj.POD, a_obj.MUNI, "NGTNID")

    colIDlist = ["0", "0", "0", "0", "0", "0", "0", "0"]

    #add fields
    for field in fields:
        AddField_management(outTable, field, "TEXT", "", "", 50)

    #read xls spreadsheet
    tnxls = dirname(tnxls_sheet)
    xl_workbook = xlrd.open_workbook(tnxls)
    xl_sheet = xl_workbook.sheet_by_index(0)
    header_row = xl_sheet.row(0)

    for idx, cell_obj in enumerate(header_row):
        val = xl_sheet.cell(0,idx).value
        if val in xls_fields:
            place = xls_fields.index(val)
            colIDlist[place] = idx

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
            if colID != "0":
                cellval = xl_sheet.cell(rowIdx,colID).value
                rowToInsertList.append(cellval)
            else:
                rowToInsertList.append("")

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
    postRoadFields = [a_obj.STS, a_obj.POD, a_obj.RD]

    folder = join(dirname(dirname(realpath(__file__))), "Domains")

    streetSuffixDict = getFieldDomain("STS", folder).keys()
    postDirectionalDict = getFieldDomain("POD", folder).keys()

    with UpdateCursor(outTable, postRoadFields) as rows:
        for row in rows:
            fullNameList = row[2].split()
            i = 1
            rd =[fullNameList[0]]
            while i < len(fullNameList):
                if fullNameList[i] not in streetSuffixDict and fullNameList[i] not in postDirectionalDict:
                    rd.append(fullNameList[i])
                elif fullNameList[i] in streetSuffixDict:
                    row[0] = fullNameList[i]
                elif fullNameList[i] in postDirectionalDict:
                    if fullNameList[0] not in ("AVENUE", "ROAD", "HIGHWAY", "HWY"):
                        row[1] = fullNameList[i]
                    else:
                        rd.append(fullNameList[i])
                i += 1

            row[2] = " ".join(rd)
            rows.updateRow(row)

    userMessage("Conversion to geodatabase table successful. " + str(endRow-1) + " rows converted. VOIP and test rows were not converted.")

def main():

    gdb = GetParameterAsText(0)
    xls = GetParameterAsText(1)
    hno = GetParameterAsText(2)
    hns = GetParameterAsText(3)
    prd = GetParameterAsText(4)
    rd = GetParameterAsText(5)
    sts = GetParameterAsText(6)
    post = GetParameterAsText(7)
    msagco = GetParameterAsText(8)
    tn = GetParameterAsText(9)

    addy_fc = join(gdb, "NG911", "AddressPoints")
    rd_fc = join(gdb, "NG911", "RoadCenterline")

    # turn off editor tracking
    DisableEditorTracking_management(addy_fc, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")
    DisableEditorTracking_management(rd_fc, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")

    xls_fields = [hno, hns, prd, rd, sts, post, msagco, tn]

    prepXLS(xls, gdb, xls_fields)

    #geocode addresses
    geocodeTable(gdb)

    # turn editor tracking back on
    EnableEditorTracking_management(addy_fc, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")
    EnableEditorTracking_management(rd_fc, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")

if __name__ == '__main__':
    main()
