#-------------------------------------------------------------------------------
# Name:        MSAG_CheckTNList
# Purpose:     Check a county's TN list against MSAG communities in the NG911 Address Point and Road Centerline files
#
# Author:      kristen
#
# Created:     03/09/2015
#-------------------------------------------------------------------------------
from arcpy import (CreateAddressLocator_geocoding, GeocodeAddresses_geocoding,
            CopyRows_management, Delete_management, AddField_management,
            CalculateField_management, GetParameterAsText, Exists, env,
            CreateTable_management, CreateCompositeAddressLocator_geocoding,
            MakeFeatureLayer_management, AddMessage, CreateFileGDB_management)
from arcpy.da import InsertCursor, SearchCursor
from NG911_DataCheck import userMessage
from os.path import join, dirname, basename, exists
from os import mkdir
from NG911_GDB_Objects import getFCObject, getTNObject, getGDBObject
from NG911_arcpy_shortcuts import getFastCount, fieldExists
from time import strftime
from sys import exit


def createLocators(gdb_object):
    addressPointPath = gdb_object.AddressPoints
    streetPath = gdb_object.RoadCenterline
    roadAliasPath = gdb_object.RoadAlias

    rc_obj = getFCObject(streetPath)
    ra_obj = getFCObject(roadAliasPath)

    tn_object = getTNObject(gdb_object.gdbPath)
    tn_gdb = tn_object.tn_gdb

    LocatorFolder = tn_object.LocatorFolder

    if not exists(LocatorFolder):
        mkdir(LocatorFolder)

    if not Exists(tn_gdb):
        CreateFileGDB_management(dirname(tn_gdb), basename(tn_gdb))

    AL1 = tn_object.AddressLocator
    AL2 = tn_object.RoadLocator
    AL3 = tn_object.CompositeLocator

    if not Exists(AL1):
        #Create address locator from NG911 Address points AL1
        addyFieldMap = """'Feature ID' OBJECTID VISIBLE NONE;'*House Number' HNO VISIBLE NONE;Side <None> VISIBLE NONE;'Prefix Direction' PRD VISIBLE NONE;
            'Prefix Type' STP VISIBLE NONE;'*Street Name' RD VISIBLE NONE;'Suffix Type' STS VISIBLE NONE;'Suffix Direction' POD VISIBLE NONE;
            'City or Place' MSAGCO VISIBLE NONE;'ZIP Code' ZIP VISIBLE NONE;State STATE VISIBLE NONE;'Street ID' <None> VISIBLE NONE;'Display X' <None> VISIBLE NONE;
            'Display Y' <None> VISIBLE NONE;'Min X value for extent' <None> VISIBLE NONE;'Max X value for extent' <None> VISIBLE NONE;'Min Y value for extent' <None> VISIBLE NONE;
            'Max Y value for extent' <None> VISIBLE NONE;'Additional Field' <None> VISIBLE NONE;'Altname JoinID' <None> VISIBLE NONE"""

        userMessage("Creating locator from address points...")

        try:
            CreateAddressLocator_geocoding("US Address - Single House", addressPointPath + " 'Primary Table'", addyFieldMap, AL1, "", "DISABLED")
        except:
            try:
                CreateAddressLocator_geocoding("US Address - Single House", addressPointPath + " 'Primary Table'", addyFieldMap, AL1, "")
            except:
                userMessage("Could not create locator from address points.")

        #report on locator status and edit minimum match score down to 75
        if Exists(AL1):
            userMessage("Created locator from address points.")

        if not Exists(AL2):
            #Create address locator from NG911 Road centerline AL2
             #generate locator
            fieldMap = """'Primary Table:Feature ID' <None> VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
                '*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;
                '*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;
                'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;
                'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;
                'Primary Table:Left City or Place' RoadCenterline:MSAGCO_L VISIBLE NONE;
                'Primary Table:Right City or Place' RoadCenterline:MSAGCO_R VISIBLE NONE;
                'Primary Table:Left ZIP Code' RoadCenterline:ZIP_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:ZIP_R VISIBLE NONE;
                'Primary Table:Left State' RoadCenterline:STATE_L VISIBLE NONE;'Primary Table:Right State' RoadCenterline:STATE_R VISIBLE NONE;
                'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;
                'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;
                'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;
                'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;
                'Primary Table:Altname JoinID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:""" + ra_obj.SEGID + """ VISIBLE NONE;
                'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' RoadAlias:A_STP VISIBLE NONE;
                'Alternate Name Table:Street Name' RoadAlias:A_RD VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;
                'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"""

            userMessage("Creating locator from road centerlines...")

            try:
                CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, AL2, "")
            except:
                try:
                    fieldMap = """'Primary Table:Feature ID' <None> VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
                    '*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;
                    '*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;
                    'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;
                    'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;
                    'Primary Table:Left City or Place' RoadCenterline:MSAGCO_L VISIBLE NONE;
                    'Primary Table:Right City or Place' RoadCenterline:MSAGCO_R VISIBLE NONE;
                    'Primary Table:Left ZIP Code' RoadCenterline:ZIP_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:ZIP_R VISIBLE NONE;
                    'Primary Table:Left State' RoadCenterline:STATE_L VISIBLE NONE;'Primary Table:Right State' RoadCenterline:STATE_R VISIBLE NONE;
                    'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;
                    'Primary Table:Display X' <None> VISIBLE NONE;'Primary Table:Display Y' <None> VISIBLE NONE;
                    'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;
                    'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;
                    'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;
                    'Primary Table:Altname JoinID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:""" + ra_obj.SEGID + """ VISIBLE NONE;
                    'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' RoadAlias:A_STP VISIBLE NONE;
                    'Alternate Name Table:Street Name' RoadAlias:A_RD VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;
                    'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"""
                    CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, AL2, "", "DISABLED")
                except:
                    try:
                        CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, AL2, "")
                    except:
                        fieldMap = """'Primary Table:Feature ID' RoadCenterline:SEGID VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
                            '*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;
                            '*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;
                            'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;
                            'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;
                            'Primary Table:Left City or Place' RoadCenterline:MSAGCO_L VISIBLE NONE;'Primary Table:Right City or Place' RoadCenterline:MSAGCO_R VISIBLE NONE;
                            'Primary Table:Left ZIP Code' RoadCenterline:ZIP_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:ZIP_R VISIBLE NONE;
                            'Primary Table:Left State' RoadCenterline:STATE_L VISIBLE NONE;'Primary Table:Right State' RoadCenterline:STATE_R VISIBLE NONE;
                            'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;
                            'Primary Table:Display X' <None> VISIBLE NONE;'Primary Table:Display Y' <None> VISIBLE NONE;
                            'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;
                            'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;
                            'Primary Table:Left parity' <None> VISIBLE NONE;'Primary Table:Right parity' <None> VISIBLE NONE;
                            'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;
                            '*Primary Table:Altname JoinID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Alias Table:Alias' RoadAlias:""" + ra_obj.SEGID + """ VISIBLE NONE;
                            '*Alias Table:Street' RoadAlias:A_RD VISIBLE NONE;'Alias Table:City' <None> VISIBLE NONE;'Alias Table:State' <None> VISIBLE NONE;
                            'Alias Table:ZIP' <None> VISIBLE NONE"""
                        try:
                            CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alias Name Table'", fieldMap, AL2, "", "DISABLED")
                        except Exception as e:
                            userMessage("Could not create locator from road data. " + str(e))

            if Exists(AL2):
                userMessage("Created road centerline locator")

        #Create composite address locator from addresspoints/road centerline AL3
        if not Exists(AL3):
            if Exists(AL1) and Exists(AL2):
                userMessage("Creating composite address locator...")
                compositeFieldMap = "Street \"Street or Intersection\" true true true 100 Text 0 0 ,First,#," + AL1 + ",Street,0,0," + AL2 + ",Street,0,0;City \"City or Placename\" true true false 40 Text 0 0 ,First,#,"  + \
                    AL1 + ",City,0,0," + AL2 + ",City,0,0;State \"State\" true true false 20 Text 0 0 ,First,#," + AL1 + ",State,0,0," + AL2 + ",State,0,0;ZIP \"ZIP Code\" true true false 10 Text 0 0 ,First,#," + \
                    AL1 + ",ZIP,0,0," + AL2 + ",ZIP,0,0"

                CreateCompositeAddressLocator_geocoding(AL1 + " AddyPt;" + AL2 + " Roads", compositeFieldMap, "AddyPt #;Roads #", AL3)


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
    fields = (a_obj.HNO, a_obj.HNS, a_obj.PRD, a_obj.RD, a_obj.MUNI, a_obj.STATE,"NPA","NXX","PHONELINE")

    colIDlist = (17,18,20,21,22,24,2,3,4)

    #add fields
    for field in fields:
        AddField_management(outTable, field, "TEXT", "", "", 50)

    #read xls spreadsheet
    xl_workbook = xlrd.open_workbook(tnxls)
    xl_sheet = xl_workbook.sheet_by_index(0)
    header_row = xl_sheet.row(0)

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

        #convert list of info to a tuple
        rowToInsert = tuple(rowToInsertList)

        #create insert cursor
        i = InsertCursor(outTable,fields)
        #insert the row of info
        i.insertRow(rowToInsert)
        #clean up
        del i, rowToInsert, rowToInsertList
        rowIdx = rowIdx + 1

    userMessage("Conversion to geodatabase table successful. " + str(endRow-1) + " rows converted.")

    userMessage("Creating single line input for geocoding...")
    #create SingleLineInput field
    sli = tn_object.DefaultFullAddress
    AddField_management(outTable, sli, "TEXT", "", "", 100)

    #concatenate field
    fldList = [a_obj.HNO,a_obj.HNS,a_obj.PRD,a_obj.RD,a_obj.MUNI,a_obj.STATE]
    CalculateField_management(outTable, sli, '!' +  ('! + " " + !').join(fldList) + '!', "PYTHON")
    #replace three spaces in a row with one
    CalculateField_management(outTable, sli, '!' + sli + '!.replace("   ", " ")', "PYTHON")
    #replace two spaces in a row with one
    CalculateField_management(outTable, sli, '!' + sli + '!.replace("  ", " ")', "PYTHON")
    userMessage("Single line input succesfully created.")

