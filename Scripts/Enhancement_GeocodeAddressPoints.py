#-------------------------------------------------------------------------------
# Name:        Enhancement_GeocodeAddressPoints
# Purpose:     Geocodes address points against road centerline
#
# Author:      kristen
#
# Created:     26/07/2016, Edited 10/28/2016, Edited 12/13/2016
# Copyright:   (c) kristen 2016
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, CreateAddressLocator_geocoding, GeocodeAddresses_geocoding,
                    Exists, MakeFeatureLayer_management, FieldInfo, MakeTableView_management,
                    AddField_management, CopyRows_management, CalculateField_management,
                    RebuildAddressLocator_geocoding, Delete_management, AddWarning, env)
from arcpy.da import SearchCursor, UpdateCursor, Editor
from NG911_GDB_Objects import getGDBObject, getFCObject
from NG911_arcpy_shortcuts import ListFieldNames, deleteExisting, getFastCount, fieldExists
from NG911_DataCheck import userMessage, RecordResults
from os.path import join, basename, dirname
from time import strftime

def main():
    gdb = GetParameterAsText(0)

    geocodeAddressPoints(gdb)

def calcSingleLineInput(gc_table, sl_field, label_fields):

    gdb = dirname(gc_table)
    label_fields.append(sl_field) #add the target field to the end
    fields = tuple(label_fields)

    sl_i = label_fields.index(sl_field)

    #start edit session
    edit = Editor(gdb)
    edit.startEditing(False, False)

    field_count = len(fields) - 1

    #run update cursor
    with UpdateCursor(gc_table, fields) as rows:
        for row in rows:

            start_int = 0
            label = ""

            #loop through the fields to see what's null & skip it
            while start_int < field_count:
                if row[start_int] is not None:
                    if row[start_int] not in ("", " "):
                        label = label + " " + str(row[start_int])
                start_int = start_int + 1

            row[sl_i] = label
            rows.updateRow(row)

    edit.stopEditing(True)

    #clean up all labels
    trim_expression = '" ".join(!' + sl_field + '!.split())'
    CalculateField_management(gc_table, sl_field, trim_expression, "PYTHON_9.3")

