#-------------------------------------------------------------------------------
# Name: NG911_DataCheck
# Purpose: Collection of functions to check submitted NG911 data
#
# Author: Kristen Jordan Koenig, Kansas Data Access and Support Center
# kristen@kgs.ku.edu
#
# Created: 19/09/2014
#-------------------------------------------------------------------------------

from arcpy import (AddField_management, AddMessage, CalculateField_management, CopyRows_management, Statistics_analysis,
                   CreateTable_management, Delete_management, Exists, Describe,
                   ListFields, MakeFeatureLayer_management, MakeTableView_management, SelectLayerByAttribute_management,
                   SelectLayerByLocation_management, env, ListDatasets,
                   AddJoin_management, RemoveJoin_management, AddWarning, CopyFeatures_management,
                   Dissolve_management, DeleteField_management, DisableEditorTracking_management, EnableEditorTracking_management,
                   ExportTopologyErrors_management, Buffer_analysis, Intersect_analysis, 
                   Point, ListFeatureClasses, SpatialReference, Project_management)
from arcpy.da import InsertCursor, SearchCursor
from os import path, remove
from os.path import basename, dirname, join, exists, abspath
from time import strftime
from Validation_ClearOldResults import ClearOldResults
from Enhancement_AddTopology import add_topology
import NG911_GDB_Objects
from NG911_arcpy_shortcuts import deleteExisting, getFastCount, cleanUp, ListFieldNames, fieldExists
from MSAG_DBComparison import prep_roads_for_comparison
from inspect import getsourcefile
from ESB_ImportPSAP import getStewardWC
from Enhancement_AddFVCRNotes import addFVCRNotes
    
    
#import time
#from math import sin, cos, atan2, sqrt, asin, pi

def checkToolboxVersion():
    import json, urllib, sys

    v = sys.version_info.major
    if v != 2:
        if exists(r"C:\Program Files\ArcGIS\Pro\bin\Python\Lib\urllib"):
            sys.path.append(r"C:\Program Files\ArcGIS\Pro\bin\Python\Lib\urllib")
            import urllib.request

#   set lots of variables
    message, toolData, toolVersion, response, mostRecentVersion = "", "", "0", "", "X"

#    get version in the .json file that is already present
    me_folder = dirname(abspath(getsourcefile(lambda:0)))
    jsonFile = join(me_folder, "ToolboxVersion.json")

#   make sure the local json file exists
    if exists(jsonFile):
        toolData = json.loads(open(jsonFile).read())
        toolVersion = toolData["toolboxVersion"]["version"]
        userMessage("You are using toolbox version: " + toolVersion)

#   get version of toolbox live online
    url = "https://raw.githubusercontent.com/kansasgis/NG911/master/Scripts/ToolboxVersion.json"

#   Error trapping in case the computer is offline or can't get to the internet
    try:

        try:
            response = urllib.request.urlopen(url).read()
            mostRecentData = json.loads(response.decode('utf-8'))
        except:
            response = urllib.urlopen(url)
            mostRecentData = json.loads(response.read())

        mostRecentVersion = mostRecentData["toolboxVersion"]["version"]
        userMessage("Most current toolbox version: " + mostRecentVersion)
    except Exception as e:
        userMessage(str(e))
        message = "Unable to check toolbox version at this time."

#    compare the two
    if toolVersion == mostRecentVersion:
        message = "Your NG911 toolbox version is up-to-date."
    else:
        if mostRecentVersion != "X":
            message = """Your version of the NG911 toolbox is not the most recent version available.
            Your results might be different than results received upon data submission. Please
            download an up-to-date copy of the toolbox at
            https://github.com/kansasgis/NG911/raw/master/KansasNG911GISTools.zip"""

#   report back to the user
    return message


def writeToText(textFile, stuff):
    mode = "w"
    if exists(textFile):
        mode = "a"
    FILE = open(textFile,mode)
    FILE.writelines(stuff)
    FILE.close()


def userMessage(msg):
    #print stuff
    try:
        print(msg)
        AddMessage(msg)
    except:
        pass


def userWarning(msg):
    try:
        print(msg)
        AddWarning(msg)
    except:
        pass


def getAddFieldInfo(table):
    obj = NG911_GDB_Objects.getFCObject(table)
    lyr = basename(table)
    #field info
    if lyr == "TemplateCheckResults":
        fieldInfo = [(table, obj.DATEFLAGGED, "DATE", "", "", ""),(table, obj.DESCRIPTION, "TEXT", "", "", 250),(table, obj.CATEGORY, "TEXT", "", "", 25),
        (table, obj.CHECK, "TEXT", "", "", 40)]
    elif lyr == "FieldValuesCheckResults":
        fieldInfo = [(table, obj.DATEFLAGGED, "DATE", "", "", ""),(table, obj.DESCRIPTION, "TEXT", "", "", 250),
            (table, obj.LAYER, "TEXT", "", "", 25),(table, obj.FIELD, "TEXT", "", "", 25),(table, obj.FEATUREID, "TEXT", "", "", 38),
            (table, obj.CHECK, "TEXT", "", "", 40)]
    elif lyr == "DASC_Communication":
        fieldInfo = [(table, "NoteDate", "DATE", "", "", ""),(table, "Description", "TEXT", "", "", 250)]

    del lyr
    return fieldInfo


def getResultsFieldList(table):
    #get field info
    fieldInfo = getAddFieldInfo(table)
    fieldList = []
    #loop through added fields
    for fi in fieldInfo:
        #append the field name
        fieldList.append(fi[1])

    return fieldList


def calcAngle(pt1, pt2, pt3):
    import math, decimal
    context = decimal.Context(prec=5, rounding="ROUND_DOWN")
    #get length of side A
    a = abs(abs(pt1[0]) - abs(pt2[0]))
    b = abs(abs(pt1[1]) - abs(pt2[1]))
    A = context.create_decimal_from_float(math.hypot(a,b))

    #get length of side B
    c = abs(abs(pt2[0]) - abs(pt3[0]))
    d = abs(abs(pt2[1]) - abs(pt3[1]))
    B = context.create_decimal_from_float(math.hypot(c,d))

    #get length of side C
    e = abs(abs(pt3[0]) - abs(pt1[0]))
    f = abs(abs(pt3[1]) - abs(pt1[1]))
    C = context.create_decimal_from_float(math.hypot(e,f))

    q = ((A*A) + (B*B) - (C*C))/(2*A*B)

    degrees = 0

    if -1 < q < 1:
        #get angle
        radian = math.acos(q)

##    radian = math.atan((pt3x - pt2x)/(pt1y - pt2y))
        degrees = radian * 180 / math.pi
    return degrees


def RecordResults(resultType, values, gdb): # Guessed on whitespace formatting here. -- DT
    if resultType == "template":
        tbl = "TemplateCheckResults"
    elif resultType == "fieldValues":
        tbl = "FieldValuesCheckResults"
    elif resultType == "DASCmessage":
        tbl = "DASC_Communication"

    table = join(gdb, tbl)
    fieldList = []

    if not Exists(table):
        CreateTable_management(gdb, tbl)

    fieldInfo = getAddFieldInfo(table)

    for fi in fieldInfo:
        if not fieldExists(table, fi[1]):
        #add field with desired parameters if it doesn't already exist
            AddField_management(fi[0],fi[1],fi[2],fi[3],fi[4],fi[5])

    fieldList = getResultsFieldList(table)

    cursor = InsertCursor(table, fieldList)
    for row in values:
        try:
            cursor.insertRow(row)
        except:
            userMessage(row)
    del cursor
    
    
def verifyESBAlignment(pathsInfoObject):
    
    gdb = pathsInfoObject.gdbPath
    
    userMessage("Checking if geodatabase has been aligned with seamless statewide data...")
    
    # set reporting variables
    values = []
    today = strftime("%m/%d/%y")
    
    # set up variables for authoritative boundary
    ab = join(gdb, "NG911", "AuthoritativeBoundary")
    
    # verify the authoritative boundary is the same as the PSAP boundary sent out
    # get spatial reference of address points
    desc = Describe(ab)
    sr = desc.spatialReference
    factoryCode = str(sr.factoryCode)
    
    # use factoryCode to get the correct psap
    # get the ng911 folder, then navigate to the psap folder
    ng911_folder = dirname(dirname(abspath(getsourcefile(lambda:0))))
    psap_gdb = join(ng911_folder, "PSAP_Data", "PSAP_Data.gdb")
    psap_big = join(psap_gdb, "PSAP_%s" % factoryCode)
    
    # get stewards from authoritative boundary
    steward_wc = getStewardWC(ab)
    
    # create another where clause to see if the data has been updated
    adjusted_wc = steward_wc + " AND Adjusted = 1"
    
    # create where clause to see how many records are present
    adj = "adj"
    
    # make sure the psap data exists
    if Exists(psap_big):
        MakeFeatureLayer_management(psap_big, adj, adjusted_wc)
        
        # get the count
        adj_count = getFastCount(adj)
        
        # clean up
        Delete_management(adj)
    
        # this means that the PSAP has not been adjusted
        if adj_count == 0:
    
            # get area and length of authoritative boundary
            with SearchCursor(ab, ["SHAPE@AREA", "SHAPE@LENGTH"]) as ab_rows:
                for ab_row in ab_rows:
                    ab_area = ab_row[0]
                    ab_length = ab_row[1]
                  
            # clean up
            try:
                del ab_rows, ab_row
            except:
                pass
    
            # make psap feature layer
            p = "p"
            MakeFeatureLayer_management(psap_big, p, steward_wc)
            
            # get control area & length
            with SearchCursor(p, ["SHAPE@AREA", "SHAPE@LENGTH"]) as p_rows:
                for p_row in p_rows:
                    p_area = p_row[0]
                    p_length = p_row[1]
        
            # clean up
            try:
                del p_rows, p_row
            except:
                pass
            
            close = True
            
            # compare area & length
            area_diff = abs(ab_area - p_area)
            leng_diff = abs(ab_length - p_length)
            
            if area_diff > 150 or leng_diff > 20:
                userMessage("Area difference is %s, length difference is %s" % (str(area_diff), str(leng_diff)))
                close = False
            
            if close == False:
                dataset_report = "Notice: Authoritative boundary does not represent statewide seamless layer."
                val = (today, dataset_report, "AuthoritativeBoundary", "GEOMETRY", "", "Verify ESB Alignment")
                values.append(val)
                userWarning(dataset_report)
            else:
        
                # check to make sure ESBs are adjusted
                
                # create feature layer from authoritative boundary
                a = "a"
                MakeFeatureLayer_management(ab, a)
                
                fds = join(gdb, "NG911")
                
                env.workspace = fds
                
                esb_list = ListFeatureClasses("ESB*")
                
                for esb in esb_list:
                    full_path = join(fds, esb)
                    # get initial feature count
                    init_count = getFastCount(full_path)
                    
                    # make a feature layer
                    b = "b"
                    MakeFeatureLayer_management(full_path, b)
                    
                    SelectLayerByLocation_management(b, "WITHIN", a)
                    
                    sel_count = getFastCount(b)
                    
                    # check counts
                    if init_count > sel_count:
                        dataset_report = "Notice: %s has not been adjusted to statewide seamless layer." % esb
                        val = (today, dataset_report, esb, "GEOMETRY", "", "Verify ESB Alignment")
                        values.append(val)
                        userWarning(dataset_report)
                    else:
                        userMessage(esb + " has been adjusted to statewide seamless layer.")
                        
                    # clean up
                    Delete_management(b)
                    
                # clean up
                Delete_management(p)
                Delete_management(a)
                
    else:
        dataset_report = "Error: PSAP_Data.gdb cannot be accessed to verify ESB Alignment."
        val = (today, dataset_report, esb, "GEOMETRY", "", "Verify ESB Alignment")
        values.append(val)
        userWarning(dataset_report) 
    
    #record issues if any exist
    if values != []:
        RecordResults("fieldValues", values, gdb)
        userWarning("This geodatabase has not been adjusted to the statewide seamless layer. See FieldValuesCheckResults.")
    else:
        userMessage("This geodatabase has been adjusted to the statewide seamless layer.")
        
        
def getStewards(fc):
    
    output = r"in_memory\Summary"
    field = "STEWARD"

    if Exists(output):
        Delete_management(output)

    wc_submit = "SUBMIT = 'Y'"
    fl_submit = "fl_submit"
    MakeTableView_management(fc, fl_submit, wc_submit)

    #run frequency to get unique list in "STEWARD" field
    Statistics_analysis(fl_submit, output, [["STEWARD","COUNT"]], "STEWARD")

    #set up empty variables to hold list of stewards in the data
    stewardList = []

    #run search cursor to get list of stewards
    with SearchCursor(output, (field)) as rows:
        for row in rows:
            if row[0] is not None:
                stewardList.append(row[0])
                
    try:
        del rows, row
    except:
        pass
                
    # clean up
    Delete_management(output)
    Delete_management(fl_submit)
                
    return stewardList


def checkStewards(pathsInfoObject):

    gdb = pathsInfoObject.gdbPath

    userMessage("Checking data stewards...")

    #get current required layer list
    layerList = pathsInfoObject.gdbObject.requiredLayers

    # set reporting variables
    values = []
    today = strftime("%m/%d/%y")

    for fc in layerList:
        
        stewardList = getStewards(fc)

        # if it's a bigger list, get the list of stewards
        if len(stewardList) > 1:

            # list of PSAPs that submit data for multiple STEWARDs
            multiStewardDict = {"Crawford": ['484988', '485643'], 
                                "Leavenworth": ['485016', '485610', '2512205'], 
                                "Montgomery": ['485556', '485598'],
                                "Butler":['2393956','485543','484977'],
                                "Labette":['485014','485641'],
                                "Nemaha":['485029','472756'],
                                "Pottawatomie":['485038','2397188','485044'],
                                "Douglas":['484992','471362']}

            # set variables
            good = False
            county = ""

            # loop through the dictionary
            for co in multiStewardDict.keys():
                coList = multiStewardDict[co]
                diff = list(set(stewardList) - set(coList))

                # test to see if there are more stewards listed than are approved
                if diff == []:
                    good = True
                    county = co

            if not good:
                # report that an unapproved steward exists in the feature class
                dataset_report = "Error: STEWARD contains values not approved for this PSAP in " + basename(fc)
                val = (today, dataset_report, basename(fc), "STEWARD", "", "Check STEWARD")
                values.append(val)
                userWarning(dataset_report)

            else:
                # report that approved stewards exist
                userMessage("All stewards approved for %s %s" % (county, basename(fc)))

        else:
            userMessage("Stewards good for " + basename(fc))
            

    #record issues if any exist
    if values != []:
        RecordResults("fieldValues", values, gdb)
        userWarning("STEWARD contains values not approved for this PSAP. See FieldValuesCheckResults.")
    else:
        userMessage("Checked stewards.")

    try:
        del stewardList
    except:
        pass


def getParityReport(phrase):
    report = ""

    # create report based on what needs to be addressed
    if phrase[1:] == "00":
        report = "Address range is 0-0, but the parity is recorded as %s instead of Z" % (phrase[0])
    elif phrase[0] == "Z":
        report = "Parity is Z (0-0), but the address range is filled in with non-zero numbers."
    elif phrase[0] in "EO" and phrase[1:] != "00":
        report = "Parity is marked as %s but the ranges filled in are %s and %s" % (phrase[0], phrase[1], phrase[2])

    if report == "":
        report = "Send this phrase to kristen@kgs.ku.edu so she can create an error message for it: " + phrase
    return report


