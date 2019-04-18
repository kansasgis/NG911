#-------------------------------------------------------------------------------
# Name:        NG911_Metadata_Fix_201408
# Purpose:     Update NG911 metadata to include field descriptions
#
# Author:      kristen
#
# Created:     20/08/2014
# Copyright:   (c) kristen 2014
#-------------------------------------------------------------------------------

def getDefinitionSource():
    defSource = "Kansas NG9-1-1 GIS Data Model"
    return defSource

def getFC_definition(FC, esb):
    #feature class definitions from the NG911 geodatabase model document
    defFc = ""

    #set feature class definition
    if FC == "AddressPoints":
        defFc = "Address points represent all structures and designated locations with an assigned street address."
    elif FC == "AuthoritativeBoundary":
        defFc = "Authoritative Boundaries are polygons representing the boundaries for which the data layers are authoritative."
    elif FC == "CountyBoundary":
        defFc = "County boundaries are polygons representing authoritative boundaries"
    elif FC in esb:
        defFc = "Emergency Service Boundaries are polygons representing the service area of the PSAP and various emergency service providers."
    elif FC == "ESZ":
        defFc = "Emergency Service Zone (ESZ) Boundaries are polygons representing a unique combination of emergency service agencies (Law Enforcement, Fire and Emergency Medical Services) designated to serve a specific range of addresses."
    elif FC == "MunicipalBoundary":
        defFc = "County boundaries are polygons representing authoritative boundaries"
    elif FC == "PSAP":
        defFc = "PSAP boundaries are polygons representing authoritative boundaries"
    elif FC == "RoadCenterline":
        defFc = "Road centerlines represent all public and addressed private streets."
    elif FC == "RoadAlias":
        defFc = "The Road Alias table holds additional names for roads, including highway designators, old names that are still in use colloquially or county road numbers that are known as alias names."

    return defFc

def fieldsWithDomains(version):
    #list of all the fields that have a domain
    fieldList = ["LOCTYPE", "STATUS", "SURFACE", "STEWARD", "AGENCYID","PLC", "RDCLASS", "PARITY", "ONEWAY", "MUNI", "COUNTY", "COUNTRY","PRD", "ZIP", "POSTCO", "STATE", "STS", "EXCEPTTION", "SUBMIT"]

    if version == "10":
        fieldList.remove("EXCEPTION")
        fieldList.remove("SUBMIT")

    return fieldList

def getDomainSource(domain):
    #domain source was obtained from info from Sherry Massey
    domSource = ""

    ks911List = ("LOCTYPE", "STATUS", "SURFACE", "STEWARD", "AGENCYID")
    NENAList = ("PLC", "RDCLASS", "PARITY", "ONEWAY", "MUNI", "COUNTY", "COUNTRY")
    NENAUSPSlist = ("PRD", "ZIP", "POSTCO", "STATE", "STS")

    #set domain source:
    if domain in ks911List:
        domSource = "Kansas NG9-1-1 GIS Data Model"
        if domain == "STEWARD":
            domSource = domSource + ": INCITS/GNIS ID for PSAP Authority"
        elif domain == "AGENCYID":
            domSource = domSource + ": KS 911 CC - LCPA"
    elif domain in NENAList:
        domSource = "NENA"
        if domain == "COUNTRY":
            domSource = domSource + ": ISO 3166-1"
        elif domain == "COUNTY":
            domSource = domSource + ": ANSI INCITS 31:2009.  Includes all counties in KS and counties in neighboring states that on the KS border"
        elif domain == "MUNI":
            domSource = domSource + ": KS State Library List of Incorporated Places in KS.  'Unincorporated' added by NENA"
        elif domain == "RDCLASS":
            domSource = domSource + ": S series in MAF/TIGER Feature Classifcation Codes (MTFCC) Attachment D"
        elif domain == "PLC":
            domSource = domSource + ": Relevant values from RFC 4589"
    elif domain in NENAUSPSlist:
        domSource = "NENA: USPS"
        if domain in ("PRD", "STATE","STS"):
            domSource = domSource + ": Pub. 28"

    return domSource


