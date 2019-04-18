#-------------------------------------------------------------------------------
# Name:        MSAG_DBComparison
# Purpose:     Compare an address point to the road centerline file
#
# Author:      kristen
#
# Created:     10/05/2017
#-------------------------------------------------------------------------------
from NG911_GDB_Objects import getFCObject
from os import remove
from os.path import join, dirname, exists
from arcpy.da import SearchCursor, UpdateCursor, Editor
from arcpy import (AddField_management, AddMessage,
                    MakeFeatureLayer_management, Delete_management,
                    CalculateField_management, Exists, Merge_management,
                    MakeTableView_management, CopyRows_management,
                    DeleteField_management, AddWarning)
from NG911_arcpy_shortcuts import getFastCount, fieldExists
import time

def prep_roads_for_comparison(rd_fc, name_field, code_fields, city_fields, field_list):

    # calculate values for NAME_OVLERAP field
    fields1 = tuple(field_list)

    # add the NAME_OVERLAP field
    if not fieldExists(rd_fc, name_field):
        AddField_management(rd_fc, name_field, "TEXT", "", "", 100)

    i = 0

    if "rcTable" in rd_fc:
        field_list.append("NGSEGID")
        i = field_list.index("NGSEGID")
    elif "apTable" in rd_fc:
        if "NGSEGID" in field_list:
            field_list.remove("NGSEGID")
        field_list.append("NGADDID")
        i = field_list.index("NGADDID")

##    AddMessage("Query field list:" + ", ".join(field_list))

    if "in_memory" not in rd_fc:

        # start edit session
        working_gdb = dirname(rd_fc)
        if working_gdb[-3:] not in ("gdb"):
            working_gdb = dirname(dirname(rd_fc))
        if r"Database Servers\GISS01_SQLEXPRESSGIS.gds" in working_gdb:
            working_gdb =  r"Database Servers\GISS01_SQLEXPRESSGIS.gds\KSNG911S(VERSION:dbo.DEFAULT)"

        # made some changes to account for Butler Co's SDE gdb
    ##    AddMessage(working_gdb)
        edit = Editor(working_gdb)
        if "dbo.DEFAULT" not in working_gdb:
            edit.startEditing(False, False)
        else:
            edit.startEditing(False, True)

    # run update cursor
    with UpdateCursor(rd_fc, fields1) as rows:
        for row in rows:
            field_count = len(fields1)
            start_int = 1
            label = ""

            # loop through the fields to see what's null & skip it
            while start_int < field_count:
                if row[start_int] is not None:
                    if row[start_int] not in ("", " "):
                        label = label + "|" + str(row[start_int]).strip().upper()
                start_int = start_int + 1

            row[0] = label.replace("||","|")
            try:
                rows.updateRow(row)
            except:
                AddMessage("Error with " + rd_fc + field_list[i] + row[i])

    if "in_memory" not in rd_fc:
        edit.stopEditing(True)

    # clean up all labels
    trim_expression = '" ".join(!' + name_field + '!.split())'
    CalculateField_management(rd_fc, name_field, trim_expression, "PYTHON_9.3")

    # covert labels to road code with MSAG city code
    code_block= """def calc_code(rd, city):
                   b = {"A":1,"B":2,"C":3,"D":4,"E":5,"F":6,"G":7,"H":8,"I":9,"J":10,"K":11,
                        "L":12,"M":13,"N":14,"O":15,"P":16,"Q":17,"R":18,"S":19,"T":20,"U":21,
                        "V":22,"W":23,"X":24,"Y":25,"Z":26," ":27,"0":28,"1":29,"2":30,"3":31,"4":32,"5":33,"6":34,"7":35,
                        "8":36,"9":37,"|":38,"-":39,"'":40,";":43}
                   tot = 0
                   if city is None or city in ('', ' ', '  '):
                       city = "   "
                   for name in rd, city:
                       name = name.strip().upper()
                       while len(name) < 3:
                           name = name + " "
                       list_len = len(name)
                       k = 0
                       while k < list_len:
                           try:
                               chars1 = b[name[k].upper()]
                           except:
                               chars1 = 42
                           if 0 < k + 1 < list_len:
                               try:
                                   chars1 = chars1 * k * b[name[k+1].upper()]
                               except:
                                   chars1 = chars1 * k * 42
                           else:
                               try:
                                   chars1 = chars1 * b[name[list_len - 1]]
                               except:
                                   chars1 = chars1 * 42
                           tot += chars1
                           k += 1

                       # make sure all the values actually work
                       if name[0].upper() not in b:
                           a0 = 42
                       else:
                           a0 = b[name[0].upper()]

                       if name[1].upper() not in b:
                           a1 = 43
                       else:
                           a1 = b[name[1].upper()]

                       if name[2].upper() not in b:
                           a2 = 44
                       else:
                           a2 = b[name[2].upper()]

                       if name[-1].upper() not in b:
                           a3 = 45
                       else:
                           a3 = b[name[-1].upper()]

                       c = len(rd) + len(city)
                       tot = tot * c - a1 + a2 - a3

                   return tot"""

    for code_field in code_fields:
        i = code_fields.index(code_field)
        city_field = city_fields[i]
        # add the NAME_OVERLAP field
        if not fieldExists(rd_fc, code_field):
            AddField_management(rd_fc, code_field, "LONG")
