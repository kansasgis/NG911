#-------------------------------------------------------------------------------
# Name:        Conversion_AddParcels
# Purpose:      Adds parcels to the NG911 geodatabase in the proper format
#
# Author:      kristen
#
# Created:      October 19, 2016, edited August 29, 2018
# Copyright:   (c) kristen 2016
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, CalculateField_management, Append_management,
                    AddField_management, DeleteField_management, Dissolve_management,
                    DeleteFeatures_management, Exists, CreateFeatureclass_management,
                    Delete_management, AddWarning)
from arcpy.da import UpdateCursor, SearchCursor
from NG911_GDB_Objects import getFCObject, getGDBObject
from os.path import join, dirname, abspath, basename
from inspect import getsourcefile
from NG911_arcpy_shortcuts import fieldExists
from NG911_DataCheck import userMessage

def getCountyInfo(county, info):
    #identify the location of the county code DBF
    me_folder = dirname(abspath(getsourcefile(lambda:0)))
    domains_folder = me_folder.replace("Scripts","Domains")
    county_dbf = join(domains_folder, "CountyCodes.dbf")

    #from county name, query out the state prefix
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
        if lenPID == 16 or lenPID == 15:
            tPID = countycode + tPID
        elif lenPID == 19 or lenPID == 18:
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

    gdb_object = getGDBObject(targetGDB)

    #set target path
    target = gdb_object.PARCELS
    
    # get parcel object
    p_obj = getFCObject(target)

    if not Exists(target):
        CreateFeatureclass_management(dirname(target), basename(target), "POLYGON")
        fieldDict = {p_obj.STEWARD: [75, "Stewards"], p_obj.NGKSPID: [19, ""], 
                     p_obj.SUBMIT: [1, "Submit"], p_obj.NOTES: [255, ""]}
        for field in fieldDict:
            length = fieldDict[field][0]
            domain = fieldDict[field][1]
            AddField_management(target, field, "TEXT", "", "", length, field, "", "", domain)

    #delete existing features in the parcels so everything can be updated quickly
    DeleteFeatures_management(target)

    #add a field so the 19 digit PID can be calculated
    if not fieldExists(target, "tempPID"):
        AddField_management(target, "tempPID", "TEXT", "", "", 50)

    #set temp output for the dissovle
    tempOutput = join("in_memory", "tempParcels")

    #dissolve features based on PID
    Dissolve_management(parcels, tempOutput, [pidField])

    #append dissolved features into the parcel target
    schema_type="NO_TEST"
    Append_management(tempOutput, target, schema_type)

    Delete_management(tempOutput)

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
            
            try:
                w_rows.updateRow(w_row)
            except:
                pass
            

    #delete tempPID field
    DeleteField_management(target, "tempPID")

    userMessage("Conversion completed successfully.")

if __name__ == '__main__':
    main()
