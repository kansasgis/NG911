#-------------------------------------------------------------------------------
# Name: NG911_DataCheck
# Purpose: Collection of functions to check submitted NG911 data
#
# Author: Kristen Jordan, Kansas Data Access and Support Center
# kristen@kgs.ku.edu
#
# Created: 19/09/2014
# Modified: 31/10/2014 by dirktall04
# Changes include: Adding the currentPathSettings variable from
# NG911_Config as the default variable passed to several Data
# Check functions, modifications to the functions to allow
# them to use that variable as a data source.
#Modified: 02/04/2014 by Kristen
#Changes include: modifying format so the checks work with the 1.1 template
#-------------------------------------------------------------------------------

from arcpy import (AddField_management, AddMessage, CalculateField_management,  CopyRows_management, CreateAddressLocator_geocoding,
                   CreateTable_management, Delete_management, Exists, GeocodeAddresses_geocoding, GetCount_management, FieldInfo,
                   ListFields, MakeFeatureLayer_management, MakeTableView_management, SelectLayerByAttribute_management, Statistics_analysis,
                   SelectLayerByLocation_management, RebuildAddressLocator_geocoding, DeleteRows_management, GetInstallInfo, env, ListDatasets,
                   AddJoin_management, RemoveJoin_management, AddWarning)
from arcpy.da import Walk, InsertCursor, ListDomains, SearchCursor
from os import path
from os.path import basename, dirname, join, exists
from time import strftime
from NG911_Config import getGDBObject, checkToolboxVersion
from Validation_ClearOldResults import ClearOldResults
import NG911_GDB_Objects
from NG911_arcpy_shortcuts import deleteExisting, getFastCount, cleanUp, ListFieldNames, fieldExists


a_obj = NG911_GDB_Objects.getDefaultNG911AddressObject()
rc_obj = NG911_GDB_Objects.getDefaultNG911RoadCenterlineObject()
esb_obj = NG911_GDB_Objects.getDefaultNG911ESBObject()
ab_obj = NG911_GDB_Objects.getDefaultNG911AuthoritativeBoundaryObject()
ra_obj = NG911_GDB_Objects.getDefaultNG911RoadAliasObject()
cb_obj = NG911_GDB_Objects.getDefaultNG911CountyBoundaryObject()
mb_obj = NG911_GDB_Objects.getDefaultNG911MunicipalBoundaryObject()
esz_obj = NG911_GDB_Objects.getDefaultNG911ESZObject()
psap_obj = NG911_GDB_Objects.getDefaultNG911ESBObject()
fvcr_obj = NG911_GDB_Objects.getDefaultNG911FieldValuesCheckResultsObject()
tcr_obj = NG911_GDB_Objects.getDefaultNG911TemplateCheckResultsObject()

layer_obj_dict = {"ADDRESSPOINTS": a_obj, "ROADCENTERLINE": rc_obj, "ESB": esb_obj, "AUTHORITATIVEBOUNDARY": ab_obj, "ROADALIAS": ra_obj, "COUNTYBOUNDARY": cb_obj,
                     "MUNICIPALBOUNDARY":mb_obj, "ESZ": esz_obj, "PSAP": esb_obj, "FieldValuesCheckResults":fvcr_obj, "TemplateCheckResults":tcr_obj}

def getLayerList():
    layerList = ["RoadAlias", "AddressPoints", "RoadCenterline", "AuthoritativeBoundary", "CountyBoundary", "ESZ", "MunicipalBoundary"]
    return layerList


def getCurrentLayerList(esb):
    layerList = getLayerList()
    for e in esb:
        layerList.append(e)
    return layerList


def userMessage(msg):
    #print stuff
    print msg
    AddMessage(msg)

def getCurrentDomainList():
    domainList = ["AddressNumbers", "AddressParity", "AgencyID", "Counties", "Country",
                    "ESBType", "Municipality", "OneWay", "PlaceType", "PointLocation", "PostalCodes",
                    "PostalCommunities", "RoadClass", "RoadDirectionals", "RoadModifier", "RoadStatus",
                    "RoadSurface", "RoadTypes", "States", "Stewards", "Exception", "Submit"]
    #or get domain list from approved source
##
##    if version == "10":
##        domainList.remove("Exception")
##        domainList.remove("Submit")

    return domainList


def fieldsWithDomains(layer):

    #list of all the fields that have a domain
    #get keyword
    keyword = basename(layer).upper()
    for e in ['FIRE','EMS','LAW','ESB','PSAP']:
        if e in layer.upper():
            keyword = "ESB"

    obj = layer_obj_dict[keyword]

    fieldList = obj.FIELDS_WITH_DOMAINS

    #take out "EXCEPTION" and "SUBMIT" from the field list if they don't exist
    actualFields = ListFieldNames(layer)

    removals = ["EXCEPTION", "SUBMIT"]

    #take out fields if it's a different version of geodatabase
    for r in removals:
        if r not in actualFields and r in fieldList:
            fieldList.remove(r)

    return fieldList

def getUniqueIDField(layer):
    for e in ['FIRE','EMS','LAW','ESB','PSAP']:
        if e in layer:
            layer = "ESB"
    obj = layer_obj_dict[layer]
    id1 = obj.UNIQUEID
    return id1

def getDomainKeyword(domainName):
    ucase_list = ["AgencyID", "Country", "OneWay"]
    if domainName == "AddressParity":
        keyword = "PARITY"
    elif domainName == "Counties":
        keyword = "COUNTY"
    elif domainName == "ESBType":
        keyword = ""
    elif domainName == "Municipality":
        keyword = "MUNI"
    elif domainName == "PlaceType":
        keyword = "PLC"
    elif domainName == "PointLocation":
        keyword = "LOCTYPE"
    elif domainName == "PostalCodes":
        keyword = "ZIP"
    elif domainName == "PostalCommunities":
        keyword = "POSTCO"
    elif domainName == "RoadClass":
        keyword = "RDClass"
    elif domainName == "RoadDirectionals":
        keyword = "PRD"
    elif domainName == "RoadModifier":
        keyword = ""
    elif domainName == "RoadStatus":
        keyword = "STATUS"
    elif domainName == "RoadSurface":
        keyword = "SURFACE"
    elif domainName == "RoadTypes":
        keyword = "STS"
    elif domainName == "States":
        keyword = "STATE"
    elif domainName == "Stewards":
        keyword = "STEWARD"
    elif domainName in ucase_list:
        keyword = domainName.upper()

    return keyword


def getAddFieldInfo(table):
    lyr = basename(table)
    #field info
    if lyr == "TemplateCheckResults":
        fieldInfo = [(table, tcr_obj.DATEFLAGGED, "DATE", "", "", ""),(table, tcr_obj.DESCRIPTION, "TEXT", "", "", 250),(table, tcr_obj.CATEGORY, "TEXT", "", "", 25)]
    elif lyr == "FieldValuesCheckResults":
        fieldInfo = [(table, fvcr_obj.DATEFLAGGED, "DATE", "", "", ""),(table, fvcr_obj.DESCRIPTION, "TEXT", "", "", 250),
            (table, fvcr_obj.LAYER, "TEXT", "", "", 25),(table, fvcr_obj.FIELD, "TEXT", "", "", 25),(table, fvcr_obj.FEATUREID, "TEXT", "", "", 38)]
    elif lyr == "DASC_Communication":
        fieldInfo = [(table, "NoteDate", "DATE", "", "", ""),(table, "Description", "TEXT", "", "", 250)]

    del lyr
    return fieldInfo