def checkParities(currentPathSettings):
    # parity "E' must have even ranges
    # parity "O" must have odd ranges
    # Parity "Z" must have 00 ranges
    # ranges that are 00 must have "Z" marked as the parity

    # set variables
    gdb = currentPathSettings.gdbPath
    roads = currentPathSettings.gdbObject.RoadCenterline
    rc_obj = NG911_GDB_Objects.getFCObject(roads)

    fields = [rc_obj.UNIQUEID, rc_obj.PARITY_R, rc_obj.PARITY_L, rc_obj.R_F_ADD, rc_obj.R_T_ADD, rc_obj.L_F_ADD, rc_obj.L_T_ADD]
    version = rc_obj.GDB_VERSION
    if version == "21":
        fields.append(rc_obj.AUTH_L)
        fields.append(rc_obj.AUTH_R)

    values = []
    recordType = "fieldValues"
    today = strftime("%m/%d/%y")
    filename = "RoadCenterline"
    check = "Check Parity"

    # these combinations are acceptable and will be used for comparisons
    a_phrase = ["EEE", "OOO", "Z00", "BOE", "BEO", "BEE", "BOO", "B0O", "B0E"]

    # make sure we're only checking roads for submission
    wc = "SUBMIT = 'Y'"
    rds = "rds"
    MakeFeatureLayer_management(roads, rds, wc)

    # run a search cursor on the road layer
    with SearchCursor(rds, fields) as rows:
        for row in rows:
            if None not in [type(row[3]), type(row[4]), type(row[5]), type(row[6])]:
                auth_l, auth_r = "Y",'Y'
                if version == 21:
                    auth_l = row[7]
                    auth_r = row[8]

                # create a dictionary that will hold even/odd/zero status of r/l/to/from numbers
                pDict = {}
                starter = 3

                # loop through all r/l/to/from address numbers to get their even/odd/zero status
                while starter < 7:
                    if row[starter] is not None:
                        if row[starter] == 0:
                            eo = "0"
                        else:
                            if (row[starter] % 2 == 0):
                                eo = "E"
                            else:
                                eo = "O"

                        pDict[str(starter)] = eo
                    else:
                        userWarning("You have one or more parities set as null. Please populate those fields.")
                    starter += 1

                # create a phrase for each side of the road
                try:
                    r_phrase = row[1] + pDict["3"] + pDict["4"]

                    l_phrase = row[2] + pDict["5"] + pDict["6"]

                    # compare the road side phrases with the phrases that are acceptable
                    # report road segments that don't match up correctly
                    if r_phrase not in a_phrase:
                        if auth_r == "Y":
                            r_report = getParityReport(r_phrase)
                            val = (today, "Error: R Side- " + r_report, filename, "", row[0], check)
                            values.append(val)
                    if l_phrase not in a_phrase:
                        if auth_l == "Y":
                            l_report = getParityReport(l_phrase)
                            val = (today, "Error: L Side- " + l_report, filename, "", row[0], check)
                            values.append(val)
                except:
                    if type(row[0]) is not None:
                        userWarning("Could not process parity check for road segment " + row[0] + ". Please check address ranges and parities for null values.")
                        val = (today, "Error: Could not process parity check. Look for null values.", filename, "", row[0], check)
                        values.append(val)
                    else:
                        userWarning("Could not process parity check for a road segment. Please check address ranges and parities for null values.")
            else:
                if type(row[0]) is not None:
                    val = (today, "Error: One or more address ranges are null", filename, "", row[0], check)
                    values.append(val)

    # report records
    if values != []:
        RecordResults(recordType, values, gdb)
        userWarning("Completed parity check. There were %s issues. Results are in table FieldValuesCheckResults" % (str(len(values))))
    else:
        userMessage("Completed parity check. No issues found.")


def checkRoadESN(currentPathSettings):
    userMessage("Checking road ESN values...")
    gdb = currentPathSettings.gdbPath
    esz = currentPathSettings.gdbObject.ESZ
    rc = currentPathSettings.gdbObject.RoadCenterline

    esz_obj = NG911_GDB_Objects.getFCObject(esz)
    rc_obj = NG911_GDB_Objects.getFCObject(rc)

    if Exists(rc) and Exists(esz):
        #set variables
        values = []
        recordType = "fieldValues"
        today = strftime("%m/%d/%y")
        filename = "RoadCenterline"
        wc_submit = rc_obj.SUBMIT + " = 'Y'"

        # define ESZ fields to examine
        esz_fields = (esz_obj.UNIQUEID, esz_obj.ESN, "SHAPE@XY")

        # define road fields to examine
        road_fields = [rc_obj.UNIQUEID, rc_obj.ESN_R, rc_obj.ESN_L, "OBJECTID", rc_obj.AUTH_L, rc_obj.AUTH_R, "SHAPE@", "SHAPE@XY"]

        # make feature layer from roads
        rd_lyr = "rd_lyr"
        MakeFeatureLayer_management(rc, rd_lyr, wc_submit)

        # make feature layer from ESZ
        esz_lyr = "esz_lyr"
        MakeFeatureLayer_management(esz, esz_lyr, wc_submit)

        if Exists(rc) and Exists(esz):
            #set variables
            values = []
            recordType = "fieldValues"
            today = strftime("%m/%d/%y")
            filename = "RoadCenterline"
            wc_submit = rc_obj.SUBMIT + " = 'Y'"

            # go through esz by esz
            with SearchCursor(esz_lyr, esz_fields, wc_submit) as rows:
                for row in rows:
                    # get ESZ variables & make a where clause
                    wc_esz = esz_obj.UNIQUEID + " = '" + row[0] + "' AND " + wc_submit

                    # single out this ESZ with a feature layer
                    eszf = "eszf"
                    MakeFeatureLayer_management(esz_lyr, eszf, wc_esz)

                    # select road features inside the current esz feature
                    SelectLayerByLocation_management(rd_lyr, "HAVE_THEIR_CENTER_IN", eszf)

                    # loop through the selected road features
                    with SearchCursor(rd_lyr, road_fields) as r_rows:
                        for r_row in r_rows:

                            # get the road variables
                            segid = r_row[0]
                            esn_r = r_row[1]
                            esn_l = r_row[2]
                            auth_l = r_row[4]
                            auth_r = r_row[5]
##                            print("%s: Right side- %s, %s Left side- %s %s" % (segid, esn_r, auth_r, esn_l, auth_l))

                            # see if the sides really don't match and one side isn't 0
                            if esn_r != esn_l and esn_r != '0' and esn_l != '0':
                                esn_list = [esn_l, esn_r]

                                # get A & B points of the road segment
                                A = r_row[6].firstPoint
                                B = r_row[6].lastPoint

                                # make a feature layer of the road
                                road_wc = rc_obj.UNIQUEID + " = '" + segid + "'"
                                rd_buff_lyr = "rd_buff_lyr"
                                MakeFeatureLayer_management(rd_lyr, rd_buff_lyr, road_wc)

                                # make a second feature layer from ESZ
                                esz_lyr_select = "esz_lyr_select"
                                MakeFeatureLayer_management(esz_lyr, esz_lyr_select)

                                # select which ESZ zones are close
                                SelectLayerByLocation_management(esz_lyr_select, "INTERSECT", rd_buff_lyr)

                                esz_esn_list = []

                                # see which eszs intersect the road segment
                                with SearchCursor(esz_lyr_select, (esz_obj.ESN)) as ez_rows:
                                    for ez_row in ez_rows:
                                        # put the intersecting esns in a list
                                        esz_esn_list.append(ez_row[0])

                                # clean up esz selection layer
                                Delete_management(esz_lyr_select)

                                # set up scoring system
                                esn_score = 0
                                l_score = 0
                                r_score = 0

                                # loop through the intersecting esz list, add points to the score
                                for ez_esn in esz_esn_list:
                                    if ez_esn in esn_list:
                                        esn_score += 1

                                # max esn_score here is 2

                                # create buffer of the line segment
                                temp_buffer = join("in_memory", "temp_buffer")
                                if Exists(temp_buffer):
                                    Delete_management(temp_buffer)

                                # buffer the road piece
                                Buffer_analysis(rd_buff_lyr, temp_buffer, "30 feet")

                                # intersect road buffer and esz boundaries
                                temp_buffer_intersect = join("in_memory", "temp_buffer_intersect")
                                if Exists(temp_buffer_intersect):
                                    Delete_management(temp_buffer_intersect)

                                Intersect_analysis([temp_buffer, esz], temp_buffer_intersect)

                                # run a search cursor on the intersection, weed out areas less than area 500
                                intersect_fields = [esz_obj.ESN, "SHAPE@TRUECENTROID", "SHAPE@AREA", "SHAPE@"]

                                esz_count = 0

                                with SearchCursor(temp_buffer_intersect, intersect_fields) as i_rows:
                                    for i_row in i_rows:

                                        if i_row[2] > 1500.0:
                                            esz_count += 1

                                            # get esn value
                                            esn_value_buff = i_row[0]

                                            # add points to the esn score if the esn is in the esn list
                                            if esn_value_buff in esn_list:
                                                esn_score += 1

                                            # perfect score here is 4+

                                            # get the centroid of that particular feature
                                            p_list = list(i_row[1])
                                            P = Point(p_list[0], p_list[1])

                                            # see if it's on the left or right
                                            # see what side of the road the esz is on
                                            direction = directionOfPoint(A, B, P)
                                            side_phrase = "ESN_" + direction

                                            # set variables based on that side of the road
                                            if direction == "R":
                                                # run a quick check
                                                if esn_value_buff == esn_r:
                                                    r_score += 1
                                            elif direction == "L":
                                                # run a quick check
                                                if esn_value_buff == esn_l:
                                                    l_score += 1

                                            esn_value_buff = ""

                                # work on generating proper reporting
                                reportStatus = False

                                # check scores
                                if esn_score == 0: # nothing matches
                                    reportStatus = True
                                    report = 'Notice: Segment ESN values %s and %s do not match ESNs of physical locations' % (esn_l, esn_r)
                                elif esn_score > 0 and esn_score <= 2:
                                    reportStatus = True
                                    if l_score == 0: # problem is maybe with the left side
                                        if r_score > 1: # problem might be on the right side actually
                                            report = 'Notice: One or both segment values does not match ESN of physical location'
                                        else:
                                            report = 'Notice: Segment ESN_L value %s does not match ESN of physical location' % (esn_l)
                                    elif r_score == 0: # problem is maybe with the right side
                                        if l_score > 1: # problem might be on the left side actually
                                            report = 'Notice: One or both segment values does not match ESN of physical location'
                                        else:
                                            report = 'Notice: Segment ESN_R value %s does not match ESN of physical location' % (esn_r)

                                    if l_score == 0 and r_score == 0:
                                        if esz_count > 1:
                                            report = 'Notice: Segment ESN values %s and %s may not match ESNs of physical locations' % (esn_l, esn_r)
                                        elif esz_count == 1:
                                            report = 'Notice: One or both segment values does not match ESN of physical location'
                                elif esn_score > 2:
                                    pass
                                    # this means things are probably fine

                                if reportStatus == True:
                                    val = (today, report, filename, side_phrase, segid, "Check Road ESN Values")
                                    values.append(val)

                                # clean up
                                Delete_management(rd_buff_lyr)
                                Delete_management(temp_buffer)
                                Delete_management(temp_buffer_intersect)

                            else:
                                esn_value = row[1]

                                # set issues to false to start with
                                L_issue = False
                                R_issue = False

                                # evaluate left side of the road considering authority
                                # the value is zero, skip it
                                if auth_l == 'Y' and str(esn_l) != "0" and esn_value != esn_l:
                                    L_issue = True

                                # evaluate right side of the road considering authority
                                # the value is zero, skip it
                                if auth_r == 'Y' and str(esn_r) != "0" and esn_value != esn_r:
                                    R_issue = True

                                # see which sides need to be reported (probably both)
                                sides = []

                                if L_issue == True:
                                    sides.append(rc_obj.ESN_L)
                                    esn_side = esn_l
                                if R_issue == True:
                                    sides.append(rc_obj.ESN_R)
                                    esn_side = esn_r

                                # report any issues that exist
                                if sides != []:
                                    side_phrase = "| ".join(sides)

                                    report = 'Notice: Segment %s value %s does not match ESN of physical location %s' % (side_phrase, esn_side, esn_value)
                                    val = (today, report, filename, side_phrase, segid, "Check Road ESN Values")
                                    values.append(val)

                                esn_side, esn_value, esn_l, esn_r = "", "", "", ""

                    # clean up feature class to repeat
                    Delete_management(eszf)

                del row, rows

        # clean up in memory esz
        Delete_management(esz_lyr)
        Delete_management(rd_lyr)

        #report records
        if values != []:
            RecordResults(recordType, values, gdb)
            userWarning("Completed road ESN check. There were %s issues. Results are in table FieldValuesCheckResults" % (str(len(values))))
        else:
            userMessage("Completed road ESN check. No issues found.")


def directionOfPoint(A, B, P):
    # code translated from https://www.geeksforgeeks.org/direction-point-line-segment/
    # subtracting co-ordinates of point A from
    # B and P, to make A as origin

    B.X -= A.X
    B.Y -= A.Y
    P.X -= A.X
    P.Y -= A.Y

    # Determining cross Product
    cross_product = B.X * P.Y - B.Y * P.X;

##    print(str(cross_product))

    # return RIGHT if cross product is positive
    if cross_product > 0:
        direction = "L"

    # return LEFT if cross product is negative
    elif cross_product < 0:
        direction = "R"

    # else, return zero
    else:
        direction = "Z"

    # return ZERO if cross product is zero.
    return direction


def checkDirectionality(fc, gdb):
    userMessage("Checking road directionality...")
    rc_obj = NG911_GDB_Objects.getFCObject(fc)

    if Exists(fc):
        #set variables
        values = []
        recordType = "fieldValues"
        today = strftime("%m/%d/%y")
        filename = "RoadCenterline"
        report = "Notice: Segment's address range is from high to low instead of low to high"

        fields = ["SHAPE@", rc_obj.UNIQUEID, rc_obj.L_F_ADD, rc_obj.L_T_ADD, rc_obj.R_F_ADD, rc_obj.R_T_ADD]

        version = rc_obj.GDB_VERSION
        if version == "21":
            fields.append(rc_obj.AUTH_L)
            fields.append(rc_obj.AUTH_R)

        lyr400 = "lyr400"

        #only check roads marked for submission
        MakeFeatureLayer_management(fc, lyr400, rc_obj.SUBMIT + "  = 'Y'")

        with SearchCursor(lyr400, fields) as rows:
            for row in rows:
                checkR, checkL = "Y", "Y"
                if version == "21":
                    checkL = row[6]
                    checkR = row[7]

                #get unique id and from/to values
                segid = row[1]
                addyList = [row[2],row[3],row[4],row[5]]

                #make sure it's not a blank road
                if addyList != [0,0,0,0]:

                    #set up values
                    lFrom = addyList[0]
                    lTo = addyList[1]
                    rFrom = addyList[2]
                    rTo = addyList[3]

                    check = "both"
                    issue = False

                    #see if we're working with any 0's
                    if lFrom == 0 or lTo == 0 or checkL == 'N':
                        check = "right"
                    elif rFrom ==0 or rTo == 0 or checkR == 'N':
                        check = "left"

                    #see if any road values don't follow low to high pattern
                    if check == "both":
                        if rTo < rFrom or lTo < lFrom:
                            issue = True
                    elif check == "right":
                        if rTo < rFrom:
                            issue = True
                    elif check == "left":
                        if lTo < lFrom:
                            issue = True

                    if issue == True:
                        val = (today, report, filename, "", segid, "Check Directionality")
                        values.append(val)

        Delete_management(lyr400)

    else:
        userWarning(fc + " does not exist")

    #report records
    if values != []:
        RecordResults(recordType, values, gdb)
        userWarning("Completed road directionality check. There were %s issues. Results are in table FieldValuesCheckResults" % (str(len(values))))
    else:
        userMessage("Completed road directionality check. No issues found.")

