#-------------------------------------------------------------------------------
# Name:        Enhancement_CreateRoadAliasRecords
# Purpose:     Create road alias records based on a name in the road centerline
#
# Author:      kristen
#
# Created:     21/04/2016
#-------------------------------------------------------------------------------
from arcpy import GetParameterAsText, CalculateField_management, MakeFeatureLayer_management, AddMessage, AddWarning
from arcpy.da import InsertCursor, SearchCursor
from NG911_GDB_Objects import getDefaultNG911RoadAliasObject, getDefaultNG911RoadCenterlineObject
from NG911_Config import getGDBObject

rc_obj = getDefaultNG911RoadCenterlineObject()
ra_obj = getDefaultNG911RoadAliasObject()

def uniqueID():
    x = str(int(time.time()))
    AddMessage(x)
    return x

def main():
    gdb = GetParameterAsText(0)
    road_name = GetParameterAsText(1).upper()
    alias_road_name = GetParameterAsText(2).upper()
    alias_road_type = GetParameterAsText(3).upper()
    label = GetParameterAsText(4)

    #get gdb object & set layer names
    gdbObject = getGDBObject(gdb)
    rc_file = gdbObject.RoadCenterline
    ra_file = gdbObject.RoadAlias

    #set where clause for query
    wc = rc_obj.RD + " = '" + road_name + "'"

    #define fields for cursors
    fields = (rc_obj.STEWARD, rc_obj.EFF_DATE, rc_obj.UNIQUEID, "OBJECTID")
    insertFields = [ra_obj.STEWARD, ra_obj.EFF_DATE, ra_obj.UNIQUEID, ra_obj.SEGID, ra_obj.A_RD, ra_obj.A_STS, ra_obj.LABEL, ra_obj.SUBMIT]

    #loop through records in the road centerline file with that name
    with SearchCursor(rc_file, (fields), wc) as rows:
        for row in rows:
            #create a new unique alias ID
            aliasPart = uniqueID()
            aliasID = aliasPart + str(row[3])

            #define new values to be inserted
            newVals = [row[0], row[1], aliasID, row[2], alias_road_name, alias_road_type, label, 'Y']

            #create insert cursor for road alias table
            cursor = InsertCursor(ra_file, insertFields)
            cursor.insertRow(newVals)

    AddWarning("New road alias records created for ALL roads named " + road_name + ". Please double-check new records for validity and accuracy.")

if __name__ == '__main__':
    main()