def getResultsFieldList(table):
    #get field info
    fieldInfo = getAddFieldInfo(table)
    fieldList = []
    #loop through added fields
    for fi in fieldInfo:
        #append the field name
        fieldList.append(fi[1])

    return fieldList


def calcAngle(pt1, pt2, pt3):
    import math, decimal
    context = decimal.Context(prec=5, rounding="ROUND_DOWN")
    #get length of side A
    a = abs(abs(pt1[0]) - abs(pt2[0]))
    b = abs(abs(pt1[1]) - abs(pt2[1]))
    A = context.create_decimal_from_float(math.hypot(a,b))

    #get length of side B
    c = abs(abs(pt2[0]) - abs(pt3[0]))
    d = abs(abs(pt2[1]) - abs(pt3[1]))
    B = context.create_decimal_from_float(math.hypot(c,d))

    #get length of side C
    e = abs(abs(pt3[0]) - abs(pt1[0]))
    f = abs(abs(pt3[1]) - abs(pt1[1]))
    C = context.create_decimal_from_float(math.hypot(e,f))

    q = ((A*A) + (B*B) - (C*C))/(2*A*B)

    degrees = 0

    if -1 < q < 1:
        #get angle
        radian = math.acos(q)

##    radian = math.atan((pt3x - pt2x)/(pt1y - pt2y))
        degrees = radian * 180 / math.pi
    return degrees


def RecordResults(resultType, values, gdb): # Guessed on whitespace formatting here. -- DT
    if resultType == "template":
        tbl = "TemplateCheckResults"
    elif resultType == "fieldValues":
        tbl = "FieldValuesCheckResults"
    elif resultType == "DASCmessage":
        tbl = "DASC_Communication"

    table = join(gdb, tbl)
    fieldList = []

    if not Exists(table):
        CreateTable_management(gdb, tbl)
        fieldInfo = getAddFieldInfo(table)

        for fi in fieldInfo:
            #add field with desired parameters
            AddField_management(fi[0],fi[1],fi[2],fi[3],fi[4],fi[5])
            #populate field list
            fieldList.append(fi[1])

    if fieldList == []:
        fieldList = getResultsFieldList(table)

    cursor = InsertCursor(table, fieldList)
    for row in values:
        try:
            cursor.insertRow(row)
        except:
            userMessage(row)
    del cursor

def geocodeAddressPoints(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    gdbObject = getGDBObject(gdb)

##    version = pathsInfoObject.gdbVersion

    env.workspace = gdb
    addressPointPath = gdbObject.AddressPoints
    streetPath = gdbObject.RoadCenterline
    roadAliasPath = gdbObject.RoadAlias

    userMessage("Geocoding address points...")

    gc_table = gdbObject.GeocodeTable
    sl_field = "SingleLineInput"
    Locator = gdbObject.Locator
    addyview = "addy_view"
    output = "gc_test"

    # Get the fields from the input
    fields = ListFieldNames(addressPointPath)

    # Create a fieldinfo object
    fieldinfo = FieldInfo()

    # Iterate through the fields and set them to fieldinfo
    for field in fields:
        if field in (a_obj.LABEL, a_obj.ZIP):
            fieldinfo.addField(field, field, "VISIBLE", "")
    else:
        fieldinfo.addField(field, field, "HIDDEN", "")

    userMessage("Preparing addresses...")
    # The created addyview layer will have fields as set in fieldinfo object
    if "SUBMIT" in fields:
        wc = a_obj.SUBMIT + " not in ('N')"
        MakeTableView_management(addressPointPath, addyview, wc, "", fieldinfo)
    else:
        MakeTableView_management(addressPointPath, addyview, "", "", fieldinfo)

    # To persist the layer on disk make a copy of the view
    try:
        deleteExisting(gc_table)
    except:
        userMessage("Please manually delete the table called gc_table and then run the geocoding again")


    if not Exists(gc_table):
        CopyRows_management(addyview, gc_table)

        #add single line input field for geocoding
        AddField_management(gc_table, sl_field, "TEXT", "", "", 250)

        #calculate field
        exp = '[' + a_obj.LABEL + '] & " " & [' + a_obj.ZIP + ']'
        CalculateField_management(gc_table, sl_field, exp, "VB")

        #generate locator
        fieldMap = """'Primary Table:Feature ID' RoadCenterline:SEGID VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
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
        'Primary Table:Altname JoinID' RoadCenterline:SEGID VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:SEGID VISIBLE NONE;
        'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' <None> VISIBLE NONE;
        'Alternate Name Table:Street Name' RoadAlias:A_RD VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;
        'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"""

        userMessage("Creating address locator...")
        # Process: Create Address Locator
        if Exists(Locator):
            RebuildAddressLocator_geocoding(Locator)
        else:
            try:
                CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, Locator, "")
            except:
                try:
                    fieldMap = """'Primary Table:Feature ID' RoadCenterline:SEGID VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
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
                    'Primary Table:Altname JoinID' RoadCenterline:SEGID VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:SEGID VISIBLE NONE;
                    'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' <None> VISIBLE NONE;
                    'Alternate Name Table:Street Name' RoadAlias:A_RD VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;
                    'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"""
                    CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, Locator, "", "DISABLED")
                except Exception as E:
                    try:
                        fieldMap = """'Primary Table:Feature ID' RoadCenterline:SEGID VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
                        '*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;
                        '*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;
                        'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;
                        'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;
                        'Primary Table:Left City or Place' RoadCenterline:MUNI_L VISIBLE NONE;'Primary Table:Right City or Place' RoadCenterline:MUNI_R VISIBLE NONE;
                        'Primary Table:Left ZIP Code' RoadCenterline:ZIP_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:ZIP_R VISIBLE NONE;
                        'Primary Table:Left State' RoadCenterline:STATE_L VISIBLE NONE;'Primary Table:Right State' RoadCenterline:STATE_R VISIBLE NONE;
                        'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;
                        'Primary Table:Display X' <None> VISIBLE NONE;'Primary Table:Display Y' <None> VISIBLE NONE;
                        'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;
                        'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;
                        'Primary Table:Left parity' <None> VISIBLE NONE;'Primary Table:Right parity' <None> VISIBLE NONE;
                        'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;
                        '*Primary Table:Altname JoinID' RoadCenterline:SEGID VISIBLE NONE;'*Alias Table:Alias' RoadAlias:SEGID VISIBLE NONE;
                        '*Alias Table:Street' RoadAlias:A_RD VISIBLE NONE;'Alias Table:City' <None> VISIBLE NONE;'Alias Table:State' <None> VISIBLE NONE;
                        'Alias Table:ZIP' <None> VISIBLE NONE"""
                        CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alias Table'", fieldMap, Locator, "", "DISABLED")
                    except Exception as E:
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
            gc_fieldMap = "Street " + a_obj.LABEL + " VISIBLE NONE;City " + a_obj.MUNI + " VISIBLE NONE;State " + a_obj.STATE + " VISIBLE NONE;ZIP " + a_obj.ZIP + " VISIBLE NONE"

            #geocode addresses
            try:
                GeocodeAddresses_geocoding(gc_table, Locator, gc_fieldMap, output, "STATIC")
                i = 1
            except:
                gc_fieldMap =  "Street " + a_obj.LABEL + " VISIBLE NONE;City " + a_obj.MUNI + " VISIBLE NONE;State " + a_obj.STATE + " VISIBLE NONE"

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

                    rfields = (a_obj.UNIQUEID, "Status", a_obj.LOCTYPE)
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
                                        report = "Error: " + report
                                    val = (today, report, filename, "", fID)
                                    values.append(val)
                                Delete_management(tblGE)

                            else:
                                report = "Error: " + str(fID) + " did not geocode against centerline"
                                val = (today, report, filename, "", fID)
                                values.append(val)

                    if rCount > 0:
                        userMessage("Completed geocoding with " + str(rCount) + " errors.")
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

