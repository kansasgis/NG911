#-------------------------------------------------------------------------------
# Name:        NG911_DataCheck
# Purpose:     Collection of functions to check submitted NG911 data
#
# Author:      Kristen Jordan, Kansas Data Access and Support Center
#               kristen@kgs.ku.edu
#
# Created:     19/09/2014
# Modified:    25/09/2014 by dirktall04
#-------------------------------------------------------------------------------

def getCurrentLayerList():
    layerList = ["RoadAlias", "AddressPoints", "RoadCenterline", "AuthoritativeBoundary", "CountyBoundary", "ESZ", "PSAP", "MunicipalBoundary", "EMS", "FIRE", "LAW"]

    #future code: have each county's geodatabase model identified with ESB layers
    #get the layer list from their standard geodatabase

    return layerList

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

def GeocodeAddressPoints(addressPointPath, streetPath):
    from os import path
    from arcpy import ListFields, FieldInfo, MakeTableView_management, CopyRows_management, AddField_management, CalculateField_management, CreateAddressLocator_geocoding

    gdb = path.dirname(addressPointPath)
    gc_table = path.join(gdb, "GeocodeTable")

    # Get the fields from the input
    fields= ListFields(addressPointPath)

    # Create a fieldinfo object
    fieldinfo = FieldInfo()

    # Iterate through the fields and set them to fieldinfo
    for field in fields:
        if field.name in ("LABEL", "ZIP"):
            fieldinfo.addField(field.name, field.name, "VISIBLE", "")
        else:
            fieldinfo.addField(field.name, field.name, "HIDDEN", "")

    # The created crime_view layer will have fields as set in fieldinfo object
    MakeTableView_management(addressPointPath, "addy_view", "", "", fieldinfo)

    # To persist the layer on disk make a copy of the view
    CopyRows_management("addy_view", gc_table)

    #add single line input field for geocoding
    AddField_management(gc_table, "SingleLineInput", "TEXT", "", "", 250)

    #calculate field
    exp = '[LABEL] & " " & [ZIP]'
    CalculateField_management(gc_table, "SingleLineInput", exp, "VB")

    #generate locator
    Locator = path.join(gdb, "Locator")
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

    # Process: Create Address Locator
    CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table'", fieldMap, Locator, "")

    #geocode table address

def checkLayerList(gdb):
    from arcpy.da import Walk
    #get current layer list
    layerList = getCurrentLayerList()

    layers = []

    for dirpath, dirnames, filenames in arcpy.da.Walk(gdb, True, '', False, ["Table","FeatureClass"]):  # @UnusedVariable @UndefinedVariable
        for filename in filenames:
            if filename not in layerList:
                print filename + " not in geodatabase layer list template"
            else:
                layers.append(filename)

    print layers

def getKeyword(layer, esb):
    if layer in esb:
        keyword = "EmergencyBoundary"
    else:
        keyword = layer

    return keyword

def getRequiredFields(folder):
    from os import path

    path1 = path.join(folder, "NG911_RequiredFields.txt")
    fieldDefDoc = open(path1, "r")

    #get the header information
    headerLine = fieldDefDoc.readline()
    valueList = headerLine.split("|")
##    print valueList

    #get field indexes
    fcIndex = valueList.index("FeatureClass")  # @UnusedVariable
    fieldIndex = valueList.index("Field\n")  # @UnusedVariable

    #create a field definition dictionary
    rfDict = {}

    #parse the text to population the field definition dictionary
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
    from os import path

    docPath = path.join(folder, field + "_Domains.txt")
##    print docPath

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

def checkValuesAgainstDomain(gdb, folder):
    from arcpy import ListFields
    from arcpy.da import Walk, SearchCursor
    from os import path

    #get list of fields with domains
    fieldsWDoms = fieldsWithDomains()

    for dirpath, dirnames, filenames in Walk(gdb, True, '', False, ["Table","FeatureClass"]):
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
                                        print filename + ": " + str(row[0]) + " value " + str(row[1]) + " not in approved domain for field " + fieldN
                                #otherwise, compare row value to domain list
                                else:
                                    if row[1].upper() not in domainList:
                                        print filename + ": " + str(row[0]) + " value " + str(row[1]) + " not in approved domain for field " + fieldN