def checkESNandMuniAttribute(currentPathSettings):
    userMessage("Checking Address Point ESN/Municipality attributes...")

    gdb = currentPathSettings.gdbPath
    esz = currentPathSettings.gdbObject.ESZ
    address_points = currentPathSettings.gdbObject.AddressPoints
    muni = currentPathSettings.gdbObject.MunicipalBoundary

    esz_obj = NG911_GDB_Objects.getFCObject(esz)
    mb_obj = NG911_GDB_Objects.getFCObject(muni)
    a_obj = NG911_GDB_Objects.getFCObject(address_points)

    values = []
    recordType = "fieldValues"
    today = strftime("%m/%d/%y")
    filename = "AddressPoints"

    try:

        if Exists(address_points):

            addy_lyr = "addy_lyr"
            MakeFeatureLayer_management(address_points, addy_lyr)

            searchDict = {esz: (esz_obj.ESN, esz_obj.UNIQUEID), muni: (mb_obj.MUNI, mb_obj.UNIQUEID)}

            for layer in searchDict.keys():
                fieldList = searchDict[layer]
                if Exists(layer):

                    with SearchCursor(layer, fieldList) as polys:
                        for poly in polys:
                            feature = fieldList[0]
                            feature_value = poly[0]

                            #make feature layer
                            lyr1 = "lyr1"
##                            qry = fieldList[1] + " = '" + str(poly[1]) + "'"
                            qryList = [fieldList[1], " = '", str(poly[1]), "'"]
                            qry = "".join(qryList)
                            MakeFeatureLayer_management(layer, lyr1, qry)

                            #select by location
                            SelectLayerByLocation_management(addy_lyr, "INTERSECT", lyr1)

                            #loop through address points
                            with SearchCursor(addy_lyr, (feature, a_obj.UNIQUEID, a_obj.LOCTYPE, "OBJECTID")) as rows:
                                for row in rows:
                                    #get value
                                    value_addy = row[0]
                                    segID = row[1]
                                    objectID = row[3]

                                    if segID is not None:
                                        try:
                                            #see if the values match
                                            if value_addy.strip() != feature_value.strip():
                                                #this issue has been demoted to a notice
                                                report = "Notice: Address point %s does not match %s in %s layer. FeatureID is ObjectID" % (feature, feature, basename(layer))
                                                val = (today, report, filename, feature, segID, "Check ESN MUNI Attributes")
                                                values.append(val)
                                        except:
                                            userMessage("Issue comparing value for %s with OBJECTID: %s" % (feature, str(objectID)))
                                    else:
                                        userMessage("Issue comparing value for %s with OBJECTID: %s" % (feature, str(objectID)))
                                        report = "Notice: Address point %s does not match %s in %s layer. FeatureID is ObjectID" % (feature, feature, basename(layer))
                                        val = (today, report, filename, feature, str(objectID), "Check ESN MUNI Attributes")
                                        values.append(val)

                            Delete_management(lyr1)
                            del lyr1

                    try:
                        del poly, polys
                    except:
                        userMessage("Poly/polys didn't exist in the Muni/ESN check. No worries.")
            Delete_management(addy_lyr)

        else:
            userWarning(address_points + " does not exist")

    except Exception as e:
        report = "Notice: ESN/Municipality check did not run. " + str(e)
        val = (today, report, filename, "", "", "Check ESN MUNI Attributes")
        values.append(val)

    #report records
    if values != []:
        RecordResults(recordType, values, gdb)
        userWarning("Address point ESN/Municipality check complete. %s issues found. Results are in the FieldValuesCheckResults table." % (str(len(values))))
    else:
        userMessage("Address point ESN/Municipality check complete. No issues found.")


def checkAddressPointGEOMSAG(currentPathSettings):
	# get address point & road centerline path & object
    userMessage("Checking address point GEOMSAG values...")
    gdb = currentPathSettings.gdbPath
    rc = currentPathSettings.gdbObject.RoadCenterline
    ap = currentPathSettings.gdbObject.AddressPoints

    rc_obj = NG911_GDB_Objects.getFCObject(rc)
    ap_obj = NG911_GDB_Objects.getFCObject(ap)

    # prep for error reporting
    values = []
    recordType = "fieldValues"
    today = strftime("%m/%d/%y")
    filename = "AddressPoints"

	# set where clause to just get address points where GEOMSAG = 'Y' and SUBMIT = 'Y'
    ap_wc = "%s = 'Y' AND %s = 'Y' AND %s <> 'NO_MATCH'" % (ap_obj.SUBMIT, ap_obj.GEOMSAG, ap_obj.RCLMATCH)

	# get feature layer of those address points
    fl_ap = "fl_ap"
    MakeFeatureLayer_management(ap, fl_ap, ap_wc)

    # see if any of these exist
    count = getFastCount(fl_ap)

    if count > 0:

        # fields should include NGADDID, RCLMATCH, & RCLSIDE
        ap_fields = [ap_obj.UNIQUEID, ap_obj.RCLMATCH, ap_obj.RCLSIDE]

    	# set up a search cursor on those address points
        with SearchCursor(fl_ap, ap_fields) as rows:
            for row in rows:
                # set variables
                addid, segid, rclside = row[0], row[1], row[2]

                if rclside == "N":
                    report = "Error: RCLSIDE set to N while RCLMATCH has a valid NGSEGID. RCLSIDE should be R or L."
                    val = (today, report, filename, "RCLSIDE", addid, "Check Address Point GEOMSAG")
                    values.append(val)
                else:
                    # set up road centerline where clause
                    rc_wc_list = [rc_obj.UNIQUEID, " = '", segid, "'"]
                    rc_wc = "".join(rc_wc_list)

                    # set up road centerline
                    if rclside is not None and rclside not in ('', ' '):
                        rc_fields = [rc_obj.SUBMIT, "GEOMSAG" + rclside]
                    	# set up a search cursor on the RCLMATCH road segment
                        with SearchCursor(rc, rc_fields, rc_wc) as r_rows:
                            for r_row in r_rows:
    
                                # if GEOMSAG on the proper road side is "Y", mark that address point as an error
                                if r_row[0] == 'Y' and r_row[1] == 'Y':
                                    report = "Error: Point duplicates GEOMSAG with RCLMATCH record %s on %s side" % (str(segid), rclside)
                                    val = (today, report, filename, "GEOMSAG", addid, "Check Address Point GEOMSAG")
                                    values.append(val)

                    else:
                        report = "Error: RCLSIDE does not have a valid value"
                        val = (today, report, filename, "RCLSIDE", addid, "Check Address Point GEOMSAG")
                        values.append(val)

    #report records
    if values != []:
        RecordResults(recordType, values, gdb)
        userWarning("Address point GEOMSAG check complete. %s issues found. Results are in the FieldValuesCheckResults table." % (str(len(values))))
    else:
        userMessage("Address point GEOMSAG check complete. No issues found.")

    # clean up
    cleanUp([fl_ap])


def checkUniqueIDFrequency(currentPathSettings):
    gdb = currentPathSettings.gdbPath
    esbList = currentPathSettings.gdbObject.esbList
    fcList = currentPathSettings.gdbObject.fcList
    esb_uniqueid = "NGESBID"

    layerList = []

    env.workspace = gdb
    table = "ESB_IDS"

    #create temp table of esbID's
    if len(esbList) > 1 and esbList[0] != esbList[1]:
        layerList = ["ESB_IDS"]

        deleteExisting(table)

        CreateTable_management(gdb, table)

        AddField_management(table, esb_uniqueid, "TEXT", "", "", 38)
        AddField_management(table, "ESB_LYR", "TEXT", "", "", 30)

        esbFields = (esb_uniqueid)

        #copy ID's & esb layer type into the table
        for esb in esbList:
            with SearchCursor(esb, esbFields) as rows:
                for row in rows:
                    typeEsb = basename(esb)
                    cursor = InsertCursor(table, (esb_uniqueid, 'ESB_LYR'))
                    cursor.insertRow((row[0], typeEsb))

        try:
            #clean up
            del rows, row, cursor
        except:
            userMessage("objects cannot be deleted, they don't exist")

    # make sure all the proper layers actually exist
    for fc in fcList:
        if Exists(fc):
            layerList.append(basename(fc))
        else:
            msg = "%s does not exist" % (fc)
            userWarning(msg)
            today = strftime("%m/%d/%y")
            values = [(today, msg)]
            RecordResults("DASCmessage", values, gdb)

    # set up reporting
    values = []
    recordType = "fieldValues"
    today = strftime("%m/%d/%y")

    #loop through layers in the gdb that aren't esb & ESB_IDS
    for layer in layerList:
        try:
            ids = []
            obj = NG911_GDB_Objects.getFCObject(layer)
            with SearchCursor(layer, (obj.UNIQUEID)) as rows:
                for row in rows:
                    if row[0] not in ids:
                        ids.append(row[0])
                    else:
                        #report duplicate IDs
                        report = "Error: %s is a duplicate ID" % (str(row[0]))
##                        if stringESBReport != "":
##                            report = report + " in " + stringESBReport
                        val = (today, report, layer, obj.UNIQUEID, row[0], "Check Unique IDs")
                        values.append(val)

##            freq_table = layer + "_freq"
##            deleteExisting(freq_table)
##            obj = NG911_GDB_Objects.getFCObject(layer)
##            Statistics_analysis(layer, freq_table, [[obj.UNIQUEID,"COUNT"]], obj.UNIQUEID)
##
##            #set parameters for the search cursor
##            where_clause = "FREQUENCY > 1"
##
##            fields = (obj.UNIQUEID, "FREQUENCY")
##
##            fl = "fl"
##
##            MakeTableView_management(freq_table, fl, where_clause)
##
##            if getFastCount(fl) > 0:
##
##                #set a search cursor with just the unique ID field
##                with SearchCursor(freq_table, fields, where_clause) as rows2:
##                    stringESBReport = ""
##                    for row2 in rows2:
##                        reportLayer = layer
##                        if layer == "ESB_IDS":
##                            reportLayer = "ESB"
##                            stringEsbInfo = []
##                            wc2List = [esb_uniqueid, " = '", str(row2[0]), "'"]
####                            wc2 = esb_uniqueid + " = '" + str(row2[0]) + "'"
##                            wc2 = "".join(wc2List)
##                            with SearchCursor("ESB_IDS", ("ESB_LYR"), wc2) as esbRows:
##                                for esbRow in esbRows:
##                                    stringEsbInfo.append(esbRow[0])
##
##                            stringESBReport = " and ".join(stringEsbInfo)
##
##                        #report duplicate IDs
##                        report = "Error: %s is a duplicate ID" % (str(row2[0]))
##                        if stringESBReport != "":
##                            report = report + " in " + stringESBReport
##                        val = (today, report, reportLayer, esb_uniqueid, row2[0], "Check Unique IDs")
##                        values.append(val)
##
##            cleanUp([freq_table, fl])

        except Exception as e:
            userWarning(str(e))
            userMessage("Issue with " + layer)

    #report duplicate records
    if values != []:
        RecordResults(recordType, values, gdb)
        userWarning("Checked unique ID frequency. There were %s issues. Results are in table FieldValuesCheckResults." % (str(len(values))))
    else:
        userMessage("All ID's are unique.")

    #if it exists, clean up table
    deleteExisting(table)

def checkFrequency(fc, freq, fields, gdb, fullFreq):

    if fullFreq == "true":
        userMessage("Checking record frequency...")
    elif fullFreq == "false":
        userMessage("Checking dual carriageways...")

    obj = NG911_GDB_Objects.getFCObject(fc)

    if Exists(fc):
        fl = "fl"
        fl1 = "fl1"
        wc = "FREQUENCY > 1"

        #remove the frequency table if it exists already
        try:
            deleteExisting(freq)
        except:
            userMessage("Please manually delete %s and then run the frequency check again" % (freq))

        if not Exists(freq):

            # set name of exported dbf
            folder = dirname(dirname(dirname(fc)))
            dbf = join(folder, "freq_shp_temp.dbf")

            # make sure the shp copy doesn't exist
            if Exists(dbf):
                Delete_management(dbf)

            # export the feature class to a shapefile
            CopyRows_management(fc, dbf)

            #set up parameters to report duplicate records
            filename = basename(fc)
            values = []
            recordType = "fieldValues"
            today = strftime("%m/%d/%y")
            hno_yes = 1

            #test to see if the HNO field is a number or text
            if basename(freq) == "AP_Freq":
                ap_fields = ListFields(fc)

                for ap_field in ap_fields:
                    if ap_field.name == "HNO" and ap_field.type != "Integer":
                        hno_yes = 0

            if hno_yes == 1:

                #see if we're working with address points or roads, create a where clause
                if basename(freq) == "AP_Freq":
##                    wc1 = obj.HNO + " <> 0 and " + obj.LOCTYPE + " = 'PRIMARY' AND SUBMIT = 'Y'"
                    wc1List = [obj.HNO, " <> 0 and ", obj.LOCTYPE, " = 'PRIMARY' AND SUBMIT = 'Y'"]
                elif basename(freq) == "Road_Freq":
##                    wc1 = obj.L_F_ADD + " <> 0 AND " + obj.L_T_ADD + " <> 0 AND " + obj.R_F_ADD + " <> 0 AND " + obj.R_T_ADD + " <> 0 AND SUBMIT = 'Y'"
                    wc1List = [obj.L_F_ADD, " <> 0 AND ", obj.L_T_ADD, " <> 0 AND ", obj.R_F_ADD, " <> 0 AND ", obj.R_T_ADD, " <> 0 AND SUBMIT = 'Y'"]
                wc1 = "".join(wc1List)

                #run query on fc to make sure 0's are ignored
                MakeTableView_management(dbf, fl1, wc1)

                #set up field strings for statistics tool
                fields = fields.replace(";;", ";")
                fieldCountList = fields.replace(";", " COUNT;") + " COUNT"

                #split field names
                fieldsList = fields.split(";")
                fl_fields = [f.strip() for f in fieldsList]

                #run frequency analysis
                try:
                    Statistics_analysis(fl1, freq, fieldCountList, fields)

                    #make feature layer
                    MakeTableView_management(freq, fl, wc)

                    #get count of the results
                    if getFastCount(fl) > 0:

                        #get field count
                        fCount = len(fl_fields)

                        #get the unique ID field name
                        id1 = obj.UNIQUEID

                        #run a search on the frequency table to report duplicate records
                        with SearchCursor(freq, fl_fields, wc) as rows:
                            for row in rows:
                                i = 0
                                #generate where clause to find duplicate ID's
                                wcList = []
                                while i < fCount:
                                    stuffList = []
                                    if row[i] != None:

                                        # see if the data type is an int
                                        if type(row[i]) != int:
                                            # if not, we need to include quotes
                                            stuffList = [" = '", row[i], "' "]
                                        else:
                                            # if it is an int, we don't want quotes included
                                            stuffList = [" = ", str(row[i]), " "]
                                    else:
                                        # or put in null
                                        stuffList = [" is null "]

                                    # make one statement from the various field components
                                    stuff = "".join(stuffList)

                                    # add to the official where clause list
                                    wcList = wcList + [str(fl_fields[i]), stuff, "and "]
                                    i += 1

                                #trim last "and " off where clause
                                if wcList[-1] == "and ":
                                    wcList.pop()

                                # create the official string where clause statement
                                wc = "".join(wcList)

                                #find records with duplicates to get their unique ID's
                                with SearchCursor(fl1, (id1), wc) as sRows:
                                    for sRow in sRows:
                                        fID = sRow[0]

                                        #add information to FieldValuesCheckResults for all duplicates
                                        if fullFreq == "true":
                                            report = "Error: %s has duplicate field information" % (str(fID))
                                        else:
                                            report = "Notice: %s has duplicate address range information" % (str(fID))
                                        val = (today, report, filename, "", str(fID), "Check " + filename + " Frequency")
                                        values.append(val)

                    else:
                        if fullFreq == "true":
                            userMessage(filename + ": Checked frequency. All records are unique.")
                        elif fullFreq == "false":
                            userMessage(filename + ": Checked dual carriageways. All records are unique.")

                except Exception as e:
                    userMessage(str(e))
                    report = "Error: Could not complete duplicate record check. " + str(e)
                    val = (today, report, filename, "", "", "Check " + filename + " Frequency")
                    values.append(val)

                #report duplicate records
                if values != []:
                    RecordResults(recordType, values, gdb)
                    userWarning("Checked frequency. There were %s duplicate records. Individual results are in table FieldValuesCheckResults" % (str(len(values))))

                #clean up
                try:
                    cleanUp([fl, fl1, freq])
                    if Exists(dbf):
                        Delete_management(dbf)
                except:
                    userMessage("Issue deleting a feature layer or frequency table.")
            else:
                userWarning("HNO field of Address Points is not an integer field.")
                val1 = (today, "Error: HNO field of Address Points is not an integer field", filename, "", "", "Check " + filename + " Frequency")
                values1 = [val1]
                RecordResults(recordType, values1, gdb)
    else:
        userWarning(fc + " does not exist")