def checkDirectionality(fc,gdb):
    userMessage("Checking road directionality...")

    #set variables
    values = []
    recordType = "fieldValues"
    today = strftime("%m/%d/%y")
    filename = "RoadCenterline"
    report = "Notice: Segment's address range is from high to low instead of low to high"

    fields = ("SHAPE@", rc_obj.UNIQUEID, rc_obj.L_F_ADD, rc_obj.L_T_ADD, rc_obj.R_F_ADD, rc_obj.R_T_ADD)

    lyr400 = "lyr400"
    #only check roads marked for submission
    if fieldExists(fc, "SUBMIT"):
        MakeFeatureLayer_management(fc, lyr400, rc_obj.SUBMIT + " not in ('N')")
    else:
        MakeFeatureLayer_management(fc, lyr400)

    with SearchCursor(lyr400, fields) as rows:
        for row in rows:

            #get unique id and from/to values
            segid = row[1]
            addyList = [row[2],row[3],row[4],row[5]]

            #make sure it's not a blank road
            if addyList != [0,0,0,0]:

                #set up values
                lFrom = addyList[0]
                lTo = addyList[1]
                rFrom = addyList[2]
                rTo = addyList[3]

                check = "both"
                issue = "no"

                #see if we're working with any 0's
                if lFrom == 0 or lTo == 0:
                    check = "right"
                elif rFrom ==0 or rTo == 0:
                    check = "left"

                #see if any road values don't follow low to high pattern
                if check == "both":
                    if rTo < rFrom or lTo < lFrom:
                        issue = "yes"
                elif check == "right":
                    if rTo < rFrom:
                        issue = "yes"
                elif check == "left":
                    if lTo < lFrom:
                        issue = "yes"

                if issue == "yes":
                    val = (today, report, filename, "", segid)
                    values.append(val)

    Delete_management(lyr400)

    #report records
    if values != []:
        RecordResults(recordType, values, gdb)
        userMessage("Completed road directionality check. There were " + str(len(values)) + " issues.")
    else:
        userMessage("Completed road directionality check. No issues found.")

def checkESNandMuniAttribute(currentPathSettings):

    NG911gdb = currentPathSettings.gdbPath
    esz = currentPathSettings.ESZ

    gdb_object = getGDBObject(NG911gdb)

    address_points = gdb_object.AddressPoints
    muni = gdb_object.MunicipalBoundary

    addy_lyr = "addy_lyr"
    MakeFeatureLayer_management(address_points, addy_lyr)

    values = []
    recordType = "fieldValues"
    today = strftime("%m/%d/%y")
    filename = "AddressPoints"

    searchDict = {esz: (esz_obj.ESN, esz_obj.UNIQUEID), muni: (mb_obj.MUNI, mb_obj.UNIQUEID)}

    for layer, fieldList in searchDict.iteritems():

        if Exists(layer):

            with SearchCursor(layer, fieldList) as polys:
                for poly in polys:
                    feature = fieldList[0]
                    feature_value = poly[0]

                    #make feature layer
                    lyr1 = "lyr1"
                    qry = fieldList[1] + " = '" + str(poly[1]) + "'"
                    MakeFeatureLayer_management(layer, lyr1, qry)

                    #select by location
                    SelectLayerByLocation_management(addy_lyr, "INTERSECT", lyr1)

                    #loop through address points
                    with SearchCursor(addy_lyr, (feature, a_obj.UNIQUEID, a_obj.LOCTYPE, "OBJECTID")) as rows:
                        for row in rows:
                            #get value
                            value_addy = row[0]
                            segID = row[1]
                            objectID = row[3]

                            if segID is not None:
                                try:
                                    #see if the values match
                                    if value_addy.strip() != feature_value.strip():
                                        #this issue has been demoted to a notice
                                        report = "Notice: Address point " + feature + " does not match " + feature + " in " + basename(layer) + " layer"
                                        val = (today, report, filename, feature, segID)
                                        values.append(val)
                                except:
                                    userMessage("Issue comparing value for " + feature + " with OBJECTID: " + str(objectID))
                            else:
                                userMessage("Issue comparing value for " + feature + " with OBJECTID: " + str(objectID))

                    Delete_management(lyr1)
                    del lyr1

            try:
                del poly, polys
            except:
                userMessage("Poly/polys didn't exist in the Muni/ESN check. No worries.")
    Delete_management(addy_lyr)

    #report records
    if values != []:
        RecordResults(recordType, values, NG911gdb)
        userMessage("Address point ESN/Municipality check complete. " + str(len(values)) + " issues found. Results are in the FieldValuesCheckResults table.")
    else:
        userMessage("Address point ESN/Municipality check complete. No issues found.")

def checkUniqueIDFrequency(currentPathSettings):
    gdb = currentPathSettings.gdbPath
    esbList = currentPathSettings.esbList
    fcList = currentPathSettings.fcList

    layerList = []

    env.workspace = gdb
    table = "ESB_IDS"

    #create temp table of esbID's
    if len(esbList) > 1 and esbList[0] != esbList[1]:
        layerList = ["ESB_IDS"]

        deleteExisting(table)

        CreateTable_management(gdb, table)

        AddField_management(table, esb_obj.UNIQUEID, "TEXT", "", "", 38)
        AddField_management(table, "ESB_LYR", "TEXT", "", "", 30)

        esbFields = (esb_obj.UNIQUEID)

        #copy ID's & esb layer type into the table
        for esb in esbList:
            with SearchCursor(esb, esbFields) as rows:
                for row in rows:
                    cursor = InsertCursor(table, (esb_obj.UNIQUEID, 'ESB_LYR'))
                    cursor.insertRow((row[0], esb))

        try:
            #clean up
            del rows, row, cursor
        except:
            print "objects cannot be deleted, they don't exist"

    else:
        for fc in fcList:
            fc = basename(fc)
            layerList.append(fc)

    #loop through layers in the gdb that aren't esb & ESB_IDS
##    layers = getCurrentLayerList(esb)
##    layers.append("ESB_IDS")

    values = []
    recordType = "fieldValues"
    today = strftime("%m/%d/%y")

    for layer in layerList:
##        if layer not in esb:
        if layer != "ESB_IDS":
            #for each layer, get the unique ID field
            uniqueID = getUniqueIDField(layer.upper())

        else:
            #for esb layers, get the unique ID field
            uniqueID = esb_obj.UNIQUEID

        freq_table = layer + "_freq"

        deleteExisting(freq_table)

        Statistics_analysis(layer, freq_table, [[uniqueID,"COUNT"]], uniqueID)

        #set parameters for the search cursor
        where_clause = "FREQUENCY > 1"
        fields = (uniqueID, "FREQUENCY")

        fl = "fl"

        MakeTableView_management(freq_table, fl, where_clause)

        if getFastCount(fl) > 0:

            #set a search cursor with just the unique ID field
            with SearchCursor(freq_table, fields, where_clause) as rows2:
                stringESBReport = ""
                for row2 in rows2:
                    reportLayer = layer
                    if layer == "ESB_IDS":
                        reportLayer = "ESB"
                        stringEsbInfo = []
                        wc2 = "ESBID = '" + str(row2[0]) + "'"
                        with SearchCursor("ESB_IDS", ("ESB_LYR"), wc2) as esbRows:
                            for esbRow in esbRows:
                                stringEsbInfo.append(esbRow[0])

                        stringESBReport = " and ".join(stringEsbInfo)

                    #report duplicate IDs
                    report = "Error: " + str(row2[0]) + " is a duplicate ID"
                    if stringESBReport != "":
                        report = report + " in " + stringESBReport
                    val = (today, report, reportLayer, uniqueID, row2[0])
                    values.append(val)

        cleanUp([freq_table, fl])

    #report duplicate records
    if values != []:
        RecordResults(recordType, values, gdb)
        userMessage("Checked unique ID frequency. Results are in table FieldValuesCheckResults.")
    else:
        userMessage("All ID's are unique.")

    #if it exists, clean up table
    deleteExisting(table)