##        try:
        CalculateField_management(rd_fc, code_field, "calc_code( !" + name_field + "!.upper(), !" + city_field + "! )", "PYTHON_9.3", code_block)
##        except:
##            CalculateField_management(rd_fc, code_field, 1, "PYTHON_9.3")


def ap_compare(hno, hno_code, ap_fc):

    segid_list = []

    wc = "CODE_COMPARE = %s AND HNO = %s AND LOCTYPE = 'PRIMARY'" % (str(hno_code), str(hno))
##    wc = "CODE_COMPARE = " + str(hno_code) + " AND HNO = " + str(hno)

    a = "a"
    MakeFeatureLayer_management(ap_fc, a, wc)
    count = getFastCount(a)

    if count > 0:
        # search cursor to get all ties

        segid_field = "NGADDID"

        rd_fields = (segid_field)

        with SearchCursor(ap_fc, rd_fields, wc) as r_rows:
            for r_row in r_rows:
                segid_list.append(r_row[0])

            try:
                del r_row, r_rows
            except:
                pass

        del rd_fields

    if len(segid_list) == 1:
        segid = segid_list[0]
    elif len(segid_list) == 0:
        segid = ""
    else:
        segid = "TIES"

    Delete_management(a)

    return segid
    del segid_list


def db_compare(hno, hno_code, tempTable, addid, txt, idField):
    # see if the text file exists already
    if exists(txt):
        method = "a"
    else:
        method = "w"

    # see if the address number is even or odd
    if hno & 1: # bitwise operation to test for odd/even (thanks to Sherry M.)
        parity = "('O','B')"
    else:
        parity = "('E','B')"

    segid_list = []

    # set up wc to query the road table accordingly
    wc = "CODE_COMPARE = " + str(hno_code) + " AND PARITY in " + parity

    # if the version is 2.1, make sure only the AUTH = Y records are used
    if fieldExists(tempTable, "AUTH"):
        wc = wc + " AND AUTH = 'Y'"

    segid_field = "NGSEGID"
    side = "N"

    rd_fields = [segid_field, "FROM_ADD", "TO_ADD", "RCLSIDE", "PARITY"]

    with SearchCursor(tempTable, rd_fields, wc) as r_rows:
        for r_row in r_rows:

            # set the counter for the range, it'll usually be 2
            range_counter = 2
            if r_row[4] == "B": # if the range is B (both sides), the counter = 1
                range_counter = 1

            # get the range by 2s
            sideRange = list(range(r_row[1], r_row[2] + range_counter, range_counter))

            # if the range was high to low, flip it
            if sideRange == []:
                sideRange = list(range(r_row[2], r_row[1] + range_counter, range_counter))

            if hno in sideRange:
                if r_row[0] is None:
                    AddWarning("An NGSEGID value is blank/null. Matching records cannot be calculated. Make sure all NGSEGIDs are populated and run again.")
                    segid_list.append("NULL_ID")
                else:
                    segid_list.append(r_row[0])

                    # grab the side, I'll reset later if it should be N
                    side = r_row[3]

        try:
            del r_row, r_rows
        except:
            pass

    del rd_fields

    if len(segid_list) == 1:
        segid = segid_list[0]
    elif len(segid_list) == 0:
        segid = ""
        side = "N"
    else:
        segids = idField + " " + addid + " TIES WHERE CLAUSE: NGSEGID in ('" + "', '".join(segid_list) + "')\n"
        writeToText(txt, segids, method)
        segid = "TIES"
        side = "N"

    return [segid, side]
    del segid_list