def checkDomainExistence(gdb, folder):
    from arcpy.da import ListDomains

    #get current domain list
    domainList = getCurrentDomainList()

    domains = {}  # @UnusedVariable

    #list domains
    for domain in arcpy.da.ListDomains(gdb):  # @UndefinedVariable
        if domain.name not in domainList:
            print domain.name + " not in geodatabase domain template"
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
                                print key + " not in domain " + domain.name

                    if um == 0:
                        print domain.name + ": domain values match"

            #for range: only address numbers have a range, so do the comparison directly
            elif domain.domainType == "Range":
                low = int(domain.range[0])
                high = int(domain.range[1])
                if low != 0:
                    print domain.name + " range low is not 0. It is " + str(low)
                if high != 999999:
                    print domain.name + " range high is not 999999. It is " + str(high)

##    print domains
def checkRequiredFieldValues(gdb, folder, esb):
    from os import path
    from arcpy.da import Walk, SearchCursor
    from arcpy import MakeTableView_management, Delete_management, GetCount_management, ListFields

    #get required fields
    rfDict = getRequiredFields(folder)

    id = "OBJECTID"

    #walk through the tables/feature classes
    for dirpath, dirnames, filenames in Walk(gdb, True, '', False, ["Table","FeatureClass"]):
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
            print wc

            #make table view using where clause
            lyr = "lyr"
            MakeTableView_management(fullPath, lyr, wc)

            #get count of the results
            result = GetCount_management(lyr)
            count = int(result.getOutput(0))

            #if count is greater than 0, it means a required value somewhere isn't filled in
            if count > 0:
                #make sure the objectID gets included in the search for reporting
                if id not in matchingFields:
                    matchingFields.append(id)

                i = len(matchingFields)
                k = 0

                #run a search cursor to get any/all records where a required field value is null
                with SearchCursor(fullPath, (matchingFields), wc) as rows:
                    for row in rows:

                        #get object ID of the field
                        oid = row[matchingFields.index(id)]

                        #loop through row
                        while k < 0:
                            #see if the value is nothing
                            if row[k] is None:
                                #report the value if it is indeed null
                                print matchingFields[k] + " is null for ObjectID " + str(oid)

                            #iterate!
                            k = k + 1
            else:
                print "All required values present for " + filename

            Delete_management(lyr)

def checkRequiredFields(gdb, folder, esb):
    from os import path
    from arcpy import ListFields
    from arcpy.da import Walk

    #get required fields
    rfDict = getRequiredFields(folder)

    #walk through the tables/feature classes
    for dirpath, dirnames, filenames in arcpy.da.Walk(gdb, True, '', False, ["Table","FeatureClass"]):  # @UnusedVariable @UndefinedVariable
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
##                print comparisonList

                #loop through required fields to make sure they exist in the geodatabase
                for comparisonField in comparisonList:
                    if comparisonField.upper() not in fields:
                        print filename + " does not have required field " + comparisonField
                    else:
                        try:
                            fieldList = (comparisonField)
                            i = 0
                            #make sure field is populated with values
                            with arcpy.da.SearchCursor(fullPath, fieldList) as rows:  # @UndefinedVariable
                                for row in rows:
                                    if row[0] in (None, "", " "):
                                        i = 1
                        except:
                            print "Error checking " + filename + "; " + comparisonField

                        if i == 0:
                            print "Required field values all present for " + filename + "; " + comparisonField
                        else:
                            print filename + "; " + comparisonField + " needs some required values filled"

def checkFeatureLocations(gdb):
    from os import path
    from arcpy import MakeFeatureLayer_management, SelectLayerByAttribute_management, SelectLayerByLocation_management, GetCount_management, Delete_management, da
    #make sure feature are all inside authoritative boundary

    #get authoritative boundary
    authBound = path.join(gdb, "NG911", "AuthoritativeBoundary")
    ab = "ab"

    MakeFeatureLayer_management(authBound, ab)

    for dirpath, dirnames, filenames in arcpy.da.Walk(gdb, True, '', False, ["FeatureClass"]):  # @UnusedVariable @UndefinedVariable
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
                    print filename + ": " + str(count) + " records not inside authoritative boundary"
                else:
                    print filename + ": all records inside authoritative boundary"

                #clean up
                Delete_management(fl)


def main():
    try:
        from NG911_Config import esb, gdb, folder
    except:
        print "Copy config file into command line"

    #check geodatabase template
##    checkLayerList(gdb)
    checkRequiredFieldValues(gdb, folder, esb)

    #check values and locations
##    checkRequiredFields(gdb, folder, esb)
##    checkValuesAgainstDomain(gdb, folder)
##    checkFeatureLocations(gdb)

    #checks we probably don't need to use
##    checkDomainExistence(gdb, folder)

if __name__ == '__main__':
    main()