def checkFrequency(fc, freq, fields, gdb):
    fl = "fl"
    fl1 = "fl1"
    wc = "FREQUENCY > 1"

    #remove the frequency table if it exists already
    try:
        deleteExisting(freq)
    except:
        userMessage("Please manually delete " + freq + " and then run the frequency check again")

    if not Exists(freq):
##        try:
            #see if we're working with address points or roads, create a where clause
            filename = ""
            if freq == join(gdb, "AP_Freq"):
                filename = "AddressPoints"
                wc1 = a_obj.HNO + " <> 0 and " + a_obj.LOCTYPE + " = 'PRIMARY'"
            elif freq == join(gdb, "Road_Freq"):
                filename = "RoadCenterline"
                wc1 = rc_obj.L_F_ADD + " <> 0 AND " + rc_obj.L_T_ADD + " <> 0 AND " + rc_obj.R_F_ADD + " <> 0 AND " + rc_obj.R_T_ADD + " <> 0"

            if fieldExists(fc, "SUBMIT"):
                wc1 = wc1 + " AND " + rc_obj.SUBMIT + " not in ('N')"

            #run query on fc to make sure 0's are ignored
            MakeTableView_management(fc, fl1, wc1)

            #split field names
            fieldsList = fields.split(";")
            fieldCountList = []
            fl_fields = []
            for f in fieldsList:
                f = f.strip()
                fList = [f,"COUNT"]
                fieldCountList.append(fList)
                fl_fields.append(f)

            #run frequency analysis
            Statistics_analysis(fl1, freq, fieldCountList, fields)

            #make feature layer
            MakeTableView_management(freq, fl, wc)

            #get count of the results
            if getFastCount(fl) > 0:

                #set up parameters to report duplicate records
                values = []
                recordType = "fieldValues"
                today = strftime("%m/%d/%y")

                #add information to FieldValuesCheckResults for all duplicates

                #get field count
                fCount = len(fl_fields)

                #get the unique ID field name
                id1 = getUniqueIDField(filename.upper())

                #run a search on the frequency table to report duplicate records
                with SearchCursor(freq, fl_fields, wc) as rows:
                    for row in rows:
                        i = 0
                        #generate where clause to find duplicate ID's
                        wc = ""
                        while i < fCount:
                            stuff = ""
                            if row[i] != None:
                                try:
                                    stuff = " = '" + row[i] + "' "
                                except:
                                    stuff = " = " + str(row[i]) + " "
                            else:
                                stuff = " is null "
                            wc = wc + fl_fields[i] + stuff + "and "
                            i += 1

                        #trim last "and " off where clause
                        wc = wc[0:-5]

                        #find records with duplicates to get their unique ID's
                        with SearchCursor(fl1, (id1), wc) as sRows:
                            for sRow in sRows:
                                fID = sRow[0]
                                report = "Error: " + str(fID) + " has duplicate field information"
                                val = (today, report, filename, "", fID)
                                values.append(val)

                #report duplicate records
                if values != []:
                    RecordResults(recordType, values, gdb)
                    userMessage("Checked frequency. Results are in table FieldValuesCheckResults")

            else:
                userMessage("Checked frequency. All records are unique.")

            #clean up
            try:
                cleanUp([fl, fl1, freq])
            except:
                userMessage("Issue deleting a feature layer or frequency table.")
##        except:
##            userMessage("Could not fully run frequency check")

