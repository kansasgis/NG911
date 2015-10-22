#-------------------------------------------------------------------------------
# Name:        NG911_DataFixes
# Purpose:     Scripts to adjust a variety of common NG911 data issues
#
# Author:      kristen
#
# Created:     21/10/2015
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, MakeTableView_management, Frequency_analysis, CalculateField_management, Delete_management, env, Exists, CreateTable_management,
    AddField_management, GetCount_management)
from arcpy.da import SearchCursor, InsertCursor
from os.path import join, dirname
from NG911_DataCheck import getFieldDomain, userMessage, RecordResults
from time import strftime

def FixDomainCase(gdb, domainFolder):
    env.workspace = gdb

    table = join(gdb, "FieldValuesCheckResults")

    if Exists(table):

        #read FieldValuesCheckResults, limit table view to only domain errors
        tbl = "tbl"
        wc = "Description IS LIKE '%not in approved domain for field%'"
        MakeTableView_management(table, tbl, wc)

        outTableInMemory = r"in_memory\outputFrequency"

        #run frequency, store in memory
        Frequency_analysis(tbl, outTableInMemory, ["Description", "Layer", "Field"])

        #run search cursor on frequency, see which fields in which layers have domain issues
        freq_fields = ("Description", "Layer", "Field")
        freq_wc = "Field is not null"

        fixDict = {}

        with SearchCursor(outTableInMemory, freq_fields, freq_wc) as rows:
            for row in rows:
                splitDesc = row[0].split()

                if len(splitDesc) == 9:
                    value = splitDesc[1]
                    layerName = row[1]
                    fieldName = row[2]

                    #test if the value in upper case is in the domain
                    domainDict = getFieldDomain(row[2], domainFolder)
                    domainList = []

                    for val in domainDict.iterkeys():
                        domainList.append(val)

                    if value.upper() in domainList:
                        #if yes, load into a master dictionary of stuff to fix (key is layer name, value is a list of fields that need help)
                        if layerName in fixDict.iterkeys():
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
            for layer, fields in fixDict.iteritems():
                report = report + layer + ": "
                #for each value in the key, calculate the attribute field to be all upper case
                for field in fields:
                    report = report + field + " "
                    CalculateField_management(layer, field, "!"+ field + "!.upper()", "PYTHON_9.3")

            userMessage("Domain values edited to be upper case: " + report)

    else:
        userMessage("FieldValuesCheckResults must be present for this tool to run.")

def FixDuplicateESBIDs(FireESB, EMSESB, LawESB):

    CalculateField_management(FireESB, "ESBID", '!ESBID! + "F"', "PYTHON_9.3")
    CalculateField_management(EMSESB, "ESBID", '!ESBID! + "E"', "PYTHON_9.3")
    CalculateField_management(LawESB, "ESBID", '!ESBID! + "L"', "PYTHON_9.3")

    userMessage("ESBIDs are now unique.")

def CreateGeocodeExceptions(gdb):

    table = join(gdb, "GeocodeExceptions")

    if not Exists(table):
        CreateTable_management(gdb, "GeocodeExceptions")
        AddField_management(table, "ADDID", "TEXT", "", "", 38)

    #read FieldValuesCheckResults for geocoding errors
    FVCR = join(gdb, "FieldValuesCheckResults")
    fields = ("DESCRIPTION", "FeatureID")
    wc = "DESCRIPTION like '%did not geocode%'"

    if Exists(FVCR):
        with SearchCursor(FVCR, fields, wc) as rows:
            for row in rows:
                addid = row[1]
                #create query clause to see if the geocoding exception already exists
                newWC = "ADDID = '" + addid + "'"
                tbl = "tbl"
                MakeTableView_management(table, tbl, newWC)

                rStatus = GetCount_management(tbl)
                rCount = int(rStatus.getOutput(0))

                #if the geocoding exception does not exist, add it
                if rCount == 0:
                    newRow = InsertCursor(table, ("ADDID"))
                    newVal = [addid]
                    newRow.insertRow(newVal)
                    del newRow

                #clean up
                Delete_management(tbl)

        userMessage("Created GeocodeExceptions table.")

    else:
        userMessage("FieldValuesCheckResults must be present for this tool to run.")