def checkLayerList(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    esb = pathsInfoObject.gdbObject.esbList

    values = []
    today = strftime("%m/%d/%y")

    #make sure the NG911 feature dataset exists
    userMessage("Checking feature dataset name...")
    env.workspace = gdb

    datasets = ListDatasets()

    if "NG911" not in datasets:
        dataset_report = "Error: No feature dataset named 'NG911' exists"
        val = (today, dataset_report, "Template")
        values.append(val)
        userMessage(dataset_report)

    userMessage("Checking geodatabase layers...")
    #get current required layer list
    layerList = pathsInfoObject.gdbObject.requiredLayers

    for l in layerList:
        if not Exists(l):
            report = "Error: Required layer %s is not in geodatabase." % (l)
            userMessage(report)
            val = (today, report, "Layer", "Check Layer List")
            values.append(val)

    # make sure ESB layers have the right names
    env.workspace = join(gdb, "NG911")
    fcs = ListFeatureClasses()
    esb_count = 0
    for esb in ["ESB_EMS", "ESB_LAW", "ESB_FIRE"]:
        if esb in fcs:
            esb_count += 1

    if esb_count == 0 and "ESB" not in fcs:
        report = "Error: No ESB layers are present in geodatabase." % (esb)
        userMessage(report)
        val = (today, report, "Layer", "Check Layer List")
        values.append(val)

    if 0 < esb_count < 3:
        report = "Error: ESB layers %s may not be named correctly in geodatabase." % (esb)
        userMessage(report)
        val = (today, report, "Layer", "Check Layer List")
        values.append(val)

    #record issues if any exist
    if values != []:
        RecordResults("template", values, gdb)
        userWarning("Not all required geodatabase datasets and/or layers are not present. See TemplateCheckResults.")
    else:
        userMessage("Checked that required layers are present.")


def getKeyword(layer, esb):
    keyword = "EmergencyBoundary" if layer in esb else layer
    return keyword


def getRequiredFields(folder):
    path1 = path.join(folder, "NG911_RequiredFields.txt")

    #create a field definition dictionary
    rfDict = {}

    #make sure file path exists
    if path.exists(path1):
        fieldDefDoc = open(path1, "r")

        #parse the text to populate the field definition dictionary
        for line in fieldDefDoc.readlines():
            stuffList = line.split("|")
            #set up values
            fc = stuffList[0]
            field = stuffList[1].rstrip()
            fieldList = []

            #see if field list already exists
            if fc in rfDict.keys():
                fieldList = rfDict[fc]

            #append new value onto list
            fieldList.append(field)

            #set value as list
            rfDict[fc] = fieldList
    else:
        userMessage("The file %s is required to run field checks." % (path1))

    return rfDict


def getFieldDomain(domain, folder):

    # get full path to domain
    docPath = path.join(folder, domain + "_Domains.txt")

    domainDict = {}

    #make sure path exists
    if path.exists(docPath):
        doc = open(docPath, "r")

        #parse the text to population the field definition dictionary
        for line in doc.readlines():
            if line != "\n":
                stuffList = line.split("|")
                domainDict[stuffList[0].strip()] = stuffList[1].strip()

    else:
        userWarning("The file %s is required to run a domain check." % (docPath))

    return domainDict


def launchRangeFinder(f_add, t_add, parity):
    sideRange = []

    if [f_add, t_add] != [0,0]:

        if parity != 'Z':
            # set the counter for the range, it'll usually be 2
            range_counter = 2
            if parity == "B": # if the range is B (both sides), the counter = 1
                range_counter = 1

            # get the range
            sideRange = []
            sideRange = list(range(f_add, t_add + range_counter, range_counter))
            high = t_add

            # if the range was high to low, flip it
            if sideRange == []:
                sideRange = list(range(t_add, f_add + range_counter, range_counter))
                high = f_add

            # make sure the range didn't extend beyond the high
            if len(sideRange) > 1:
                while sideRange[-1] > high:
                    sideRange.pop()

    return sideRange


def checkMsagLabelCombo(msag, label, overlaps, rd_fc, fields, msagList, name_field, txt):
    address_list = []
    checked_segids = []
    dict_ranges = {}
    for msagfield in msagList:
        side = msagfield[-1]

        if "'" in label:
            label = label.replace("'", "''")
        
        wc = "%s = '%s' AND %s = '%s' AND SUBMIT = 'Y' AND AUTH_%s = 'Y' and GEOMSAG%s = 'Y'" % (msagfield, msag, 
                                                                                                 name_field, label,
                                                                                                 side, side)

        with SearchCursor(rd_fc, fields, wc) as rows:
            for row in rows:
                l_f_add, l_t_add, r_f_add, r_t_add, parity_l, parity_r, segid, msagco_l, msagco_r = row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7].strip(), row[8].strip()
                if segid + "|2" not in checked_segids:

                    # deal with the left side first
                    for side_of_road in [[l_f_add, l_t_add, parity_l, msagco_l, "L"],[r_f_add, r_t_add, parity_r, msagco_r, "R"]]:

                        # make sure the range isn't 0,0 or null
                        if [side_of_road[0], side_of_road[1]] != [0,0] and None not in [side_of_road[0], side_of_road[1]]:
                            if side_of_road[3] == msag:
                                thisRange = launchRangeFinder(side_of_road[0], side_of_road[1], side_of_road[2])
                                if thisRange != []:
                                    dict_ranges[segid + "|" + side_of_road[4]] = thisRange
                                    for lR in thisRange:
                                        if lR not in address_list:
                                            address_list.append(lR)
                                        else:
                                            # find out where the overlap is
                                            # lR is the value that exists somewhere else
                                            for key in dict_ranges:
                                                values = dict_ranges[key]
                                                if lR in values:
                                                    k_segid = key.split("|")[0]
                                                    # make sure the script isn't comparing a road segment to itself
                                                    writeToText(txt, "Address " + str(lR) + " overlaps between NGSEGID " + str(k_segid) + " and NGSEGID " + str(segid) + "\n")
                                                    if k_segid not in overlaps:
                                                        overlaps.append(k_segid)
                                                    # this means there's an overlap & we found the partner
                                                    if segid not in overlaps:
                                                        overlaps.append(segid)

                    if msagco_l == msagco_r:
                        checked_segids.append(segid + "|2")
                    else:
                        if segid + "|1" in checked_segids:
                            checked_segids.remove(segid + "|1")
                            checked_segids.append(segid + "|2")
                        else:
                            checked_segids.append(segid + "|1")

    del checked_segids, address_list, dict_ranges, row, rows
    return overlaps