def listmetadatafiles(folder):
    from os import listdir
    mList = []
    list = listdir(folder)
    for names in list:
        if names.endswith(".xml"):
            mList.append(names)
    return mList

def cleanUp(gdb):
    from os.path import join, dirname
    from os import listdir, remove

    folder = dirname(gdb)
    list = listdir(folder)
    for names in list:
        if names.endswith(".log"):
            if "_export" in names:
                path = join(folder, names)
                remove(path)

def getKeyword(layer, esb):
    if layer in esb:
        keyword = "EmergencyBoundary"
    else:
        keyword = layer

    return keyword

def getFieldDomain(field, folder):
    from os.path import join

    docPath = join(folder, field + "_Domains.txt")
##    print docPath

    doc = open(docPath, "r")

    domainDict = {}

    #parse the text to population the field definition dictionary
    for line in doc.readlines():
        stuffList = line.split("|")
        #print stuffList
        domainDict[stuffList[0]] = stuffList[1].rstrip()

    return domainDict

def parseFieldDefs(keyword, folder):
    from os.path import join

    path = join(folder, "NG911_FieldDefinitions.txt")
    fieldDefDoc = open(path, "r")

    #create a field definition dictionary
    defDict = {}

    #parse the text to population the field definition dictionary
    for line in fieldDefDoc.readlines():
        stuffList = line.split("|")

        #limit to specific feature class keyword fields
        if stuffList[0] == keyword:
            defDict[stuffList[1]] = stuffList[2].rstrip()

    return defDict

def editXMLInfo(metadataPath, newNode, aboveNode, value):
    import xml.etree.ElementTree as ET

    #get xml file set up
    xml1 = ET.ElementTree()
    xml1.parse(metadataPath)
    root = xml1.getroot()

    #see if the node already exists
    k = root.getiterator(newNode)
    #if not, it needs to be added
    if len(k) == 0:
        r = root.getiterator(aboveNode)[0]
        a = ET.SubElement(r, newNode)
        a.text = value
        xml1.write(metadataPath)

def editFieldInfo(metadataPath, newNode, fieldName, value):
    import xml.etree.ElementTree as ET

    #get xml file set up
    xml1 = ET.ElementTree()
    xml1.parse(metadataPath)
    root = xml1.getroot()

    attrlabl_all = root.getiterator("attrlabl")
    for attrlabl in attrlabl_all:
        if attrlabl.text.upper() == fieldName:
            #navigate to the correct attribute based on the field index
            index = attrlabl_all.index(attrlabl)
            attr = root.getiterator("attr")[index]

            #get list of existing children
            children = attr.getchildren()
            children_list = []
            for child in children:
                children_list.append(child.tag)
            #see if node is already in there
            if newNode not in children_list:
                #if the node doesn't exist, add it with the right info
                attr_newNode = ET.SubElement(attr, newNode)
                attr_newNode.text = value
                xml1.write(metadataPath)

def editDomain(metadataPath, fieldName, fldDomSource, fldDomainDict):
    import xml.etree.ElementTree as ET

    #get xml file set up
    xml1 = ET.ElementTree()
    xml1.parse(metadataPath)
    root = xml1.getroot()

    attrlabl_all = root.getiterator("attrlabl")
    for attrlabl in attrlabl_all:
        if attrlabl.text.upper() == fieldName:
            index = attrlabl_all.index(attrlabl)
            attr = root.getiterator("attr")[index]

            children = attr.getchildren()
            children_list = []
            for child in children:
                children_list.append(child.tag)
            if "attrdomv" not in children_list:
                #add attribute domain header
                attr_newNode = ET.SubElement(attr, "attrdomv")
                for domv, domd in fldDomainDict.iteritems():
                    #add domain
                    edom = ET.SubElement(attr_newNode, "edom")
                    #add domain value
                    edomv = ET.SubElement(edom, "edomv")
                    edomv.text = domv
                    #add domain definition
                    edomvd = ET.SubElement(edom, "edomvd")
                    edomvd.text = domd
                    #add domain definition source
                    edomvds = ET.SubElement(edom, "edomvds")
                    edomvds.text = fldDomSource
                xml1.write(metadataPath)

