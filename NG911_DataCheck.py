#-------------------------------------------------------------------------------
# Name:        NG911_DataCheck
# Purpose:     Collection of functions to check submitted NG911 data
#
# Author:      Kristen Jordan, Kansas Data Access and Support Center
#               kristen@kgs.ku.edu
#
# Created:     19/09/2014
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
    import arcpy, os

    gdb = os.path.dirname(addressPointPath)
    gc_table = os.path.join(gdb, "GeocodeTable")

    # Get the fields from the input
    fields= arcpy.ListFields(addressPointPath)

    # Create a fieldinfo object
    fieldinfo = arcpy.FieldInfo()

    # Iterate through the fields and set them to fieldinfo
    for field in fields:
        if field.name in ("LABEL", "ZIP"):
            fieldinfo.addField(field.name, field.name, "VISIBLE", "")
        else:
            fieldinfo.addField(field.name, field.name, "HIDDEN", "")

    # The created crime_view layer will have fields as set in fieldinfo object
    arcpy.MakeTableView_management(addressPointPath, "addy_view", "", "", fieldinfo)

    # To persist the layer on disk make a copy of the view
    arcpy.CopyRows_management("addy_view", gc_table)

    #add single line input field for geocoding
    arcpy.AddField_management(gc_table, "SingleLineInput", "TEXT", "", "", 250)

    #calculate field
    exp = '[LABEL] & " " & [ZIP]'
    arcpy.CalculateField_management(gc_table, "SingleLineInput", exp, "VB")

    #generate locator
    Locator = os.path.join(gdb, "Locator")
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
    arcpy.CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table'", fieldMap, Locator, "")

    #geocode table address

def checkLayerList(gdb):
    import arcpy
    #get current layer list
    layerList = getCurrentLayerList()

    layers = []

    for dirpath, dirnames, filenames in arcpy.da.Walk(gdb, True, '', False, ["Table","FeatureClass"]):
        for filename in filenames:
            if filename not in layerList:
                print filename + " not in geodatabase layer list template"
            else:
                layers.append(filename)

    print layers

def getKeyword(layer, esb):
    if layer in ("AuthoritativeBoundary", "CountyBoundary", "MunicipalBoundary"):
        keyword = "Boundaries"
    elif layer in esb:
        keyword = "EmergencyBoundary"
    else:
        keyword = layer

    return keyword

def getRequiredFields(folder):
    import os

    path = os.path.join(folder, "NG911_RequiredFields.txt")
    fieldDefDoc = open(path, "r")

    #get the header information
    headerLine = fieldDefDoc.readline()
    valueList = headerLine.split("|")
##    print valueList

    #get field indexes
    fcIndex = valueList.index("FeatureClass")
    fieldIndex = valueList.index("Field\n")

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

def getFieldDomain(keyword):
    import os

    folder = r"E:\Kristen\Data\NG911\Domains"

    docPath = os.path.join(folder, keyword + "_Domains.txt")
##    print docPath

    doc = open(docPath, "r")

    headerLine = doc.readline()
    valueList = headerLine.split("|")

    valueIndex = valueList.index("Values")
    defIndex = valueList.index("Definition\n")

    domainDict = {}

    #parse the text to population the field definition dictionary
    for line in doc.readlines():
        stuffList = line.split("|")
        #print stuffList
        domainDict[stuffList[0]] = stuffList[1].rstrip()

    return domainDict

def checkDomainExistence(gdb):
    import arcpy
    #get current domain list
    domainList = getCurrentDomainList()

    domains = {}

    #list domains
    for domain in arcpy.da.ListDomains(gdb):
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
                    cv_recorded = getFieldDomain(keyword)
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

def checkRequiredFields(gdb, folder, esb):
    import arcpy, os
    #get required fields
    rfDict = getRequiredFields(folder)

    #walk through the tables/feature classes
    for dirpath, dirnames, filenames in arcpy.da.Walk(gdb, True, '', False, ["Table","FeatureClass"]):
        for filename in filenames:
            fields = []
            fullPath = os.path.join(gdb, filename)

            #list fields
            fs = arcpy.ListFields(fullPath)
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
                            with arcpy.da.SearchCursor(fullPath, fieldList) as rows:
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
    import arcpy, os
    #make sure feature are all inside authoritative boundary

    #get authoritative boundary
    authBound = os.path.join(gdb, "NG911", "AuthoritativeBoundary")
    ab = "ab"

    arcpy.MakeFeatureLayer_management(authBound, ab)

    for dirpath, dirnames, filenames in arcpy.da.Walk(gdb, True, '', False, ["FeatureClass"]):
        for filename in filenames:
            if filename != "AuthoritativeBoundary":
                #get full path name & create a feature layer
                fullPath = os.path.join(gdb, filename)
                fl = "fl"
                arcpy.MakeFeatureLayer_management(fullPath, fl)

                #select by location to get count of features outside the authoritative boundary
                arcpy.SelectLayerByLocation_management(fl, "INTERSECT", ab)
                arcpy.SelectLayerByAttribute_management(fl, "SWITCH_SELECTION", "")
                #get count of selected records
                result = arcpy.GetCount_management(fl)
                count = int(result.getOutput(0))

                #report results
                if count > 0:
                    print filename + ": " + str(count) + " records not inside authoritative boundary"
                else:
                    print filename + ": all records inside authoritative boundary"

                #clean up
                arcpy.Delete_management(fl)


def main():
    try:
        from NG911_Config import esb, gdb, folder
    except:
        print "Copy config file into command line"

##    checkFeatureLocations(gdb)
##    checkLayerList(gdb)
##    checkDomainExistence(gdb)

    checkRequiredFields(gdb, folder, esb)

if __name__ == '__main__':
    main()
