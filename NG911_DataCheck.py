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
                   SelectLayerByLocation_management) # @UnusedImport
from arcpy.da import Walk, InsertCursor, ListDomains, SearchCursor  # @UnresolvedImport

from os import path
from os.path import basename, dirname, join

from time import strftime


def getCurrentLayerList(esb):
    layerList = ["RoadAlias", "AddressPoints", "RoadCenterline", "AuthoritativeBoundary", "CountyBoundary", "ESZ", "PSAP", "MunicipalBoundary"]
    for e in esb:
        layerList.append(e)
        #future code: have each county's geodatabase model identified with ESB layers
        #get the layer list from their standard geodatabase
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
        fieldInfo = [(table, "DateFlagged", "DATE", "", "", ""),(table, "Description", "TEXT", "", "", 250),(table, "Layer", "TEXT", "", "", 25),(table, "Field", "TEXT", "", "", 25),(table, "FeatureID", "LONG", "", "", "")]

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
        cursor.insertRow(row)
    del cursor


def geocodeAddressPoints(addressPointPath, streetPath):
    userMessage("Geocoding address points...")

    gdb = dirname(addressPointPath)
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
    CopyRows_management(addyview, gc_table)

    #add single line input field for geocoding
    AddField_management(gc_table, sl_field, "TEXT", "", "", 250)

    #calculate field
    exp = '[LABEL] & " " & [ZIP]'
    CalculateField_management(gc_table, sl_field, exp, "VB")

    #generate locator
    fieldMap = """'Feature ID' '' VISIBLE NONE;'*From Left' L_F_ADD VISIBLE NONE;'*To Left' L_T_ADD VISIBLE NONE;
    '*From Right' R_F_ADD VISIBLE NONE;'*To Right' R_T_ADD VISIBLE NONE;'Prefix Direction' PRD VISIBLE NONE;
    'Prefix Type' '' VISIBLE NONE;'*Street Name' RD VISIBLE NONE;'Suffix Type' STS VISIBLE NONE;
    'Suffix Direction' '' VISIBLE NONE;'Left City or Place' MUNI_L VISIBLE NONE;
    'Right City or Place' MUNI_R VISIBLE NONE;'Left ZIP Code' ZIP_L VISIBLE NONE;'Right ZIP Code' ZIP_R VISIBLE NONE;
    'Left State' STATE_L VISIBLE NONE;'Right State' STATE_R VISIBLE NONE;'Left Street ID' '' VISIBLE NONE;
    'Right Street ID' '' VISIBLE NONE;'Min X value for extent' '' VISIBLE NONE;
    'Max X value for extent' '' VISIBLE NONE;'Min Y value for extent' '' VISIBLE NONE;
    'Max Y value for extent' '' VISIBLE NONE;'Left Additional Field' '' VISIBLE NONE;
    'Right Additional Field' '' VISIBLE NONE;'Altname JoinID' '' VISIBLE NONE"""

    userMessage("Creating address locator...")
    # Process: Create Address Locator
    CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table'", fieldMap, Locator, "")

    userMessage("Geocoding addresses...")
    #geocode table address
    GeocodeAddresses_geocoding(gc_table, Locator, "'Single Line Input' SingleLineInput VISIBLE NONE", output, "STATIC")

    userMessage("Completed geocoding. Results are in table " + output)


