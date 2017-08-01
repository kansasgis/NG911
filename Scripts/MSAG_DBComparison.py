#-------------------------------------------------------------------------------
# Name:        MSAG_DBComparison
# Purpose:     Compare an address point to the road centerline file
#
# Author:      kristen
#
# Created:     10/05/2017
#-------------------------------------------------------------------------------
from NG911_GDB_Objects import (getDefault20NG911AddressObject,
                        getDefault20NG911RoadCenterlineObject,
                        getFCObject)
from os.path import join, dirname
from arcpy.da import SearchCursor, UpdateCursor, Editor
from arcpy import (Copy_management, AddField_management, AddMessage,
                    MakeFeatureLayer_management, Delete_management,
                    CalculateField_management, Exists, Merge_management,
                    MakeTableView_management, CopyRows_management,
                    DeleteField_management)
from NG911_arcpy_shortcuts import getFastCount, fieldExists
import time

def prep_roads_for_comparison(rd_fc, name_field, code_fields, city_fields, field_list):

    working_gdb = dirname(dirname(rd_fc))

    rd_object = getDefault20NG911RoadCenterlineObject()

    # add the NAME_OVERLAP field
    if not fieldExists(rd_fc, name_field):
        AddField_management(rd_fc, name_field, "TEXT", "", "", 50)

    # calculate values for NAME_OVLERAP field
    fields1 = tuple(field_list)

    # start edit session
    edit = Editor(working_gdb)
    edit.startEditing(False, False)

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
                        label = label + "|" + str(row[start_int]).strip()
                start_int = start_int + 1

            row[0] = label.replace("||","|")
            rows.updateRow(row)

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
                       while len(name) < 3:
                           name = name + " "
                       list_len = len(name)
                       k = 0
                       while k < list_len:
                           try:
                               chars1 = b[name[k]]
                           except:
                               chars1 = 42
                           if 0 < k + 1 < list_len:
                               try:
                                   chars1 = chars1 * k * b[name[k+1]]
                               except:
                                   chars1 = chars1 * k * 41
                           else:
                               chars1 = chars1 * b[name[list_len - 1]]
                           tot += chars1
                           k += 1
                       tot = tot * b[name[0]] - b[name[1]] + b[name[2]]
                   return tot"""

    for code_field in code_fields:
        i = code_fields.index(code_field)
        city_field = city_fields[i]
        # add the NAME_OVERLAP field
        if not fieldExists(rd_fc, code_field):
            AddField_management(rd_fc, code_field, "LONG")
        try:
            CalculateField_management(rd_fc, code_field, "calc_code( !" + name_field + "!.upper(), !" + city_field + "! )", "PYTHON_9.3", code_block)
        except:
            CalculateField_management(rd_fc, code_field, 1, "PYTHON_9.3")


def db_compare(hno, hno_code, tempTable):

    # see if the address number is even or odd
    if int(str(hno)[-1]) & 1: # bitwise operation to test for odd/even (thanks to Sherry M.)
        parity = "('O','B')"
    else:
        parity = "('E','B')"

    segid_list = []

    wc = "CODE_COMPARE = " + str(hno_code) + " AND PARITY in " + parity

    segid_field = "NGSEGID"
    if not fieldExists(tempTable, segid_field):
        segid_field = "SEGID"

    rd_fields = (segid_field, "FROM_", "TO")
    with SearchCursor(tempTable, rd_fields, wc) as r_rows:
        for r_row in r_rows:
            f_add = r_row[1]
            t_add = r_row[2]

            # get high and low
            if f_add < t_add:
                low = f_add
                high = t_add
            else:
                low = t_add
                high = f_add

            if low <= hno <= high:
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

    return segid
    del segid_list


def launch_compare(gdb, output_table, HNO, addy_city_field, addy_field_list):
##    start_time = time.time()
    rd_fc = join(gdb, "NG911", "RoadCenterline")
    name_field = "NAME_COMPARE"
    code_field = "CODE_COMPARE"
    city_field = "MSAGCO"
    rd_object = getFCObject(rd_fc)

    # prep address points with concatenated label field
    if addy_field_list[0] != name_field:
        addy_field_list[0] = name_field
    prep_roads_for_comparison(output_table, name_field, [code_field], [addy_city_field], addy_field_list)

    # prep road centerline with concatenated label field
    road_field_list = rd_object.LABEL_FIELDS
    road_field_list[0] = name_field
    prep_roads_for_comparison(rd_fc, name_field, [code_field + "_L", code_field +"_R"], [ city_field + "_L", city_field + "_R"], road_field_list)

    segid_field = rd_object.UNIQUEID

    l_field_info = """OBJECTID OBJECTID HIDDEN NONE;Shape Shape HIDDEN NONE;STEWARD STEWARD HIDDEN NONE;L_UPDATE L_UPDATE HIDDEN NONE;
    EFF_DATE EFF_DATE HIDDEN NONE;EXP_DATE EXP_DATE HIDDEN NONE;""" + segid_field + " " + segid_field + """ VISIBLE NONE;STATE_L STATE_L HIDDEN NONE;
    STATE_R STATE_R HIDDEN NONE;COUNTY_L COUNTY_L HIDDEN NONE;COUNTY_R COUNTY_R HIDDEN NONE;MUNI_L MUNI_L HIDDEN NONE;
    MUNI_R MUNI_R HIDDEN NONE;L_F_ADD FROM VISIBLE NONE;L_T_ADD TO VISIBLE NONE;R_F_ADD R_F_ADD HIDDEN NONE;
    R_T_ADD R_T_ADD HIDDEN NONE;PARITY_L PARITY VISIBLE NONE;PARITY_R PARITY_R HIDDEN NONE;POSTCO_L POSTCO_L HIDDEN NONE;
    POSTCO_R POSTCO_R HIDDEN NONE;ZIP_L ZIP_L HIDDEN NONE;ZIP_R ZIP_R HIDDEN NONE;ESN_L ESN_L HIDDEN NONE;ESN_R ESN_R HIDDEN NONE;
    MSAGCO_L MSAGCO_L HIDDEN NONE;MSAGCO_R MSAGCO_R HIDDEN NONE;PRD PRD HIDDEN NONE;STP STP HIDDEN NONE;RD RD HIDDEN NONE;
    STS STS HIDDEN NONE;POD POD HIDDEN NONE;POM POM HIDDEN NONE;SPDLIMIT SPDLIMIT HIDDEN NONE;ONEWAY ONEWAY HIDDEN NONE;
    RDCLASS RDCLASS HIDDEN NONE;UPDATEBY UPDATEBY HIDDEN NONE;LABEL LABEL HIDDEN NONE;ELEV_F ELEV_F HIDDEN NONE;
    ELEV_T ELEV_T HIDDEN NONE;SURFACE SURFACE HIDDEN NONE;STATUS STATUS HIDDEN NONE;TRAVEL TRAVEL HIDDEN NONE;
    LRSKEY LRSKEY HIDDEN NONE;EXCEPTION EXCEPTION HIDDEN NONE;SUBMIT SUBMIT HIDDEN NONE;NOTES NOTES HIDDEN NONE;
    UNINC_L UNINC_L HIDDEN NONE;UNINC_R UNINC_R HIDDEN NONE;Shape_Length Shape_Length HIDDEN NONE;ESN_C ESN_C HIDDEN NONE;
    NAME_COMPARE NAME_COMPARE VISIBLE NONE;CODE_COMPARE_L CODE_COMPARE VISIBLE NONE;CODE_COMPARE_R CODE_COMPARE_R HIDDEN NONE"""

    r_field_info = """OBJECTID OBJECTID HIDDEN NONE;Shape Shape HIDDEN NONE;STEWARD STEWARD HIDDEN NONE;L_UPDATE L_UPDATE HIDDEN NONE;
    EFF_DATE EFF_DATE HIDDEN NONE;EXP_DATE EXP_DATE HIDDEN NONE;""" + segid_field + " " + segid_field + """ VISIBLE NONE;STATE_L STATE_L HIDDEN NONE;
    STATE_R STATE_R HIDDEN NONE;COUNTY_L COUNTY_L HIDDEN NONE;COUNTY_R COUNTY_R HIDDEN NONE;MUNI_L MUNI_L HIDDEN NONE;
    MUNI_R MUNI_R HIDDEN NONE;L_F_ADD L_F_ADD HIDDEN NONE;L_T_ADD L_T_ADD HIDDEN NONE;R_F_ADD FROM VISIBLE NONE;
    R_T_ADD TO VISIBLE NONE;PARITY_L PARITY_L HIDDEN NONE;PARITY_R PARITY VISIBLE NONE;POSTCO_L POSTCO_L HIDDEN NONE;
    POSTCO_R POSTCO_R HIDDEN NONE;ZIP_L ZIP_L HIDDEN NONE;ZIP_R ZIP_R HIDDEN NONE;ESN_L ESN_L HIDDEN NONE;ESN_R ESN_R HIDDEN NONE;
    MSAGCO_L MSAGCO_L HIDDEN NONE;MSAGCO_R MSAGCO_R HIDDEN NONE;PRD PRD HIDDEN NONE;STP STP HIDDEN NONE;RD RD HIDDEN NONE;
    STS STS HIDDEN NONE;POD POD HIDDEN NONE;POM POM HIDDEN NONE;SPDLIMIT SPDLIMIT HIDDEN NONE;ONEWAY ONEWAY HIDDEN NONE;
    RDCLASS RDCLASS HIDDEN NONE;UPDATEBY UPDATEBY HIDDEN NONE;LABEL LABEL HIDDEN NONE;ELEV_F ELEV_F HIDDEN NONE;
    ELEV_T ELEV_T HIDDEN NONE;SURFACE SURFACE HIDDEN NONE;STATUS STATUS HIDDEN NONE;TRAVEL TRAVEL HIDDEN NONE;
    LRSKEY LRSKEY HIDDEN NONE;EXCEPTION EXCEPTION HIDDEN NONE;SUBMIT SUBMIT HIDDEN NONE;NOTES NOTES HIDDEN NONE;
    UNINC_L UNINC_L HIDDEN NONE;UNINC_R UNINC_R HIDDEN NONE;Shape_Length Shape_Length HIDDEN NONE;ESN_C ESN_C HIDDEN NONE;
    NAME_COMPARE NAME_COMPARE VISIBLE NONE;CODE_COMPARE_L CODE_COMPARE_L HIDDEN NONE;CODE_COMPARE_R CODE_COMPARE VISIBLE NONE"""

    # set up list of lists to look at each side of the road
    side_lists = [[rd_object.PARITY_L, rd_object.L_F_ADD, rd_object.L_T_ADD, rd_object.UNIQUEID,  code_field + "_L", "RoadCenterline_Layer", l_field_info],
                  [rd_object.PARITY_R, rd_object.R_F_ADD, rd_object.R_T_ADD, rd_object.UNIQUEID, code_field + "_R", "RoadCenterline_Layer2", r_field_info]]

    wanted_fields = ["PARITY", "FROM_", "TO", "CODE_COMPARE"]
    # create a temp table of road segments
    # do not include 0-0 ranges or records not for submission
    for side in side_lists:
        wc = "(" + side[1] + " <> 0 or " + side[2] + " <> 0) AND SUBMIT not in ('N')"
        lyr = "lyr"
        # include- high, low, code field, parity, and NGSEGID_L or _R
        MakeTableView_management(rd_fc, lyr, wc, "", side[6])
        if Exists(join(gdb, side[5])):
            Delete_management(join(gdb, side[5]))
        CopyRows_management(lyr, join(gdb, side[5]))
        Delete_management(lyr)

        fields = [side[0], side[1], side[2], side[4]]

        # make sure that the side-neutral field names get added for comparison
        for w_f in wanted_fields:
            if not fieldExists(join(gdb, side[5]), w_f):
                if "PARITY" in w_f:
                    AddField_management(join(gdb, side[5]), w_f, "TEXT", "", "", 1)
                    CalculateField_management(join(gdb, side[5]), w_f, "!" + fields[wanted_fields.index(w_f)] + "!", "PYTHON", "")
                else:
                    AddField_management(join(gdb, side[5]), w_f, "LONG")
                    CalculateField_management(join(gdb, side[5]), w_f, "!" + fields[wanted_fields.index(w_f)] + "!", "PYTHON", "")


    #create a temporary table of side-specific ranges
    tempTable = join(gdb, "RoadsTemp")
    if Exists(tempTable):
        Delete_management(tempTable)
    rc_1 = join(gdb, "RoadCenterline_Layer")
    rc_2 = join(gdb, "RoadCenterline_Layer2")
    Merge_management([rc_1, rc_2], tempTable)

    Delete_management(rc_1)
    Delete_management(rc_2)

    # make sure the MATCH field exists
    if not fieldExists(output_table, "MATCH"):
        AddField_management(output_table, "MATCH", "TEXT", "", "", 1)
    if not fieldExists(output_table, rd_object.UNIQUEID):
        AddField_management(output_table, rd_object.UNIQUEID, "TEXT", "", "", 38)

    addy_fields = (HNO, code_field, "MATCH", rd_object.UNIQUEID)

    non_match_count = 0
    count = 1

    # set up reporting so the user knows how things are coming along
    total = getFastCount(output_table)
    half = round(total/2,0)
    quarter = round(half/2,0)
    three_quarters = half + quarter
    timeDict = {quarter: "1/4", half:"1/2", three_quarters:"3/4"}

    # loop through address points to compare each one
    with UpdateCursor(output_table, addy_fields) as rows:
        for row in rows:
##            r_start_time = time.time()
            hno, hno_code = row[0], row[1]
            if hno not in (None, "", " "):
                try:
                    hno = int(hno)
                    segid = db_compare(hno, hno_code, tempTable)
                except:
                    segid = ""
            else:
                segid = ""

            match = "M"
            if segid == "TIES":
                match = "T"
                non_match_count += 1
            elif segid == "":
                match = "U"
                non_match_count += 1

            row[2] = match
            row[3] = segid

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
        print("Some address points did not match. Results are available in " + output_table + ". Please examine the MATCH field to find U (unmatched) records or T (ties).")
        AddMessage("Some address points did not match. Results are available in " + output_table + ". Please examine the MATCH field to find U (unmatched) records or T (ties).")

##    end_time = time.time()
##    print("Elapsed time was %g seconds" % (end_time - start_time))

    # clean up
    Delete_management(tempTable)

    DeleteField_management(output_table, "NAME_COMPARE;CODE_COMPARE")
    DeleteField_management(rd_fc, "NAME_COMPARE;CODE_COMPARE_L;CODE_COMPARE_R")

if __name__ == '__main__':
    main()
