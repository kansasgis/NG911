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
#-------------------------------------------------------------------------------


from arcpy import (AddField_management, AddMessage, CalculateField_management,  CopyRows_management, CreateAddressLocator_geocoding, # @UnusedImport
                   CreateTable_management, Delete_management, Exists, GeocodeAddresses_geocoding, GetCount_management, FieldInfo, # @UnusedImport
                   ListFields, MakeFeatureLayer_management, MakeTableView_management, SelectLayerByAttribute_management, # @UnusedImport
                   SelectLayerByLocation_management, RebuildAddressLocator_geocoding, Frequency_analysis, DeleteRows_management, GetInstallInfo) # @UnusedImport
from arcpy.da import Walk, InsertCursor, ListDomains, SearchCursor  # @UnresolvedImport

from os import path
from os.path import basename, dirname, join

from time import strftime


def getCurrentLayerList(esb):
    layerList = ["RoadAlias", "AddressPoints", "RoadCenterline", "AuthoritativeBoundary", "CountyBoundary", "ESZ", "PSAP", "MunicipalBoundary"]
    for e in esb:
        layerList.append(e)
    return layerList


def userMessage(msg):
    print msg
    AddMessage(msg)


def getCurrentDomainList():
    domainList = ["AddressNumbers", "AddressParity", "AgencyID", "Counties", "Country",
                    "ESBType", "Municipality", "OneWay", "PlaceType", "PointLocation", "PostalCodes",
                    "PostalCommunities", "RoadClass", "RoadDirectionals", "RoadModifier", "RoadStatus",
                    "RoadSurface", "RoadTypes", "States", "Stewards"]
    #or get domain list from approved source

    return domainList


def fieldsWithDomains():
    #list of all the fields that have a domain
    fieldList = ["LOCTYPE", "STATUS", "SURFACE", "STEWARD", "AGENCYID","PLC", "RDCLASS", "PARITY", "ONEWAY", "MUNI", "COUNTY", "COUNTRY","PRD", "ZIP", "POSTCO", "STATE", "STS"]

    return fieldList

def getUniqueIDField(layer):
    id_dict = {"ADDRESSPOINTS":"ADDID", "AUTHORITATIVEBOUNDARY":"ABID", "COUNTYBOUNDARY":"CountyID", "ESB":"ESBID", "ESZ":"ESZID", "MUNICIPALBOUNDARY":"MUNI_ID", "PSAP":"ESBID", "ROADCENTERLINE":"SEGID", "ROADALIAS":"ALIASID"}
    try:
        id1 = id_dict[layer]
    except:
        id1 = ""
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
        fieldInfo = [(table, "DateFlagged", "DATE", "", "", ""),(table, "Description", "TEXT", "", "", 250),(table, "Category", "TEXT", "", "", 25)]
    elif lyr == "FieldValuesCheckResults":
        fieldInfo = [(table, "DateFlagged", "DATE", "", "", ""),(table, "Description", "TEXT", "", "", 250),(table, "Layer", "TEXT", "", "", 25),(table, "Field", "TEXT", "", "", 25),(table, "FeatureID", "TEXT", "", "", 38)]

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


