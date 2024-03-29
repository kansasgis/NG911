#-------------------------------------------------------------------------------
# Name:        Enhancement_AddKSPID
# Purpose:     Add KSPID to NG911 Address Points
#
# Author:      kristen
#
# Created:     25/07/2016
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, MakeFeatureLayer_management,
Delete_management, CalculateField_management, SpatialJoin_analysis,
AddJoin_management, AddField_management, DeleteField_management,
Exists, AddWarning)
from arcpy.da import UpdateCursor, SearchCursor
from inspect import getsourcefile
from os.path import abspath, dirname, join
from NG911_DataCheck import userMessage
from NG911_arcpy_shortcuts import ListFieldNames, cleanUp
from NG911_GDB_Objects import getFCObject
from sys import exit

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
    else:
        userMessage("Error updating KSPID for a null or blank value")
        tPID = ""

    return tPID

def main():

    #get county name
    county = GetParameterAsText(0).upper()
    #get address point layer
    addy_pts = GetParameterAsText(1)
    #get parcel layer
    parcels = GetParameterAsText(2)
    #get column of PID from parcel layer
    pid_column = GetParameterAsText(3)

    # get object
    a = getFCObject(addy_pts)

    #see if pid_column is already set to KSPID, and if so, edit accordingly
    if pid_column == "KSPID":
        pid_column += "_1"

    #identify the location of the county code DBF
    me_folder = dirname(abspath(getsourcefile(lambda:0)))
    domains_folder = me_folder.replace("Scripts","Domains")
    county_dbf = join(domains_folder, "CountyCodes.dbf")

    #from county name, query out the state prefix
    countycode = ""
    county_wc = '"COUNTY" = ' + "'" + county + "'"
    c_fields = ("STATECODE")
    with SearchCursor(county_dbf, c_fields, county_wc) as c_rows:
        for c_row in c_rows:
            countycode = c_row[0]

    if countycode == "":
        AddWarning("County name was not valid. Cannot process data.")
        exit()

    #create layer of parcels & address points
    p_lyr = "p_lyr"
    MakeFeatureLayer_management(parcels, p_lyr)
    a_lyr = "a_lyr"
    MakeFeatureLayer_management(addy_pts, a_lyr)

    #run a spatial join between the address points and parcels
    workingFile = join("in_memory", "AddyKSPID_Working")
    if Exists(workingFile):
        Delete_management(workingFile)
    userMessage("Executing spatial join...")
    SpatialJoin_analysis(a_lyr, p_lyr, workingFile)
    AddField_management(workingFile, "KSPID19", "TEXT", "", "", 19)
    Delete_management(p_lyr)
    Delete_management(a_lyr)

    #try deleting all fields except the necessary ones
    userMessage("Cleaning up columns...")
    sj_fields = ListFieldNames(workingFile)
    for sj_field in sj_fields:
        if sj_field not in [pid_column, a.UNIQUEID, "KSPID19", "OBJECTID", "SHAPE"]:
            if "OBJECTID" not in sj_field:
                DeleteField_management(workingFile, sj_field)

    null_kspid = False

    #make sure the KSPID column is populated with a properly formatted KSPID
    userMessage("Calculating KSPID values...")
    with UpdateCursor(workingFile, ("KSPID19", pid_column, a.UNIQUEID)) as w_rows:
        for w_row in w_rows:
            #get the value of the parcel ID
            pid = w_row[1]

            if pid is not None:

                #turn the parcel ID into a KSPID
                kspid = makeKSPID(pid, countycode)
                w_row[0] = kspid
                w_rows.updateRow(w_row)
            else:
                ngaddid = w_row[2]
                userMessage("Null KSPID for %s %s " % (a.UNIQUEID, str(ngaddid)))
                null_kspid = True

    if null_kspid == True:
        userMessage("The address points listed above may not intersect a parcel.")

    # convert address points to a layer again
    ap = "ap"
    MakeFeatureLayer_management(addy_pts, ap)

    #convert the working file to a layer
    w_lyr = "w_lyr"
    MakeFeatureLayer_management(workingFile, w_lyr)

    #join the working file to the original address point file to copy over the KSPIDs
    AddJoin_management(ap, a.UNIQUEID, w_lyr, a.UNIQUEID)

    userMessage("Copying KSPID values...")

    #make feature layer excepting any records where the KSPID didn't populate
    #KJ edit: 07/26/2016 end of day notes: this still isn't working. What else can I do to make this work?
    j_lyr = "j_lyr"
    j_wc = "ADDYKSPID_WORKING.KSPID19 not in ('', ' ')"
    MakeFeatureLayer_management(ap, j_lyr, j_wc)

    #import the KSPID over to the address file
    CalculateField_management(j_lyr, "ADDRESSPOINTS." + a.KSPID, "!ADDYKSPID_WORKING.KSPID19!", "PYTHON_9.3")

    #clean up
    cleanUp([w_lyr, ap, j_lyr, workingFile])


if __name__ == '__main__':
    main()