def FindOverlaps(working_gdb):
##    start_time = time.time()
    userMessage("Checking overlapping address ranges...")
    #get gdb object
    gdb_object = NG911_GDB_Objects.getGDBObject(working_gdb)

    env.workspace = working_gdb
    env.overwriteOutput = True
    rd_fc = gdb_object.RoadCenterline         # Our street centerline feature class
    final_fc = join(gdb_object.gdbPath, "AddressRange_Overlap")
    rd_object = NG911_GDB_Objects.getFCObject(rd_fc)
    name_field = "NAME_OVERLAP"
    parity_l = rd_object.PARITY_L
    parity_r = rd_object.PARITY_R
    left_from = rd_object.L_F_ADD         # The left from address field
    left_to = rd_object.L_T_ADD            # The left to address field
    right_from = rd_object.R_F_ADD        # The right from address field
    right_to = rd_object.R_T_ADD            # The right to address field
    msagco_l = rd_object.MSAGCO_L
    msagco_r = rd_object.MSAGCO_R
    segid = rd_object.UNIQUEID
    auth_l = rd_object.AUTH_L
    auth_r = rd_object.AUTH_R
    geomsag_l = rd_object.GEOMSAGL
    geomsag_r = rd_object.GEOMSAGR
    fields = (left_from,left_to,right_from,right_to,parity_l,parity_r,segid,msagco_l,msagco_r)
    msagList = [msagco_l, msagco_r]
    txt = working_gdb.replace(".gdb", "_OverlappingAddressSpecifics.txt")
    if exists(txt):
        remove(txt)

    # set up issue reporting variables
    values = []
    resultType = "fieldValues"
    today = strftime("%m/%d/%y")

    # turn off editor tracking
    DisableEditorTracking_management(rd_fc, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")

    # clean up if final overlap output already exists
    if Exists(final_fc):
        Delete_management(final_fc)

    # add the NAME_OVERLAP field
    if not fieldExists(rd_fc, name_field):
        AddField_management(rd_fc, name_field, "TEXT", "", "", 150)
    
    # calculate the label field
    code_block = """def calc_name(prd, stp, rd, sts, pod, pom):
    row = [prd, stp, rd, sts, pod, pom]
    field_count = len(row)
    start_int = 0
    lstLabel = []

    while start_int < field_count:
        if row[start_int] is not None and row[start_int] not in ("", " "):
            lstLabel.append(str(row[start_int]))
        start_int += 1
    return " ".join(lstLabel)"""
    expression = "calc_name(!PRD!, !STP!, !RD!, !STS!, !POD!, !POM!)"
    CalculateField_management(rd_fc, name_field, expression, "PYTHON_9.3", code_block)

    # make sure the text file notification only shows up if there's an overlap problem
    overlap_error_flag = 0

##    try:
    if 1 == 1:
        already_checked = []
        rd_fields = [msagco_l, msagco_r, name_field, segid, auth_l, auth_r, geomsag_l, geomsag_r]

        overlaps = []

        with SearchCursor(rd_fc, rd_fields, "SUBMIT = 'Y'") as all_rows:
            for all_row in all_rows:

                # in the 2.1 geodatabase, make sure only authoritative sides are checked
                checkL, checkR = 0,0
                if all_row[4] == "Y" and all_row[6] == "Y":
                    checkL = 1
                if all_row[5] == "Y" and all_row[7] == "Y":
                    checkR = 1

                # make sure each MSAGCO_X is populated with a value
                i = 0
                while i < 2:
                    if all_row[i] is None or all_row[i] in ('', ' '):
                        if i == 0:
                            checkL = 0 # this means the left side MSAG isn't a thing
                            report = "Error: MSAGCO_L needs to be a real value"
                            val = (today, report, basename(rd_fc), "MSAGCO_L", all_row[3], "Overlapping Address Range")
                            values.append(val)
                        elif i == 1:
                            checkR = 0 # this means the right side MSAG isn't a thing
                            report = "Error: MSAGCO_R needs to be a real value"
                            val = (today, report, basename(rd_fc), "MSAGCO_R", all_row[3], "Overlapping Address Range")
                            values.append(val)

                    i += 1


                if checkL == 1 and all_row[0] + "|" + all_row[2] not in already_checked:
                    # check the left side MSAGCO & LABEL combo
                    overlaps = checkMsagLabelCombo(all_row[0], all_row[2], overlaps, rd_fc, fields, msagList, name_field, txt)
                    already_checked.append(all_row[0] + "|" + all_row[2])
                    
                runRight = False
                    
                # add some logic in cases where the right side would need to be checked
                if checkL == 0 and checkR == 1:
                    runRight = True
                    
                if all_row[0] != all_row[1]:
                    runRight = True

                # if the r & l msagco are different, run the right side
                if checkR == 1 and runRight and all_row[1] + "|" + all_row[2] not in already_checked:
                    overlaps = checkMsagLabelCombo(all_row[1], all_row[2], overlaps, rd_fc, fields, msagList, name_field, txt)
                    already_checked.append(all_row[1] + "|" + all_row[2])

##        now_time = time.time()
##        print("Marker: done checking MSAGs. Elapsed time was %g seconds" % (now_time - start_time))

        if overlaps != []:
            overlap_error_flag = 1
            userMessage("%s overlapping address range segments found. Please see %s for overlap results." % (str(len(overlaps)), final_fc))
            # add code here for exporting the overlaps to a feature class
            wcList = [segid, " in ('" +"','".join(overlaps), "')"]
            wc = "".join(wcList)
##            wc = segid + " in ('" +"','".join(overlaps) + "')"
            overlaps_lyr = "overlaps_lyr"
            MakeFeatureLayer_management(rd_fc, overlaps_lyr, wc)

            # get the count of persisting overlaps
            count = getFastCount(overlaps_lyr)

            # if there are more than 1, copy the layer
            if count > 0:
                CopyFeatures_management(overlaps_lyr, final_fc)

            Delete_management(overlaps_lyr)

            # add reporting for overlapping segments
            for ov in overlaps:
                report = "Error: %s has an overlapping address range." % (str(ov))
                val = (today, report, basename(rd_fc), "", ov, "Overlapping Address Range")
                values.append(val)

##            now_time = time.time()
##            print("Marker: done creating error report. Elapsed time was %g seconds" % (now_time - start_time))

        else:
            userMessage("No overlaping address ranges found.")
##
##            now_time = time.time()
##            print("Marker: skipped error reporting. Elapsed time was %g seconds" % (now_time - start_time))

##    except Exception as e:
##        userWarning(str(e))

    # delete field if need be
    if fieldExists(rd_fc, name_field):
        try:
            DeleteField_management(rd_fc, name_field)
        except:
            pass

    if values != []:
        RecordResults(resultType, values, working_gdb)
        userWarning("Completed checking overlapping addresses: %s issues found. See table FieldValuesCheckResults for results." % (str(len(values))))
        if overlap_error_flag == 1:
            userWarning("All specific overlaps with corresponding NGSEGIDs are listed in " + txt)
    else:
        userMessage("Completed checking overlapping addresses: 0 issues found")

##    now_time = time.time()
##    print("Marker: done reporting. Elapsed time was %g seconds" % (now_time - start_time))

    # turn editor tracking back on
    EnableEditorTracking_management(rd_fc, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")

##    end_time = time.time()
##    print("Elapsed time was %g seconds" % (end_time - start_time))


def checkRCLMATCH(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    ap = pathsInfoObject.gdbObject.AddressPoints
    rc = pathsInfoObject.gdbObject.RoadCenterline

    a_obj = NG911_GDB_Objects.getFCObject(ap)
    r_obj = NG911_GDB_Objects.getFCObject(rc)

    userMessage("Checking RCLMATCH field...")
    #set up parameters to report duplicate records
    values = []
    resultType = "fieldValues"
    today = strftime("%m/%d/%y")

    # set variables for comparison
    name_field = "NAME_COMPARE"
    code_field = "CODE_COMPARE"
    city_field = a_obj.MSAGCO
    road_field_list = ["NAME_COMPARE", "PRD", "STP", "RD", "STS", "POD", "POM"]
    addy_field_list = ["NAME_COMPARE", "PRD", "STP", "RD", "STS", "POD", "POM"]

    # set holders for issues
    ngsegid_doesnt_exist = []
    doesnt_match_range = []
    streets_or_msags_dont_match = []
    null_values = []
    no_rclside = []

    # prep roads & address points for comparison

    # copy the roads to a table for comparison
    rc_table_view = "rc_table_view"
    rt = join("in_memory", "rcTable")
    if Exists(rt):
        Delete_management(rt)
    wc = r_obj.SUBMIT + " = 'Y'"
    MakeTableView_management(rc, rc_table_view, wc)
    CopyRows_management(rc_table_view, rt)
    prep_roads_for_comparison(rt, name_field, [code_field + "_L", code_field +"_R"], [ city_field + "_L", city_field + "_R"], road_field_list)

    # copy address points to a table for comparison
    ap_table_view = "ap_table_view"
    at = join("in_memory", "apTable")
    if Exists(at):
        Delete_management(at)
    wcList = [a_obj.SUBMIT, " = 'Y' AND ", a_obj.RCLMATCH, " <> 'NO_MATCH'"]
    wc = "".join(wcList)
    MakeFeatureLayer_management(ap, ap_table_view, wc)
    CopyRows_management(ap_table_view, at)

    prep_roads_for_comparison(at, name_field, [code_field], [city_field], addy_field_list)

    # make address points into a table view
    a = "a"
    MakeTableView_management(at, a)

    # check to see if any RCLSIDE values are null
    wc_rclside = "RCLSIDE IS NULL and SUBMIT = 'Y' and LOCTYPE = 'PRIMARY'"
    rcl = "rcl"
    SelectLayerByAttribute_management(a, "NEW_SELECTION", wc_rclside)
    rcl_count = getFastCount(a)

    if rcl_count > 0:
        with SearchCursor(a, ("NGADDID")) as rows:
            for row in rows:
                no_rclside.append(row[0])
            del row, rows

    # clean up and clear selection
    Delete_management(rcl)
    del rcl_count
    SelectLayerByAttribute_management(a, "CLEAR_SELECTION")

    # join road & address table based on RCLMATCH & NGSEGID
    r = "r"
    MakeTableView_management(rt, r)
    AddJoin_management(a, a_obj.RCLMATCH, r, r_obj.UNIQUEID)

    a_ngaddid = "apTable.NGADDID"

    # this will catch if the NGSEGID doesn't exist in the road centerline file
    SelectLayerByAttribute_management(a, "NEW_SELECTION", "rcTable.NGSEGID is null")
    count = getFastCount(a)

    # get a list of all the NGADDIDs with the issue that the RCLMATCH doesn't exist in the road centerline
    if count > 0:
        with SearchCursor(a, (a_ngaddid)) as rows:
            for row in rows:
                ngsegid_doesnt_exist.append(row[0])
            del row, rows

    # clear selection
    SelectLayerByAttribute_management(a, "CLEAR_SELECTION")

    # jump into the records to see where things aren't matching
    # select records where code_compare doesn't match
    sides = ["L", "R"]

    # split up points by side
    for side in sides:

        # first, toss out any where code compares don't match
##        compare_codes_wc = a_obj.RCLSIDE + " = '" + side + "' AND rcTable.NGSEGID is not null AND apTable.CODE_COMPARE <> rcTable.CODE_COMPARE_" + side
        compare_codes_wc_list = [a_obj.RCLSIDE, " = '", side, "' AND rcTable.NGSEGID is not null AND apTable.CODE_COMPARE <> rcTable.CODE_COMPARE_", side]
        compare_codes_wc = "".join(compare_codes_wc_list)
        SelectLayerByAttribute_management(a, "NEW_SELECTION", compare_codes_wc)
        count = getFastCount(a)

        # see if any address points had the problem
        if count > 0:
            with SearchCursor(a, (a_ngaddid)) as rows:
                for row in rows:
                    streets_or_msags_dont_match.append(row[0])
                del row, rows

        # clear selection
        SelectLayerByAttribute_management(a, "CLEAR_SELECTION")

        # look at ranges
##        compare_ranges_wc = a_obj.RCLSIDE + " = '" + side + "' AND rcTable.NGSEGID is not null AND apTable.CODE_COMPARE = rcTable.CODE_COMPARE_" + side
        compare_ranges_wc_list = [a_obj.RCLSIDE, " = '", side, "' AND rcTable.NGSEGID is not null AND apTable.CODE_COMPARE = rcTable.CODE_COMPARE_", side]
        compare_ranges_wc = "".join(compare_ranges_wc_list)

        # get count of potential problems
        SelectLayerByAttribute_management(a, "NEW_SELECTION", compare_ranges_wc)
        count = getFastCount(a)

        if count > 0:

            flds = (a_ngaddid, "apTable.HNO", "rcTable.%s_F_ADD" % (side), "rcTable.%s_T_ADD" % (side), "rcTable.PARITY_%s" % (side))

            with SearchCursor(a, flds, compare_ranges_wc) as rows:
                for row in rows:
                    if None not in [type(row[2]), type(row[3])]:

                        # set the counter for the range, it'll usually be 2
                        range_counter = 2
                        if row[4] == "B": # if the range is B (both sides), the counter = 1
                            range_counter = 1

                        # get the range by the specified count
                        if row[3] > row[2]:
                            sideRange = list(range(row[2], row[3] + 2, range_counter))

                        # if the range was high to low, flip it
                        else:
                            sideRange = list(range(row[3], row[2] + 2, range_counter))

                        # see if HNO is in the range
                        if int(row[1]) not in sideRange:
                            doesnt_match_range.append(row[0])
    ##                        userMessage("HNO: " + str(row[1]))
    ##                        userMessage("From: " + str(row[2]))
    ##                        userMessage("To: " + str(row[3]))
    ##                        userMessage("Range: " + str(sideRange))

                    else:
                        null_values.append(row[0])
                del row, rows

    issueDict = {"Error: RCLMATCH is reporting an NGSEGID that does not exist in the road centerline": ngsegid_doesnt_exist,
                 "Error: RCLMATCH does not correspond to an NGSEGID that matches attributes": streets_or_msags_dont_match,
                 "Error: HNO does not fit in range of corresponding RCLMATCH": doesnt_match_range,
                 "Error: Road segment address ranges include one or more null values": null_values,
                 "Error: RCLSIDE is null": no_rclside}

    # this catches if the NGSEGID doesn't exist in the road centerline file
    for issue in issueDict:
        issueList = issueDict[issue]
        if issueList != []:
            for ngaddid in issueList:
                if "null values" not in issue:
                    val = (today, issue, "AddressPoints", "RCLMATCH", ngaddid, "Check RCLMATCH")
                else:
                    val = (today, issue, "RoadCenterline", "RCLMATCH", ngaddid, "Check RCLMATCH")
                values.append(val)

    # clean up
    cleanUp([at, rt, a, r, ap_table_view, rc_table_view])

    if values != []:
        RecordResults(resultType, values, gdb)
        userWarning("Check complete. %s issues found. See table FieldValuesCheckResults for results." % (str(len(values))))
    else:
        userMessage("Check complete. All RCLMATCH records correspond to appropriate road centerline segments.")


def checkMSAGCOspaces(fc1, gdb):
    # define necessary variables
    fcobj = NG911_GDB_Objects.getFCObject(fc1)
    uniqueID = fcobj.UNIQUEID

    values = []
    resultType = "fieldValues"
    today = strftime("%m/%d/%y")
    fc = basename(fc1)

    # see which MSAGCO fields we're working with
    if "Address" in fc:
        fields = ["MSAGCO"]
    else:
        fields = ["MSAGCO_L","MSAGCO_R"]

    wc_root = "SUBMIT = 'Y' AND "

    # loop through the fields to see if there are any leading or trailing spaces in the values
    for field in fields:

        # set up the where clauses to find leading or trailing spaces
        wcList = [field + " like ' %'", field + " like '% '", field + " is null", field + " in ('', ' ')"]
        for wc in wcList:
            fl = "fl"
            MakeFeatureLayer_management(fc, fl, wc_root + wc)

            # do reporting if issues are found
            if getFastCount(fl) > 0:
                with SearchCursor(fl, (uniqueID)) as rows:
                    for row in rows:
                        report = "Error: %s has a leading or trailing space or is null or blank." % field
                        val = (today, report, fc, field, row[0], "Check Values Against Domains")
                        values.append(val)

            # clean up between iterations
            Delete_management(fl)

    if values != []:
        RecordResults(resultType, values, gdb)
        userWarning("Check complete. %s issues found. See table FieldValuesCheckResults for results." % (str(len(values))))
    else:
        userMessage("Check complete. No MSAGCO records have leading or trailing spaces.")


def checkValuesAgainstDomain(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    folder = pathsInfoObject.domainsFolderPath
    fcList = pathsInfoObject.gdbObject.fcList

    userMessage("Checking field values against approved domains...")
    #set up parameters to report duplicate records
    values = []
    resultType = "fieldValues"
    today = strftime("%m/%d/%y")

    #set environment
    env.workspace = gdb

    for fullPath in fcList:
        if Exists(fullPath):
            fc = basename(fullPath)
            obj = NG911_GDB_Objects.getFCObject(fullPath)

            #only check records marked for submission
            worked = 0
            fullPathlyr = "fullPathlyr"
            wc2 = "SUBMIT = 'Y'"
            try:
                MakeTableView_management(fullPath, fullPathlyr, wc2)
                count = getFastCount(fullPathlyr)
                if count > 0:
                    worked = 1
                else:
                    userMessage("No values are marked for submission. Please mark records for submission by placing Y in the SUBMIT field.")
            except:
                userMessage("Cannot check required field values for " + fc)

            if worked == 1:

                #get list of fields with domains
                fieldsWDoms = obj.FIELDS_WITH_DOMAINS

                id1 = obj.UNIQUEID
                if id1 != "":

                    for fieldN in fieldsWDoms.keys():
                        # get domain
                        domain = fieldsWDoms[fieldN]
                        userMessage("Checking: " + fieldN)

                        #get the full domain dictionary
                        if fieldN != "HNO":
                            domainDict = getFieldDomain(domain, folder)
                            if domainDict != {}:
                                #put domain values in a list
                                domainList = []

                                for val in domainDict.keys():
                                    domainList.append(val)

                                #add values for some CAD users of blank and space (edit suggested by Sherry M. & Keith S. Dec 2014)
                                if domain != "YN": # except if it's YN- it's two values. Fill it in.
                                    domainList.append('')
                                    domainList.append(" ")

                                #if the domain is counties, add county names to the list without "COUNTY" so both will work (edit suggest by Keith S. Dec 2014)
                                if fieldN == "COUNTY":
                                    q = len(domainList)
                                    i = 0
                                    while i < q:
                                        dl1 = domainList[i].split(" ")[0]
                                        domainList.append(dl1)
                                        i += 1

                                with SearchCursor(fullPathlyr, (id1, fieldN)) as rows:
                                    for row in rows:
                                        # if the row is null, skip it
                                        if row[1] is None or row[1] in ['',' ']:
                                            pass
                                        # see if the value is in the domain list
                                        elif row[1] not in domainList:
                                            fID = row[0]
                                            report = "Error: Value %s not in approved domain for field %s" % (str(row[1]), fieldN)
                                            val = (today, report, fc, fieldN, fID, "Check Values Against Domains")
                                            values.append(val)

                        else:
                            # check HNO field of address points to make sure all values are valid
                            with SearchCursor(fullPathlyr, (id1, fieldN)) as rows:
                                for row in rows:
                                    hno = row[1]
                                    if hno > 999999 or hno < 0:
                                        report = "Error: Value %s not in approved domain for field %s" % (str(row[1]), fieldN)
                                        val = (today, report, fc, fieldN, row[0], "Check Values Against Domains")
                                        values.append(val)

                            del rows, row

                userMessage("Checked " + fc)

            Delete_management(fullPathlyr)

            # make sure the parcel ID's go through testing for character length
            if "PARCELS" in basename(fullPath).upper():
                checkKSPID(fullPath, "NGKSPID")

        else:
            userWarning(fullPath + " does not exist")

    if values != []:
        RecordResults(resultType, values, gdb)
        userWarning("Completed checking fields against domains: %s issues found. See table FieldValuesCheckResults for results." % (str(len(values))))
    else:
        userMessage("Completed checking fields against domains: 0 issues found")


def checkRequiredFieldValues(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    fcList = pathsInfoObject.gdbObject.fcList

    userMessage("Checking that required fields have all values...")

    #get today's date
    today = strftime("%m/%d/%y")

    values = []

    #walk through the tables/feature classes
    for filename in fcList:
        if Exists(filename):
            layer = basename(filename)
            obj = NG911_GDB_Objects.getFCObject(filename)
            id1 = obj.UNIQUEID

            if id1 != "":
                requiredFieldList = obj.REQUIRED_FIELDS

                #get list of fields in the feature class
                fields = ListFieldNames(filename)

                #convert lists to sets
                set1 = set(requiredFieldList)
                set2 = set(fields)

                #get the set of fields that are the same
                matchingFields = list(set1 & set2)

                #only work with records that are for submission
                lyr2 = "lyr2"
                worked = 0
                wc2 = "SUBMIT = 'Y'"
                try:
                    MakeTableView_management(filename, lyr2, wc2)
                    worked = 1
                except:
                    userMessage("Cannot check required field values for " + layer)

                if worked == 1:

                    #get count of the results
                    if getFastCount(lyr2) > 0:

                        #create where clause to select any records where required values aren't populated
##                        wc = ""
                        wcList = []

                        for field in matchingFields:
                            wcList = wcList + [" ", field, " is null", " or "]
##                            wc = wc + " " + field + " is null or "

                        wcList.pop() # take off the last " is null or"
##                        wc = wc[0:-4]
                        wc = "".join(wcList)

                        #make table view using where clause
#                        lyr = "lyr"
#                        MakeTableView_management(lyr2, lyr, wc)

                        SelectLayerByAttribute_management(lyr2, "NEW_SELECTION", wc)

                        #if count is greater than 0, it means a required value somewhere isn't filled in
                        if getFastCount(lyr2) > 0:
                            #make sure the objectID gets included in the search for reporting
                            if id1 not in matchingFields:
                                matchingFields.append(id1)

                            try:
                                #run a search cursor to get any/all records where a required field value is null
                                with SearchCursor(lyr2, (matchingFields), wc) as rows:
                                    for row in rows:
                                        k = 0
                                        #get object ID of the field
                                        oid = str(row[matchingFields.index(id1)])

                                        #loop through row
                                        while k < len(matchingFields):
                                            #see if the value is nothing
                                            if row[k] is None:
                                                #report the value if it is indeed null
                                                report = "Error: %s is null for Feature ID %s" % (matchingFields[k], oid)
                                                userMessage(report)
                                                val = (today, report, basename(filename), matchingFields[k], oid, "Check Required Field Values")
                                                values.append(val)

                                            #iterate!
                                            k = k + 1
                            except:
                                userMessage("Could not check all fields in %s. Looking for " % (layer) + ", ".join(matchingFields) )
                        else:
                            userMessage( "All required values present for " + layer)

#                        Delete_management(lyr)
#                        del lyr

                    else:
                        userMessage(layer + " has no records marked for submission. Data will not be verified.")
                    Delete_management(lyr2)
        else:
            userWarning(filename + " does not exist.")

    if values != []:
        RecordResults("fieldValues", values, gdb)
        userWarning("Completed check for required field values: %s issues found. See table FieldValuesCheckResults for results." % (str(len(values))))
    else:
        userMessage("Completed check for required field values: 0 issues found")



def checkRequiredFields(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    fcList = pathsInfoObject.gdbObject.fcList

    userMessage("Checking that required fields exist...")

    #get today's date
    today = strftime("%m/%d/%y")
    values = []

    #walk through the tables/feature classes
    for fullPath in fcList:
        filename = basename(fullPath)
        if Exists(fullPath):

            obj = NG911_GDB_Objects.getFCObject(fullPath)
            comparisonList = obj.REQUIRED_FIELDS

            #list fields
            fields = ListFieldNames(fullPath)

            missingFields = list(set(comparisonList) - set(fields))

            if missingFields != []:

                #loop through required fields to make sure they exist in the geodatabase
                for comparisonField in missingFields:
                    report = "Error: %s does not have required field %s" % (filename, comparisonField)
                    userMessage(report)
                    #add issue to list of values
                    val = (today, report, "Field", "Check Required Fields")
                    values.append(val)
        else:
            userWarning(fullPath + " does not exist")

    userMessage("Checking that the HNO field is an integer...")

    #test to see if the HNO field is a number or text
    fc = pathsInfoObject.gdbObject.AddressPoints
    ap_fields = ListFields(fc)
    for ap_field in ap_fields:
        if ap_field.name == "HNO" and ap_field.type != "Integer":
            report = "Error: HNO field of Address Points is not an integer"
            userMessage(report)
            val = (today, report, "Field", "Check Required Fields")
            values.append(val)

    #record issues if any exist
    if values != []:
        RecordResults("template", values, gdb)
        userWarning("Completed check for required fields: %s issues found. See table FieldValuesCheckResults for results." % (str(len(values))))
    else:
        userMessage("Completed check for required fields: 0 issues found")


def checkSubmissionNumbers(pathsInfoObject):
    #set variables
    gdb = pathsInfoObject.gdbPath
    fcList = pathsInfoObject.gdbObject.fcList

    today = strftime("%m/%d/%y")
    values = []

    skipList = ["HYDRANTS", "GATES", "PARCELS", "CELLSECTORS", "BRIDGES", "CELLSITES",
         "MUNICIPALBOUNDARY", "COUNTYBOUNDARY"]

    for fc in fcList:
        if Exists(fc):
            #count records that are for submission
            lyr2 = "lyr2"
            wc2 = "SUBMIT = 'Y'"
            if "AddressPoints" in fc:
                wc2 = wc2 + " AND LOCTYPE = 'PRIMARY'"
            MakeTableView_management(fc, lyr2, wc2)

            #get count of the results
            count = getFastCount(lyr2)
            bn = basename(fc)

            umList = [bn, ": ", str(count), " records marked for submission"]
            um = "".join(umList)
            userMessage(um)

            if count == 0:
                report = "Error: %s has 0 records for submission" % (bn)
                if bn.upper() in skipList or bn[0:3].upper() == 'UT_':
                    report = report.replace("Error", "Notice")
                #add issue to list of values
                val = (today, report, "Submission", "Check Submission Counts")
                values.append(val)

            Delete_management(lyr2)
        else:
            userWarning(fc + " does not exist")

    #record issues if any exist
    if values != []:
        RecordResults("template", values, gdb)
        userWarning("One or more layers had no features to submit. See table TemplateCheckResults.")
    else:
        userMessage("All layers had features to submit.")

def checkFeatureLocations(pathsInfoObject):
    gdb = pathsInfoObject.gdbPath
    fcList = pathsInfoObject.gdbObject.fcList

    #get geodatabase object
    gdbObject = pathsInfoObject.gdbObject

    RoadAlias = gdbObject.RoadAlias
    if RoadAlias in fcList:
        fcList.remove(RoadAlias)

    userMessage("Checking feature locations...")

    #get today's date
    today = strftime("%m/%d/%y")
    values = []

    #make sure features are all inside authoritative boundary

    #get authoritative boundary
    authBound = gdbObject.AuthoritativeBoundary
    countyBound = gdbObject.CountyBoundary
    parcels = gdbObject.PARCELS
    ab = "ab"
    addedField = 0

    # disable editor tracking
    DisableEditorTracking_management(authBound)

    #see if authoritative boundary has more than 1 feature
    #if more than one feature is in the authoritative boundary, use the county boundary instead
    if Exists(authBound):
        if getFastCount(authBound) > 1:
            if Exists(countyBound):
                authBound = countyBound
            else:
                # see if the STATE field exists to dissolve features
                if not fieldExists(authBound, "STATE"):

                    # if not, add the field
                    AddField_management(authBound, "STATE", "TEXT", "", "", 2)
                    CalculateField_management(authBound, "STATE", '"KS"', "PYTHON_9.3", "")
                    addedField = 1 # toggle flag

                # set up to dissolve features on STATE into an in-memory layer
                auth = "auth"
                MakeFeatureLayer_management(authBound, auth)
                authBound = r"in_memory\Auth"

                Dissolve_management(auth, authBound, ["STATE"])

    else:
        if Exists(countyBound):
            authBound = countyBound

    #remove some layers from being checked
    for f in [authBound, countyBound, parcels]:
        if f in fcList:
            fcList.remove(f)

    MakeFeatureLayer_management(authBound, ab)

    for fullPath in fcList:
        if Exists(fullPath):
            fl = "fl"
##            wc = "SUBMIT = 'Y'"
            wcList = ["SUBMIT = 'Y'"]
            if "RoadCenterline" in fullPath:
                rc_obj = NG911_GDB_Objects.getFCObject(fullPath)
##                wc = wc + " AND " + rc_obj.EXCEPTION + " not in ('EXCEPTION INSIDE', 'EXCEPTION BOTH')"
                wcList = wcList + [" AND ", rc_obj.EXCEPTION, " not in ('EXCEPTION INSIDE', 'EXCEPTION BOTH')"]
                if rc_obj.GDB_VERSION == "21":
##                    wc = wc + " AND AUTH_L = 'Y' AND AUTH_R = 'Y'"
                    wcList.append(" AND AUTH_L = 'Y' AND AUTH_R = 'Y'")
            wc = "".join(wcList)
            MakeFeatureLayer_management(fullPath, fl, wc)

            try:
                #select by location to get count of features outside the authoritative boundary
                SelectLayerByLocation_management(fl, "WITHIN", ab)
                SelectLayerByAttribute_management(fl, "SWITCH_SELECTION", "")

                #get count of selected records
                #report results
                if getFastCount(fl) > 0:
                    layer = basename(fullPath)
                    obj = NG911_GDB_Objects.getFCObject(fullPath)
                    id1 = obj.UNIQUEID
                    if id1 != '':
                        fields = (id1)
                        if "AddressPoints" in fullPath:
                            fields = (id1, obj.LOCTYPE)
                        with SearchCursor(fl, fields) as rows:
                            for row in rows:
                                fID = row[0]
                                report = "Error: Feature not inside authoritative boundary"
                                if "AddressPoints" in fullPath:
                                    if row[1] != 'PRIMARY':
                                        report = report.replace("Error:", "Notice:")

                                val = (today, report, layer, " ", fID, "Check Feature Locations")
                                values.append(val)

                        userMessage(basename(fullPath) + ": issues with some feature locations")
                    else:
                        userMessage("Could not process features in " + fullPath)
                else:
                    userMessage(basename(fullPath) + ": all records inside authoritative boundary")
            except:
                userMessage("Could not check locations of " + fullPath)

            finally:

                #clean up
                Delete_management(fl)
               
            # check to see if the address points have values outside the boundaries of Kansas
            if "AddressPoints" in fullPath:
                
                # create a layer of address points that are for submission and have lat/long calculated
                wc = "SUBMIT = 'Y' AND LAT <> 0 AND LONG <> 0"
                fl_ap = "fl_ap"
                MakeFeatureLayer_management(fullPath, fl_ap, wc)
                
                # see if the count is higher than 0
                if getFastCount(fl_ap) > 0:
                    
                    # find some boundary layer to use
                    if Exists(authBound):
                        ext_boundary = authBound
                    elif Exists(join(gdb, "NG911", "CountyBoundary")):
                        ext_boundary = join(gdb, "NG911", "CountyBoundary")
                    elif Exists(join(gdb, "NG911", "ESB")):
                        ext_boundary = join(gdb, "NG911", "ESB")
                    else:
                        ext_boundary = join(gdb, "NG911", "ESB_EMS")
                    
                    # get GCS bounding coordinates of the authoritative boundary
                    ab_copy = r"in_memory\EXT"
                    ab_gcs = join(gdb, "EXT_GCS")
                
                    # copy first
                    CopyFeatures_management(ext_boundary, ab_copy)
                     
                    # reproject AB in memory to GCS
                    sr = SpatialReference(4269)
                    Project_management(ab_copy, ab_gcs, sr)
                    
                    # get bounding coordinates
                    ext = Describe(ab_gcs).extent
                    
                    # create feature layer of any features that are outside Kansas by GCS
                    outobounds_wc = "SUBMIT = 'Y' AND (LONG < %s OR LONG > %s OR LAT < %s OR LAT > %s)" % (ext.XMin, ext.XMax, ext.YMin, ext.YMax)
                    fl_ap_outside = "fl_ap_outside"
                    MakeFeatureLayer_management(fullPath, fl_ap_outside, outobounds_wc)
                    
                    if getFastCount(fl_ap_outside) > 0:
                        
                        obj = NG911_GDB_Objects.getFCObject(fullPath)
                        id1 = obj.UNIQUEID
                        layer = basename(fullPath)
                        
                        # if there are, report the features
                        with SearchCursor(fl_ap_outside, (id1)) as rows1:
                            for row1 in rows1:
                                fID = row1[0]
                                report = "Error: Lat or Long field outside PSAP geographic coordinates"
                                val = (today, report, layer, "LAT|LONG", fID, "Check Feature Locations")
                                values.append(val)
                                
                        # clean up
                        try:
                            del row1, rows1
                        except:
                            pass
                        
                    # clean up
                    Delete_management(fl_ap_outside)
                    Delete_management(ab_copy)
                    Delete_management(ab_gcs)
                    
                # clean up
                Delete_management(fl_ap)
                

    if values != []:
        RecordResults("fieldValues", values, gdb)
        userWarning("Completed check on feature locations: %s issues found. See table FieldValuesCheckResults." % (str(len(values))))
    else:
        userMessage("Completed check on feature locations: 0 issues found")

    # clean up if various methods were used
    if authBound == r"in_memory\Auth":
        Delete_management(authBound)
    if addedField == 1:
        try:
            DeleteField_management(gdbObject.AuthoritativeBoundary, "STATE")
        except:
            pass

    # re-enable editor tracking
    EnableEditorTracking_management(gdbObject.AuthoritativeBoundary, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")

def findInvalidGeometry(pathsInfoObject):
    userMessage("Checking for invalid geometry...")

    #set variables
    gdb = pathsInfoObject.gdbPath
    gdbObject = pathsInfoObject.gdbObject
    fcList = gdbObject.fcList

    for f in fcList:
        if "RoadAlias" in f:
            fcList.remove(f)

    today = strftime("%m/%d/%y")
    values = []
    report = "Error: Invalid geometry"

    invalidDict = {"point": 1, "polyline": 2, "polygon":3}

    #loop through feature classes
    for fullPath in fcList:
        layer = basename(fullPath)

        if Exists(fullPath):
            obj = NG911_GDB_Objects.getFCObject(fullPath)
            id_column = obj.UNIQUEID

            if fieldExists(fullPath, id_column):

                #set up fields for cursor
                fields = ("SHAPE@", id_column)

                with SearchCursor(fullPath, fields) as rows:
                    for row in rows:
                        geom = row[0]
                        fid = row[1]

                        try:
                            #get geometry type
                            geomType = geom.type

                            #find the minimum number of required points
                            minNum = invalidDict[geomType]

                            #get the count of points in the geometry
                            count = geom.pointCount

                            #if the count is smaller than the minimum number, there's a problem
                            if count < minNum:
                                val = (today, report, layer, " ", fid, "Find Invalid Geometry")
                                values.append(val)
                        except:
                            #if this errors, there's an error accessing the geometry, hence problems
                            val = (today, report, layer, " ", fid, "Find Invalid Geometry")
                            values.append(val)

            else:
                userMessage("ID column %s does not exist in %s" % (id_column, fullPath))

        else:
            userWarning(fullPath + " does not exist")

    if values != []:
        RecordResults("fieldValues", values, gdb)
        userWarning("Completed for invalid geometry: %s issues found. See FieldValuesCheckResults." % (str(len(values))))
    else:
        userMessage("Completed for invalid geometry: 0 issues found")

def checkCutbacks(pathsInfoObject):
    userMessage("Checking for geometry cutbacks...")

    gdb = pathsInfoObject.gdbPath
    gdbObject = pathsInfoObject.gdbObject
    road_fc = gdbObject.RoadCenterline
    roads = "roads"
    rc_obj = NG911_GDB_Objects.getFCObject(road_fc)

    if Exists(road_fc):

        #make feature layer so only roads marked for submission are checked
        MakeFeatureLayer_management(road_fc, roads, rc_obj.SUBMIT + " = 'Y'")

        #set up tracking variables
        cutbacks = []
        values = []
        today = strftime("%m/%d/%y")
        layer = "RoadCenterline"

        k = 0

        #set up search cursor on roads layer
        with SearchCursor(roads, ("SHAPE@", rc_obj.UNIQUEID)) as rows:
            for row in rows:
                geom = row[0]
                segid = row[1]

                try:

                    #loop through geometry parts
                    for part in geom:
                        part_coords = []

                        #don't check simple roads
                        if len(part) > 4:
                            #loop through points
                            for pnt in part:
                                #set up points in a straightforward list
                                pc = []
                                if pnt:
                                    pc = [pnt.X, pnt.Y]
                                    part_coords.append(pc)
                                else:
                                    pass

                            #loop through coordinate list
                            if part_coords != []:
                                i = 1
                                while i < (len(part_coords)-1):

                                    #calculate the angle between three points
                                    angle = calcAngle(part_coords[i-1],part_coords[i],part_coords[i+1])
        ##                            print angle

                                    #if the angle is quite sharp, it might indicate a cutback
                                    if 0 < angle < 55:
                                        if segid not in cutbacks:
                                            report = "Notice: This segment might contain a geometry cutback"
                                            val = (today, report, layer, " ", segid, "Check for Cutbacks")
                                            values.append(val)
                                            cutbacks.append(segid)
                                    i += 1
                except:
                    userMessage("Issue checking a cutback with segment " + segid)
                    k += 1

        Delete_management(roads)
    else:
        userWarning(road_fc + " does not exist")

    if values != []:
        RecordResults("fieldValues", values, gdb)
        userWarning("Completed check on cutbacks: %s issues found. See FieldValuesCheckResults." % (str(len(values))))
    else:
        userMessage("Completed check on cutbacks: 0 issues found")

    if k != 0:
        userMessage("Could not complete cutback check on %s segments." % (str(k)))
        
        
def checkLineSelfIntersections(roads):
    
    userMessage("Checking lines for self-intersections...")
    
    intersections = []
    
    wc = "SUBMIT = 'Y'"
    
    try:
    
        with SearchCursor(roads, ("SHAPE@", "NGSEGID"), wc) as rows:
            for row in rows:
                ngsegid = row[1]
                
                touche = row[0].crosses(row[0])
            
                if touche:
                    intersections.append(ngsegid)
    
                # loop through parts of the line geometry            
                for part in row[0]:
                    
                    # check to see if first and last part are the same
                    if [part[0].X, part[0].Y] == [part[-1].X, part[-1].Y]:
                        pass
                        
                    # else, check for self intersections
                    else:
                    
                        # create a list of all the points
                        lstPoints = []
                        for pt in part:
                            lstPoints.append([pt.X, pt.Y])
                            
                        # get a count of how many times each point happens
                        for pt in lstPoints:
                            count = lstPoints.count(pt)
                            
                            # if the count is greater than 1...
                            if count > 1:
                                
                                # get the index of the first time the point happens
                                index = lstPoints.index(pt)
                                
                                # if the next time it happens is the index + 1, then ignore
                                if lstPoints[index + 1] == pt:
                                    pass
                                else:
                                    # this is a real duplicate point
                                    if ngsegid not in intersections:
                                        intersections.append(ngsegid)
                                     
                                try:
                                    del index
                                except:
                                    pass
                                        
                        del lstPoints, pt, count
                        
                del part
                
        del row, rows, wc
        
                    
        if intersections != []:                
            userWarning("Total self-looping roads: %s. See FieldValuesCheckResults for specifics." % str(len(intersections)))
            
            # do reporting
            values = []
            today = strftime("%m/%d/%y")
            layer = basename(roads)
            
            # populate values
            for ngsegid in intersections:
                report = "Notice: %s road geometry loops back on itself" % ngsegid
                val = (today, report, layer, "GEOMETRY", ngsegid, "Self-intersections")
                values.append(val)
                
            if dirname(roads)[-3:] != 'gdb':
                gdb = dirname(dirname(roads))
            else:
                gdb = dirname(roads)
                
            RecordResults("fieldValues", values, gdb)
            try:
                del values, today, layer
            except:
                pass
        else:
            userMessage("No self-intersecting roads found.")
        
    except:
        userWarning("Unable to check roads for self-intersections. If you are on ArcMap 10.4.1, this is probably ok. If not, there is probably an error with your data.")

        
    try:
        del intersections, ngsegid, report, val, gdb
    except:
        pass


def getNumbers():
    numbers = "0123456789"
    return numbers


def checkKSPID(fc, field):
    # make sure the KSPID value is 19 characters long
    values = []
    kspid_wc = "%s is not null and CHAR_LENGTH(%s) <> 19" % (field, field)
##    kspid_wc = "NGKSPID is not null and CHAR_LENGTH(NGKSPID) <> 19"
    userMessage(fc + " " + field + " " + kspid_wc)
    kspid_fl = "kspid_fl"
    MakeFeatureLayer_management(fc, kspid_fl, kspid_wc)

    # get the count of how many are too long or short
    if getFastCount(kspid_fl) > 0:
        today = strftime("%m/%d/%y")
        layer = basename(fc)
        if layer == "AddressPoints":
            fields = (field, "NGADDID")
            ID_index = 1
        else:
            fields = (field)
            ID_index = 0

        with SearchCursor(kspid_fl, fields, kspid_wc) as rows:
            for row in rows:
                if layer == "AddressPoints":
                    # try to make sure we're not getting any blanks reported in Address Points
                    if row[0] not in ('', ' '):
                        fid = row[ID_index]
                        report = "Error: %s value is not the required 19 characters." % (field)
                        val = (today, report, layer, field, fid, "Check " + field)
                        values.append(val)

                else:
                    fid = row[ID_index]
                    report = "Error: %s value is not the required 19 characters." % (field)
                    val = (today, report, layer, field, fid, "Check " + field)
                    values.append(val)

    # report
    msgList = ["Completed check on ", basename(fc), " ", field, ": "]
    if values != []:
        if dirname(fc)[-3:] != 'gdb':
            gdb = dirname(dirname(fc))
        else:
            gdb = dirname(fc)
        RecordResults("fieldValues", values, gdb)
        msgList = msgList + [str(len(values)), " issues found. See FieldValuesCheckResults. Parcel IDs must be 19 digits with county code and no dots or dashes."]
        msg = "".join(msgList)
        userWarning(msg)
    else:
        msgList.append("0 issues found")
        msg = "".join(msgList)
        userMessage(msg)

    Delete_management(kspid_fl)


def VerifyRoadAlias(gdb, domainFolder):
    gdbObject = NG911_GDB_Objects.getGDBObject(gdb)
    #set up variables for search cursor
    roadAlias = gdbObject.RoadAlias
    ra_obj = NG911_GDB_Objects.getFCObject(roadAlias)
    fieldList = (ra_obj.A_RD, ra_obj.ALIASID)

    if Exists(roadAlias):

        #get highway values
        hwy_text = join(domainFolder, "KS_HWY.txt")

        hwy_dict = {}

        #make sure file path exists
        if exists(hwy_text):
            fieldDefDoc = open(hwy_text, "r")

            #parse the text to populate the field definition dictionary
            for line in fieldDefDoc.readlines():
                stuffList = line.split("|")

                #set up values
                route_num = stuffList[1].rstrip()
                route_name = stuffList[0]

                #see if the road list already exists in the hwy dictionary
                if route_num not in hwy_dict:
                    nameList = [route_name]
                else:
                    nameList = hwy_dict[route_num]
                    nameList.append(route_name)

                #set dictionary value to name list
                hwy_dict[route_num] = nameList

        #get variables set up
        #where clause for the search cursor
        wc = "%s is null or %s in ('HWY', '', ' ')" % (ra_obj.A_STS, ra_obj.A_STS)

        #variables for error reporting
        errorList = []
        values = []
        filename = basename(roadAlias)
        field = ra_obj.A_RD
        recordType = "fieldValues"
        today = strftime("%m/%d/%y")

        #get a list of numbers
        numbers = getNumbers()

        #start search cursor to examine records
        with SearchCursor(roadAlias, fieldList, wc) as rows:
            for row in rows:
                fID = row[1] #road alias ID for reporting
                try:
                    road = row[0]
                    first_char = road[0]

                    #see if first character indicates a highway
                    if first_char in "IUK0123456789":

                        for n in numbers:

                            #see if the road name has numbers in it
                            if n in road:

                                roadNum = road #working variable to strip out all alphabet characters

                                #get just the road number with no other characters
                                for r in roadNum:
                                    if r not in numbers:
                                        roadNum = roadNum.replace(r, "")

                                #see if the road number is in the highway dictionary
                                if roadNum in hwy_dict:
                                    if road not in hwy_dict[roadNum]:
                                        if fID not in errorList:
                                            errorList.append(fID)
                                            report = "Notice: %s is not in the approved highway name list" % (road)
                                            val = (today, report, filename, field, fID, "Check Road Alias")
                                            values.append(val)

                except:
                    report = "Error: Issue with road alias record"
                    val = (today, report, filename, field, fID, "Check Road Alias")
                    values.append(val)

    else:
        userWarning(roadAlias + " does not exist")


    #report records
    if values != []:
        #set up custom error count message
        count = len(errorList)
        if count > 1:
            countReport = "There were %s issues." % (str(count))
        else:
            countReport = "There was 1 issue."

        RecordResults(recordType, values, gdb)
        userWarning("Checked highway names in the road alias table. %s Results are in table FieldValuesCheckResults" % (countReport))
    else:
        userMessage("Checked highway names in the road alias table.")

def checkJoin(gdb, inputTable, joinTable, where_clause, errorMessage, field):
    #set up tracking variables
    values = []
    today = strftime("%m/%d/%y")
    layer = field.split(".")[0]
    recordType = "fieldValues"
    rc_obj = NG911_GDB_Objects.getFCObject(join(gdb, "NG911", "RoadCenterline"))

    AddJoin_management(inputTable, rc_obj.UNIQUEID, joinTable, rc_obj.UNIQUEID)
    tbl = "tbl"

    #get the fast count to see if issues exist
    MakeTableView_management(inputTable, tbl, where_clause)

    #see if any issues exist
    #catalog issues
    if getFastCount(tbl) > 0:
        fields = (field, "RoadCenterline." + rc_obj.RD)
        #NOTE: have to run the search cursor on the join table, running it on the table view throws an error
        with SearchCursor(inputTable, fields, where_clause) as rows:
            for row in rows:
                if row[1] is not None:
                    if " TO " in row[1] or "RAMP" in row[1] or "OLD" in row[1]:
                        #print("this is probably an exception")
                        pass
                    else:
                        val = (today, errorMessage, layer, "", row[0], "Check Road Alias")
                        values.append(val)

    #clean up
    RemoveJoin_management(inputTable)
    Delete_management(tbl)

    #report records
    if values != []:
        RecordResults(recordType, values, gdb)

    valCount = len(values)

    return valCount

def checkRoadAliases(pathsInfoObject):
    userMessage("Checking road alias table...")

    gdb = pathsInfoObject.gdbPath
    gdbObject = pathsInfoObject.gdbObject

    #make road layer into a feature layer
    roads = gdbObject.RoadCenterline
    road_alias = gdbObject.RoadAlias
    rc_obj = NG911_GDB_Objects.getFCObject(roads)
    ra_obj = NG911_GDB_Objects.getFCObject(road_alias)

    if Exists(roads) and Exists(road_alias):
        rdslyr = "RoadCenterlineQ"
        if fieldExists(roads, rc_obj.SUBMIT):
            MakeFeatureLayer_management(roads, rdslyr, rc_obj.SUBMIT + " = 'Y'")
        else:
            MakeFeatureLayer_management(roads, rdslyr)

        #make road alias into a table view

        ra_tbl = "RoadAliasQ"
        if fieldExists(road_alias, ra_obj.SUBMIT):
            MakeTableView_management(road_alias, ra_tbl, ra_obj.SUBMIT + " = 'Y'")
        else:
            MakeTableView_management(road_alias, ra_tbl)

        #make sure all road alias records relate back to the road centerline file
        alias_count = checkJoin(gdb, ra_tbl, rdslyr, "RoadCenterline.%s is null" % (rc_obj.RD), "Notice: Road alias entry does not have a corresponding road centerline segment", "RoadAlias." + ra_obj.UNIQUEID)

        #see if the highways link back to a road alias record
        wcList = ["(RoadCenterline.", rc_obj.RD, " like '%HIGHWAY%' or RoadCenterline.", rc_obj.RD, " like '%HWY%' or RoadCenterline.", rc_obj.RD, " like '%INTERSTATE%') and RoadAlias.", ra_obj.A_RD, " is null"]
        wc = "".join(wcList)
        hwy_count = checkJoin(gdb, rdslyr, ra_tbl, wc,
                "Notice: Road centerline highway segment does not have a corresponding road alias record", "RoadCenterline." + rc_obj.UNIQUEID)

        total_count = alias_count + hwy_count

        if total_count > 0:
            userMessage("Checked road alias records. There were %s issues. Results are in table FieldValuesCheckResults" % (str(total_count)))
        else:
            userMessage("Checked road alias records. No errors were found.")

        #verify domain values
        VerifyRoadAlias(gdb, pathsInfoObject.domainsFolderPath)

        cleanUp([rdslyr, ra_tbl])
    else:
        if not Exists(roads):
            userWarning(roads + " does not exist")
            userWarning(road_alias + " does not exist")


def checkESBDisplayLength(pathsInfoObject):
    userMessage("Checking ESB DISPLAY field length...")
    esbList = pathsInfoObject.gdbObject.esbList

    #set variables for working with the data
    gdb = pathsInfoObject.gdbObject.gdbPath
    recordType = "fieldValues"
    field = "DISPLAY"
    today = strftime("%m/%d/%y")
    values = []

    for esb in esbList:
        fc = basename(esb)
        if fieldExists(esb, "DISPLAY"):
            e = "e"
            wc = "CHAR_LENGTH(DISPLAY) > 32"
            MakeFeatureLayer_management(esb, e, wc)

            if getFastCount(e) > 0:
                with SearchCursor(e, ("NGESBID")) as rows:
                    for row in rows:
                        msg = "Notice: DISPLAY length longer than 32 characters, value will be truncated"
                        val = (today, msg, fc, field, row[0], "Check ESB DISPLAY length")
                        values.append(val)
            Delete_management(e)

    if values != []:
        RecordResults(recordType, values, gdb)
        userWarning("Checked ESB DISPLAY length. There were %s issues." % str(len(values)))
    else:
        userMessage("Checked ESB DISPLAY length. No issues found.")


def checkTopology(gdbObject, check_polygons, check_roads):

    userMessage("Validating topology...")

    #set variables for working with the data
    gdb = gdbObject.gdbPath
    recordType = "fieldValues"
    today = strftime("%m/%d/%y")
    values = []
    count = 0

    #export topology errors as feature class
    topology = gdbObject.Topology

    # make sure topology is all set up correctly & validate
    add_topology(gdb, "true")

    if Exists(topology):
        out_basename = "NG911"
        polyErrors = "%s_poly" % out_basename
        lineErrors = "%s_line" % out_basename
        pointErrors = "%s_point" % out_basename

        for topE in (lineErrors, pointErrors, polyErrors):
            full = join(gdb, topE)
            if Exists(full):
                Delete_management(full)

        # export topology
        userMessage("Exporting topology errors...")
        ExportTopologyErrors_management(topology, gdb, out_basename)

        # query the polygon results for issues
        polyFC = join(gdb, polyErrors)
        lineFC = join(gdb, lineErrors)
        pointFC = join(gdb, pointErrors)

        # create a dictionary of the counts
        top_fields = ["OriginObjectClassName", "OriginObjectID", "RuleDescription"]
        top_fields_line = ["OriginObjectClassName", "OriginObjectID", "RuleDescription", "SHAPE@LENGTH"]

        top_dict = {polyFC: top_fields, lineFC: top_fields_line, pointFC: top_fields}

        # make a list of all of the exceptions in road attributes sp these aren't reported
        roads = gdbObject.RoadCenterline
        rd_object = rd_object = NG911_GDB_Objects.getFCObject(roads)
        wc = rd_object.EXCEPTION + " <> 'NOT EXCEPTION'"
        exceptions = {}
        with SearchCursor(roads, ("OBJECTID", rd_object.EXCEPTION), wc) as rows:
            for row in rows:
                exceptions[row[0]] = row[1]

        # set up exception definition dictionary
        exc_dict = {"EXCEPTION INSIDE": ["Must Be Inside"],
                    "EXCEPTION DANGLES": ["Must Not Have Dangles"],
                    "EXCEPTION BOTH": ["Must Be Inside", "Must Not Have Dangles"]}

        # loop through polygon and line errors
        for errorFC in top_dict:
            userMessage("Top Dict " + errorFC)
            fields = top_dict[errorFC]

            # start a search cursor to report issues
            wc = "isException = 0"
            lyr = "lyr"
            MakeFeatureLayer_management(errorFC, lyr, wc)
            k = getFastCount(lyr)

            if k > 0:

                # set up ESB tracking
                esb_list = []
                esb_lengths = []
                reportESB = False
                esb_dict = {}

                with SearchCursor(lyr, fields) as rows:
                    for row in rows:

                        fc = row[0]
                        objectID = row[1]
                        ruleDesc = row[2]
                        
                        # userMessage("fc is |%s|" % fc)

                        # get the issues
                        if basename(errorFC) == "NG911_poly" and check_polygons == True:
                            fc_full = join(gdb, "NG911", fc)
                            
                            if fc_full != join(gdb, "NG911", ""):
                                fc_lyr = "fc_lyr"
                                MakeFeatureLayer_management(fc_full, fc_lyr)
    
                                #add join
                                AddJoin_management(fc_lyr, "OBJECTID", lyr, "OriginObjectID")
    
                                obj = NG911_GDB_Objects.getFCObject(fc_full)
    
                                #set query and field variables
                                qry = "%s.OriginObjectID IS NOT NULL and %s.isException = 0 and %s.SUBMIT = 'Y'" % (basename(errorFC), basename(errorFC), basename(fc_full))
                                fields2 = ("%s.%s" % (fc, obj.UNIQUEID), basename(errorFC) + ".RuleDescription", basename(errorFC) + ".isException")
    
                                #set up search cursor to loop through records
                                with SearchCursor(fc_lyr, fields2, qry) as rows2:
    
                                    for row2 in rows2:
                                        # make sure we're not reporting back an exception
                                        if row2[2] not in (1, "1"):
    
                                            # report the issues back as notices
                                            msg = "Error: Topology issue- %s" % row2[1]
                                            val = (today, msg, fc, "", row2[0], "Check Topology")
                                            values.append(val)
                                    try:
                                        del row2, rows2
                                    except:
                                        pass
    
                                #clean up & reset
                                RemoveJoin_management(fc_lyr)
                                Delete_management(fc_lyr)

                        elif basename(errorFC) == "NG911_line":
                            if check_polygons == True and "ESB" in fc:
                                # get some stats to analyze after the loop

                                # ESB layer must be unique
                                if fc not in esb_list:
                                    esb_list.append(fc)
                                else:
                                    reportESB = True

                                # rules must be "Must Not Have Gaps"
                                if ruleDesc != "Must Not Have Gaps":
                                    reportESB = True

                                # shape must all be the same
                                esb_length = row[3]
                                if esb_lengths == []:
                                    esb_lengths.append(esb_length)
                                elif esb_length not in esb_lengths:
                                    reportESB = True

                                # collect ESB issue details in case we have to report
                                if fc not in esb_dict:
                                    esb_dict[fc] = [ruleDesc]
                                else:
                                    rules = esb_dict[fc]
                                    rules.append(ruleDesc)
                                    esb_dict[fc] = rules

                            if check_roads == True and "Road" in fc:

                                # see if the road is marked as an exception or not
                                wc = "SUBMIT = 'Y' AND OBJECTID = " + str(objectID)
                                with SearchCursor(roads, (rd_object.UNIQUEID, rd_object.EXCEPTION), wc) as j_rows:
                                    for j_row in j_rows:
                                        # get the NGSEGID & the exception
                                        ngsegid = j_row[0]
                                        rd_exc = j_row[1]

                                        # check to see if the exception has been marked
                                        if rd_exc in exc_dict:

                                            # get the list of plausible exceptions
                                            plausibleException = exc_dict[rd_exc]

                                            # if the reported issue isn't in acceptable exceptions,
                                            # then report it
                                            if ruleDesc not in plausibleException:
                                                userMessage("In attributes: " + ", ".join(plausibleException))
                                                userMessage("In topology: " + ruleDesc)
                                                # then report the issue
                                                msg = "Error: Topology issue- %s" % ruleDesc
                                                val = (today, msg, fc, "", ngsegid, "Check Topology")
                                                values.append(val)

                                            # the else implying that the marked exception and the
                                            # found issue match, so it should not be marked

                                        # this means it isn't marked, so report the topology issue
                                        elif rd_exc == "NOT EXCEPTION":
                                            # then report the issue
                                            msg = "Error: Topology issue- %s" % ruleDesc
                                            val = (today, msg, fc, "", ngsegid, "Check Topology")
                                            values.append(val)

                                    try:
                                        del j_row, j_rows
                                    except:
                                        pass


                # report back polygon issues
                if reportESB == True:
                    for esb in esb_dict:
                        rules = esb_dict[esb]
                        for rule in rules:
                            # report the issues back as notices
                            msg = "Error: Topology issue- %s" % rule
                            val = (today, msg, esb, "", "", "Check Topology")
                            values.append(val)
            Delete_management(lyr)



    else:
        msg = "Error: Topology does not exist"
        val = (today, msg, "", "", "", "Check Topology")
        values.append(val)

    #report records
    count = 0
    if values != []:
        count = len(values)
        RecordResults(recordType, values, gdb)


    #give the user some feedback
    messageList = ["Topology check complete.", str(count), "issues found."]
    if count > 0:
        messageList.append("Results in FieldValuesCheckResults.")
    elif count == 0:
        #clean up topology export if there were no errors
        for topE in (lineErrors, pointErrors, polyErrors):
            full = join(gdb, topE)
            if Exists(full):
                Delete_management(full)

    message = " ".join(messageList)
    userMessage(message)


def checkToolboxVersionFinal():
    versionResult = checkToolboxVersion()
    if versionResult == "Your NG911 toolbox version is up-to-date.":
        userMessage(versionResult)
    else:
        userWarning(versionResult)

def sanityCheck(currentPathSettings):
    # fcList will contain all layers in GDB so everything will be checked

    # clear out template check results & field check results
    gdb = currentPathSettings.gdbPath
    ClearOldResults(gdb, "true", "true")

    gdbObject = currentPathSettings.gdbObject

    # check template
    checkLayerList(currentPathSettings)
    checkRequiredFields(currentPathSettings)
    checkRequiredFieldValues(currentPathSettings)
    checkStewards(currentPathSettings)
    checkSubmissionNumbers(currentPathSettings)
    findInvalidGeometry(currentPathSettings)

    # common layer checks
    checkValuesAgainstDomain(currentPathSettings)
    checkESBDisplayLength(currentPathSettings)
    checkFeatureLocations(currentPathSettings)
    verifyESBAlignment(currentPathSettings)
    
    # see if we can check out the stewards
    try:
        ab = gdbObject.AuthoritativeBoundary
        stew = getStewards(ab)
        first_steward = stew[0]
        
    except:
        first_steward = ''
        
    try:
        # don't run topology on certain stewards (like Johnson)
        if first_steward not in ['485010']:
            checkTopology(gdbObject, True, True) # check polygons
            
        else:
            userMessage('Intentionally skipped running topology check')
            RecordResults("template", [strftime("%m/%d/%y"), "Notice: Intentionally did not validate topology", "Topology"], gdb)
            
    except Exception as e:
        userWarning(str(e))
        RecordResults("template", [strftime("%m/%d/%y"), "Error: Could not validate topology", "Topology"], gdb)
    checkUniqueIDFrequency(currentPathSettings)

    # check address points
##    geocodeAddressPoints(currentPathSettings)
    addressPoints = gdbObject.AddressPoints
    checkKSPID(addressPoints, "KSPID")
    checkMSAGCOspaces(addressPoints, gdb)
    if fieldExists(addressPoints, "RCLMATCH"):
        checkRCLMATCH(currentPathSettings)
        checkAddressPointGEOMSAG(currentPathSettings)
    AP_freq = gdbObject.AddressPointFrequency
    a_obj = NG911_GDB_Objects.getFCObject(addressPoints)
    AP_fields = a_obj.FREQUENCY_FIELDS_STRING
    checkFrequency(addressPoints, AP_freq, AP_fields, gdb, "true")
    if Exists(gdbObject.ESZ):
        checkESNandMuniAttribute(currentPathSettings)
    else:
        userMessage("ESZ layer does not exist. Cannot complete check.")


    # check roads
    roads = gdbObject.RoadCenterline
    road_freq = gdbObject.RoadCenterlineFrequency
    rc_obj = NG911_GDB_Objects.getFCObject(roads)
    road_fields = rc_obj.FREQUENCY_FIELDS_STRING

    # make sure editor tracking is turned on for the roads
    try:
        EnableEditorTracking_management(roads, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")
    except:
        userWarning("Could not reenable editor tracking on roads.")
        pass

    checkMSAGCOspaces(roads, gdb)
    checkFrequency(roads, road_freq, road_fields, gdb, "true")
    checkCutbacks(currentPathSettings)
    checkLineSelfIntersections(roads)
    checkDirectionality(roads, gdb)
    checkRoadAliases(currentPathSettings)
    # complete check for duplicate address ranges on dual carriageways
    fields = rc_obj.FREQUENCY_FIELDS
    fields.remove("ONEWAY")
    fields_string = ";".join(fields)
    checkFrequency(roads, road_freq, fields_string, gdb, "false")
    # check for overlapping address ranges
    FindOverlaps(gdb)
    # check parities
    checkParities(currentPathSettings)
    
    # add NOTES to FVCR
    if Exists(gdbObject.FieldValuesCheckResults):
        addFVCRNotes(gdb)

    # verify that the check resulted in 0 issues
    sanity = 0 # flag to return at end
    numErrors = 0 # the total number of errors

    fieldCheckResults = gdbObject.FieldValuesCheckResults
    templateResults = gdbObject.TemplateCheckResults

    for table in [fieldCheckResults, templateResults]:
        if Exists(table):
            tbl = "tbl"
            wc = "Description not like '%Notice%'"
            MakeTableView_management(table, tbl, wc)
            count = getFastCount(tbl)
            numErrors = numErrors + count
            Delete_management(tbl)

    #change result = 1
    if numErrors == 0:
        sanity = 1
        today = strftime("%m/%d/%y")
        values = [(today, "Passed all checks")]
        RecordResults("DASCmessage", values, gdb)
        userMessage("Geodatabase passed all data checks.")
    else:
        userWarning("There were %s issues with the data that will prevent a successful submission. Please view errors in the TemplateCheckResults and:or FieldValuesCheckResults tables." % (str(numErrors)))
        userWarning("For documentation on Interpreting Tool Results, please copy and paste this link into your web browser: https://goo.gl/aUlrLH")

    checkToolboxVersionFinal()

    return sanity

def main_check(checkType, currentPathSettings):

    checkList = currentPathSettings.checkList
    gdb = currentPathSettings.gdbPath
    env.workspace = gdb
    env.overwriteOutput = True

    gdbObject = currentPathSettings.gdbObject

    #give user a warning if they didn't select any validation checks
    stuffToCheck = 0
    for cI in checkList:
        if cI == "true":
            stuffToCheck += 1
    if stuffToCheck == 0:
        userMessage("Warning: you choose no validation checks.")

    #check geodatabase template
    if checkType == "template":
        if checkList[0] == "true":
            checkLayerList(currentPathSettings)

        if checkList[1] == "true":
            checkRequiredFields(currentPathSettings)

        if checkList[2] == "true":
            checkRequiredFieldValues(currentPathSettings)
            checkStewards(currentPathSettings)

        if checkList[3] == "true":
            checkSubmissionNumbers(currentPathSettings)

        if checkList[4] == "true":
            findInvalidGeometry(currentPathSettings)

    #check address points
    elif checkType == "AddressPoints":
        addressPoints = gdbObject.AddressPoints
        if checkList[0] == "true":
            checkValuesAgainstDomain(currentPathSettings)
            checkMSAGCOspaces(addressPoints, gdb)
            checkKSPID(addressPoints, "KSPID")
            if fieldExists(addressPoints, "RCLMATCH"):
                checkRCLMATCH(currentPathSettings)
                checkAddressPointGEOMSAG(currentPathSettings)

        if checkList[1] == "true":
            checkFeatureLocations(currentPathSettings)

        if checkList[2] == "true":
            AP_freq = gdbObject.AddressPointFrequency
            a_obj = NG911_GDB_Objects.getFCObject(addressPoints)
            AP_fields = a_obj.FREQUENCY_FIELDS_STRING
            checkFrequency(addressPoints, AP_freq, AP_fields, gdb, "true")

        if checkList[3] == "true":
            checkUniqueIDFrequency(currentPathSettings)

        if checkList[4] == "true":
            if Exists(gdbObject.ESZ):
                checkESNandMuniAttribute(currentPathSettings)
            else:
                userMessage("ESZ layer does not exist, cannot complete check.")

    #check roads
    elif checkType == "Roads":
        roads = gdbObject.RoadCenterline
        rc_obj = NG911_GDB_Objects.getFCObject(roads)
        if checkList[0] == "true":
            checkValuesAgainstDomain(currentPathSettings)
            checkMSAGCOspaces(roads, gdb)

            # check parity
            checkParities(currentPathSettings)

        if checkList[1] == "true":
            checkFeatureLocations(currentPathSettings)

        if checkList[2] == "true":
            road_freq = gdbObject.RoadCenterlineFrequency
            road_fields = rc_obj.FREQUENCY_FIELDS_STRING
            checkFrequency(roads, road_freq, road_fields, gdb, "true")

            # complete check for duplicate address ranges on dual carriageways
            road_freq = gdbObject.RoadCenterlineFrequency
            fields = rc_obj.FREQUENCY_FIELDS
            fields.remove("ONEWAY")
            fields_string = ";".join(fields)
            checkFrequency(roads, road_freq, fields_string, gdb, "false")

        if checkList[3] == "true":
            checkUniqueIDFrequency(currentPathSettings)

        if checkList[4] == "true":
            checkCutbacks(currentPathSettings)
            checkTopology(gdbObject, False, True) # just check roads
            checkLineSelfIntersections(roads)

        if checkList[5] == "true":
            checkDirectionality(roads, gdb)

        if checkList[6] == "true":
            checkRoadAliases(currentPathSettings)

        if checkList[7] == "true":
            # check for address range overlaps
            FindOverlaps(gdb)


    # run standard checks
    elif checkType == "standard":

        if checkList[0] == "true":
            checkValuesAgainstDomain(currentPathSettings)
            checkESBDisplayLength(currentPathSettings)

        if checkList[1] == "true":
            verifyESBAlignment(currentPathSettings)
            checkFeatureLocations(currentPathSettings)
            
            # see if we can check out the stewards
            try:
                ab = gdbObject.AuthoritativeBoundary
                stew = getStewards(ab)
                first_steward = stew[0]
                
            except:
                first_steward = ''
                
            try:
                # don't run topology on certain stewards (like Johnson)
                if first_steward not in ['485010']:
                    checkTopology(gdbObject, True, False) # check polygons
                    
                else:
                    userMessage('Intentionally skipped running polygon topology check')
                    RecordResults("template", [strftime("%m/%d/%y"), "Message: Intentionally did not validate polygon topology", "Topology"], gdb)

            except Exception as e:
                userWarning(str(e))
                RecordResults("template", [strftime("%m/%d/%y"), "Error: Could not validate topology", "Topology"], gdb)

        if checkList[2] == "true":
            checkUniqueIDFrequency(currentPathSettings)
            
    # add NOTES to FVCR
    if Exists(gdbObject.FieldValuesCheckResults):
        addFVCRNotes(gdb)

    # work on reporting
    fieldCheckResults = gdbObject.FieldValuesCheckResults
    templateResults = gdbObject.TemplateCheckResults
    numErrors = 0

    for table in [fieldCheckResults, templateResults]:
        if Exists(table):
            tbl = "tbl"
            wc = "Description not like '%Notice%'"
            MakeTableView_management(table, tbl, wc)
            count = getFastCount(tbl)
            numErrors = numErrors + count
            Delete_management(tbl)

    # change result = 1
    if numErrors > 0:
        BigMessage = """There were issues with the data. Please view errors in
        the TemplateCheckResults and:or FieldValuesCheckResults tables. For
        documentation on Interpreting Tool Results, please copy and paste this
        link into your web browser: https://goo.gl/aUlrLH"""
        userWarning(BigMessage)

    checkToolboxVersionFinal()