def AddUniqueIDField(outTable, uniqueIDField):
    if not fieldExists(outTable, uniqueIDField):
        AddField_management(outTable, uniqueIDField, "TEXT", "", "", 50) #KK EDIT: changed from 38 to 50

    if not fieldExists(outTable, "NXX"):
        CalculateField_management(outTable, uniqueIDField, "uniqueID() + str(!OBJECTID!)", "PYTHON", "def uniqueID():\\n  x = '%d' % time.time()\\n  str(x)\\n  return x")
    else:
        CalculateField_management(outTable, uniqueIDField, "!NPA! + !NXX! + !PHONELINE!", "PYTHON")

def geocodeTable(gdb, field):
    #geocode addresses
    tn_object = getTNObject(gdb)
    AL3 = tn_object.CompositeLocator
    tname = tn_object.TN_List
##    tname = r"E:\Kristen\Data\NG911\Template20\KSNG911N_20_DK_TN\TN_Working.gdb\TN_List_20161026_1"
    GC_output = tn_object.ResultsFC
    uniqueFieldID = tn_object.UNIQUEID
    tn_gdb = tn_object.tn_gdb

    #add unique ID to TN List table
    AddUniqueIDField(tname, uniqueFieldID)

    #delete geocoding output if it exists already
    if Exists(GC_output):
        Delete_management(GC_output)

    #try composite first
    AddMessage("Geocoding TN addresses...")
    try:
        in_address_fields = "SingleLine " + field + " VISIBLE NONE"
        GeocodeAddresses_geocoding(tname, AL3, in_address_fields, GC_output, "STATIC")
    except Exception as e:
        userMessage("Cannot geocode addresses. " + str(e))
        exit()

    #see if any records did not match
    wc = "Status <> 'M'"
    lyr = "lyr"
    MakeFeatureLayer_management(GC_output, lyr, wc)

    rCount = getFastCount(lyr)
    if rCount > 0:
        userMessage("Geocoding complete. " + str(rCount) + " records did not geocode. Processing results...")
        if fieldExists(GC_output, uniqueFieldID):
            idName = uniqueFieldID
        else:
            idName = "USER_" + uniqueFieldID

        fieldList = ("Status", idName)

        #create report table
        reportTable = tn_object.ResultsTable
        reportTableName = basename(reportTable)

        if Exists(reportTable):
            Delete_management(reportTable)
        CreateTable_management(tn_gdb, reportTableName)

        #add reporting fields
        AddField_management(reportTable, idName, "TEXT", "", "", 38)
        AddField_management(reportTable, "STATUS", "TEXT", "", "", 1)
        AddField_management(reportTable, "DESCRIPTION", "TEXT", "", "", 100)

        with SearchCursor(lyr, fieldList) as rows:
            for row in rows:
                cursor = InsertCursor(reportTable, [idName, "STATUS", "DESCRIPTION"])
                message = "Record did not geocode against the data."
                if row[0] == "T":
                    message = "Record was a geocoding tie."
                try:
                    cursor.insertRow([row[1], row[0], message])
                except Exception as e:
                    userMessage(str(e))

                del cursor
        userMessage("Results processed. Please see results in " + reportTable)
    else:
        userMessage("Geocoding complete. All records geocoded successfully.")

def main():

    tnxls = GetParameterAsText(0)
    gdb = GetParameterAsText(1)

    #prep TN list
    prepXLS(tnxls, gdb)

    #get gdb object
    gdb_object = getGDBObject(gdb)

    #create locators
    createLocators(gdb_object)

    #geocode addresses
    geocodeTable(gdb, "SingleLineInput")


if __name__ == '__main__':
    main()