def updateMetadata(layer, pathList, folder, esb, template10):
    from arcpy import ImportMetadata_conversion, AddMessage, ListFields
    from os import remove

    #get paths
    metadataPath = pathList[1]
    gdbPath = pathList[0]

    version = "11"
    if template10 == "true":
        version = "10"

    #for layer name, get FC_definition & definition source
    fcDef = getFC_definition(layer, esb)
    #write feature class definition
    editXMLInfo(metadataPath, "enttypd", "enttyp", fcDef)

    #get general definition source
    defSource = getDefinitionSource()
    #write definition source
    editXMLInfo(metadataPath, "enttypds", "enttyp", defSource)

    #get keyword (in case it's a general layer name for boundaries or such)
    keyword = getKeyword(layer, esb)

    #get field definitions based on the keyword
    fieldDefDict = parseFieldDefs(keyword, folder)

    #create complete field list
    fields = ListFields(gdbPath)
    fieldNames = []
    for field in fields:
        fieldNames.append((field.name).upper())

    #get list of fields with domains
    fieldsWDoms = fieldsWithDomains(version)

    #see if fields from complete list have domains
    for fieldName in fieldNames:

        if "_" in fieldName:
            fieldN = fieldName.split("_")[0]
        else:
            fieldN = fieldName

        #get field definition
        if fieldN in fieldDefDict:
            fieldDef = fieldDefDict[fieldN]

            #add field definition and definition source
            editFieldInfo(metadataPath, "attrdef", fieldN, fieldDef)
            editFieldInfo(metadataPath, "attrdefs", fieldN, defSource)

            if fieldN in fieldsWDoms:
                #get domain definition
                fldDomSource = getDomainSource(fieldN)
                #get domain from txt file
                fldDomainDict = getFieldDomain(fieldN, folder)

                #edit domain
                editDomain(metadataPath, fieldN, fldDomSource, fldDomainDict)

    #import metadata back to layer
    ImportMetadata_conversion (metadataPath, "FROM_FGDC", gdbPath, "DISABLED")

    AddMessage("Metadata successfully updated for " + layer)

    #delete metadata file
    remove(metadataPath)

def main(gdb, domainFolder, ESBlist, version):
    from os.path import dirname, join
    from arcpy import GetInstallInfo, env, ExportMetadataMultiple_conversion
    from arcpy.da import Walk

    workingF = dirname(gdb)
    dir = GetInstallInfo("desktop")["InstallDir"]
    translator = dir + "Metadata/Translator/ARCGIS2FGDC.xml"

    #loop through geodatabase to get each layer
    env.workspace = gdb
    fcs = [] #feature class and table paths
    esb = []

    for dirpath, dirnames, filenames in Walk(gdb, True, '', False, ["Table","FeatureClass"]):
        for filename in filenames:
            fc_path = join(dirpath,filename)
            fcs.append(fc_path)
            if fc_path in ESBlist:
                esb.append(filename)

##    arcpy.AddMessage(esb)

    fcString = ";".join(fcs)

    #export metadata layer
    ExportMetadataMultiple_conversion(fcString, translator, workingF)

    #get list of metadata files
    metadatas = listmetadatafiles(workingF)

    #create dictionary of layer names and full gdb paths
    mDict = {}
    for metadata in metadatas:
        #get complete path names
        fullPath = join(workingF, metadata)

        #and get the little name
        layerName = metadata.split("_export")[0]

        #loop through fields
        for fc in fcs:
            if layerName in fc:
                mDict[layerName] = (fc, fullPath)

    #loop through metadata dictionary
    for key, list1 in mDict.iteritems():
        print(key)
        updateMetadata(key, list1, domainFolder, esb, version)

    #clean up log files
    cleanUp(gdb)

if __name__ == '__main__':
    from arcpy import GetParameterAsText
    gdb = GetParameterAsText(0)
    domainFolder = GetParameterAsText(1)
    ESBlist = GetParameterAsText(2)
    template10 = GetParameterAsText(3)

##    gdb = r"E:\Kristen\Data\NG911\RSDigital_SF_NG911_psap.gdb"
    main(gdb, domainFolder, ESBlist, template10)