def RecordResults(resultType, values, gdb): # Guessed on whitespace formatting here. -- DT
    if resultType == "template":
        tbl = "TemplateCheckResults"
    elif resultType == "fieldValues":
        tbl = "FieldValuesCheckResults"

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

    addressPointPath = pathsInfoObject.addressPointsPath
    streetPath = join(gdb, "RoadCenterline")
    roadAliasPath = join(gdb, "RoadAlias")

    userMessage("Geocoding address points...")

    gc_table = join(gdb, "GeocodeTable")
    sl_field = "SingleLineInput"
    Locator = join(gdb, "Locator")
    addyview = "addy_view"
    output = join(gdb, "gc_test")

    # Get the fields from the input
    fields = ListFields(addressPointPath)

    # Create a fieldinfo object
    fieldinfo = FieldInfo()

    # Iterate through the fields and set them to fieldinfo
    for field in fields:
        if field.name in ("LABEL", "ZIP"):
            fieldinfo.addField(field.name, field.name, "VISIBLE", "")
    else:
        fieldinfo.addField(field.name, field.name, "HIDDEN", "")

    userMessage("Preparing addresses...")
    # The created addyview layer will have fields as set in fieldinfo object
    MakeTableView_management(addressPointPath, addyview, "", "", fieldinfo)

    # To persist the layer on disk make a copy of the view
    if Exists(gc_table):
        Delete_management(gc_table)
    CopyRows_management(addyview, gc_table)

    #add single line input field for geocoding
    AddField_management(gc_table, sl_field, "TEXT", "", "", 250)

    #calculate field
    exp = '[LABEL] & " " & [ZIP]'
    CalculateField_management(gc_table, sl_field, exp, "VB")

    #generate locator
    fieldMap = """'Primary Table:Feature ID' <None> VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
    '*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;
    '*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;
    'Primary Table:Prefix Type' <None> VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;
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
        CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, Locator, "")

    userMessage("Geocoding addresses...")

    #geocode table address
    if Exists(output):
        Delete_management(output)

    i = 0

    #set up geocoding
    gc_fieldMap = "Street LABEL VISIBLE NONE;City MUNI VISIBLE NONE;State State VISIBLE NONE;ZIP ZIP VISIBLE NONE"

    #geocode addresses
    try:
        GeocodeAddresses_geocoding(gc_table, Locator, gc_fieldMap, output, "STATIC")
        i = 1
    except:
        gc_fieldMap = "Street LABEL VISIBLE NONE;City MUNI VISIBLE NONE;State State VISIBLE NONE"

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

        rStatus = GetCount_management(lyr)
        rCount = int(rStatus.getOutput(0))

        if rCount > 0:
            #set up parameters to report records that didn't geocode
            values = []
            recordType = "fieldValues"
            today = strftime("%m/%d/%y")
            filename = "AddressPoints"

            rfields = ("ADDID")
            with SearchCursor(output, rfields, wc) as rRows:
                for rRow in rRows:
                    fID = rRow[0]
                    report = str(fID) + " did not geocode against centerline"
                    val = (today, report, filename, "", fID)
                    values.append(val)

            #report records
            if values != []:
                RecordResults(recordType, values, gdb)

            userMessage("Completed geocoding with " + str(rCount) + " errors.")

        else:
            #this means all the records geocoded
            userMessage("All records geocoded successfully.")
            Delete_management(output)

def checkFrequency(fc, freq, fields, wc, gdb):
    fl = "fl"
    fl1 = "fl1"

    #remove the frequency table if it exists already
    if Exists(freq):
        Delete_management(freq)

    #see if we're working with address points or roads, create a where clause
    filename = ""
    if freq == join(gdb, "AP_Freq"):
        filename = "AddressPoints"
        wc1 = "HNO <> 0"
    elif freq == join(gdb, "Road_Freq"):
        filename = "RoadCenterline"
        wc1 = "L_F_ADD <> 0 AND L_T_ADD <> 0 AND R_F_ADD <> 0 AND R_T_ADD <> 0"

    #run query on fc to make sure 0's are ignored
    MakeTableView_management(fc, fl1, wc1)

    #run frequency analysis
    Frequency_analysis(fl1, freq, fields, "")

    #get count of records
    rFreq = GetCount_management(freq)
    rCount = int(rFreq.getOutput(0))

    #delete records

    #make feature layer
    MakeTableView_management(freq, fl, wc)

    #get count of the results
    result = GetCount_management(fl)
    count = int(result.getOutput(0))

    if rCount != count:
        #Delete
        DeleteRows_management(fl)

        #set up parameters to report duplicate records
        values = []
        recordType = "fieldValues"
        today = strftime("%m/%d/%y")

        #add information to FieldValuesCheckResults for all duplicates
        #get fields
        fl_fields1 = fields.split(";")
        fl_fields = []
        for f1 in fl_fields1:
            f = f1.strip()
            fl_fields.append(f)

        #get field count
        fCount = len(fl_fields)

        #get the unique ID field name
        id1 = getUniqueIDField(filename.upper())

        #run a search on the frequency table to report duplicate records
        with SearchCursor(freq, fl_fields) as rows:
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
##                userMessage(wc)

                #find records with duplicates to get their unique ID's
                with SearchCursor(fl1, (id1), wc) as sRows:
                    for sRow in sRows:
                        fID = sRow[0]
                        report = str(fID) + " has duplicate field information"
                        val = (today, report, filename, "", fID)
                        values.append(val)

        #report duplicate records
        if values != []:
            RecordResults(recordType, values, gdb)
            userMessage("Checked frequency. Results are in table FieldValuesCheckResults")
    elif rCount == count:
        userMessage("All records are unique.")

    Delete_management(freq)

def checkLayerList(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    esb = pathsInfoObject.esbList # Not currently dynamic.

    userMessage("Checking geodatabase layers...")
    #get current layer list
    layerList = getCurrentLayerList(esb)
    layers = []
    for dirpath, dirnames, filenames in Walk(gdb, True, '', False, ["Table","FeatureClass"]):  # @UnusedVariable
        ignoreList = ("gc_test", "TemplateCheckResults", "FieldValuesCheckResults", "GeocodeTable")
        for filename in filenames:
            if not filename in ignoreList:
                if filename not in layerList:
                    userMessage( filename + " not in geodatabase layer list template")
                else:
                    layers.append(filename)

    userMessage("Finished checking layers: ")
    userMessage(layers)


def getKeyword(layer, esb):
    if layer in esb:
        keyword = "EmergencyBoundary"
    else:
        keyword = layer

    return keyword


def getRequiredFields(folder):
    path1 = path.join(folder, "NG911_RequiredFields.txt")
    fieldDefDoc = open(path1, "r")

    #get the header information
    headerLine = fieldDefDoc.readline()
    valueList = headerLine.split("|")
    ## print valueList

    #get field indexes
    fcIndex = valueList.index("FeatureClass")  # @UnusedVariable
    fieldIndex = valueList.index("Field\n")  # @UnusedVariable

    #create a field definition dictionary
    rfDict = {}

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

    return rfDict


def getFieldDomain(field, folder):
##    userMessage(field)

    docPath = path.join(folder, field + "_Domains.txt")
    ## print docPath

    doc = open(docPath, "r")

    headerLine = doc.readline()
    valueList = headerLine.split("|")

    valueIndex = valueList.index("Values")  # @UnusedVariable
    defIndex = valueList.index("Definition\n")  # @UnusedVariable

    domainDict = {}

    #parse the text to population the field definition dictionary
    for line in doc.readlines():
        if line != "\n":
            stuffList = line.split("|")
##            userMessage(stuffList)
            domainDict[stuffList[0].rstrip().lstrip()] = stuffList[1].rstrip().lstrip()

    return domainDict


def checkValuesAgainstDomain(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    folder = pathsInfoObject.domainsFolderPath
    fcList = pathsInfoObject.fcList
    esb = pathsInfoObject.esbList

    userMessage("Checking field values against approved domains...")
    #set up parameters to report duplicate records
    values = []
    resultType = "fieldValues"
    today = strftime("%m/%d/%y")
    filename = ""

    #get list of fields with domains
    fieldsWDoms = fieldsWithDomains()

    for fullPath in fcList:
        fc = basename(fullPath)
        layer = fc.upper()
        if fc in esb:
            layer = "ESB"

        id1 = getUniqueIDField(layer)
        if id1 != "":
            fields = []
            #create complete field list
            fields = ListFields(fullPath)
            fieldNames = []

            for field in fields:
                fieldNames.append((field.name).upper())

            #see if fields from complete list have domains
            for fieldN in fieldNames:

                #if field has a domain
                if fieldN in fieldsWDoms:

                    #get the full domain dictionary
                    domainDict = getFieldDomain(fieldN, folder)

                    #put domain values in a list
                    domainList = []

                    for val in domainDict.iterkeys():
                        domainList.append(val.upper())

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
                    with SearchCursor(fullPath, (id1, fieldN), wc) as rows:
                        for row in rows:
                            if row[1] is not None:
                                fID = row[0]
                                #see if field domain is actually a range
                                if fieldN == "HNO":
                                    hno = row[1]
                                    if hno > 999999 or hno < 0:
                                        report = "Value " + str(row[1]) + " not in approved domain for field " + fieldN
                                        val = (today, report, fc, fieldN, fID)
                                        values.append(val)
                                #otherwise, compare row value to domain list
                                else:
                                    if row[1].upper() not in domainList:
                                        report = "Value " + str(row[1]) + " not in approved domain for field " + fieldN
                                        val = (today, report, fc, fieldN, fID)
                                        values.append(val)

    if values != []:
        RecordResults(resultType, values, gdb)

    userMessage("Completed checking fields against domains: " + str(len(values)) + " issues found")


def checkRequiredFieldValues(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    folder = pathsInfoObject.domainsFolderPath
    esb = pathsInfoObject.esbList

    userMessage("Checking that required fields have all values...")

    #get today's date
    today = strftime("%m/%d/%y")

    #get required fields
    rfDict = getRequiredFields(folder)

    values = []

    #walk through the tables/feature classes
    for dirpath, dirnames, filenames in Walk(gdb, True, '', False, ["Table","FeatureClass"]):  # @UnusedVariable
        for filename in filenames:
            if filename.upper() not in ("FIELDVALUESCHECKRESULTS", "TEMPLATECHECKRESULTS"):
                fullPath = path.join(gdb, filename)
                if filename.upper() in esb:
                    layer = "ESB"
                else:
                    layer = filename.upper()
                id1 = getUniqueIDField(layer)
                if id1 != "":

                    #get the keyword to acquire required field names
                    keyword = getKeyword(filename, esb)

                    #goal: get list of required fields that are present in the feature class
                    #get the appropriate required field list
                    if keyword in rfDict:
                        requiredFieldList = rfDict[keyword]

                    rfl = []
                    for rf in requiredFieldList:
                        rfl.append(rf.upper())

                    #get list of fields in the feature class
                    allFields = ListFields(fullPath)

                    #make list of field names
                    fields = []
                    for aF in allFields:
                        fields.append(aF.name.upper())

                    #convert lists to sets
                    set1 = set(rfl)
                    set2 = set(fields)

                    #get the set of fields that are the same
                    matchingFields = list(set1 & set2)

                    #create where clause to select any records where required values aren't populated
                    wc = ""

                    for field in matchingFields:
                        wc = wc + " " + field + " is null or "

                    wc = wc[0:-4]

                    #make table view using where clause
                    lyr = "lyr"
                    MakeTableView_management(fullPath, lyr, wc)

                    #get count of the results
                    result = GetCount_management(lyr)
                    count = int(result.getOutput(0))


                    #if count is greater than 0, it means a required value somewhere isn't filled in
                    if count > 0:
                        #make sure the objectID gets included in the search for reporting
                        if id1 not in matchingFields:
                            matchingFields.append(id1)

                        #run a search cursor to get any/all records where a required field value is null
                        with SearchCursor(fullPath, (matchingFields), wc) as rows:
                            for row in rows:
                                k = 0
                                #get object ID of the field
                                oid = str(row[matchingFields.index(id1)])

                                #loop through row
                                while k < len(matchingFields):
                                    #see if the value is nothing
                                    if row[k] is None:
                                        #report the value if it is indeed null
                                        report = matchingFields[k] + " is null for Feature ID " + oid
                                        userMessage(report)
                                        val = (today, report, filename, matchingFields[k], oid)
                                        values.append(val)

                                    #iterate!
                                    k = k + 1
                    else:
                        userMessage( "All required values present for " + filename)

                    Delete_management(lyr)

    if values != []:
        RecordResults("fieldValues", values, gdb)

    userMessage("Completed check for required field values: " + str(len(values)) + " issues found")


def checkRequiredFields(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    folder = pathsInfoObject.domainsFolderPath
    esb = pathsInfoObject.esbList

    userMessage("Checking that required fields exist...")

    #get today's date
    today = strftime("%m/%d/%y")
    values = []

    #get required fields
    rfDict = getRequiredFields(folder)

    #walk through the tables/feature classes
    for dirpath, dirnames, filenames in Walk(gdb, True, '', False, ["Table","FeatureClass"]):  # @UnusedVariable
        for filename in filenames:
            fields = []
            fullPath = path.join(gdb, filename)

            #list fields
            fs = ListFields(fullPath)

            for f in fs:
                fields.append(f.name.upper())

            #get the keyword to acquire required field names
            keyword = getKeyword(filename, esb)

            #get the appropriate comparison list
            if keyword in rfDict:
                comparisonList = rfDict[keyword]
                ## print comparisonList

                #loop through required fields to make sure they exist in the geodatabase
                for comparisonField in comparisonList:
                    if comparisonField.upper() not in fields:
                        report = filename + " does not have required field " + comparisonField
                        userMessage(report)
                        #add issue to list of values
                        val = (today, report, "Field")
                        values.append(val)

    #record issues if any exist
    if values != []:
        RecordResults("template", values, gdb)

    userMessage("Completed check for required fields: " + str(len(values)) + " issues found")


def checkFeatureLocations(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    fcList = pathsInfoObject.fcList
    esb = pathsInfoObject.esbList

    RoadAlias = join(gdb, "RoadAlias")

    if RoadAlias in fcList:
        fcList.remove(RoadAlias)

    userMessage("Checking feature locations...")

    #get today's date
    today = strftime("%m/%d/%y")
    values = []

    #make sure features are all inside authoritative boundary

    #get authoritative boundary
    authBound = path.join(gdb, "NG911", "AuthoritativeBoundary")
    ab = "ab"

    MakeFeatureLayer_management(authBound, ab)

    for fullPath in fcList:
        fl = "fl"
        MakeFeatureLayer_management(fullPath, fl)

        #select by location to get count of features outside the authoritative boundary
        SelectLayerByLocation_management(fl, "WITHIN", ab)
        SelectLayerByAttribute_management(fl, "SWITCH_SELECTION", "")
        #get count of selected records
        result = GetCount_management(fl)
        count = int(result.getOutput(0))

        #report results
        if count > 0:
            layer = basename(fullPath)
            if layer in esb:
                layerName = "ESB"
            else:
                layerName = layer
            id1 = getUniqueIDField(layerName.upper())
            report = "Feature not inside authoritative boundary"
            if id1 != '':
                with SearchCursor(fl, (id1)) as rows:
                    for row in rows:
                        fID = row[0]
                        val = (today, report, layer, " ", fID)
                        values.append(val)
            else:
                userMessage("Could not process features in " + fullPath)
        else:
            userMessage( fullPath + ": all records inside authoritative boundary")

        #clean up
        Delete_management(fl)

    if values != []:
        RecordResults("fieldValues", values, gdb)


    userMessage("Completed check on feature locations: " + str(len(values)) + " issues found")


def main_check(checkType, currentPathSettings):
##    try:
##        from NG911_Config import currentPathSettings # currentPathSettings should have all the path information available. ## import esb, gdb, folder
##    except:
##        userMessage( "Copy config file into command line")

    checkList = currentPathSettings.checkList

    #check geodatabase template
    if checkType == "template":
        if checkList[0] == "true":
            checkLayerList(currentPathSettings)

        if checkList[1] == "true":
            checkRequiredFields(currentPathSettings)

        if checkList[2] == "true":
            checkRequiredFieldValues(currentPathSettings)

    #check address points
    elif checkType == "AddressPoints":
        if checkList[0] == "true":
            checkValuesAgainstDomain(currentPathSettings)

        if checkList[1] == "true":
            checkFeatureLocations(currentPathSettings)

        if checkList[2] == "true":
            geocodeAddressPoints(currentPathSettings)

        if checkList[3] == "true":
            addressPoints = join(currentPathSettings.gdbPath, "AddressPoints")
            AP_freq = join(currentPathSettings.gdbPath, "AP_Freq")
            AP_fields = "MUNI;HNO;HNS;PRD;STP;RD;STS;POD;POM;ZIP;BLD;FLR;UNIT;ROOM;SEAT;LOC;LOCTYPE"
            AP_wc = "Frequency = 1 or LOCTYPE <> 'Primary'"
            checkFrequency(addressPoints, AP_freq, AP_fields, AP_wc, currentPathSettings.gdbPath)

    #check roads
    elif checkType == "Roads":
        if checkList[0] == "true":
            checkValuesAgainstDomain(currentPathSettings)

        if checkList[1] == "true":
            checkFeatureLocations(currentPathSettings)

        if checkList[2] == "true":
            roads = join(currentPathSettings.gdbPath, "RoadCenterline")
            road_freq = join(currentPathSettings.gdbPath, "Road_Freq")
            road_fields = """STATE_L;STATE_R;COUNTY_L;COUNTY_R;MUNI_L;MUNI_R;L_F_ADD;L_T_ADD;R_F_ADD;R_T_ADD;
            PARITY_L;PARITY_R;POSTCO_L;POSTCO_R;ZIP_L;ZIP_R;ESN_L;ESN_R;MSAGCO_L;MSAGCO_R;PRD;STP;RD;STS;POD;
            POM;SPDLIMIT;ONEWAY;RDCLASS;LABEL;ELEV_F;ELEV_T;ESN_C;SURFACE;STATUS;TRAVEL;LRSKEY"""
            road_wc = "Frequency = 1"
            checkFrequency(roads, road_freq, road_fields, road_wc, currentPathSettings.gdbPath)

    #check boundaries or ESB
    elif checkType in ("admin", "ESB"):
        if checkList[0] == "true":
            checkValuesAgainstDomain(currentPathSettings)

        if checkList[1] == "true":
            checkFeatureLocations(currentPathSettings)

if __name__ == '__main__':
    main()
