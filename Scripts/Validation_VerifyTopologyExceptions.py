#-------------------------------------------------------------------------------
# Name:        Validation_VerifyTopologyExceptions
# Purpose:     Double check that all road centerline topology errors are noted as exceptions
#
# Author:      kristen
#
# Created:     03/09/2015
#-------------------------------------------------------------------------------
from arcpy import (ExportTopologyErrors_management, AddJoin_management, GetParameterAsText,
MakeFeatureLayer_management, MakeTableView_management, RemoveJoin_management, Delete_management, Exists, ListFields)
from arcpy.da import SearchCursor
from NG911_Config import getGDBObject
from NG911_DataCheck import RecordResults, userMessage
from os.path import join, basename
from time import strftime
from NG911_GDB_Objects import getDefaultNG911RoadCenterlineObject

def main():

    gdb = GetParameterAsText(0)
    cleanUpTopology = GetParameterAsText(1)
    gdbObject = getGDBObject(gdb)

    userMessage("Validating topology exceptions...")

    #export topology errors as feature class
    topology = gdbObject.Topology
    out_basename = "NG911"
    rc_obj = getDefaultNG911RoadCenterlineObject()

    userMessage("Exporting topology errors...")
    ExportTopologyErrors_management(topology, gdb, out_basename)

    #exporting the topology creates three layers (pt, lines, polys)
    #we want to work with the line & point layers
    lineErrors = out_basename + "_line"
    pointErrors = out_basename + "_point"

    #create feature layer from the road centerline file
    road = gdbObject.RoadCenterline
    rd = "rd"
    MakeFeatureLayer_management(road, rd)

    flds = ListFields(rd)

    if rc_obj.EXCEPTION in flds:

        #set variables for working with the data
        recordType = "fieldValues"
        today = strftime("%m/%d/%y")
        filename = basename(road)
        values = []
        count = 0

        #join lines & points to centerline
        #topology.OriginObjectID = RoadCenterline.OBJECTID
        for errors in (lineErrors, pointErrors):
            fullDataset = join(gdb, errors)
            #create feture layer
            e = "e"
            MakeFeatureLayer_management(fullDataset, e)

            #add join
            AddJoin_management(rd, "OBJECTID", e, "OriginObjectID")

            #for this, only make sure dangles & outside authoritative boundary are marked as exceptions in both the topology & the road centerline
            rules = ('esriTRTLineNoDangles','esriTRTLineInsideArea')

            #set query and field variables
            qry = errors + ".OriginObjectID IS NOT NULL"
            fields = ("RoadCenterline." + rc_obj.UNIQUEID, "RoadCenterline." + rc_obj.EXCEPTION, errors + ".RuleType", errors + ".RuleDescription", errors + ".isException")

            try:
                #set up search cursor to loop through records
                with SearchCursor(rd, fields, qry) as rows:
                    for row in rows:
                        msg = ""
                        segID = row[0]

                        rule = row[2]
                        if rule in rules:
                            #means it's really an exception
                            if row[1] == "NOT EXCEPTION" and row[4] == 1:
                                #not marked as an exception in the road centerline file
                                msg = "Needs to be marked as a topology exception in the road centerline file"
                            elif row[1] != "NOT EXCEPTION" and row[4] == 0:
                                #not marked in the topology or incorrectly marked in the road centerline
                                msg = "Either marked incorrectly in the road centerline or needs to be marked as an exception in the topology"
                        else:
                            #note other exceptions in FieldValuesCheckResults table, access the real SEGID (just roads)
                            msg = "Feature has topology error: " + row[3]

                        #if an error was generated, add it to the error list
                        if msg != "":
                            val = (today, msg, filename, "", segID)
                            values.append(val)

                #report records
                if values != []:
                    count = len(values)
                    RecordResults(recordType, values, gdb)

                #clean up & reset
                RemoveJoin_management(rd)
                Delete_management(e)
                values = []

                #give the user some feedback
                message = "Topology check complete. " + str(count) + " issues found."
                if count > 0:
                    message = message + " Results in FieldValuesCheckResults."
                userMessage(message)



            except:
                userMessage("Error attempting topology validation.")

            finally:
                Delete_management(e)
                del e

        #clean up topology export if desired by the user
        if cleanUpTopology == "true":
            polyErrors = out_basename + "_poly"
            for topE in (lineErrors, pointErrors, polyErrors):
                full = join(gdb, topE)
                if Exists(full):
                    Delete_management(full)
    else:
        userMessage("Road Centerline does not have an exception field. Cannot check topology.")

if __name__ == '__main__':
    main()
