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

from arcpy import (AddField_management, AddMessage, CalculateField_management, CopyRows_management, Statistics_analysis,
                   CreateTable_management, Delete_management, Exists, GetCount_management, FieldInfo,
                   ListFields, MakeFeatureLayer_management, MakeTableView_management, SelectLayerByAttribute_management,
                   SelectLayerByLocation_management, DeleteRows_management, GetInstallInfo, env, ListDatasets,
                   AddJoin_management, RemoveJoin_management, AddWarning)
from arcpy.da import Walk, InsertCursor, ListDomains, SearchCursor
from os import path
from os.path import basename, dirname, join, exists
from time import strftime
from Validation_ClearOldResults import ClearOldResults
import NG911_GDB_Objects
from NG911_arcpy_shortcuts import deleteExisting, getFastCount, cleanUp, ListFieldNames, fieldExists

def checkToolboxVersion():
    import json, urllib, sys
    from inspect import getsourcefile
    from os.path import abspath, dirname, join, exists
    from arcpy import AddMessage

    v = sys.version_info.major
    if v != 2:
        if exists(r"C:\Program Files\ArcGIS\Pro\bin\Python\Lib\urllib"):
            sys.path.append(r"C:\Program Files\ArcGIS\Pro\bin\Python\Lib\urllib")
            import request

#   set lots of variables
    message, toolData, toolVersion, response, mostRecentVersion = "", "", "0", "", "X"

#    get version in the .json file that is already present
    me_folder = dirname(abspath(getsourcefile(lambda:0)))
    jsonFile = join(me_folder, "ToolboxVersion.json")

#   make sure the local json file exists
    if exists(jsonFile):
        toolData = json.loads(open(jsonFile).read())
        toolVersion = toolData["toolboxVersion"]["version"]
        AddMessage(toolVersion)

#   get version of toolbox live online
    url = "https://raw.githubusercontent.com/kansasgis/NG911/master/Scripts/ToolboxVersion.json"

#   Error trapping in case the computer is offline or can't get to the internet
    try:

        try:
            response = request.urlopen(url).read()
            mostRecentData = json.loads(response.decode('utf-8'))
        except:
            response = urllib.urlopen(url)
            mostRecentData = json.loads(response.read())

        mostRecentVersion = mostRecentData["toolboxVersion"]["version"]
        AddMessage(mostRecentVersion)
    except:
        message = "Unable to check toolbox version at this time."

#    compare the two
    if toolVersion == mostRecentVersion:
        message = "Your NG911 toolbox version is up-to-date."
    else:
        if mostRecentVersion != "X":
            message = """Your version of the NG911 toolbox is not the most recent version available.
            Your results might be different than results received upon data submission. Please
            download an up-to-date copy of the toolbox at
            https://github.com/kansasgis/NG911/raw/master/KansasNG911GISTools.zip"""

#   report back to the user
    return message


##def getLayerList():
##    layerList = ["RoadAlias", "AddressPoints", "RoadCenterline", "AuthoritativeBoundary", "CountyBoundary", "ESZ", "MunicipalBoundary"]
##    return layerList
##
##
##def getCurrentLayerList(esb):
##    layerList = getLayerList()
##    for e in esb:
##        layerList.append(e)
##    return layerList


def userMessage(msg):
    #print stuff
    try:
        print(msg)
        AddMessage(msg)
    except:
        pass

def getCurrentDomainList():
    domainList = ["AddressNumbers", "AddressParity", "AgencyID", "Counties", "Country",
                    "ESBType", "Municipality", "OneWay", "PlaceType", "PointLocation", "PostalCodes",
                    "PostalCommunities", "RoadClass", "RoadDirectionals", "RoadModifier", "RoadStatus",
                    "RoadSurface", "RoadTypes", "States", "Stewards", "Exception", "Submit"]
    #or get domain list from approved source

    return domainList