def geocodeAddressPoints(gdb):

    #set paths
    env.workspace = gdb

    #get geodatabase object
    gdbObject = getGDBObject(gdb)
    addressPointPath = gdbObject.AddressPoints
    streetPath = gdbObject.RoadCenterline
    roadAliasPath = gdbObject.RoadAlias

    a_obj = getFCObject(addressPointPath)
    rc_obj = getFCObject(streetPath)
    ra_obj = getFCObject(roadAliasPath)

    if Exists(addressPointPath) and Exists(streetPath) and Exists(roadAliasPath):

        userMessage("Geocoding address points...")

        gc_table = gdbObject.GeocodeTable
        sl_field = "SingleLineInput"
        Locator = join(dirname(gdb), basename(gdb).replace(".gdb", "_LOC")) #moved locator into a folder location & out of the geodatabase
        addyview = "addy_view"
        output = join(gdb, "gc_test")

        #make sure only records for submission are geocoded
        wc = a_obj.SUBMIT + " not in ('N')"
        MakeTableView_management(addressPointPath, addyview, wc)

        #delete the Geocode_Table if it exists
        try:
            deleteExisting(gc_table)
        except:
            userMessage("Please manually delete the table called gc_table and then run the geocoding again")


        if not Exists(gc_table):
            CopyRows_management(addyview, gc_table)

            #add single line input field for geocoding
            AddField_management(gc_table, sl_field, "TEXT", "", "", 250)

            #calculate field
            calcSingleLineInput(gc_table, sl_field, a_obj.GEOCODE_LABEL_FIELDS)

            #generate locator
            fieldMap = """'Primary Table:Feature ID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
            '*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;
            '*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;
            'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;
            'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;
            'Primary Table:Left City or Place' RoadCenterline:MUNI_L VISIBLE NONE;
            'Primary Table:Right City or Place' RoadCenterline:MUNI_R VISIBLE NONE;
            'Primary Table:Left ZIP Code' RoadCenterline:ZIP_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:ZIP_R VISIBLE NONE;
            'Primary Table:Left State' RoadCenterline:STATE_L VISIBLE NONE;'Primary Table:Right State' RoadCenterline:STATE_R VISIBLE NONE;
            'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;
            'Primary Table:Display X' <None> VISIBLE NONE;'Primary Table:Display Y' <None> VISIBLE NONE;
            'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;
            'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;
            'Primary Table:Left parity' <None> VISIBLE NONE;'Primary Table:Right parity' <None> VISIBLE NONE;
            'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;
            '*Primary Table:Altname JoinID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:""" + ra_obj.SEGID + """ VISIBLE NONE;
            'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' RoadAlias:A_STP VISIBLE NONE;
            'Alternate Name Table:Street Name' RoadAlias:A_RD VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;
            'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"""

            userMessage("Creating address locator...")
            # Process: Create Address Locator
            if Exists(Locator):
                RebuildAddressLocator_geocoding(Locator)
            else:
                try:
                    CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, Locator, "", "DISABLED")
                except:
                    try:
                        #this field map does not contain parity information
                        fieldMap = """'Primary Table:Feature ID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
                        '*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;
                        '*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;
                        'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;
                        'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;
                        'Primary Table:Left City or Place' RoadCenterline:MUNI_L VISIBLE NONE;
                        'Primary Table:Right City or Place' RoadCenterline:MUNI_R VISIBLE NONE;
                        'Primary Table:Left ZIP Code' RoadCenterline:ZIP_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:ZIP_R VISIBLE NONE;
                        'Primary Table:Left State' RoadCenterline:STATE_L VISIBLE NONE;'Primary Table:Right State' RoadCenterline:STATE_R VISIBLE NONE;
                        'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;
                        'Primary Table:Display X' <None> VISIBLE NONE;'Primary Table:Display Y' <None> VISIBLE NONE;
                        'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;
                        'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;
                        'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;
                        '*Primary Table:Altname JoinID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:""" + ra_obj.SEGID + """ VISIBLE NONE;
                        'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' <None> VISIBLE NONE;
                        'Alternate Name Table:Street Name' RoadAlias:A_RD VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;
                        'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"""
                        CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, Locator, "", "DISABLED")
                    except Exception as E:
                        try:
                            #this field map does not contain display x/y or parity information
                            fieldMap = """'Primary Table:Feature ID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
                            '*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;
                            '*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;
                            'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;
                            'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;
                            'Primary Table:Left City or Place' RoadCenterline:MUNI_L VISIBLE NONE;
                            'Primary Table:Right City or Place' RoadCenterline:MUNI_R VISIBLE NONE;
                            'Primary Table:Left ZIP Code' RoadCenterline:ZIP_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:ZIP_R VISIBLE NONE;
                            'Primary Table:Left State' RoadCenterline:STATE_L VISIBLE NONE;'Primary Table:Right State' RoadCenterline:STATE_R VISIBLE NONE;
                            'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;
                            'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;
                            'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;
                            'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;
                            'Primary Table:Altname JoinID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:""" + ra_obj.SEGID + """ VISIBLE NONE;
                            'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' <None> VISIBLE NONE;
                            'Alternate Name Table:Street Name' RoadAlias:A_RD VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;
                            'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"""
                            CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, Locator, "", "DISABLED")
                        except Exception as E:
                            try:
                                # 10.5 field map
                                fieldMap = """'Primary Table:Feature ID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
                                '*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;
                                '*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Left Parity' RoadCenterline:PARITY_L VISIBLE NONE;
                                'Primary Table:Right Parity' RoadCenterline:PARITY_R VISIBLE NONE;'Primary Table:Full Street Name' RoadCenterline:LABEL VISIBLE NONE;
                                'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;
                                '*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;
                                'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;'Primary Table:Left City or Place' RoadCenterline:MUNI_L VISIBLE NONE;
                                'Primary Table:Right City or Place' RoadCenterline:MUNI_R VISIBLE NONE;'Primary Table:Left County' RoadCenterline:COUNTY_L VISIBLE NONE;
                                'Primary Table:Right County' RoadCenterline:COUNTY_R VISIBLE NONE;'Primary Table:Left State' RoadCenterline:STATE_L VISIBLE NONE;
                                'Primary Table:Right State' RoadCenterline:STATE_R VISIBLE NONE;'Primary Table:Left State Abbreviation' RoadCenterline:STATE_L VISIBLE NONE;
                                'Primary Table:Right State Abbreviation' RoadCenterline:STATE_R VISIBLE NONE;'Primary Table:Left ZIP Code' RoadCenterline:ZIP_L VISIBLE NONE;
                                'Primary Table:Right ZIP Code' RoadCenterline:ZIP_R VISIBLE NONE;'Primary Table:Country Code' <None> VISIBLE NONE;
                                'Primary Table:3-Digit Language Code' <None> VISIBLE NONE;'Primary Table:2-Digit Language Code' <None> VISIBLE NONE;
                                'Primary Table:Admin Language Code' <None> VISIBLE NONE;'Primary Table:Left Block ID' <None> VISIBLE NONE;
                                'Primary Table:Right Block ID' <None> VISIBLE NONE;'Primary Table:Left Street ID' <None> VISIBLE NONE;
                                'Primary Table:Right Street ID' <None> VISIBLE NONE;'Primary Table:Street Rank' <None> VISIBLE NONE;
                                'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;
                                'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;
                                'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;
                                '*Primary Table:Altname JoinID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'Primary Table:City Altname JoinID' <None> VISIBLE NONE;
                                '*Alternate Name Table:JoinID' RoadAlias:""" + ra_obj.SEGID + """ VISIBLE NONE;'Alternate Name Table:Full Street Name' RoadAlias:LABEL VISIBLE NONE;
                                'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' RoadAlias:A_STP VISIBLE NONE;
                                'Alternate Name Table:Street Name' RoadAlias:A_RD VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;
                                'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"""
                                CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, Locator, "", "DISABLED")
                            except:

                                userMessage(Locator)
                                userMessage("Cannot create address locator. Please email kristen@kgs.ku.edu this error message: " + str(E))


        if Exists(Locator):
            userMessage("Geocoding addresses...")

            #geocode table address
            deleteExisting(output)

            #define geocoding exception table
            ge = join(gdb, "GeocodeExceptions")

            i = 0

            #set up geocoding
            gc_fieldMap = "Street SingleLineInput VISIBLE NONE;City " + a_obj.MUNI + " VISIBLE NONE;State " + a_obj.STATE + " VISIBLE NONE;ZIP " + a_obj.ZIP + " VISIBLE NONE"

            #geocode addresses
            try:
                GeocodeAddresses_geocoding(gc_table, Locator, gc_fieldMap, output, "STATIC")

                i = 1
            except:
                gc_fieldMap =  "Street SingleLineInput VISIBLE NONE;City " + a_obj.MUNI + " VISIBLE NONE;State " + a_obj.STATE + " VISIBLE NONE"

                try:
                    GeocodeAddresses_geocoding(gc_table, Locator, gc_fieldMap, output, "STATIC")
                    i = 1
                except:
                    userMessage("Could not geocode address points")

            #report records that didn't geocode
            if i == 1:
                wc = "Status <> 'M'"
                lyr = "lyr"

                MakeFeatureLayer_management(output, lyr, wc)

                rCount = getFastCount(lyr)
                if rCount > 0:
                    #set up parameters to report records that didn't geocode
                    values = []
                    recordType = "fieldValues"
                    today = strftime("%m/%d/%y")
                    filename = "AddressPoints"

                    if fieldExists(output, a_obj.LOCTYPE):
                        rfields = (a_obj.UNIQUEID, "Status", a_obj.LOCTYPE)
                    else:
                        rfields = ("USER_" + a_obj.UNIQUEID, "Status", "USER_" + a_obj.LOCTYPE)
                    try:
                        with SearchCursor(output, rfields, wc) as rRows:
                            for rRow in rRows:
                                fID = rRow[0]

                                #see if the fID exists as an exception
                                if Exists(ge):
                                    wcGE = a_obj.UNIQUEID + " = '" + fID + "'"
                                    tblGE = "tblGE"
                                    MakeTableView_management(ge, tblGE, wcGE)

                                    geCount = getFastCount(tblGE)

                                    if geCount != 0:
                                        userMessage(fID + " has already been marked as a geocoding exception")
                                        rCount = rCount - 1
                                    else:
                                        #report as an error
                                        if rRow[1] == "U":
                                            report = str(fID) + " did not geocode against centerline."
                                        elif rRow[1] == "T":
                                            report = str(fID) + " geocoded against more than one centerline segment. Possible address range overlap."
                                        if rRow[2] != "PRIMARY":
                                            report = "Notice: " + report
                                            rCount = rCount - 1
                                        else:
                                            report = "Notice: " + report
                                        val = (today, report, filename, "", fID, "Geocode Address Points")
                                        values.append(val)
                                    Delete_management(tblGE)

                                else:
                                    report = "Notice: " + str(fID) + " did not geocode against centerline"
                                    val = (today, report, filename, "", fID, "Geocode Address Points")
                                    values.append(val)

                    except Exception as e:
                        userMessage("Error processing unmatched records. " + str(e))
                    if rCount > 0:
                        userMessage("Completed geocoding with " + str(rCount) + " issues. These do not prohibit a successful data submission.")
                        #report records
                        if values != []:
                            RecordResults(recordType, values, gdb)
                    else:
                        userMessage("Some records did not geocode, but they are marked as exceptions.")

                else:
                    #this means all the records geocoded
                    userMessage("All records geocoded successfully.")
                    try:
                        Delete_management(output)
                    except:
                        userMessage("Geocoding table could not be deleted")

                Delete_management(lyr)
                del lyr
        else:
            userMessage("Could not geocode addresses")

    else:
        AddWarning("One or more layers necessary for geocoding do no exist.")

if __name__ == '__main__':
    main()