def checkLayerList(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    esb = pathsInfoObject.esbList # Not currently dynamic.
    
    userMessage("Checking geodatabase layers...")
    #get current layer list
    layerList = getCurrentLayerList(esb)
    layers = []
    for dirpath, dirnames, filenames in Walk(gdb, True, '', False, ["Table","FeatureClass"]):  # @UnusedVariable
        for filename in filenames:
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
        stuffList = line.split("|")
        #print stuffList
        domainDict[stuffList[0]] = stuffList[1].rstrip()

    return domainDict


def checkValuesAgainstDomain(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    folder = pathsInfoObject.domainsFolderPath
    
    userMessage("Checking field values against approved domains...")

    #get list of fields with domains
    fieldsWDoms = fieldsWithDomains()
    for dirpath, dirnames, filenames in Walk(gdb, True, '', False, ["Table","FeatureClass"]):  # @UnusedVariable
        for filename in filenames:
            fields = []
            fullPath = path.join(gdb, filename)
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

                    #loop through records for that particular field to see if all values match domain
                    wc = fieldN + " is not null"
                    with SearchCursor(fullPath, ("OBJECTID", fieldN), wc) as rows:
                        for row in rows:
                            if row[1] is not None:
                                #see if field domain is actually a range
                                if fieldN == "HNO":
                                    hno = row[1]
                                    if hno > 999999 or hno < 0:
                                        userMessage( filename + ": " + str(row[0]) + " value " + str(row[1]) + " not in approved domain for field " + fieldN)
                                    #otherwise, compare row value to domain list
                                    else:
                                        if row[1].upper() not in domainList:
                                            userMessage( filename + ": " + str(row[0]) + " value " + str(row[1]) + " not in approved domain for field " + fieldN)

    userMessage("Completed checking fields against domains")


def checkDomainExistence(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    folder = pathsInfoObject.domainsFolderPath
    
    #get current domain list
    domainList = getCurrentDomainList()
    domains = {}  # @UnusedVariable

    #list domains
    for domain in ListDomains(gdb):
        if domain.name not in domainList:
            userMessage( domain.name + " not in geodatabase domain template")
        else:
            #check domain type
            #for coded values: compare values to text files
            if domain.domainType == "CodedValue":
                cv = domain.codedValues
                #get keyword
                keyword = getDomainKeyword(domain.name)

                if keyword <> "":
                    #get the established domain values and definitions in a dictionary
                    cv_recorded = getFieldDomain(keyword, folder)
                    um = 0

                    #see if the domains match
                    if cv != cv_recorded:
                        for key in cv.iterkeys():
                            #check for upper/lower matches
                            if key.upper() not in cv_recorded and key.lower() not in cv_recorded:
                                um = 1
                                userMessage( key + " not in domain " + domain.name)

                    if um == 0:
                        userMessage( domain.name + ": domain values match")

            #for range: only address numbers have a range, so do the comparison directly
            elif domain.domainType == "Range":
                low = int(domain.range[0])
                high = int(domain.range[1])

                if low != 0:
                    userMessage( domain.name + " range low is not 0. It is " + str(low))

                if high != 999999:
                    userMessage( domain.name + " range high is not 999999. It is " + str(high))
                    ## print domains


def checkRequiredFieldValues(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    folder = pathsInfoObject.domainsFolderPath
    esb = pathsInfoObject.esbList

    userMessage("Checking that required fields have all values...")

    #get today's date
    today = strftime("%m/%d/%y")

    #get required fields
    rfDict = getRequiredFields(folder)

    ObjectXID = "OBJECTID"
    values = []

    #walk through the tables/feature classes
    for dirpath, dirnames, filenames in Walk(gdb, True, '', False, ["Table","FeatureClass"]):  # @UnusedVariable
        for filename in filenames:
            fullPath = path.join(gdb, filename)

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
                if ObjectXID not in matchingFields:
                    matchingFields.append(ObjectXID)

                i = len(matchingFields)  # @UnusedVariable
                k = 0

                #run a search cursor to get any/all records where a required field value is null
                with SearchCursor(fullPath, (matchingFields), wc) as rows:
                    for row in rows:
                        #get object ID of the field
                        oid = str(row[matchingFields.index(ObjectXID)])

                        #loop through row
                        while k < 0:
                            #see if the value is nothing
                            if row[k] is None:
                                #report the value if it is indeed null
                                report = matchingFields[k] + " is null for ObjectID " + oid
                                userMessage(report)
                                val = (today, report, filename, matchingFields[k], oid)
                                values.append(val)

                                #iterate!
                                k = k + 1
            else:
                userMessage( "All required values present for " + filename)

            Delete_management(lyr)

    if values != "":
        RecordResults("fieldValues", values, gdb)

    userMessage("Completed check for required field values")


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

    userMessage("Completed check for required fields")


def checkFeatureLocations(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    
    userMessage("Checking feature locations...")

    #get today's date
    today = strftime("%m/%d/%y")
    values = []

    #make sure features are all inside authoritative boundary

    #get authoritative boundary
    authBound = path.join(gdb, "NG911", "AuthoritativeBoundary")
    ab = "ab"

    MakeFeatureLayer_management(authBound, ab)

    for dirpath, dirnames, filenames in Walk(gdb, True, '', False, ["FeatureClass"]):  # @UnusedVariable
        for filename in filenames:
            if filename != "AuthoritativeBoundary":
                #get full path name & create a feature layer
                fullPath = path.join(gdb, filename)
                fl = "fl"
                MakeFeatureLayer_management(fullPath, fl)

                #select by location to get count of features outside the authoritative boundary
                SelectLayerByLocation_management(fl, "INTERSECT", ab)
                SelectLayerByAttribute_management(fl, "SWITCH_SELECTION", "")
                #get count of selected records
                result = GetCount_management(fl)
                count = int(result.getOutput(0))

                #report results
                if count > 0:
                    fields = ("OBJECTID")
                    with SearchCursor(fl, fields) as rows:
                        for row in rows:
                            val = (today, "Feature not inside authoritative boundary", filename, "", row[0])
                            values.append(val)
                else:
                    userMessage( filename + ": all records inside authoritative boundary")

                #clean up
                Delete_management(fl)

    userMessage("Completed check on feature locations")

    if values != []:
        RecordResults("fieldValues", values, gdb)


def main():
    try:
        from NG911_Config import currentPathSettings # currentPathSettings should have all the path information available. ## import esb, gdb, folder
    except:
        userMessage( "Copy config file into command line")

    #check geodatabase template
    checkLayerList(currentPathSettings)
    checkRequiredFields(currentPathSettings)
    checkRequiredFieldValues(currentPathSettings)

    #check values and locations
    checkValuesAgainstDomain(currentPathSettings)
    checkFeatureLocations(currentPathSettings)
    addy_pt = join(currentPathSettings.gdbPath, "AddressPoints")
    street = join(currentPathSettings.gdbPath, "RoadCenterline")
    geocodeAddressPoints(addy_pt, street)
    ###checkAddressPointFrequency(addy_pt, gdb) # Commented out because I didn't find the function definition.

    #checks we probably don't need to use
    ## checkDomainExistence(gdb, folder)

if __name__ == '__main__':
    main()
