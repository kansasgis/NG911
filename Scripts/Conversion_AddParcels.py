#-------------------------------------------------------------------------------
# Name:        Conversion_AddParcels
# Purpose:      Adds parcels to the NG911 geodatabase in the proper format
#
# Author:      kristen
#
# Created:      October 19, 2016
# Copyright:   (c) kristen 2016
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, CalculateField_management, Append_management,
                    AddField_management, DeleteField_management, Dissolve_management,
                    DeleteFeatures_management)
from arcpy.da import UpdateCursor, SearchCursor
from NG911_GDB_Objects import getFCObject
from os.path import join, dirname, abspath
from inspect import getsourcefile
from NG911_arcpy_shortcuts import fieldExists
from NG911_DataCheck import userMessage

def getCountyInfo(county, info):
    #identify the location of the county code DBF
    me_folder = dirname(abspath(getsourcefile(lambda:0)))
    domains_folder = me_folder.replace("Scripts","Domains")
    county_dbf = join(domains_folder, "CountyCodes.dbf")

    #from county name, query out the state prefix
    countycode = ""
    county_wc = '"COUNTY" = ' + "'" + county + "'"

    if info == "countycode":
        c_fields = ("STATECODE")
    elif info == "steward":
        c_fields = ("STEWARDID")

    with SearchCursor(county_dbf, c_fields, county_wc) as c_rows:
        for c_row in c_rows:
            info_return = c_row[0]

    if info_return == "":
        AddWarning("County name was not valid. Cannot process data.")
        exit()

    return info_return

def PIDreplace(pid, ch):
    if pid is not None:
        newPID = pid.replace(ch, "")
    else:
        newPID = " "
    return newPID

def makeKSPID(tPID, countycode):
    #copy the ORKA function here to create a 19 digit PID

    if tPID != '':
        tPID = PIDreplace(tPID, "-")
        tPID = PIDreplace(tPID, ".")
        tPID = PIDreplace(tPID, " ")
        lenPID = len(tPID)

        #check PID length to see what needs to be adjusted
        if lenPID == 16:
            tPID = countycode + tPID
        elif lenPID == 19:
            tPID = tPID
        elif lenPID == 21:
            tPID = tPID[0:19]
        else:
            if tPID is None:
                tPID = " "
            try:
                userMessage("Error updating KSPID for " + tPID)
            except:
                userMessage("Error updating KSPID for a null value")
            finally:
                tPID = ""

    return tPID

def main():
    parcels = GetParameterAsText(0)
    pidField = GetParameterAsText(1)
    county = GetParameterAsText(2).upper().replace("COUNTY", "").strip()
    targetGDB = GetParameterAsText(3)

    #set target path
    target = join(targetGDB, "PARCELS")

    #delete existing features in the parcels so everything can be updated quickly
    DeleteFeatures_management(target)

    #get parcel object
    p_obj = getFCObject(target)

    #add a field so the 19 digit PID can be calculated
    if not fieldExists(target, "tempPID"):
        AddField_management(target, "tempPID", "TEXT", "", "", 50)

    #set temp output for the dissovle
    tempOutput = join("in_memory", "tempParcels")

    #dissolve features based on PID
    Dissolve_management(parcels, tempOutput, [pidField])

    #append dissolved features into the parcel target
    #set up parameters for the append
    schema_type="NO_TEST"
    field_mapping= """STEWARD "STEWARD" true true false 50 Text 0 0 ,First,#;NGKSPID"NGKSPID" true true false 19 Text 0 0 ,First,#;SUBMIT "SUBMIT" true true false 1 Text 0 0 ,First,#;NOTES "NOTES" true true false 50 Text 0 0 ,First,#;tempPID "tempPID" true true false 19 Text 0 0 ,First,#,""" + tempOutput + "," + pidField + """,-1,-1;SHAPE_Length "SHAPE_Length" false true true 8 Double 0 0 ,First,#;SHAPE_Area "SHAPE_Area" false true true 8 Double 0 0 ,First,#"""
    Append_management(tempOutput, target, schema_type, field_mapping, "")

    #get values for the steward and county code
    steward = getCountyInfo(county, "steward")
    countyCode = getCountyInfo(county, "countycode")

    #fill in default values
    CalculateField_management(target, p_obj.STEWARD, "'" + steward + "'", "PYTHON")
    CalculateField_management(target, p_obj.SUBMIT, "'Y'", "PYTHON")

    #make sure the PID is the proper 19 digit version
    with UpdateCursor(target, ("tempPID", p_obj.NGKSPID)) as w_rows:
        for w_row in w_rows:
            #get the value of the parcel ID
            pid = w_row[0]

            #turn the parcel ID into a KSPID
            kspid = makeKSPID(pid, countyCode)
            w_row[1] = kspid
            w_rows.updateRow(w_row)

    #delete tempPID field
    DeleteField_management(target, "tempPID")

if __name__ == '__main__':
    main()