def writeToText(textFile, stuff, method):
    FILE = open(textFile, method)
    FILE.writelines(stuff)
    FILE.close()


def launch_compare(gdb, output_table, HNO, addy_city_field, addy_field_list, queryAP):

##    start_time = time.time()
    rd_fc = join(gdb, "NG911", "RoadCenterline")
    ap_fc = join(gdb, "NG911", "AddressPoints")
    name_field = "NAME_COMPARE"
    code_field = "CODE_COMPARE"
    city_field = "MSAGCO"
    rd_object = getFCObject(rd_fc)

    # flip switch for gdb instead of in_memory
    storage = "in_memory"
    #storage = gdb

    # prep address points with concatenated label field

    prep_roads_for_comparison(output_table, name_field, [code_field], [addy_city_field], addy_field_list)

    # prep road centerline with concatenated label field
    road_field_list = ["NAME_COMPARE", "PRD", "STP", "RD", "STS", "POD", "POM"]
    version = rd_object.GDB_VERSION

    # copy the roads to a table for comparison
    rc_table_view = "rc_table_view"

    rt = join(storage, "rcTable" + version)
    if Exists(rt):
        Delete_management(rt)
    wc = "SUBMIT = 'Y'"
    MakeTableView_management(rd_fc, rc_table_view, wc)
    CopyRows_management(rc_table_view, rt)
    prep_roads_for_comparison(rt, name_field, [code_field + "_L", code_field +"_R"], [ city_field + "_L", city_field + "_R"], road_field_list)

    # prep address points with concatenated label field if necessary
    if queryAP == True:
        addy_field_list1 = ["NAME_COMPARE", "PRD", "STP", "RD", "STS", "POD", "POM"]
        prep_roads_for_comparison(ap_fc, name_field, [code_field], [city_field], addy_field_list1)

    if version == "20":

        l_field_info = """OBJECTID OBJECTID HIDDEN NONE;Shape Shape HIDDEN NONE;STEWARD STEWARD HIDDEN NONE;L_UPDATE L_UPDATE HIDDEN NONE;
        EFF_DATE EFF_DATE HIDDEN NONE;EXP_DATE EXP_DATE HIDDEN NONE;NGSEGID NGSEGID VISIBLE NONE;STATE_L STATE_L HIDDEN NONE;
        STATE_R STATE_R HIDDEN NONE;COUNTY_L COUNTY_L HIDDEN NONE;COUNTY_R COUNTY_R HIDDEN NONE;MUNI_L MUNI_L HIDDEN NONE;
        MUNI_R MUNI_R HIDDEN NONE;L_F_ADD FROM_ADD VISIBLE NONE;L_T_ADD TO_ADD VISIBLE NONE;R_F_ADD R_F_ADD HIDDEN NONE;
        R_T_ADD R_T_ADD HIDDEN NONE;PARITY_L PARITY VISIBLE NONE;PARITY_R PARITY_R HIDDEN NONE;POSTCO_L POSTCO_L HIDDEN NONE;
        POSTCO_R POSTCO_R HIDDEN NONE;ZIP_L ZIP_L HIDDEN NONE;ZIP_R ZIP_R HIDDEN NONE;ESN_L ESN_L HIDDEN NONE;ESN_R ESN_R HIDDEN NONE;
        MSAGCO_L MSAGCO VISIBLE NONE;MSAGCO_R MSAGCO_R HIDDEN NONE;PRD PRD HIDDEN NONE;STP STP HIDDEN NONE;RD RD HIDDEN NONE;
        STS STS HIDDEN NONE;POD POD HIDDEN NONE;POM POM HIDDEN NONE;SPDLIMIT SPDLIMIT HIDDEN NONE;ONEWAY ONEWAY HIDDEN NONE;
        RDCLASS RDCLASS HIDDEN NONE;UPDATEBY UPDATEBY HIDDEN NONE;LABEL LABEL HIDDEN NONE;ELEV_F ELEV_F HIDDEN NONE;
        ELEV_T ELEV_T HIDDEN NONE;SURFACE SURFACE HIDDEN NONE;STATUS STATUS HIDDEN NONE;TRAVEL TRAVEL HIDDEN NONE;
        LRSKEY LRSKEY HIDDEN NONE;EXCEPTION EXCEPTION HIDDEN NONE;SUBMIT SUBMIT HIDDEN NONE;NOTES NOTES HIDDEN NONE;
        UNINC_L UNINC_L HIDDEN NONE;UNINC_R UNINC_R HIDDEN NONE;Shape_Length Shape_Length HIDDEN NONE;ESN_C ESN_C HIDDEN NONE;
        NAME_COMPARE NAME_COMPARE VISIBLE NONE;CODE_COMPARE_L CODE_COMPARE VISIBLE NONE;CODE_COMPARE_R CODE_COMPARE_R HIDDEN NONE"""

        r_field_info = """OBJECTID OBJECTID HIDDEN NONE;Shape Shape HIDDEN NONE;STEWARD STEWARD HIDDEN NONE;L_UPDATE L_UPDATE HIDDEN NONE;
        EFF_DATE EFF_DATE HIDDEN NONE;EXP_DATE EXP_DATE HIDDEN NONE;NGSEGID NGSEGID VISIBLE NONE;STATE_L STATE_L HIDDEN NONE;
        STATE_R STATE_R HIDDEN NONE;COUNTY_L COUNTY_L HIDDEN NONE;COUNTY_R COUNTY_R HIDDEN NONE;MUNI_L MUNI_L HIDDEN NONE;
        MUNI_R MUNI_R HIDDEN NONE;L_F_ADD L_F_ADD HIDDEN NONE;L_T_ADD L_T_ADD HIDDEN NONE;R_F_ADD FROM_ADD VISIBLE NONE;
        R_T_ADD TO_ADD VISIBLE NONE;PARITY_L PARITY_L HIDDEN NONE;PARITY_R PARITY VISIBLE NONE;POSTCO_L POSTCO_L HIDDEN NONE;
        POSTCO_R POSTCO_R HIDDEN NONE;ZIP_L ZIP_L HIDDEN NONE;ZIP_R ZIP_R HIDDEN NONE;ESN_L ESN_L HIDDEN NONE;ESN_R ESN_R HIDDEN NONE;
        MSAGCO_L MSAGCO_L HIDDEN NONE;MSAGCO_R MSAGCO VISIBLE NONE;PRD PRD HIDDEN NONE;STP STP HIDDEN NONE;RD RD HIDDEN NONE;
        STS STS HIDDEN NONE;POD POD HIDDEN NONE;POM POM HIDDEN NONE;SPDLIMIT SPDLIMIT HIDDEN NONE;ONEWAY ONEWAY HIDDEN NONE;
        RDCLASS RDCLASS HIDDEN NONE;UPDATEBY UPDATEBY HIDDEN NONE;LABEL LABEL HIDDEN NONE;ELEV_F ELEV_F HIDDEN NONE;
        ELEV_T ELEV_T HIDDEN NONE;SURFACE SURFACE HIDDEN NONE;STATUS STATUS HIDDEN NONE;TRAVEL TRAVEL HIDDEN NONE;
        LRSKEY LRSKEY HIDDEN NONE;EXCEPTION EXCEPTION HIDDEN NONE;SUBMIT SUBMIT HIDDEN NONE;NOTES NOTES HIDDEN NONE;
        UNINC_L UNINC_L HIDDEN NONE;UNINC_R UNINC_R HIDDEN NONE;Shape_Length Shape_Length HIDDEN NONE;ESN_C ESN_C HIDDEN NONE;
        NAME_COMPARE NAME_COMPARE VISIBLE NONE;CODE_COMPARE_L CODE_COMPARE_L HIDDEN NONE;CODE_COMPARE_R CODE_COMPARE VISIBLE NONE"""

    elif version == "21":
        l_field_info = """OBJECTID OBJECTID HIDDEN NONE;Shape Shape HIDDEN NONE;STEWARD STEWARD HIDDEN NONE;L_UPDATE L_UPDATE HIDDEN NONE;
        EFF_DATE EFF_DATE HIDDEN NONE;EXP_DATE EXP_DATE HIDDEN NONE;NGSEGID NGSEGID VISIBLE NONE;STATE_L STATE_L HIDDEN NONE;
        STATE_R STATE_R HIDDEN NONE;COUNTY_L COUNTY_L HIDDEN NONE;COUNTY_R COUNTY_R HIDDEN NONE;MUNI_L MUNI_L HIDDEN NONE;
        MUNI_R MUNI_R HIDDEN NONE;L_F_ADD FROM_ADD VISIBLE NONE;L_T_ADD TO_ADD VISIBLE NONE;R_F_ADD R_F_ADD HIDDEN NONE;
        R_T_ADD R_T_ADD HIDDEN NONE;PARITY_L PARITY VISIBLE NONE;PARITY_R PARITY_R HIDDEN NONE;POSTCO_L POSTCO_L HIDDEN NONE;
        POSTCO_R POSTCO_R HIDDEN NONE;ZIP_L ZIP_L HIDDEN NONE;ZIP_R ZIP_R HIDDEN NONE;ESN_L ESN_L HIDDEN NONE;ESN_R ESN_R HIDDEN NONE;
        MSAGCO_L MSAGCO VISIBLE NONE;MSAGCO_R MSAGCO_R HIDDEN NONE;PRD PRD HIDDEN NONE;STP STP HIDDEN NONE;RD RD HIDDEN NONE;
        STS STS HIDDEN NONE;POD POD HIDDEN NONE;POM POM HIDDEN NONE;SPDLIMIT SPDLIMIT HIDDEN NONE;ONEWAY ONEWAY HIDDEN NONE;
        RDCLASS RDCLASS HIDDEN NONE;UPDATEBY UPDATEBY HIDDEN NONE;LABEL LABEL HIDDEN NONE;ELEV_F ELEV_F HIDDEN NONE;
        ELEV_T ELEV_T HIDDEN NONE;SURFACE SURFACE HIDDEN NONE;STATUS STATUS HIDDEN NONE;TRAVEL TRAVEL HIDDEN NONE;
        LRSKEY LRSKEY HIDDEN NONE;EXCEPTION EXCEPTION HIDDEN NONE;SUBMIT SUBMIT HIDDEN NONE;NOTES NOTES HIDDEN NONE;
        UNINC_L UNINC_L HIDDEN NONE;UNINC_R UNINC_R HIDDEN NONE;Shape_Length Shape_Length HIDDEN NONE;
        AUTH_L AUTH VISIBLE NONE;AUTH_R AUTH_R HIDDEN NONE;GEOMSAGL GEOMSAGL HIDDEN NONE;GEOMSAGR GEOMSAGR HIDDEN NONE;
        NAME_COMPARE NAME_COMPARE VISIBLE NONE;CODE_COMPARE_L CODE_COMPARE VISIBLE NONE;CODE_COMPARE_R CODE_COMPARE_R HIDDEN NONE"""

        r_field_info = """OBJECTID OBJECTID HIDDEN NONE;Shape Shape HIDDEN NONE;STEWARD STEWARD HIDDEN NONE;L_UPDATE L_UPDATE HIDDEN NONE;
        EFF_DATE EFF_DATE HIDDEN NONE;EXP_DATE EXP_DATE HIDDEN NONE;NGSEGID NGSEGID VISIBLE NONE;STATE_L STATE_L HIDDEN NONE;
        STATE_R STATE_R HIDDEN NONE;COUNTY_L COUNTY_L HIDDEN NONE;COUNTY_R COUNTY_R HIDDEN NONE;MUNI_L MUNI_L HIDDEN NONE;
        MUNI_R MUNI_R HIDDEN NONE;L_F_ADD L_F_ADD HIDDEN NONE;L_T_ADD L_T_ADD HIDDEN NONE;R_F_ADD FROM_ADD VISIBLE NONE;
        R_T_ADD TO_ADD VISIBLE NONE;PARITY_L PARITY_L HIDDEN NONE;PARITY_R PARITY VISIBLE NONE;POSTCO_L POSTCO_L HIDDEN NONE;
        POSTCO_R POSTCO_R HIDDEN NONE;ZIP_L ZIP_L HIDDEN NONE;ZIP_R ZIP_R HIDDEN NONE;ESN_L ESN_L HIDDEN NONE;ESN_R ESN_R HIDDEN NONE;
        MSAGCO_L MSAGCO_L HIDDEN NONE;MSAGCO_R MSAGCO VISIBLE NONE;PRD PRD HIDDEN NONE;STP STP HIDDEN NONE;RD RD HIDDEN NONE;
        STS STS HIDDEN NONE;POD POD HIDDEN NONE;POM POM HIDDEN NONE;SPDLIMIT SPDLIMIT HIDDEN NONE;ONEWAY ONEWAY HIDDEN NONE;
        RDCLASS RDCLASS HIDDEN NONE;UPDATEBY UPDATEBY HIDDEN NONE;LABEL LABEL HIDDEN NONE;ELEV_F ELEV_F HIDDEN NONE;
        ELEV_T ELEV_T HIDDEN NONE;SURFACE SURFACE HIDDEN NONE;STATUS STATUS HIDDEN NONE;TRAVEL TRAVEL HIDDEN NONE;
        LRSKEY LRSKEY HIDDEN NONE;EXCEPTION EXCEPTION HIDDEN NONE;SUBMIT SUBMIT HIDDEN NONE;NOTES NOTES HIDDEN NONE;
        UNINC_L UNINC_L HIDDEN NONE;UNINC_R UNINC_R HIDDEN NONE;Shape_Length Shape_Length HIDDEN NONE;
        AUTH_L AUTH_L HIDDEN NONE;AUTH_R AUTH VISIBLE NONE;GEOMSAGL GEOMSAGL HIDDEN NONE;GEOMSAGR GEOMSAGR HIDDEN NONE;
        NAME_COMPARE NAME_COMPARE VISIBLE NONE;CODE_COMPARE_L CODE_COMPARE_L HIDDEN NONE;CODE_COMPARE_R CODE_COMPARE VISIBLE NONE"""

    # set up list of lists to look at each side of the road
    side_lists = [[rd_object.PARITY_L, rd_object.L_F_ADD, rd_object.L_T_ADD, rd_object.UNIQUEID,  code_field + "_L", "RoadCenterline_Layer", l_field_info],
                  [rd_object.PARITY_R, rd_object.R_F_ADD, rd_object.R_T_ADD, rd_object.UNIQUEID, code_field + "_R", "RoadCenterline_Layer2", r_field_info]]


    # create a temp table of road segments
    # do not include 0-0 ranges or records not for submission
    for side in side_lists:
        # get the side
        side_x = side[4][-1]

        # set up field equivalences
        wanted_fields_dict = {"PARITY": side[0], "FROM_ADD": side[1], "TO_ADD": side[2],
                        "CODE_COMPARE": side[4]}

        if version == "21":
            wanted_fields_dict["AUTH"] = "AUTH_" + side_x

        # set up where clause
        wc = "(" + side[1] + " <> 0 or " + side[2] + " <> 0)"
        lyr = "lyr"
        # include- high, low, code field, parity, and NGSEGID_L or _R
        MakeTableView_management(rt, lyr, wc, "", side[6])

        holder = join(storage, side[5])
        if Exists(holder):
            Delete_management(holder)
        CopyRows_management(lyr, holder)
        Delete_management(lyr)

        # made sure the table has a column for what side of the street it is
        if not fieldExists(holder, "RCLSIDE"):
            AddField_management(holder, "RCLSIDE", "TEXT", "", "", 1)
        CalculateField_management(holder, "RCLSIDE", '"' + side_x + '"', "PYTHON_9.3", "")

        # make sure that the side-neutral field names get added for comparison
        for w_f in wanted_fields_dict.keys():
            if not fieldExists(holder, w_f):
                if "PARITY" in w_f or "AUTH" in w_f:
                    if not fieldExists(holder, w_f):
                        AddField_management(holder, w_f, "TEXT", "", "", 1)
                    CalculateField_management(holder, w_f, "!" + wanted_fields_dict[w_f] + "!", "PYTHON", "")

                else:
                    if not fieldExists(holder, w_f):
                        AddField_management(holder, w_f, "LONG")
                    CalculateField_management(holder, w_f, "!" + wanted_fields_dict[w_f] + "!", "PYTHON", "")


    #create a temporary table of side-specific ranges
    if "TN_List" in output_table:
        tempTable = join(dirname(output_table), "RoadList_" + time.strftime('%Y%m%d'))
    else:
        tempTable = join(storage, "RoadsTemp")
    if Exists(tempTable):
        Delete_management(tempTable)

    rc_1 = join(storage, "RoadCenterline_Layer")
    rc_2 = join(storage, "RoadCenterline_Layer2")
    Merge_management([rc_1, rc_2], tempTable)

    Delete_management(rc_1)
    Delete_management(rc_2)
    Delete_management(rt)

    # make sure certain fields exist in the address point layer
    makeSureFieldDict = {"MATCH": 1, rd_object.UNIQUEID: 38, "MATCH_LAYER": 20, "RCLSIDE": 1}

    for fld in makeSureFieldDict.keys():
        length = makeSureFieldDict[fld]
        if not fieldExists(output_table, fld):
            AddField_management(output_table, fld, "TEXT", "", "", length)

    idField = "NGADDID"
    if "TN_List" in output_table:
        idField = "NGTNID"

    addy_fields = [HNO, code_field, "MATCH", rd_object.UNIQUEID, "MATCH_LAYER", "RCLSIDE", idField]

    non_match_count = 0
    count = 1

    # set up reporting so the user knows how things are coming along
    total = getFastCount(output_table)
    half = round(total/2,0)
    quarter = round(half/2,0)
    three_quarters = half + quarter
    timeDict = {quarter: "1/4", half:"1/2", three_quarters:"3/4"}

    # create a text file that will report back geocoding ties
    txt = gdb.replace(".gdb", "_TIES.txt")
    if exists(txt):
        remove(txt)

    # loop through address points to compare each one
    no1_wc = "CODE_COMPARE <> 1"
    with UpdateCursor(output_table, addy_fields, no1_wc) as rows:
        for row in rows:
