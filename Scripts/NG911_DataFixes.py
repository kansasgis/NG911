#-------------------------------------------------------------------------------
# Name:        NG911_DataFixes
# Purpose:     Scripts to adjust a variety of common NG911 data issues
#
# Author:      kristen
#
# Created:     21/10/2015
#-------------------------------------------------------------------------------
from arcpy import (MakeTableView_management, Frequency_analysis, CalculateField_management, 
                   Delete_management, env, Exists, CreateTable_management,
                   AddField_management, GetCount_management, ListFeatureClasses)
from arcpy.da import SearchCursor, InsertCursor
from os.path import join, basename
from NG911_DataCheck import getFieldDomain, userMessage
from NG911_GDB_Objects import getGDBObject, getFCObject
from NG911_arcpy_shortcuts import fieldExists, CalcWithWC


def FixDomainCase(gdb, domainFolder):
    env.workspace = gdb
    gdbObject = getGDBObject(gdb)

    table = gdbObject.FieldValuesCheckResults
    fvcr_object = getFCObject(table)

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
                    if fieldName[-2:] in ["_L", "_R"]:
                        fieldNameForDict = fieldName.strip("_L").strip("_R")
                    else:
                        fieldNameForDict = fieldName
                    domainDict = getFieldDomain(fieldNameForDict, domainFolder)
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
    e = getFCObject(FireESB)

    CalculateField_management(FireESB, e.ESBID, '!' + e.ESBID + '! + "F"', "PYTHON_9.3")
    CalculateField_management(EMSESB, e.ESBID, '!' + e.ESBID + '! + "E"', "PYTHON_9.3")
    CalculateField_management(LawESB, e.ESBID, '!' + e.ESBID + '! + "L"', "PYTHON_9.3")

    userMessage(e.ESBID + "s are now unique.")


def CreateGeocodeExceptions(gdb):

    gdbObject = getGDBObject(gdb)

    table = gdbObject.GeocodeExceptions
    addressPoints = gdbObject.AddressPoints
    a = getFCObject(addressPoints)
    FVCR = gdbObject.FieldValuesCheckResults
    fvcr_obj = getFCObject(FVCR)

    #set up table if it doesn't exist yet
    if not Exists(table):
        CreateTable_management(gdb, basename(table))

    if not fieldExists(table, a.UNIQUEID):
        AddField_management(table, a.UNIQUEID, "TEXT", "", "", 38)
    if not fieldExists(table, a.LABEL):
        AddField_management(table, a.LABEL, "TEXT", "", "", 300)
    if not fieldExists(table, a.NOTES):
        AddField_management(table, a.NOTES, "TEXT", "", "", 100)

    #after the table is set up, get the geocoding exceptions object
    ge = getFCObject(gdbObject.GeocodeExceptions)

    #read FieldValuesCheckResults for geocoding errors
    fields = (fvcr_obj.DESCRIPTION, fvcr_obj.FEATUREID)
    wc = fvcr_obj.DESCRIPTION + " like '%did not geocode%'"

    if Exists(FVCR):
        with SearchCursor(FVCR, fields, wc) as rows:
            for row in rows:
                addid = row[1]
                #create query clause to see if the geocoding exception already exists
                newWC = ge.UNIQUEID + " = '" + addid + "'"
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

                            newRow = InsertCursor(table, (ge.UNIQUEID, ge.LABEL))
                            newVal = (addid, label)
                            newRow.insertRow(newVal)
                            del newRow

                #clean up
                Delete_management(tbl)

        userMessage("Created " + basename(table) + " table.")

    else:
        userMessage(basename(FVCR) + " must be present for this tool to run.")


def FixMSAGCOspaces(gdb):

    gdbObject = getGDBObject(gdb)
    addressPoints = gdbObject.AddressPoints
    roadCenterlines = gdbObject.RoadCenterline
    
    a = getFCObject(addressPoints)
    rc = getFCObject(roadCenterlines)

    CalculateField_management(addressPoints, a.MSAGCO, "!%s!.strip()" % a.MSAGCO, "PYTHON_9.3", "")

    for m in [rc.MSAGCO_L, rc.MSAGCO_R]:
        CalculateField_management(roadCenterlines, m, "!" + m + "!.strip()", "PYTHON_9.3", "")

    userMessage("Leading and trailing spaces removed from MSAGCO fields.")


def fixKSPID(gdb):
    gdbObject = getGDBObject(gdb)
    addressPoints = gdbObject.AddressPoints
    
    a = getFCObject(addressPoints)

    CalculateField_management(addressPoints, a.KSPID, '!%s!.replace("-", "").replace(".", "")' % a.KSPID, "PYTHON_9.3", "")

    userMessage("Dots and dashes in KSPID replaced.")


def fixSubmit(gdb):
    from arcpy import MakeTableView_management
    
    gdb_obj = getGDBObject(gdb)

    fds = gdb_obj.NG911_FeatureDataset
    ap = gdb_obj.AddressPoints
    
    submit = ap.SUBMIT

    # list all fcs
    env.workspace = fds
    fcs = ListFeatureClasses()

    # set up where clause
    wc = "%s not in ('N')" % submit

    # loop through feature classes and edit the field
    for fc in fcs:
        full_path = join(fds, fc)
        CalcWithWC(full_path, submit, '"Y"', wc)

    # make sure the road alias record gets updated too
    fl_calc = "fl_calc"
    ra = gdb_obj.RoadAlias
    if Exists(ra):
        MakeTableView_management(ra, fl_calc, wc)
        CalculateField_management(fl_calc, submit, '"Y"', "PYTHON_9.3", "")
    Delete_management(fl_calc)