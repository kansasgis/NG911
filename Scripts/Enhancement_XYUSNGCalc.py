#-------------------------------------------------------------------------------
# Name:        Enhancement_XYUSNGCalc
# Purpose:      Calculate Lat, Long & USNG fields based on point locations
#
# Author:       Sherry Massey with assist from Kristen Jordan
#
# Created:     01/04/2014
# Copyright:   (c) SMassey 2014
# Edited:       April 13, 2016 by Kristen Jordan-Koenig: had project access address point object for field names & convert X & Y coordinates as well
# Licence:     Subject to Creative Commons Attribution-ShareAlike 4.0 International Public License
#-------------------------------------------------------------------------------
import CoordConvertor
from arcpy import (GetParameterAsText, AddMessage, Describe, SpatialReference, 
                   PointGeometry, Point, MakeFeatureLayer_management, 
                   Delete_management)
from arcpy.da import Editor, UpdateCursor
from os.path import dirname
from NG911_GDB_Objects import getFCObject

def main():

    #declare parameter variables for feature class and
    #X and Y fields and the National Grid field
    fc = GetParameterAsText(0)
    updateOnlyBlank = GetParameterAsText(1)

    calc_coordinates(fc, updateOnlyBlank)

def calc_coordinates(fc, updateOnlyBlank):

    ct = CoordConvertor.CoordTranslator()

    AddMessage("Calculating coordinates. For large datasets, this process can a while.")

    #get default address point object
    a = getFCObject(fc)

    #set field names based on object
    xField = a.X
    yField = a.Y
    NG = a.USNGRID

    #establish workspace
    path = dirname(fc)

    if '.gdb' in path:
        place = path.find('.gdb') + 4
    else:
        if '.sde' in path:
            place = path.find('.sde') + 4
        else:
            place = len(path) - 1

    workspace = path[:place]

    AddMessage(workspace)

    #Start an edit session
    edit = Editor(workspace)

    # Edit session is started without an undo/redo stack for versioned data
    #  (for second argument, use False for unversioned data)
    edit.startEditing(False, True)

    # Start an edit operation
    edit.startOperation()

    flcc = "flcc"
    # If necessary, only update blank records
    if updateOnlyBlank == "true":
        wc = NG + " IS NULL OR " + NG + " = '' OR " + NG  + " = ' '"
        MakeFeatureLayer_management(fc, flcc, wc)
    else:
        MakeFeatureLayer_management(fc, flcc)

    #define the field list
    fields = (xField, yField, NG, "SHAPE@X", "SHAPE@Y") #modify this to access the shape field

    #get desired spatial reference
    sr = SpatialReference("WGS 1984")

    #get current spatial reference
    sr_org = Describe(fc).SpatialReference

    #calculate the NG coordinate for each row
    try:
        with UpdateCursor(flcc, fields) as cursor:
            for row in cursor:
                #see if the x/y fields are blank or are populated
                if row[0] is None or row[0] == 0:
                    #create new point object
                    point = Point()
                    point.X = row[3]
                    point.Y = row[4]

                    #convert to a point geometry
                    pointGeom = PointGeometry(point, sr_org)

                    #reproject the point geometry into WGS 1984
                    point2 = pointGeom.projectAs(sr, "WGS_1984_(ITRF00)_To_NAD_1983")

                    #turn the point geometry back into a normal point with the "first point" functionality
                    firstPoint = point2.firstPoint

                    #get the x/y position
                    x = firstPoint.X
                    y = firstPoint.Y

                    #update the x & y fields along the way
                    row[0] = x
                    row[1] = y
                else:
                    x = row[0]
                    y = row[1]

                #some error trapping, just in case...
                if x is not None:
                    if y is not None:
                        #convert the x & y coordinates to USNG and update the field
                        row[2] = ct.AsMGRS([y,x], 5, False)
                cursor.updateRow(row)

        #release the locks on the data
        del row
        del cursor

        AddMessage("Lat/Long and USNG coordinates successfully updated.")
    except:
        AddMessage("Lat/Long and USNG coordinates could not be updated.")

    finally:
        # Stop the edit operation.
        edit.stopOperation()

        # Stop the edit session and save the changes
        edit.stopEditing(True)
        
        Delete_management(flcc)

    AddMessage("Processing complete.")

if __name__ == '__main__':
    main()