##            r_start_time = time.time()
            # set defaults
            segid = ""
            side = ""
            addid = row[6]

            # start testing out addresses
            hno, hno_code = row[0], row[1]
            if hno not in (None, "", " "):
                try:
                    hno = int(hno)
                    match_combo = db_compare(hno, hno_code, tempTable, addid, txt, idField)
                    segid = match_combo[0]
                    side = match_combo[1]
                except:
                    hno = ""

            match = "M"
            layer = "RoadCenterline"
            if segid == "TIES":
                match = "T"
                side = "N"
                non_match_count += 1
            elif segid == "":
                if queryAP == True and hno not in (None, "", " "):
                    segid = ap_compare(hno, hno_code, ap_fc)
                    match = "M"
                    side = "N"
                    layer = "AddressPoints"
                    if segid =="TIES":
                        match = "T"
                        side = "N"
                        non_match_count += 1
                    elif segid == "":
                        match = "U"
                        side = "N"
                        non_match_count += 1
                else:
                    match = "U"
                    side = "N"
                    non_match_count += 1

            if match == "U":
                layer = ""

            row[2] = match
            row[3] = segid
            row[4] = layer
            if version == "21":
                row[5] = side

            rows.updateRow(row)
##            r_end_time = time.time()
##            print("Record time: %g seconds" % (r_end_time - r_start_time))
##            AddMessage("Record time: %g seconds" % (r_end_time - r_start_time))
            if count in timeDict:
                fraction = timeDict[count]
                AddMessage("Processing is " + fraction + " complete.")
##                partial_time = time.time()
##                AddMessage("Elapsed time s %g seconds" % (partial_time - start_time))
##
            count += 1

    if non_match_count == 0:
        print("All address points match. Good job.")
        AddMessage("All address points match. Good job.")
    else:
        print("Some address points did not match. Results are available in " + output_table + ", ties are listed in " + txt + ". Please examine the MATCH field to find U (unmatched) records or T (ties).")
        AddMessage("Some address points did not match. Results are available in " + output_table + ", ties are listed in " + txt + ". Please examine the MATCH field to find U (unmatched) records or T (ties).")

##    end_time = time.time()
##    print("Elapsed time was %g seconds" % (end_time - start_time))

    # clean up
    if "TN_List" not in output_table:
        try:
            Delete_management(tempTable)
        except:
            pass

    for field in ["NAME_COMPARE", "CODE_COMPARE", "CODE_COMPARE_L", "CODE_COMPARE_R"]:
        for data in [ap_fc]:
            if fieldExists(data, field):
                try:
                    DeleteField_management(data, field)
                except:
                    pass

if __name__ == '__main__':
    main()
