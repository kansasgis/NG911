#-------------------------------------------------------------------------------
# Name:        NG911_DataFixes
# Purpose:     Scripts to adjust a variety of common NG911 data issues
#
# Author:      kristen
#
# Created:     21/10/2015
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, MakeTableView_management, Frequency_analysis, CalculateField_management, Delete_management, env, Exists, CreateTable_management,
    AddField_management, GetCount_management, ListFields)
from arcpy.da import SearchCursor, InsertCursor
from os.path import join, dirname, basename
from NG911_DataCheck import getFieldDomain, userMessage, RecordResults
from time import strftime
from NG911_GDB_Objects import getDefaultNG911AddressObject, getDefaultNG911GeocodeExceptionsObject, getDefaultNG911FieldValuesCheckResultsObject, getDefaultNG911ESBObject
from NG911_Config import getGDBObject

def FixDomainCase(gdb, domainFolder):
    env.workspace = gdb
    gdb_object = getGDBObject(gdb)

    table = gdb_object.FieldValuesCheckResults
    fvcr_object = getDefaultNG911FieldValuesCheckResultsObject()

    if Exists(table):

        #read FieldValuesCheckResults, limit table view to only domain errors
        tbl = "tbl"
        wc = fvcr_object.DESCRIPTION + " LIKE '%not in approved domain for field%'"
        MakeTableView_management(table, tbl, wc)

        outTableInMemory = r"in_memory\outputFrequency"

        #run frequency, store in memory
        Frequency_analysis(tbl, outTableInMemory, [fvcr_object.DESCRIPTION, fvcr_object.LAYER, fvcr_object.FIELD])

        #run search cursor on frequency, see which fields in which layers have domain issues
        freq_fields = (fvcr_object.DESCRIPTION, fvcr_object.LAYER, fvcr_object.FIELD)
        freq_wc = fvcr_object.FIELD + " is not null and " + fvcr_object.FIELD + " not in ('',' ')"

        fixDict = {}

        with SearchCursor(outTableInMemory, freq_fields, freq_wc) as rows:
            for row in rows:
                #get the offending value out of the error message
                value = ((row[0].strip("Error: Value ")).replace(" not in approved domain for field ", "|")).split("|")[0]
                layerName = row[1]
                fieldName = row[2]

                #make sure the field name is not blank
                if fieldName not in ('',' '):
                    #test if the value in upper case is in the domain
                    domainDict = getFieldDomain(fieldName, domainFolder)
                    domainList = []

                    for val in domainDict:
                        domainList.append(val)

                    if value.upper() in domainList:
                        #if yes, load into a master dictionary of stuff to fix (key is layer name, value is a list of fields that need help)
                        if layerName in fixDict:
                            fieldsToFix = fixDict[layerName]

                            #see if field name is already in list of those to fix
                            if fieldName not in fieldsToFix:
                                fieldsToFix.append(fieldName)
                                fixDict[layerName] = fieldsToFix

                        else:
                            fixDict[layerName] = [fieldName]


        Delete_management("in_memory")

        #loop through resulting list
        if fixDict != {}:
            report = ""
            userMessage(fixDict)
            for layer in fixDict:
                fields = fixDict[layer]
                report = report + layer + ": "
                #for each value in the key, calculate the attribute field to be all upper case
                for field in fields:
                    report = report + field + " "
                    CalculateField_management(layer, field, "!"+ field + "!.upper()", "PYTHON_9.3")

            userMessage("Domain values edited to be upper case: " + report)

    else:
        userMessage(basename(table) + " must be present for this tool to run.")

def FixDuplicateESBIDs(FireESB, EMSESB, LawESB):
    e = getDefaultNG911ESBObject()

    CalculateField_management(FireESB, e.ESBID, '!' + e.ESBID + '! + "F"', "PYTHON_9.3")
    CalculateField_management(EMSESB, e.ESBID, '!' + e.ESBID + '! + "E"', "PYTHON_9.3")
    CalculateField_management(LawESB, e.ESBID, '!' + e.ESBID + '! + "L"', "PYTHON_9.3")

    userMessage(e.ESBID + "s are now unique.")

def CreateGeocodeExceptions(gdb):

    gdb_object = getGDBObject(gdb)

    table = gdb_object.GeocodeExceptions
    addressPoints = gdb_object.AddressPoints
    a = getDefaultNG911AddressObject()
    ge = getDefaultNG911GeocodeExceptionsObject()
    fvcr_obj = getDefaultNG911FieldValuesCheckResultsObject()

    if not Exists(table):
        CreateTable_management(gdb, basename(table))

    table_fields = ListFields(table)
    lstTable_fields = []

    for tf in table_fields:
        lstTable_fields.append(tf.name)

    if ge.ADDID not in lstTable_fields:
        AddField_management(table, ge.ADDID, "TEXT", "", "", 38)
    if ge.LABEL not in lstTable_fields:
        AddField_management(table, ge.LABEL, "TEXT", "", "", 300)
    if ge.NOTES not in lstTable_fields:
        AddField_management(table, ge.NOTES, "TEXT", "", "", 100)

    #read FieldValuesCheckResults for geocoding errors
    FVCR = gdb_object.FieldValuesCheckResults
    fields = (fvcr_obj.DESCRIPTION, fvcr_obj.FEATUREID)
    wc = fvcr_obj.DESCRIPTION + " like '%did not geocode%'"

    if Exists(FVCR):
        with SearchCursor(FVCR, fields, wc) as rows:
            for row in rows:
                addid = row[1]
                #create query clause to see if the geocoding exception already exists
                newWC = ge.ADDID + " = '" + addid + "'"
                tbl = "tbl"
                MakeTableView_management(table, tbl, newWC)

                rStatus = GetCount_management(tbl)
                rCount = int(rStatus.getOutput(0))

                #if the geocoding exception does not exist, add it
                if rCount == 0:
                    with SearchCursor(addressPoints, (a.LABEL), newWC) as addy_rows:
                        for addy_row in addy_rows:
                            label = addy_row[0]
                            userMessage(label)

                            newRow = InsertCursor(table, (ge.ADDID, ge.LABEL))
                            newVal = (addid, label)
                            newRow.insertRow(newVal)
                            del newRow

                #clean up
                Delete_management(tbl)

        userMessage("Created " + basename(table) + " table.")

    else:
        userMessage(basename(FVCR) + " must be present for this tool to run.")