def fieldsWithDomains(layer):

    obj = NG911_GDB_Objects.getFCObject(layer)
    fieldList = obj.FIELDS_WITH_DOMAINS
##    userMessage(fieldList)
    return fieldList

def getUniqueIDField(layer):
##    userMessage(layer)
    obj = NG911_GDB_Objects.getFCObject(layer)
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
    obj = NG911_GDB_Objects.getFCObject(table)
    lyr = basename(table)
    #field info
    if lyr == "TemplateCheckResults":
        fieldInfo = [(table, obj.DATEFLAGGED, "DATE", "", "", ""),(table, obj.DESCRIPTION, "TEXT", "", "", 250),(table, obj.CATEGORY, "TEXT", "", "", 25)]
    elif lyr == "FieldValuesCheckResults":
        fieldInfo = [(table, obj.DATEFLAGGED, "DATE", "", "", ""),(table, obj.DESCRIPTION, "TEXT", "", "", 250),
            (table, obj.LAYER, "TEXT", "", "", 25),(table, obj.FIELD, "TEXT", "", "", 25),(table, obj.FEATUREID, "TEXT", "", "", 38)]
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

def checkDirectionality(fc,gdb):
    userMessage("Checking road directionality...")
    rc_obj = NG911_GDB_Objects.getFCObject(fc)

    if Exists(fc):
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

    else:
        AddWarning(fc + " does not exist")

    #report records
    if values != []:
        RecordResults(recordType, values, gdb)
        userMessage("Completed road directionality check. There were " + str(len(values)) + " issues.")
    else:
        userMessage("Completed road directionality check. No issues found.")

def checkESNandMuniAttribute(currentPathSettings):

    gdb = currentPathSettings.gdbPath
    esz = currentPathSettings.gdbObject.ESZ
    address_points = currentPathSettings.gdbObject.AddressPoints
    muni = currentPathSettings.gdbObject.MunicipalBoundary

    esz_obj = currentPathSettings.esz_obj
    mb_obj = currentPathSettings.mb_obj
    a_obj = currentPathSettings.a_obj

    values = []
    recordType = "fieldValues"
    today = strftime("%m/%d/%y")
    filename = "AddressPoints"

    try:

        if Exists(address_points):

            addy_lyr = "addy_lyr"
            MakeFeatureLayer_management(address_points, addy_lyr)

            searchDict = {esz: (esz_obj.ESN, esz_obj.UNIQUEID), muni: (mb_obj.MUNI, mb_obj.UNIQUEID)}

            for layer in searchDict.keys():
                fieldList = searchDict[layer]
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
                                        report = "Notice: Address point " + feature + " does not match " + feature + " in " + basename(layer) + " layer. FeatureID is ObjectID"
                                        val = (today, report, filename, feature, str(objectID))
                                        values.append(val)

                            Delete_management(lyr1)
                            del lyr1

                    try:
                        del poly, polys
                    except:
                        userMessage("Poly/polys didn't exist in the Muni/ESN check. No worries.")
            Delete_management(addy_lyr)

        else:
            AddWarning(address_points + " does not exist")

    except Exception as e:
        report = "Notice: ESN/Municipality check did not run. " + str(e)
        val = (today, report, filename, "", "")
        values.append(val)

    #report records
    if values != []:
        RecordResults(recordType, values, gdb)
        userMessage("Address point ESN/Municipality check complete. " + str(len(values)) + " issues found. Results are in the FieldValuesCheckResults table.")
    else:
        userMessage("Address point ESN/Municipality check complete. No issues found.")


