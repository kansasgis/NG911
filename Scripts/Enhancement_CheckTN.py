#-------------------------------------------------------------------------------
# Name:        Enhancement_CheckTNList
# Purpose:     Check a county's TN list against MSAG communities in the NG911 Address Point and Road Centerline files
#
# Author:      kristen
#
# Created:     03/09/2015
#-------------------------------------------------------------------------------
from arcpy import (CreateAddressLocator_geocoding, GeocodeAddresses_geocoding, CopyRows_management, Delete_management, AddField_management, CalculateField_management,
    GetParameterAsText, Exists, env, CreateTable_management, CreateCompositeAddressLocator_geocoding)
from arcpy.da import InsertCursor
from NG911_DataCheck import userMessage
from NG911_Config import getGDBObject
from os.path import join

def createLocators(gdb_object):
    addressPointPath = gdb_object.AddressPoints
    streetPath = gdb_object.RoadCenterline
    roadAliasPath = gdb_object.RoadAlias

    AL1 = join(gdb_object.gdbPath, "AddressLocator")
    AL2 = join(gdb_object.gdbPath, "RoadLocator")
    AL3 = join(gdb_object.gdbPath, "CompositeLoc")
    AL4 = join(gdb_object.gdbPath, "AltCountyLoc")

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
                'Primary Table:Altname JoinID' RoadCenterline:SEGID VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:SEGID VISIBLE NONE;
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
                    'Primary Table:Altname JoinID' RoadCenterline:SEGID VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:SEGID VISIBLE NONE;
                    'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' RoadAlias:A_STP VISIBLE NONE;
                    'Alternate Name Table:Street Name' RoadAlias:A_RD VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;
                    'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"""
                    CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, AL2, "", "DISABLED")
                except:
                    try:
                        CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, AL2, "")
                    except:
                        userMessage("Could not create locator from road data")

            if Exists(AL2):
                userMessage("Created road centerline locator")

        if not Exists(AL4):
            #Create address locator from copy of Road centerline using the county field as the city field AL4
            AL4_fieldMap = """'Primary Table:Feature ID' <None> VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
                '*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;
                '*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;
                'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;
                'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;
                'Primary Table:Left City or Place' RoadCenterline:COUNTY_L VISIBLE NONE;
                'Primary Table:Right City or Place' RoadCenterline:COUNTY_R VISIBLE NONE;
                'Primary Table:Left ZIP Code' RoadCenterline:ZIP_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:ZIP_R VISIBLE NONE;
                'Primary Table:Left State' RoadCenterline:STATE_L VISIBLE NONE;'Primary Table:Right State' RoadCenterline:STATE_R VISIBLE NONE;
                'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;
                'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;
                'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;
                'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;
                'Primary Table:Altname JoinID' RoadCenterline:SEGID VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:SEGID VISIBLE NONE;
                'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' RoadAlias:A_STP VISIBLE NONE;
                'Alternate Name Table:Street Name' RoadAlias:A_RD VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;
                'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"""

            userMessage("Creating county alternate locator from road centerlines...")

            try:
                CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", AL4_fieldMap, AL4, "")
            except:
                try:
                    AL4_fieldMap = """'Primary Table:Feature ID' <None> VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
                    '*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;
                    '*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;
                    'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;
                    'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;
                    'Primary Table:Left City or Place' RoadCenterline:COUNTY_L VISIBLE NONE;
                    'Primary Table:Right City or Place' RoadCenterline:COUNTY_R VISIBLE NONE;
                    'Primary Table:Left ZIP Code' RoadCenterline:ZIP_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:ZIP_R VISIBLE NONE;
                    'Primary Table:Left State' RoadCenterline:STATE_L VISIBLE NONE;'Primary Table:Right State' RoadCenterline:STATE_R VISIBLE NONE;
                    'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;
                    'Primary Table:Display X' <None> VISIBLE NONE;'Primary Table:Display Y' <None> VISIBLE NONE;
                    'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;
                    'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;
                    'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;
                    'Primary Table:Altname JoinID' RoadCenterline:SEGID VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:SEGID VISIBLE NONE;
                    'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' RoadAlias:A_STP VISIBLE NONE;
                    'Alternate Name Table:Street Name' RoadAlias:A_RD VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;
                    'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"""
                    CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", AL4_fieldMap, AL4, "", "DISABLED")
                except:
                    userMessage("Could not create county alternate locator from road data")

            if Exists(AL4):
                userMessage("Created county alternate locator")

        #Create composite address locator from addresspoints/road centerline AL3
        if not Exists(AL3):
            userMessage("Creating composite address locator...")
            compositeFieldMap = "Street \"Street or Intersection\" true true true 100 Text 0 0 ,First,#," + AL1 + ",Street,0,0," + AL2 + ",Street,0,0;City \"City or Placename\" true true false 40 Text 0 0 ,First,#,"  + \
                AL1 + ",City,0,0," + AL2 + ",City,0,0;State \"State\" true true false 20 Text 0 0 ,First,#," + AL1 + ",State,0,0," + AL2 + ",State,0,0;ZIP \"ZIP Code\" true true false 10 Text 0 0 ,First,#," + \
                AL1 + ",ZIP,0,0," + AL2 + ",ZIP,0,0"

            CreateCompositeAddressLocator_geocoding(AL1 + " AddyPt;" + AL2 + " Roads;" + AL4 + " Alt", compositeFieldMap, "AddyPt #;Roads #;Alt #", AL3)

def prepXLS(tnxls, gdb):
    import xlrd

    userMessage("Converting spreadsheet to geodatabase table...")
    #create gdb table
    tname = "TN_Prepped"
    outTable = join(gdb, tname)
    CreateTable_management(gdb, tname)

    #add fields
    fields = ("HNO", "SUF", "PREDIR", "STREET", "SFX", "POSTDIR", "COMMUNITY", "STATE")

    colIDlist = (5,6,7,8,9,10,11,13)

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
    AddField_management(outTable, "SingleLineInput", "TEXT", "", "", 100)

    #concatenate field
    CalculateField_management(outTable, "SingleLineInput", '[HNO] & " " & [SUF] & " " & [PREDIR] & " " & [STREET] & " " & [SFX] & " " & [POSTDIR]& " " & [COMMUNITY]& " " & [STATE]', "VB")
    #replace three spaces in a row with one
    CalculateField_management(outTable, "SingleLineInput", 'Replace([SingleLineInput], "   ", " ")', "VB")
    #replace two spaces in a row with one
    CalculateField_management(outTable, "SingleLineInput", 'Replace([SingleLineInput], "  ", " ")', "VB")
    userMessage("Single line input succesfully created.")

def main():

    tnxls = GetParameterAsText(0)
    gdb = GetParameterAsText(1)

    #prep TN list
    prepXLS(tnxls, gdb)
    outTable = join(gdb, "TN_Prepped")

    #get gdb object
    gdb_object = getGDBObject(gdb)

    #create locators
    createLocators(gdb_object)

    #geocode addresses
    AL3 = join(gdb_object.gdbPath, "CompositeLoc")
    GC_output = join(gdb, "TN_GC_Output")

    #try composite first
    userMessage("Geocoding TN addresses...")
    in_address_fields = "SingleLine SingleLineInput VISIBLE NONE"
    GeocodeAddresses_geocoding(outTable, AL3, in_address_fields, GC_output, "STATIC")
    userMessage("Geocoding complete. Results are in: " + GC_output)

if __name__ == '__main__':
    main()