def checkLayerList(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    esb = pathsInfoObject.esbList

    values = []
    today = strftime("%m/%d/%y")

    #make sure the NG911 feature dataset exists
    userMessage("Checking feature dataset name...")
    env.workspace = gdb

    datasets = ListDatasets()

    if "NG911" not in datasets:
        dataset_report = "Error: No feature dataset named 'NG911' exists"
        val = (today, dataset_report, "Template")
        values.append(val)
        userMessage(dataset_report)

    userMessage("Checking geodatabase layers...")
    #get current layer list
    layerList = getCurrentLayerList(esb)
    if "CountyBoundary" in layerList:
        layerList.remove("CountyBoundary")
    if "MunicipalBoundary" in layerList:
        layerList.remove("MunicipalBoundary")
    layers = []
    for dirpath, dirnames, filenames in Walk(gdb, True, '', False, ["Table","FeatureClass"]):
##        ignoreList = ("gc_test", "TemplateCheckResults", "FieldValuesCheckResults", "GeocodeTable")
        for fn in filenames:
            name = basename(fn)
            layers.append(name.upper())

##    userMessage(layers)

    #report any required layers that are not present
    for l in layerList:
        if l.upper() not in layers:
            report = "Error: Required layer " + l + " is not in geodatabase."
            userMessage(report)
            val = (today, report, "Layer")
            values.append(val)

    #record issues if any exist
    if values != []:
        RecordResults("template", values, gdb)


def getKeyword(layer, esb):
    if layer in esb:
        keyword = "EmergencyBoundary"
    else:
        keyword = layer

    return keyword


def getRequiredFields(folder):
    path1 = path.join(folder, "NG911_RequiredFields.txt")

    #create a field definition dictionary
    rfDict = {}

    #make sure file path exists
    if path.exists(path1):
        fieldDefDoc = open(path1, "r")

        #get the header information
        headerLine = fieldDefDoc.readline()
        valueList = headerLine.split("|")
        ## print valueList

        #get field indexes
        fcIndex = valueList.index("FeatureClass")
        fieldIndex = valueList.index("Field\n")

        #parse the text to populate the field definition dictionary
        for line in fieldDefDoc.readlines():
            stuffList = line.split("|")
            #set up values
            fc = stuffList[0]
            field = stuffList[1].rstrip()
            fieldList = []

            #see if field list already exists
            if fc in rfDict.iterkeys():
                fieldList = rfDict[fc]

            #append new value onto list
            fieldList.append(field)

            #set value as list
            rfDict[fc] = fieldList
    else:
        userMessage("The file " + path1 + " is required to run field checks.")

    return rfDict


def getFieldDomain(field, folder):
##    userMessage(field)
    if "_" in field:
        f = field.split("_")
        field = f[0]

    docPath = path.join(folder, field + "_Domains.txt")
    ## print docPath

    domainDict = {}

    #make sure path exists
    if path.exists(docPath):
        doc = open(docPath, "r")

        headerLine = doc.readline()
        valueList = headerLine.split("|")

        valueIndex = valueList.index("Values")
        defIndex = valueList.index("Definition\n")


        #parse the text to population the field definition dictionary
        for line in doc.readlines():
            if line != "\n":
                stuffList = line.split("|")
    ##            userMessage(stuffList)
                domainDict[stuffList[0].rstrip().lstrip()] = stuffList[1].rstrip().lstrip()

    else:
        userMessage("The file " + docPath + " is required to run a domain check.")

    return domainDict


def checkValuesAgainstDomain(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    folder = pathsInfoObject.domainsFolderPath
    fcList = pathsInfoObject.fcList
    esb = pathsInfoObject.esbList
##    version = pathsInfoObject.gdbVersion

    userMessage("Checking field values against approved domains...")
    #set up parameters to report duplicate records
    values = []
    resultType = "fieldValues"
    today = strftime("%m/%d/%y")
    filename = ""

    #set environment
    env.workspace = gdb

    for fullPath in fcList:
        fc = basename(fullPath).replace("'", "")
        layer = fc.upper()
        if fc in esb:
            layer = "ESB"

        #only check records marked for submission
        fullPathlyr = "fullPathlyr"
        worked = 0
        if not fieldExists(fullPath, "SUBMIT"):
            MakeTableView_management(fullPath, fullPathlyr)
            worked = 1
        else:
            wc2 = rc_obj.SUBMIT + " not in ('N')"
            try:
                MakeTableView_management(fullPath, fullPathlyr, wc2)
                worked = 1
            except:
                userMessage("Cannot check required field values for " + layer)

        if worked == 1:

            #get list of fields with domains
            fieldsWDoms = fieldsWithDomains(fullPath)

    ##        #remove "STATUS" field if we aren't working with road centerline- edit suggested by Sherry M., 6/16/2015
    ##        if layer != "ROADCENTERLINE":
    ##            if "STATUS" in fieldsWDoms:
    ##                fieldsWDoms.remove("STATUS")

            id1 = getUniqueIDField(layer)
            if id1 != "":
                #create complete field list
                fieldNames = ListFieldNames(fc)

                #see if fields from complete list have domains
                for fieldN in fieldNames:

                    #userMessage(fieldN)
                    #if field has a domain
                    if fieldN in fieldsWDoms:
                        domain = ""
                        if fieldN[0:2] == "A_":
                            domain = fieldN[2:]
                        else:
                            domain = fieldN

                        userMessage("Checking: " + fieldN)
                        #get the full domain dictionary
                        domainDict = getFieldDomain(domain, folder)

                        if domainDict != {}:
                            #put domain values in a list
                            domainList = []

                            for val in domainDict.iterkeys():
                                domainList.append(val)

                            #add values for some CAD users of blank and space (edit suggested by Sherry M. & Keith S. Dec 2014)
                            domainList.append('')
                            domainList.append(" ")

                            #if the domain is counties, add county names to the list without "COUNTY" so both will work (edit suggest by Keith S. Dec 2014)
                            if fieldN == "COUNTY":
                                q = len(domainList)
                                i = 0
                                while i < q:
                                    dl1 = domainList[i].split(" ")[0]
        ##                            userMessage(dl1)
                                    domainList.append(dl1)
                                    i += 1

                            #loop through records for that particular field to see if all values match domain
                            wc = fieldN + " is not null"
                            with SearchCursor(fullPathlyr, (id1, fieldN), wc) as rows:
                                for row in rows:
                                    if row[1] is not None:
                                        fID = row[0]
                                        #see if field domain is actually a range
                                        if fieldN == a_obj.HNO:
                                            hno = row[1]
                                            if hno > 999999 or hno < 0:
                                                report = "Error: Value " + str(row[1]) + " not in approved domain for field " + fieldN
                                                val = (today, report, fc, fieldN, fID)
                                                values.append(val)
                                        #otherwise, compare row value to domain list
                                        else:
    ##                                        userMessage("Checking value: " + row[1])
                                            if row[1] not in domainList:
                                                report = "Error: Value " + str(row[1]) + " not in approved domain for field " + fieldN
                                                val = (today, report, fc, fieldN, fID)
                                                values.append(val)

                        else:
                            userMessage("Could not compare domain for " + fieldN)
            userMessage("Checked " + layer)

        Delete_management(fullPathlyr)

    if values != []:
        RecordResults(resultType, values, gdb)

    userMessage("Completed checking fields against domains: " + str(len(values)) + " issues found")


def checkRequiredFieldValues(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    folder = pathsInfoObject.domainsFolderPath
    esb = pathsInfoObject.esbList
##    version = pathsInfoObject.gdbVersion
    fcList = pathsInfoObject.fcList

    userMessage("Checking that required fields have all values...")

    #get today's date
    today = strftime("%m/%d/%y")

    #get required fields
    rfDict = getRequiredFields(folder)

    if rfDict != {}:

        values = []
        requiredFieldList = []
        #walk through the tables/feature classes
##        for dirpath, dirnames, filenames in Walk(gdb, True, '', False, ["Table","FeatureClass"]):
##            for filename in filenames:
##                if filename.upper() not in ("FIELDVALUESCHECKRESULTS", "TEMPLATECHECKRESULTS", "GEOCODEEXCEPTIONS"):
##                    fullPath = path.join(gdb, filename)
##        userMessage(fcList)
        for filename in fcList:
##            userMessage(filename)
            for l in ['FIRE','LAW','EMS','ESB','PSAP']:
                if l in filename.upper():
                    layer = "ESB"
                else:
                    layer = basename(filename).upper()
##            userMessage(layer)
            id1 = getUniqueIDField(layer)
            if id1 != "":

                #get the keyword to acquire required field names
                keyword = getKeyword(layer, esb)

                #goal: get list of required fields that are present in the feature class
                #get the appropriate required field list
                if keyword in rfDict:
                    requiredFieldList = rfDict[keyword]

                rfl = []
                for rf in requiredFieldList:
                    rfl.append(rf.upper())

                #get list of fields in the feature class
                fields = ListFieldNames(filename)

                #convert lists to sets
                set1 = set(rfl)
                set2 = set(fields)

                #get the set of fields that are the same
                matchingFields = list(set1 & set2)

                #only work with records that are for submission
                lyr2 = "lyr2"
                worked = 0
                if not fieldExists(filename, "SUBMIT"):
                    MakeTableView_management(filename, lyr2)
                    worked = 1
                else:
                    wc2 = rc_obj.SUBMIT + " not in ('N')"
                    try:
                        MakeTableView_management(filename, lyr2, wc2)
                        worked = 1
                    except:
                        userMessage("Cannot check required field values for " + layer)

                if worked == 1:

                    #get count of the results
                    if getFastCount(lyr2) > 0:

                        #create where clause to select any records where required values aren't populated
                        wc = ""

                        for field in matchingFields:
                            wc = wc + " " + field + " is null or "

                        wc = wc[0:-4]

                        #make table view using where clause
                        lyr = "lyr"
                        MakeTableView_management(lyr2, lyr, wc)

                        #if count is greater than 0, it means a required value somewhere isn't filled in
                        if getFastCount(lyr) > 0:
                            #make sure the objectID gets included in the search for reporting
                            if id1 not in matchingFields:
                                matchingFields.append(id1)

                            #run a search cursor to get any/all records where a required field value is null
                            with SearchCursor(lyr, (matchingFields), wc) as rows:
                                for row in rows:
                                    k = 0
                                    #get object ID of the field
                                    oid = str(row[matchingFields.index(id1)])

                                    #loop through row
                                    while k < len(matchingFields):
                                        #see if the value is nothing
                                        if row[k] is None:
                                            #report the value if it is indeed null
                                            report = "Error: " + matchingFields[k] + " is null for Feature ID " + oid
                                            userMessage(report)
                                            val = (today, report, filename, matchingFields[k], oid)
                                            values.append(val)

                                        #iterate!
                                        k = k + 1
                        else:
                            userMessage( "All required values present for " + layer)

                        Delete_management(lyr)
                        del lyr

                    else:
                        userMessage(layer + " has no records marked for submission. Data will not be verified.")
                    Delete_management(lyr2)

        if values != []:
            RecordResults("fieldValues", values, gdb)

        userMessage("Completed check for required field values: " + str(len(values)) + " issues found")

    else:
        userMessage("Could not check required field values")


def checkRequiredFields(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    folder = pathsInfoObject.domainsFolderPath
    esb = pathsInfoObject.esbList
##    version = pathsInfoObject.gdbVersion

    userMessage("Checking that required fields exist...")

    #get today's date
    today = strftime("%m/%d/%y")
    values = []

    #get required fields
    rfDict = getRequiredFields(folder)

    if rfDict != {}:

        #walk through the tables/feature classes
        for dirpath, dirnames, filenames in Walk(gdb, True, '', False, ["Table","FeatureClass"]):
            for filename in filenames:
                fullPath = path.join(gdb, filename)

                #list fields
                fields = ListFieldNames(fullPath)

                #get the keyword to acquire required field names
                keyword = getKeyword(filename, esb)

                #get the appropriate comparison list
                if keyword in rfDict:
                    comparisonList = rfDict[keyword]
                    ## print comparisonList

                    #work around for geodatabases in version 1.0
                    if not fieldExists(fullPath, "EXCEPTION"):
                        if rc_obj.EXCEPTION in comparisonList:
                            comparisonList.remove(rc_obj.EXCEPTION)

                    #loop through required fields to make sure they exist in the geodatabase
                    for comparisonField in comparisonList:
                        if comparisonField.upper() not in fields:
                            report = "Error: " + filename + " does not have required field " + comparisonField
                            userMessage(report)
                            #add issue to list of values
                            val = (today, report, "Field")
                            values.append(val)

        #record issues if any exist
        if values != []:
            RecordResults("template", values, gdb)

        userMessage("Completed check for required fields: " + str(len(values)) + " issues found")

    else:
        userMessage("Could not check for required fields.")

def checkSubmissionNumbers(pathsInfoObject):
    #set variables
    gdb = pathsInfoObject.gdbPath
    esb = pathsInfoObject.esbList
##    version = pathsInfoObject.gdbVersion
    gdbObject = getGDBObject(gdb)
    fcList = pathsInfoObject.fcList

##    #create list of feature classes & tables to check
##    fcList = [gdbObject.AddressPoints, gdbObject.RoadCenterline, gdbObject.RoadAlias, gdbObject.AuthoritativeBoundary, gdbObject.MunicipalBoundary]
##    for e in esb:
##        full_path = join(gdb, "NG911", e)
##        fcList.append(full_path)

    today = strftime("%m/%d/%y")
    values = []

    for fc in fcList:
        #count records that are for submission
        lyr2 = "lyr2"
        if not fieldExists(fc, "SUBMIT"):
            MakeTableView_management(fc, lyr2)
        else:
            wc2 = rc_obj.SUBMIT + " not in ('N')"
            if "AddressPoints" in fc:
                wc2 = wc2 + " AND " + a_obj.LOCTYPE + " = 'PRIMARY'"
            MakeTableView_management(fc, lyr2, wc2)

        #get count of the results
        count = getFastCount(lyr2)

        userMessage(basename(fc) + ": " + str(count) + " records marked for submission")

        if count == 0:
            report = "Error: " + basename(fc) + " has 0 records for submission"
            if "MunicipalBoundary" in fc:
                report = report.replace("Error", "Notice")
            #add issue to list of values
            val = (today, report, "Submission")
            values.append(val)

        Delete_management(lyr2)

    #record issues if any exist
    if values != []:
        RecordResults("template", values, gdb)

def checkFeatureLocations(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    fcList = pathsInfoObject.fcList
    esb = pathsInfoObject.esbList
##    version = pathsInfoObject.gdbVersion

    gdbObject = getGDBObject(gdb)

    RoadAlias = gdbObject.RoadAlias

    if RoadAlias in fcList:
        fcList.remove(RoadAlias)

    userMessage("Checking feature locations...")

    #get today's date
    today = strftime("%m/%d/%y")
    values = []

    #make sure features are all inside authoritative boundary

    #get authoritative boundary
    authBound = gdbObject.AuthoritativeBoundary
    ab = "ab"

    #see if authoritative boundary has more than 1 feature
    #if more than one feature is in the authoritative boundary, use the county boundary instead
    if getFastCount(authBound) > 1:
        authBound = gdbObject.CountyBoundary

    MakeFeatureLayer_management(authBound, ab)

    for fullPath in fcList:
        if "CountyBoundary" not in fullPath:
            userMessage(fullPath)
            fl = "fl"
            if fieldExists(fullPath, "SUBMIT") == False:
                MakeFeatureLayer_management(fullPath, fl)
            else:
                wc = rc_obj.SUBMIT + " not in ('N')"
                if "RoadCenterline" in fullPath:
                    wc = wc + " AND " + rc_obj.EXCEPTION + " not in ('EXCEPTION INSIDE', 'EXCEPTION BOTH')"
                MakeFeatureLayer_management(fullPath, fl, wc)

            try:

                #select by location to get count of features outside the authoritative boundary
                SelectLayerByLocation_management(fl, "WITHIN", ab)
                SelectLayerByAttribute_management(fl, "SWITCH_SELECTION", "")
                #get count of selected records
                #report results
                if getFastCount(fl) > 0:
                    layer = basename(fullPath)
                    if layer in esb:
                        layerName = "ESB"
                    else:
                        layerName = layer
                    id1 = getUniqueIDField(layerName.upper())
                    if id1 != '':
                        fields = (id1)
                        if "AddressPoints" in fullPath:
                            fields = (id1, a_obj.LOCTYPE)
                        with SearchCursor(fl, fields) as rows:
                            for row in rows:
                                fID = row[0]
                                report = "Error: Feature not inside authoritative boundary"
                                if "AddressPoints" in fullPath:
                                    if row[1] != 'PRIMARY':
                                        report = report.replace("Error:", "Notice:")

                                val = (today, report, layer, " ", fID)
                                values.append(val)
                    else:
                        userMessage("Could not process features in " + fullPath)
                else:
                    userMessage( fullPath + ": all records inside authoritative boundary")
            except:
                userMessage("Could not check locations of " + fullPath)

            finally:

                #clean up
                Delete_management(fl)

    if values != []:
        RecordResults("fieldValues", values, gdb)


    userMessage("Completed check on feature locations: " + str(len(values)) + " issues found")

def findInvalidGeometry(pathsInfoObject):
    userMessage("Checking for invalid geometry...")

    #set variables
    gdb = pathsInfoObject.gdbPath
    esb = pathsInfoObject.esbList
##    version = pathsInfoObject.gdbVersion
    gdbObject = getGDBObject(gdb)
    fcList = pathsInfoObject.fcList

    today = strftime("%m/%d/%y")
    values = []
    report = "Error: Invalid geometry"

    invalidDict = {"point": 1, "polyline": 2, "polygon":3}

    #loop through feature classes
    for fullPath in fcList:

        #get the unique ID column
        layer = basename(fullPath)

        if layer.upper() != "ROADALIAS":
            if layer in esb:
                layerName = "ESB"
            else:
                layerName = layer

            id_column = getUniqueIDField(layerName.upper())

            #set up fields for cursor
            fields = ("SHAPE@", id_column)

            with SearchCursor(fullPath, fields) as rows:
                for row in rows:
                    geom = row[0]
                    fid = row[1]

                    try:
                        #get geometry type
                        geomType = geom.type

                        #find the minimum number of required points
                        minNum = invalidDict[geomType]

                        #get the count of points in the geometry
                        count = geom.pointCount

                        #if the count is smaller than the minimum number, there's a problem
                        if count < minNum:
                            val = (today, report, layer, " ", fid)
                            values.append(val)
                    except:
                        #if this errors, there's an error accessing the geometry, hence problems
                        val = (today, report, layer, " ", fid)
                        values.append(val)

    if values != []:
        RecordResults("fieldValues", values, gdb)

    userMessage("Completed for invalid geometry: " + str(len(values)) + " issues found")

def checkCutbacks(pathsInfoObject):
    userMessage("Checking for geometry cutbacks...")

    gdb = pathsInfoObject.gdbPath
    gdbObject = getGDBObject(gdb)
    road_fc = gdbObject.RoadCenterline
    roads = "roads"

    #make feature layer so only roads marked for submission are checked
    if fieldExists(road_fc, "SUBMIT"):
        MakeFeatureLayer_management(road_fc, roads, rc_obj.SUBMIT + " not in ('N')")
    else:
        MakeFeatureLayer_management(road_fc, roads)

    #set up tracking variables
    cutbacks = []
    values = []
    today = strftime("%m/%d/%y")
    layer = "RoadCenterline"

    k = 0

    #set up search cursor on roads layer
    with SearchCursor(roads, ("SHAPE@",rc_obj.UNIQUEID)) as rows:
        for row in rows:
            try:
                geom = row[0]
                segid = row[1]

                #loop through geometry parts
                for part in geom:
                    part_coords = []

                    #don't check simple roads
                    if len(part) > 4:
                        #loop through points
                        for pnt in part:
                            #set up points in a straightforward list
                            pc = []
                            if pnt:
                                pc = [pnt.X, pnt.Y]
                                part_coords.append(pc)
                            else:
                                print("interior ring")

                        #loop through coordinate list
                        if part_coords != []:
                            i = 1
                            while i < (len(part_coords)-1):

                                #calculate the angle between three points
                                angle = calcAngle(part_coords[i-1],part_coords[i],part_coords[i+1])
    ##                            print angle

                                #if the angle is quite sharp, it might indicate a cutback
                                if 0 < angle < 55:
                                    if segid not in cutbacks:
                                        report = "Notice: This segment might contain a geometry cutback"
                                        val = (today, report, layer, " ", segid)
                                        values.append(val)
                                        cutbacks.append(segid)
                                i += 1
            except Exception as e:
                userMessage("Issue checking a cutback.")
                k += 1

    Delete_management(roads)

    if values != []:
        RecordResults("fieldValues", values, gdb)

    if k != 0:
        userMessage("Could not complete cutback check on " + str(k) + " segments.")

    userMessage("Completed check on cutbacks: " + str(len(values)) + " issues found")

def getNumbers():
    numbers = "0123456789"
    return numbers

def VerifyRoadAlias(gdb, domainFolder):
    gdbObject = getGDBObject(gdb)
    #set up variables for search cursor
    roadAlias = gdbObject.RoadAlias
    fieldList = (ra_obj.A_RD, ra_obj.ALIASID)

    #get highway values
    hwy_text = join(domainFolder, "KS_HWY.txt")

    hwy_dict = {}

    #make sure file path exists
    if exists(hwy_text):
        fieldDefDoc = open(hwy_text, "r")

        #get the header information
        headerLine = fieldDefDoc.readline()
        valueList = headerLine.split("|")
        ## print valueList

        #get field indexes
        rNameIndex = valueList.index("ROUTENAME")
        rNumIndex = valueList.index("ROUTENUM\n")

        #parse the text to populate the field definition dictionary
        for line in fieldDefDoc.readlines():
            stuffList = line.split("|")

            #set up values
            route_num = stuffList[1].rstrip()
            route_name = stuffList[0]

            #see if the road list already exists in the hwy dictionary
            if route_num not in hwy_dict:
                nameList = [route_name]
            else:
                nameList = hwy_dict[route_num]
                nameList.append(route_name)

            #set dictionary value to name list
            hwy_dict[route_num] = nameList

    #get variables set up
    #where clause for the search cursor
    wc = ra_obj.A_STS + " is null or " + ra_obj.A_STS + " in ('HWY', '', ' ')"

    #variables for error reporting
    errorList = []
    values = []
    filename = basename(roadAlias)
    field = ra_obj.A_RD
    recordType = "fieldValues"
    today = strftime("%m/%d/%y")

    #get a list of numbers
    numbers = getNumbers()

    #start search cursor to examine records
    with SearchCursor(roadAlias, fieldList, wc) as rows:
        for row in rows:
            fID = row[1] #road alias ID for reporting
            try:
                road = row[0]
                first_char = road[0]

                #see if first character indicates a highway
                if first_char in "IUK0123456789":

                    for n in numbers:

                        #see if the road name has numbers in it
                        if n in road:

                            roadNum = road #working variable to strip out all alphabet characters

                            #get just the road number with no other characters
                            for r in roadNum:
                                if r not in numbers:
                                    roadNum = roadNum.replace(r, "")

                            #see if the road number is in the highway dictionary
                            if roadNum in hwy_dict:
                                if road not in hwy_dict[roadNum]:
                                    if fID not in errorList:
                                        errorList.append(fID)
                                        report = "Notice: " + road + " is not in the approved highway name list"
                                        val = (today, report, filename, field, fID)
                                        values.append(val)
            except Exception as e:
                report = "Error: Issue with road alias record"
                val = (today, report, filename, field, fID)
                values.append(val)


    #report records
    if values != []:
        #set up custom error count message
        count = len(errorList)
        if count > 1:
            countReport = "There were " + str(count) + " issues. "
        else:
            countReport = "There was 1 issue. "

        RecordResults(recordType, values, gdb)
        userMessage("Checked highway names in the road alias table. " + countReport + "Results are in table FieldValuesCheckResults")
    else:
        userMessage("Checked highway names in the road alias table. No errors were found.")

def checkJoin(gdb, inputTable, joinTable, where_clause, errorMessage, field):
    #set up tracking variables
    values = []
    today = strftime("%m/%d/%y")
    layer = field.split(".")[0]
    recordType = "fieldValues"

    AddJoin_management(inputTable, rc_obj.UNIQUEID, joinTable, rc_obj.UNIQUEID)
    tbl = "tbl"

    #get the fast count to see if issues exist
    MakeTableView_management(inputTable, tbl, where_clause)

    #see if any issues exist
    #catalog issues
    if getFastCount(tbl) > 0:
        fields = (field, "RoadCenterline." + rc_obj.RD)
        #NOTE: have to run the search cursor on the join table, running it on the table view throws an error
        with SearchCursor(inputTable, fields, where_clause) as rows:
            for row in rows:
                if row[1] is not None:
                    if " TO " in row[1] or "RAMP" in row[1] or "OLD" in row[1]:
                        print "this is probably an exception"
                    else:
                        val = (today, errorMessage, layer, "", row[0])
                        values.append(val)

    #clean up
    RemoveJoin_management(inputTable)
    Delete_management(tbl)

    #report records
    if values != []:
        RecordResults(recordType, values, gdb)

    valCount = len(values)

    return valCount

def checkRoadAliases(pathsInfoObject):
    userMessage("Checking road alias table...")

    gdb = pathsInfoObject.gdbPath
    gdbObject = getGDBObject(gdb)

    #make road layer into a feature layer
    roads = gdbObject.RoadCenterline
    rdslyr = "RoadCenterline"
    if fieldExists(roads, rc_obj.SUBMIT):
        MakeFeatureLayer_management(roads, rdslyr, rc_obj.SUBMIT + " not in ('N')")
    else:
        MakeFeatureLayer_management(roads, rdslyr)

    #make road alias into a table view
    road_alias = gdbObject.RoadAlias
    ra_tbl = "RoadAlias"
    if fieldExists(road_alias, ra_obj.SUBMIT):
        MakeTableView_management(road_alias, ra_tbl, ra_obj.SUBMIT + " not in ('N')")
    else:
        MakeTableView_management(road_alias, ra_tbl)

    #make sure all road alias records relate back to the road centerline file
    alias_count = checkJoin(gdb, ra_tbl, rdslyr, "RoadCenterline." + rc_obj.RD + " is null", "Notice: Road alias entry does not have a corresponding road centerline segment", "RoadAlias." + ra_obj.UNIQUEID)

    #see if the highways link back to a road alias record
    hwy_count = checkJoin(gdb, rdslyr, ra_tbl, "(RoadCenterline." + rc_obj.RD + " like '%HIGHWAY%' or RoadCenterline." + rc_obj.RD + " like '%HWY%' or RoadCenterline." + rc_obj.RD + " like '%INTERSTATE%') and RoadAlias." + ra_obj.A_RD + " is null",
                                "Notice: Road centerline highway segment does not have a corresponding road alias record", "RoadCenterline." + rc_obj.UNIQUEID)

    total_count = alias_count + hwy_count

    if total_count > 0:
        userMessage("Checked road alias records. There were " + str(total_count) + " issues. Results are in table FieldValuesCheckResults")
    else:
        userMessage("Checked road alias records. No errors were found.")

    #verify domain values
    VerifyRoadAlias(gdb, pathsInfoObject.domainsFolderPath)

    cleanUp([rdslyr, ra_tbl])


def checkToolboxVersionFinal():
    versionResult = checkToolboxVersion()
    if versionResult == "Your NG911 toolbox version is up-to-date.":
        userMessage(versionResult)
    else:
        AddWarning(versionResult)

def sanityCheck(currentPathSettings):

    #fcList will contain all layers in GDB so everything will be checked

    #clear out template check results & field check results
    gdb = currentPathSettings.gdbPath
    ClearOldResults(gdb, "true", "true")

    gdbObject = getGDBObject(gdb)

    #check template
    checkLayerList(currentPathSettings)
    checkRequiredFields(currentPathSettings)
    checkRequiredFieldValues(currentPathSettings)
    checkSubmissionNumbers(currentPathSettings)
    findInvalidGeometry(currentPathSettings)

    #common layer checks
    checkValuesAgainstDomain(currentPathSettings)
    checkFeatureLocations(currentPathSettings)
    checkUniqueIDFrequency(currentPathSettings)

    #check address points
    geocodeAddressPoints(currentPathSettings)
    addressPoints = gdbObject.AddressPoints
    AP_freq = gdbObject.AddressPointFrequency
    AP_fields = a_obj.FREQUENCY_FIELDS_STRING
    checkFrequency(addressPoints, AP_freq, AP_fields, currentPathSettings.gdbPath)
    if Exists(currentPathSettings.ESZ):
        checkESNandMuniAttribute(currentPathSettings)
    else:
        userMessage("ESZ layer does not exist. Cannot complete check.")


    #check roads
    roads = gdbObject.RoadCenterline
    road_freq = gdbObject.RoadCenterlineFrequency
    road_fields = rc_obj.FREQUENCY_FIELDS_STRING
    checkFrequency(roads, road_freq, road_fields, currentPathSettings.gdbPath)
    checkCutbacks(currentPathSettings)
    checkDirectionality(roads, currentPathSettings.gdbPath)
    checkRoadAliases(currentPathSettings)

    #verify that the check resulted in 0 issues
    sanity = 0 #flag to return at end
    numErrors = 0 #the total number of errors

    fieldCheckResults = gdbObject.FieldValuesCheckResults
    templateResults = gdbObject.TemplateCheckResults

    for table in [fieldCheckResults, templateResults]:
        if Exists(table):
            tbl = "tbl"
            wc = "Description not like '%Notice%'"
            MakeTableView_management(table, tbl, wc)
            count = getFastCount(tbl)
            numErrors = numErrors + count
            Delete_management(tbl)

    #change result = 1
    if numErrors == 0:
        sanity = 1
        today = strftime("%m/%d/%y")
        values = [(today, "Passed all checks")]
        RecordResults("DASCmessage", values, gdb)
        userMessage("Geodatabase passed all data checks.")
    else:
        userMessage("There were " + str(numErrors) + " issues with the data. Please view errors in the TemplateCheckResults and:or FieldValuesCheckResults tables.")

    checkToolboxVersionFinal()

    return sanity

def main_check(checkType, currentPathSettings):
##    try:
##        from NG911_Config import currentPathSettings # currentPathSettings should have all the path information available. ## import esb, gdb, folder
##    except:
##        userMessage( "Copy config file into command line")

    checkList = currentPathSettings.checkList
    env.workspace = currentPathSettings.gdbPath
    env.overwriteOutput = True

    gdbObject = getGDBObject(currentPathSettings.gdbPath)

    #give user a warning if they didn't select any validation checks
    stuffToCheck = 0
    for cI in checkList:
        if cI == "true":
            stuffToCheck = stuffToCheck + 1
    if stuffToCheck == 0:
        userMessage("Warning: you choose no validation checks.")

    #check geodatabase template
    if checkType == "template":
        if checkList[0] == "true":
            checkLayerList(currentPathSettings)

        if checkList[1] == "true":
            checkRequiredFields(currentPathSettings)

        if checkList[2] == "true":
            checkRequiredFieldValues(currentPathSettings)

        if checkList[3] == "true":
            checkSubmissionNumbers(currentPathSettings)

        if checkList[4] == "true":
            findInvalidGeometry(currentPathSettings)

    #check address points
    elif checkType == "AddressPoints":
        if checkList[0] == "true":
            checkValuesAgainstDomain(currentPathSettings)

        if checkList[1] == "true":
            checkFeatureLocations(currentPathSettings)

        if checkList[2] == "true":
            geocodeAddressPoints(currentPathSettings)

        if checkList[3] == "true":
            addressPoints = gdbObject.AddressPoints
            AP_freq = gdbObject.AddressPointFrequency
            AP_fields = a_obj.FREQUENCY_FIELDS_STRING
            checkFrequency(addressPoints, AP_freq, AP_fields, currentPathSettings.gdbPath)

        if checkList[4] == "true":
            checkUniqueIDFrequency(currentPathSettings)

        if checkList[5] == "true":
            if Exists(currentPathSettings.ESZ):
                checkESNandMuniAttribute(currentPathSettings)
            else:
                userMessage("ESZ layer does not exist, cannot complete check.")

    #check roads
    elif checkType == "Roads":
        roads = gdbObject.RoadCenterline
        if checkList[0] == "true":
            checkValuesAgainstDomain(currentPathSettings)

        if checkList[1] == "true":
            checkFeatureLocations(currentPathSettings)

        if checkList[2] == "true":
            road_freq = gdbObject.RoadCenterlineFrequency
            road_fields = rc_obj.FREQUENCY_FIELDS_STRING
            checkFrequency(roads, road_freq, road_fields, currentPathSettings.gdbPath)

        if checkList[3] == "true":
            checkUniqueIDFrequency(currentPathSettings)

        if checkList[4] == "true":
            checkCutbacks(currentPathSettings)

        if checkList[5] == "true":
            checkDirectionality(roads, currentPathSettings.gdbPath)

        if checkList[6] == "true":
            checkRoadAliases(currentPathSettings)

    #check boundaries or ESB
    elif checkType in ("admin", "ESB"):
        if checkList[0] == "true":
            checkValuesAgainstDomain(currentPathSettings)

        if checkList[1] == "true":
            checkFeatureLocations(currentPathSettings)

        if checkList[2] == "true":
            checkUniqueIDFrequency(currentPathSettings)

    checkToolboxVersionFinal()

if __name__ == '__main__':
    main()