def checkUniqueIDFrequency(currentPathSettings):
    gdb = currentPathSettings.gdbPath
    esbList = currentPathSettings.gdbObject.esbList
    fcList = currentPathSettings.gdbObject.fcList
    esb_obj = currentPathSettings.esb_obj

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
                    typeEsb = basename(esb)
                    cursor = InsertCursor(table, (esb_obj.UNIQUEID, 'ESB_LYR'))
                    cursor.insertRow((row[0], typeEsb))

        try:
            #clean up
            del rows, row, cursor
        except:
            userMessage("objects cannot be deleted, they don't exist")


    for fc in fcList:
        if Exists(fc):
            fc = basename(fc)
            layerList.append(fc)
        else:
            AddWarning(fc + " does not exist")
            today = strftime("%m/%d/%y")
            values = [(today, fc + " does not exist")]
            RecordResults("DASCmessage", values, gdb)

    #loop through layers in the gdb that aren't esb & ESB_IDS
    values = []
    recordType = "fieldValues"
    today = strftime("%m/%d/%y")

    for layer in layerList:
        uniqueID = getUniqueIDField(layer)
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
                        wc2 = esb_obj.UNIQUEID + " = '" + str(row2[0]) + "'"
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

    obj = NG911_GDB_Objects.getFCObject(fc)

    if Exists(fc):
        fl = "fl"
        fl1 = "fl1"
        wc = "FREQUENCY > 1"

        #remove the frequency table if it exists already
        try:
            deleteExisting(freq)
        except:
            userMessage("Please manually delete " + freq + " and then run the frequency check again")

        if not Exists(freq):
                #see if we're working with address points or roads, create a where clause
                filename = basename(fc)

                if basename(freq) == "AP_Freq":
                    wc1 = obj.HNO + " <> 0 and " + obj.LOCTYPE + " = 'PRIMARY'"
                elif basename(freq) == "Road_Freq":
                    wc1 = obj.L_F_ADD + " <> 0 AND " + obj.L_T_ADD + " <> 0 AND " + obj.R_F_ADD + " <> 0 AND " + obj.R_T_ADD + " <> 0"

                if fieldExists(fc, "SUBMIT"):
                    wc1 = wc1 + " AND SUBMIT not in ('N')"

                #run query on fc to make sure 0's are ignored
                MakeTableView_management(fc, fl1, wc1)

                #set up field strings for statistics tool
                fields = fields.replace(";;", ";")
                fieldCountList = fields.replace(";", " COUNT;") + " COUNT"

                #split field names
                fieldsList = fields.split(";")
                fl_fields = []
                for f in fieldsList:
                    f = f.strip()
                    fl_fields.append(f)

                #set up parameters to report duplicate records
                values = []
                recordType = "fieldValues"
                today = strftime("%m/%d/%y")

                #run frequency analysis
                try:
                    Statistics_analysis(fl1, freq, fieldCountList, fields)

                    #make feature layer
                    MakeTableView_management(freq, fl, wc)

                    #get count of the results
                    if getFastCount(fl) > 0:


                        #get field count
                        fCount = len(fl_fields)

                        #get the unique ID field name
                        id1 = obj.UNIQUEID

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

                                        #add information to FieldValuesCheckResults for all duplicates
                                        report = "Error: " + str(fID) + " has duplicate field information"
                                        val = (today, report, filename, "", fID)
                                        values.append(val)

                    else:
                        userMessage("Checked frequency. All records are unique.")

                except Exception as e:
                    userMessage(str(e))
                    report = "Error: Could not complete duplicate record check. " + str(e)
                    val = (today, report, filename, "", "")
                    values.append(val)

                #report duplicate records
                if values != []:
                    RecordResults(recordType, values, gdb)
                    userMessage("Checked frequency. Results are in table FieldValuesCheckResults")

                #clean up
                try:
                    cleanUp([fl, fl1, freq])
                except:
                    userMessage("Issue deleting a feature layer or frequency table.")

    else:
        AddWarning(fc + " does not exist")


