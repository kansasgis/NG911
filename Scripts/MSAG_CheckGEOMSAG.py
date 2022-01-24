# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 12:31:34 2022

@author: kristen
"""
from arcpy import (GetParameterAsText, Exists, CreateFileGDB_management,
                   Delete_management, MakeFeatureLayer_management, 
                   CopyFeatures_management, Describe, Array, Point, Polyline,
                   DeleteFeatures_management, RemoveSpatialIndex_management,
                   Append_management)
from arcpy.da import SearchCursor, InsertCursor, Editor
from os.path import join, dirname, basename, exists
from os import mkdir
from time import strftime
from NG911_GDB_Objects import getGDBObject
from NG911_arcpy_shortcuts import getFastCount
from NG911_DataCheck import FindOverlaps


class geomsag_working_Object(object):

    def __init__(self, u_gdb_path):

        self.gdbPath = u_gdb_path
        self.FieldValuesCheckResults = join(u_gdb_path, "FieldValuesCheckResults")


def getGeomsagWorkingObject(gdb_path):

    geomsag_working = geomsag_working_Object(gdb_path)

    return geomsag_working


def ap_geomsag_convert(ap, roads):
    # query out which address points are marked as GEOMSAG = Y
    wc = "GEOMSAG = 'Y'"
#    wc = "GEOMSAG = 'Y' and STEWARD = '484991'"
    ap_lyr = "ap_lyr"
    
    if Exists(ap_lyr):
        Delete_management(ap_lyr)
        
    MakeFeatureLayer_management(ap, ap_lyr, wc)

    # make sure features are pulled back by the query
    count = getFastCount(ap_lyr)

    # clean up
    Delete_management(ap_lyr)
    
    # create list of issue points
    not_inserted_ap = []

    if count > 0:
        print("Processing address points GEOMSAG conversion...")
        # desired line length (could change based on West's preferences)
        length = .00002

        # get the spatial reference
        desc = Describe(roads)
        sr = desc.SpatialReference
        
        # make a copy of the roads, but empty  
        rw = roads + "_wrk"
        
        if Exists(rw):
            Delete_management(rw)
        
        # set variables, make a feature layer of 1 road
        wc_rw = "OBJECTID = 1"
        fl_rw = "fl_rw"
        MakeFeatureLayer_management(roads, fl_rw, wc_rw)
        
        # copy roads
        CopyFeatures_management(fl_rw, rw)
        
        # delete all features
        DeleteFeatures_management(rw)
        
        # clean up
        Delete_management(fl_rw)
            
        RemoveSpatialIndex_management(rw)

        ap_fields = ["NGADDID", "SHAPE@XY", "STEWARD", "STATE", "COUNTY", "HNO", "PRD", "STP", "RD", "STS", "POD", "POM", "ESN", "MSAGCO",
                    "ZIP", "L_UPDATE"]

        road_fields = ["NGSEGID", "SHAPE@", "STEWARD", "STATE_L", "STATE_R", "COUNTY_L", "COUNTY_R", "L_F_ADD", "L_T_ADD", "R_F_ADD", "R_T_ADD",
                        "PARITY_L", "PARITY_R", "PRD", "STP", "RD", "STS", "POD", "POM", "ESN_L", "ESN_R", "MSAGCO_L", "MSAGCO_R",
                        "ZIP_L", "ZIP_R", "GEOMSAGL", "GEOMSAGR", "AUTH_L", "AUTH_R", "SUBMIT", "L_UPDATE", "NOTES"]

        # create list of unique addresses to avoid duplicates
        inserted_ap = []

        # loop through each record in a search cursor
        with SearchCursor(ap, ap_fields, wc) as a_rows:
            for a_row in a_rows:
                
                # make sure nulls, spaces, and blanks are all represented by blanks
                null_dict = {"PRD": a_row[6], "STP": a_row[7], "STS": a_row[9], "POD": a_row[10], "POM":a_row[11]}
                for street_part in null_dict:
                    value = null_dict[street_part]
                    if value is None or value == ' ':
                        null_dict[street_part] = ''

                ap_info = [a_row[4], a_row[5], null_dict["PRD"], null_dict["STP"], a_row[8], null_dict["STS"],
                        null_dict["POD"], null_dict["POM"], a_row[12], a_row[13], a_row[14]]
                
                if ap_info not in inserted_ap:
                    ap_id = a_row[0]

                    # get existing point geometry
                    x = a_row[1][0]
                    y = a_row[1][1]

                    # calculate new point
                    new_x = x + length
                    new_y = y + length

                    # create array and two points
                    array = Array()
                    point0 = Point(x, new_y)
                    point1 = Point(x, y)
                    point2 = Point(new_x, y)

                    # add points to the array
                    array.add(point0)
                    array.add(point1)
                    array.add(point2)

                    # create a polyline of the two points
                    polyline = Polyline(array, sr)

                    # see if HNO is even or odd
                    if a_row[5] % 2 == 0:
                        parity = "E"
                    else:
                        parity = "O"
                        
                    if 1==1:
#                    try:
                        
                        # get workspace
                        workspace = dirname(roads)

                        # contain inserts in an edit session
                        edit = Editor(workspace)
                        edit.startEditing(False, False)
                        edit.startOperation()
    
                            # using an insert cursor, insert the information into the road centerline
                        cursor = InsertCursor(rw, road_fields)
                        attributes = (("AP" + str(ap_id))[0:37], polyline, a_row[2], a_row[3], a_row[3], a_row[4], a_row[4], a_row[5], a_row[5], "0", "0",
                                    parity, "Z", null_dict["PRD"], null_dict["STP"], a_row[8], null_dict["STS"],
                              null_dict["POD"], null_dict["POM"], a_row[12], a_row[12],
                                    a_row[13], a_row[13], a_row[14], a_row[14], "Y", "N", "Y", "N", "Y", a_row[15], "EGDMS AP conversion")
#                        print(attributes)

                        cursor.insertRow(attributes)
                        del cursor
#                        print("Inserted %s" % ("AP" + str(ap_id)))
    
                        # close out the editing session
                        edit.stopOperation()
                        edit.stopEditing(True)
    
                        # append info to list of added address points
                        inserted_ap.append(ap_info)
                            
        Append_management(rw, roads, "TEST")    
        print("Added plines")    
        
        Delete_management(rw)

    else:
        print("No address points marked for GEOMSAG")
        
    return(not_inserted_ap)
    

def main():
    
    # get geodatabase
    gdb = GetParameterAsText(0)
    
    gdb_obj = getGDBObject(gdb)
    
    roads = gdb_obj.RoadCenterline
    address = gdb_obj.AddressPoints
    
    # is it worth checking to see if any address points are GEOMSAG = 'Y' at the beginning?
    
    today = strftime('%Y%m%d')
    
    # set up working geodatabase and feature class
    root_folder = join(dirname(gdb), basename(gdb).replace(".gdb","") + "_GEOMSAG")
    geomsag_gdb = join(root_folder, "GEOMSAG_Working.gdb")
    output_fc = join(geomsag_gdb, "GEOMSAG_" + today) 

    if not exists(root_folder):
        mkdir(root_folder)

    if not Exists(geomsag_gdb):
        CreateFileGDB_management(dirname(geomsag_gdb), basename(geomsag_gdb))

    if Exists(output_fc):
        Delete_management(output_fc)
        
    # copy GEOMSAG = Y roads to working geodatabase
    wc = "GEOMSAGL = 'Y' or GEOMSAGR = 'Y'"
    
    fl_gmsag = "fl_gmsag"
    
    if Exists(fl_gmsag):
        Delete_management(fl_gmsag)
    
    MakeFeatureLayer_management(roads, fl_gmsag, wc)
    
    CopyFeatures_management(fl_gmsag, output_fc)
    
    # add the plines
    ap_geomsag_convert(address, output_fc)
    
    # check for overlapping address ranges
    gdb_object = geomsag_working_Object(geomsag_gdb)
    FindOverlaps(gdb_object, geomsag=True, road_fc = output_fc)
    
    # clean up
    Delete_management(fl_gmsag)
        
if __name__ == '__main__':
    main()