def checkLayerList(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    esb = pathsInfoObject.gdbObject.esbList

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
    #get current required layer list
    layerList = pathsInfoObject.gdbObject.requiredLayers

    for l in layerList:
        if not Exists(l):
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
            if fc in rfDict.keys():
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
    fcList = pathsInfoObject.gdbObject.fcList
    esb = pathsInfoObject.gdbObject.esbList
    rc_obj = pathsInfoObject.rc_obj

    userMessage("Checking field values against approved domains...")
    #set up parameters to report duplicate records
    values = []
    resultType = "fieldValues"
    today = strftime("%m/%d/%y")
    filename = ""

    #set environment
    env.workspace = gdb

    for fullPath in fcList:
        if Exists(fullPath):
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
##                    k = getFastCount(fullPathlyr)
##                    userMessage("Record count: " + str(k))
                except:
                    userMessage("Cannot check required field values for " + layer)

            if worked == 1:

                #get list of fields with domains
                fieldsWDoms = fieldsWithDomains(fullPath)

        ##        #remove "STATUS" field if we aren't working with road centerline- edit suggested by Sherry M., 6/16/2015
        ##        if layer != "ROADCENTERLINE":
        ##            if "STATUS" in fieldsWDoms:
        ##                fieldsWDoms.remove("STATUS")

                id1 = getUniqueIDField(fullPath)
                if id1 != "":
                    #create complete field list
                    fieldNames = ListFieldNames(fullPath)

                    #see if fields from complete list have domains
                    for fieldN in fieldNames:

                        #userMessage(fieldN)
                        #if field has a domain
                        if fieldN in fieldsWDoms:
                            domain = ""
                            if fieldN[0:2] == "A_":
                                domain = fieldN[2:]

                            elif fieldN in ['GATE_TYPE','SIREN','RF_OP','KNOXBOX','KEYPAD','MAN_OPEN','GATEOPEN']:
                                domain = "YNU"
                            else:
                                domain = fieldN

                            userMessage("Checking: " + fieldN)
                            #get the full domain dictionary
                            domainDict = getFieldDomain(domain, folder)
                            if domainDict != {}:
                                #put domain values in a list
                                domainList = []

                                for val in domainDict.keys():
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
                                        domainList.append(dl1)
                                        i += 1
                                #run statistics on the field
                                a_obj = NG911_GDB_Objects.getFCObject(join(gdb, "NG911", "AddressPoints"))

                                #see if the domain is a range issue
                                if fieldN == a_obj.HNO:
                                    with SearchCursor(fullPathlyr, (id1, fieldN)) as rows:
                                        for row in rows:
                                            hno = row[1]
                                            if hno > 999999 or hno < 0:
                                                report = "Error: Value " + str(row[1]) + " not in approved domain for field " + fieldN
                                                val = (today, report, fc, fieldN, fID)
                                                values.append(val)

                                    del rows, row

                                #otherwise, compare row value to domain list
                                else:
                                    output = join("in_memory", "domainStat")
                                    Statistics_analysis(fullPathlyr, output, [[fieldN, "COUNT"]], fieldN)

                                    listOfBadValues = []
                                    with SearchCursor(output, (fieldN)) as rows:
                                        for row in rows:
                                            if row[0] not in domainList:
                                                if row[0] is not None:
                                                    listOfBadValues.append(row[0])
                                    try:
                                        del rows, row
                                    except:
                                        pass
                                    Delete_management(output)
                                    del output

                                    if len(listOfBadValues) > 0:
                                        for badun in listOfBadValues:
                                            if badun is not None:
                                                wc = str(fieldN) + " = '" + str(badun) + "'"
                                                userMessage(wc)
                                            else:
                                                wc = fieldN + " is null"

                                            with SearchCursor(fullPathlyr, (id1, fieldN), wc) as rows:
                                                for row in rows:
                                                    fID = row[0]
                                                    if row[1] is None:
                                                        fieldVal = "Null"
                                                    else:
                                                        fieldVal = row[1]
                                                    report = "Error: Value " + str(row[1]) + " not in approved domain for field " + fieldN
                                                    val = (today, report, fc, fieldN, fID)
                                                    values.append(val)
                                            del rows, row

                userMessage("Checked " + layer)

            Delete_management(fullPathlyr)

        else:
            AddWarning(fullPath + " does not exist")

    if values != []:
        RecordResults(resultType, values, gdb)

    userMessage("Completed checking fields against domains: " + str(len(values)) + " issues found")


def checkRequiredFieldValues(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    folder = pathsInfoObject.domainsFolderPath
    esb = pathsInfoObject.gdbObject.esbList
    fcList = pathsInfoObject.gdbObject.fcList
    rc_obj = pathsInfoObject.rc_obj

    userMessage("Checking that required fields have all values...")

    #get today's date
    today = strftime("%m/%d/%y")

    values = []

    #walk through the tables/feature classes
    for filename in fcList:
        if Exists(filename):
            layer = basename(filename)
            id1 = getUniqueIDField(filename)

            if id1 != "":
                obj = NG911_GDB_Objects.getFCObject(filename)
                requiredFieldList = obj.REQUIRED_FIELDS

                #get list of fields in the feature class
                fields = ListFieldNames(filename)

                #convert lists to sets
                set1 = set(requiredFieldList)
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
                                            val = (today, report, basename(filename), matchingFields[k], oid)
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
        else:
            AddWarning(filename + " does not exist.")

    if values != []:
        RecordResults("fieldValues", values, gdb)

    userMessage("Completed check for required field values: " + str(len(values)) + " issues found")



def checkRequiredFields(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    fcList = pathsInfoObject.gdbObject.fcList

    userMessage("Checking that required fields exist...")

    #get today's date
    today = strftime("%m/%d/%y")
    values = []

    #walk through the tables/feature classes
    for fullPath in fcList:
        filename = basename(fullPath)
        if Exists(fullPath):

            obj = NG911_GDB_Objects.getFCObject(fullPath)
            comparisonList = obj.REQUIRED_FIELDS

            #list fields
            fields = ListFieldNames(fullPath)

            #loop through required fields to make sure they exist in the geodatabase
            for comparisonField in comparisonList:
                if comparisonField.upper() not in fields:
                    report = "Error: " + filename + " does not have required field " + comparisonField
                    userMessage(report)
                    #add issue to list of values
                    val = (today, report, "Field")
                    values.append(val)
        else:
            AddWarning(fullPath + " does not exist")

    #record issues if any exist
    if values != []:
        RecordResults("template", values, gdb)

    userMessage("Completed check for required fields: " + str(len(values)) + " issues found")


def checkSubmissionNumbers(pathsInfoObject):
    #set variables
    gdb = pathsInfoObject.gdbPath
    esb = pathsInfoObject.gdbObject.esbList

    fcList = pathsInfoObject.gdbObject.fcList


    today = strftime("%m/%d/%y")
    values = []

    for fc in fcList:
        if Exists(fc):
            #count records that are for submission
            lyr2 = "lyr2"
            if not fieldExists(fc, "SUBMIT"):
                MakeTableView_management(fc, lyr2)
            else:
                rc_obj = pathsInfoObject.rc_obj
                wc2 = rc_obj.SUBMIT + " not in ('N')"
                if "AddressPoints" in fc:
                    a_obj = pathsInfoObject.a_obj
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
        else:
            AddWarning(fc + " does not exist")

    #record issues if any exist
    if values != []:
        RecordResults("template", values, gdb)

def checkFeatureLocations(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    fcList = pathsInfoObject.gdbObject.fcList
    esb = pathsInfoObject.gdbObject.esbList

    #get geodatabase object
    gdbObject = pathsInfoObject.gdbObject
    rc_obj = pathsInfoObject.rc_obj
    a_obj = pathsInfoObject.a_obj

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
    countyBound = gdbObject.CountyBoundary
    ab = "ab"

    #see if authoritative boundary has more than 1 feature
    #if more than one feature is in the authoritative boundary, use the county boundary instead
    if Exists(authBound):
        if getFastCount(authBound) > 1:
            authBound = countyBound
    else:
        authBound = countyBound

    if authBound in fcList:
        fcList.remove(authBound)
    if countyBound in fcList:
        fcList.remove(countyBound)

    MakeFeatureLayer_management(authBound, ab)

    for fullPath in fcList:
        if Exists(fullPath):
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

                    id1 = getUniqueIDField(fullPath)
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

                        userMessage(basename(fullPath) + ": issues with some feature locations")
                    else:
                        userMessage("Could not process features in " + fullPath)
                else:
                    userMessage(basename(fullPath) + ": all records inside authoritative boundary")
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
    gdbObject = pathsInfoObject.gdbObject
    esb = gdbObject.esbList
    fcList = gdbObject.fcList

    for f in fcList:
        if "RoadAlias" in f:
            fcList.remove(f)

    today = strftime("%m/%d/%y")
    values = []
    report = "Error: Invalid geometry"

    invalidDict = {"point": 1, "polyline": 2, "polygon":3}

    #loop through feature classes
    for fullPath in fcList:

        if Exists(fullPath):
            #get the unique ID column
##            layer = basename(fullPath)
##
##            if layer.upper() != "ROADALIAS":
##                if layer in esb:
##                    layerName = "ESB"
##                else:
##                    layerName = layer

            id_column = getUniqueIDField(fullPath)

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

        else:
            AddWarning(fullPath + " does not exist")

    if values != []:
        RecordResults("fieldValues", values, gdb)

    userMessage("Completed for invalid geometry: " + str(len(values)) + " issues found")

def checkCutbacks(pathsInfoObject):
    userMessage("Checking for geometry cutbacks...")

    gdb = pathsInfoObject.gdbPath
    gdbObject = pathsInfoObject.gdbObject
    road_fc = gdbObject.RoadCenterline
    roads = "roads"
    rc_obj = pathsInfoObject.rc_obj

    if Exists(road_fc):


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
    else:
        AddWarning(road_fc + " does not exist")

    if values != []:
        RecordResults("fieldValues", values, gdb)

    if k != 0:
        userMessage("Could not complete cutback check on " + str(k) + " segments.")

    userMessage("Completed check on cutbacks: " + str(len(values)) + " issues found")

def getNumbers():
    numbers = "0123456789"
    return numbers

def VerifyRoadAlias(gdb, domainFolder):
    gdbObject = NG911_GDB_Objects.getGDBObject(gdb)
    #set up variables for search cursor
    roadAlias = gdbObject.RoadAlias
    ra_obj = NG911_GDB_Objects.getFCObject(roadAlias)
    fieldList = (ra_obj.A_RD, ra_obj.ALIASID)

    if Exists(roadAlias):

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

    else:
        AddWarning(roadAlias + " does not exist")


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
        userMessage("Checked highway names in the road alias table.")

def checkJoin(gdb, inputTable, joinTable, where_clause, errorMessage, field):
    #set up tracking variables
    values = []
    today = strftime("%m/%d/%y")
    layer = field.split(".")[0]
    recordType = "fieldValues"
    rc_obj = NG911_GDB_Objects.getFCObject(join(gdb, "NG911", "RoadCenterline"))

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
                        print("this is probably an exception")
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
    gdbObject = pathsInfoObject.gdbObject

    #make road layer into a feature layer
    roads = gdbObject.RoadCenterline
    rc_obj = pathsInfoObject.rc_obj
    ra_obj = pathsInfoObject.ra_obj
    road_alias = gdbObject.RoadAlias

    if Exists(roads) and Exists(road_alias):
        rdslyr = "RoadCenterlineQ"
        if fieldExists(roads, rc_obj.SUBMIT):
            MakeFeatureLayer_management(roads, rdslyr, rc_obj.SUBMIT + " not in ('N')")
        else:
            MakeFeatureLayer_management(roads, rdslyr)

        #make road alias into a table view

        ra_tbl = "RoadAliasQ"
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
    else:
        if not Exists(roads):
            AddWarning(roads + " does not exist")
            AddWarning(road_alias + " does not exist")


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

    gdbObject = currentPathSettings.gdbObject

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
##    geocodeAddressPoints(currentPathSettings)
    addressPoints = gdbObject.AddressPoints
    AP_freq = gdbObject.AddressPointFrequency
    AP_fields = currentPathSettings.a_obj.FREQUENCY_FIELDS_STRING
    checkFrequency(addressPoints, AP_freq, AP_fields, currentPathSettings.gdbPath)
    if Exists(gdbObject.ESZ):
        checkESNandMuniAttribute(currentPathSettings)
    else:
        userMessage("ESZ layer does not exist. Cannot complete check.")


    #check roads
    roads = gdbObject.RoadCenterline
    road_freq = gdbObject.RoadCenterlineFrequency
    road_fields = currentPathSettings.rc_obj.FREQUENCY_FIELDS_STRING
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
        AddWarning("There were " + str(numErrors) + " issues with the data. Please view errors in the TemplateCheckResults and:or FieldValuesCheckResults tables.")
        AddWarning("For documentation on Interpreting Tool Results, please copy and paste this link into your web browser: https://goo.gl/aUlrLH")

    checkToolboxVersionFinal()

    return sanity

def main_check(checkType, currentPathSettings):

    checkList = currentPathSettings.checkList
    env.workspace = currentPathSettings.gdbPath
    env.overwriteOutput = True

    gdbObject = currentPathSettings.gdbObject

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
            addressPoints = gdbObject.AddressPoints
            AP_freq = gdbObject.AddressPointFrequency
            AP_fields = currentPathSettings.a_obj.FREQUENCY_FIELDS_STRING
            checkFrequency(addressPoints, AP_freq, AP_fields, currentPathSettings.gdbPath)

        if checkList[3] == "true":
            checkUniqueIDFrequency(currentPathSettings)

        if checkList[4] == "true":
            if Exists(gdbObject.ESZ):
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
            road_fields = currentPathSettings.rc_obj.FREQUENCY_FIELDS_STRING
            checkFrequency(roads, road_freq, road_fields, currentPathSettings.gdbPath)

        if checkList[3] == "true":
            checkUniqueIDFrequency(currentPathSettings)

        if checkList[4] == "true":
            checkCutbacks(currentPathSettings)

        if checkList[5] == "true":
            checkDirectionality(roads, currentPathSettings.gdbPath)

        if checkList[6] == "true":
            checkRoadAliases(currentPathSettings)

    #run standard checks
    elif checkType == "standard":

        if checkList[0] == "true":
            checkValuesAgainstDomain(currentPathSettings)

        if checkList[1] == "true":
            checkFeatureLocations(currentPathSettings)

        if checkList[2] == "true":
            checkUniqueIDFrequency(currentPathSettings)

    fieldCheckResults = gdbObject.FieldValuesCheckResults
    templateResults = gdbObject.TemplateCheckResults
    numErrors = 0

    for table in [fieldCheckResults, templateResults]:
        if Exists(table):
            tbl = "tbl"
            wc = "Description not like '%Notice%'"
            MakeTableView_management(table, tbl, wc)
            count = getFastCount(tbl)
            numErrors = numErrors + count
            Delete_management(tbl)

    #change result = 1
    if numErrors > 0:
        BigMessage = """There were issues with the data. Please view errors in
        the TemplateCheckResults and:or FieldValuesCheckResults tables. For
        documentation on Interpreting Tool Results, please copy and paste this
        link into your web browser: https://goo.gl/aUlrLH"""
        AddWarning(BigMessage)

    checkToolboxVersionFinal()

if __name__ == '__main__':
    main()
