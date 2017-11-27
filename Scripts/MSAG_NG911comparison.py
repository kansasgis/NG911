#-------------------------------------------------------------------------------
# Name:        MSAG_NG911comparison
# Purpose:     Compares MSAG with the road centerline file
#
# Author:      kristen
#
# Created:     26/08/2016
# Copyright:   (c) kristen 2016
#-------------------------------------------------------------------------------
from arcpy import (ExcelToTable_conversion, AddJoin_management, RemoveJoin_management,
                MakeTableView_management, MakeFeatureLayer_management,
                AddField_management, CalculateField_management, GetParameterAsText,
                Exists, CopyFeatures_management, CreateFileGDB_management,
                SelectLayerByAttribute_management, Delete_management, Dissolve_management,
                CreateTable_management, Statistics_analysis, Merge_management, AddMessage)
from arcpy.da import UpdateCursor, SearchCursor, InsertCursor
from os import mkdir
from os.path import exists, dirname, basename, join
from time import strftime


class MSAG_Object(object):
    #good object to have around
    def __init__(self, u_workspace_folder, u_workingGDB, u_workingRoads, u_msag_table,
                u_rc_names, u_rc_merged_msag, u_msag_merged_msag, u_rc_mm_freq, u_msag_mm_freq,
                u_msag_names):

        self.workspace_folder = u_workspace_folder
        self.workingGDB = u_workingGDB
        self.workingRoads = u_workingRoads
        self.msag_table = u_msag_table
        self.rc_names = u_rc_names
        self.rc_merged_msag = u_rc_merged_msag
        self.msag_merged_msag = u_msag_merged_msag
        self.rc_mm_freq = u_rc_mm_freq
        self.msag_mm_freq = u_msag_mm_freq
        self.msag_names = u_msag_names


def getMSAGObject(gdb, today):
    #too many things to remember, needed an object
    workspace_folder = join(dirname(gdb), "MSAG_analysis_" + today)
    workingGDB = join(workspace_folder, "MSAG_analysis_" + today + ".gdb")
    workingRoads = join(workingGDB, "RoadCenterline")
    msag_table = join(workingGDB, "MSAG_" + today)
    rc_names = workingRoads + "_NAMES"
    msag_names = msag_table + "_NAMES"
    rc_merged_msag = workingRoads + "_MERGED_MSAG"
    msag_merged_msag = msag_table + "_MERGED_MSAG"
    rc_mm_freq = rc_merged_msag + "_freq"
    msag_mm_freq = msag_merged_msag + "_freq"
    MSAG_Default = MSAG_Object(workspace_folder, workingGDB, workingRoads, msag_table,
        rc_names, rc_merged_msag, msag_merged_msag, rc_mm_freq, msag_mm_freq, msag_names)
    return MSAG_Default

def ListFieldNames(item):
    #create a list of field names
    from arcpy import ListFields
    fields = ListFields(item)
    fieldList = []
    for f in fields:
        fieldList.append(f.name.upper())
    return fieldList

def fieldExists(fc, fieldName):
    exists = False
    fields = ListFieldNames(fc)
    if fieldName in fields:
        exists = True
    return exists

def userMessage(msg):
    AddMessage(msg)
    print(msg)

def makeFriendlyRangeMsg(reporting):
    #turns a list of ranges into a printable format
    msg = ""
    for pair in reporting:
        if len(pair) == 2:
            low = pair[0]
            high = pair[1]
            if low != high:
                msg += "Rng: " + str(low) + "-" + str(high) + ", "
            else:
                msg += "Val: " + str(pair[0]) + ", "

    msg = msg[0:-2]
    return msg

def getRanges(data):
    #from http://stackoverflow.com/questions/2361945/detecting-consecutive-integers-in-a-list
    from itertools import groupby
    from operator import itemgetter
    listOfLists = []
    #create lists of consecutive numbers
    for k, g in groupby(enumerate(data), lambda i_x: i_x[0]-i_x[1]):
        floob = list(map(itemgetter(1), g))
        #add the low & high of the range to the list o/ lists
        listOfLists.append([floob[0], floob[len(floob)-1]])

    return listOfLists

def prepRoads(msag_object, gdb, field):
    workingRoads = msag_object.workingRoads

    if not Exists(workingRoads):
        CopyFeatures_management(join(gdb, "NG911", "RoadCenterline"), workingRoads)
        userMessage("Copied roads")

    #prep roads
    road_fields = {field+"_L": 250, field + "_R": 250, "L_R_SAME": 1}
    for k in road_fields:
        if not fieldExists(workingRoads, k):
            AddField_management(workingRoads, k, "TEXT", "", "", road_fields[k])

    #replace nulls in road centerline
    fields_with_nulls = ['PRD', 'STS']
    for fwn in fields_with_nulls:
        wcf = fwn + " is null"
        fl = "fl"
        MakeFeatureLayer_management(workingRoads, fl, wcf)
        CalculateField_management(fl, fwn, "''", "PYTHON")
        Delete_management(fl)

    #calculate fields to hold directionally appropriate full street name, MSAGCO & ESN
    CalculateField_management(workingRoads, field+"_L", "(!PRD!+!RD!+!STS!+'|'+!MSAGCO_L!+'|'+!ESN_L!).replace(' ','').upper()", "PYTHON")
    CalculateField_management(workingRoads, field+"_R", "(!PRD!+!RD!+!STS!+'|'+!MSAGCO_R!+'|'+!ESN_R!).replace(' ','').upper()", "PYTHON")

##    chars = r'"/\[]{}-.,?;:`~!@#$%^&*()' + "'"
##    for char in chars:
    CalculateField_management(workingRoads, field+"_L", "!" + field + "_L!.replace(" + "'" + '"' + "'" + ",'')", "PYTHON")
    CalculateField_management(workingRoads, field+"_R", "!" + field + "_R!.replace(" + "'" + '"' + "'" + ",'')", "PYTHON")
    CalculateField_management(workingRoads, field+"_L", "!" + field + "_L!.replace(" + '"' + "'" + '"' + ",'')", "PYTHON")
    CalculateField_management(workingRoads, field+"_R", "!" + field + "_R!.replace(" + '"' + "'" + '"' + ",'')", "PYTHON")

    #record L/R same status
    wc_list = {"COMPARE_L = COMPARE_R": "'Y'", "L_R_SAME is null":"'N'"}
    for wc in wc_list:
        wr = "wr"
        exp = wc_list[wc]
        MakeFeatureLayer_management(workingRoads, wr, wc)
        CalculateField_management(wr, "L_R_SAME", exp, "PYTHON")
        Delete_management(wr)

    userMessage("Prepped roads for analysis")

def prepMSAG(msag_object, msag, field):
    msag_table = msag_object.msag_table

    #import msag to table
    if not Exists(msag_table):
        ExcelToTable_conversion(msag, msag_table)
        userMessage("MSAG spreadsheet converted")

    #add comparison fields
    if not fieldExists(msag_table, field):
        AddField_management(msag_table, field, "TEXT", "", "", 250)

    #calculate msag field to hold dir, street, community & esn
    expression = "(str(!DIR!) + !STREET! + '|'+ !COMMUNITY! + '|'+ str(!ESN!)).replace(' ', '').upper()"
    CalculateField_management(msag_table, field, expression, "PYTHON")

    #remove any strange characters
    CalculateField_management(msag_table, field, "!" + field + "!.replace(" + "'" + '"' + "'" + ",'')", "PYTHON")
    CalculateField_management(msag_table, field, "!" + field + "!.replace(" + '"' + "'" + '"' + ",'')", "PYTHON")

    userMessage("Prepped MSAG for analysis")

def insertReports(workingGDB, report, records, high, low):
    #prepare reporting
    report_table = join(workingGDB, "MSAG_reporting")
    if not Exists(report_table):
        CreateTable_management(dirname(report_table), basename(report_table))
    if not fieldExists(report_table, "REPORT"):
        AddField_management(report_table, "REPORT", "TEXT", "", "", 255)
    if not fieldExists(report_table, "COMPARISON"):
        AddField_management(report_table, "COMPARISON", "TEXT", "", "", 50)

    fld = ["REPORT", "COMPARISON"]
    cursor = InsertCursor(report_table, fld)
    for r in records:
        if len(fld) == 2:
            cursor.insertRow((report[0:254], r))

def consolidateMSAG(table, compare_field, hilow_fields):
    #Run stats on combine field
    dissolve_names = table + "_NAMES"
    if Exists(dissolve_names):
        Delete_management(dissolve_names)

    #make sure all road segments get represented
    if basename(table) == "RoadCenterline":
        #get all the left side names
        dissolve_left = table + "_NAMES_L"
        if Exists(dissolve_left):
            Delete_management(dissolve_left)
        Statistics_analysis(table, dissolve_left, [[compare_field, "COUNT"]], compare_field)
        AddField_management(dissolve_left, "COMPARE", "TEXT", "", "", 100)
        CalculateField_management(dissolve_left, "COMPARE", "!COMPARE_L!", "PYTHON")

        #get all the ride side names
        dissolve_right = table + "_NAMES_R"
        if Exists(dissolve_right):
            Delete_management(dissolve_right)
        Statistics_analysis(table, dissolve_right, [["COMPARE_R", "COUNT"]], "COMPARE_R")
        AddField_management(dissolve_right, "COMPARE", "TEXT", "", "", 100)
        CalculateField_management(dissolve_right, "COMPARE", "!COMPARE_R!", "PYTHON")

        #put both tables into one
        dissolve_all = table + "_NAMES_A"
        if Exists(dissolve_all):
            Delete_management(dissolve_all)
        Merge_management([dissolve_left, dissolve_right], dissolve_all)

        Statistics_analysis(dissolve_all, dissolve_names, [["COMPARE", "COUNT"]], "COMPARE")
        userMessage(basename(table) + " names created")

    else:
        #just run name statistics
        Statistics_analysis(table, dissolve_names, [[compare_field, "COUNT"]], compare_field)
        userMessage(basename(table) + " names created")

    #create table for rc to msag conversion
    NG911_msag = table + "_MERGED_MSAG"
    if not Exists(NG911_msag):
        CreateTable_management(dirname(NG911_msag), basename(NG911_msag))
    fields_dict = {"COMPARE": 100, "LOW":10, "HIGH":10}
    for f in fields_dict:
        if not fieldExists(NG911_msag, f):
            AddField_management(NG911_msag, f, "TEXT", "", "", fields_dict[f])

    userMessage("Analyzing name highs and lows...")
    #this needs to be adjusted to account for R & L, or both
    #loop through names
    with SearchCursor(dissolve_names, ("COMPARE")) as n_rows:
        for n_row in n_rows:
            name = n_row[0]
            #run basic MSAG merge
            if name is not None:
                name_wc = compare_field + " = '" + name + "'"
                if "RoadCenterline" in table:
                    name_wc = name_wc + " AND L_R_SAME = 'Y'"
                writeSegmentInfo(table, hilow_fields, name_wc, NG911_msag, name)

                #run R & L isolated analysis
                if "RoadCenterline" in table:
                    r_wc = "COMPARE_R = '" + name + "' AND L_R_SAME = 'N'"
                    writeSegmentInfo(table, ("R_F_ADD", "R_T_ADD"), r_wc, NG911_msag, name)

                    l_wc = "COMPARE_L = '" + name + "' AND L_R_SAME = 'N'"
                    writeSegmentInfo(table, ("L_F_ADD", "L_T_ADD"), l_wc, NG911_msag, name)

    del n_row, n_rows

    userMessage("Consolidated MSAG complete for " + basename(table))

def writeSegmentInfo(table, hilow_fields, name_wc, NG911_msag, name):
    seg_list = []
    hilow_len = len(hilow_fields)
    with SearchCursor(table, hilow_fields, name_wc) as rows:

        for row in rows:
            #create sorted list of address components
            field_i = 0
            num_list = []
            while field_i < hilow_len:
                if row[field_i] is not None and row[field_i] != '':
                    num_list.append(int(row[field_i]))
                field_i += 1
            num_list.sort()

            if num_list != []:
                if num_list[0] == 0 and num_list[1] == 0:
                    pass
                else:
                    #add the high and low to the seg_list
                    seg_list.append(num_list[0])
                    seg_list.append(num_list[hilow_len - 1])

    if seg_list != []:
        seg_list.sort()
        i = len(seg_list)
        k = 1
        pop_list = []
        while k + 1 < i:
            #index 0 will definitely be the low so we don't need to worry about it
            #compare the high of one range with the low of the next
            temp_high = seg_list[k]
            temp_nextLow = seg_list[k + 1]

            if temp_nextLow - temp_high == 1:
                pop_list.append(temp_high)
                pop_list.append(temp_nextLow)

            k += 2

        #remove values from list that can be absorbed into others
        if pop_list != []:
            for popIt in pop_list:
                seg_list.remove(popIt)

        count = len(seg_list)
        pair_int = 0

        #write consolidated records
        while pair_int < count:
            cursor = InsertCursor(NG911_msag, ("COMPARE", "LOW","HIGH"))
            cursor.insertRow((name, seg_list[pair_int], seg_list[pair_int + 1]))
            pair_int += 2

            del cursor

def compareMSAGnames(msag_object):
    #compare MSAG segments
    msag_names = msag_object.msag_names
    road_names = msag_object.rc_names
    workingRoads = msag_object.workingRoads

    #add report field
    for tbl in (msag_names, road_names):
        if not fieldExists(tbl, "REPORT"):
            AddField_management(tbl, "REPORT", "TEXT", "", "", 255)

    lyr_msag_names = "lyr_msag_names"
    lyr_road_names = "lyr_road_names"
    MakeTableView_management(msag_names, lyr_msag_names)
    MakeTableView_management(road_names, lyr_road_names)

    #add join
    AddJoin_management(lyr_msag_names, "COMPARE", lyr_road_names, "COMPARE")
    wc_msag_names = basename(road_names) + ".COMPARE is null"

    SelectLayerByAttribute_management(lyr_msag_names, "NEW_SELECTION", wc_msag_names)
    CalculateField_management(lyr_msag_names, "REPORT", "'Does not have a road centerline match'", "PYTHON")

    #find records without a match
    records = []
    with SearchCursor(lyr_msag_names, (basename(msag_names) + ".COMPARE"), wc_msag_names) as msag_rows:
        for msag_row in msag_rows:
            records.append(msag_row[0])

    #report issues
    if records != []:
        insertReports(dirname(workingRoads), "Does not have a road centerline match", records, '', '')

    #clean up: remove the join
    RemoveJoin_management(lyr_msag_names)

    #add join other direction
    AddJoin_management(lyr_road_names, "COMPARE", lyr_msag_names, "COMPARE")
    wc_road_names = basename(msag_names) + ".COMPARE is null"

    SelectLayerByAttribute_management(lyr_road_names, "NEW_SELECTION", wc_road_names)
    CalculateField_management(lyr_road_names, "REPORT", "'Does not have an MSAG match'", "PYTHON")

    #find records without a match
    records = []
    with SearchCursor(lyr_road_names, (basename(road_names) + ".COMPARE"), wc_road_names) as road_rows:
        for road_row in road_rows:
            records.append(road_row[0])

    #report issues
    if records != []:
        insertReports(dirname(workingRoads), "Does not have an MSAG match", records, '', '')

    #clean up: remove the join
    RemoveJoin_management(lyr_road_names)

def compareMSAGranges(msag_object):
    #loop through road centerline names
    userMessage("Comparing MSAG ranges...")
    rc_names = msag_object.rc_names
    rc_merged_msag = msag_object.rc_merged_msag
    msag_merged_msag = msag_object.msag_merged_msag
    rc_mm_freq = msag_object.rc_mm_freq
    msag_mm_freq = msag_object.msag_mm_freq

    #run frequency on merged MSAG names, the ones with one entry in each are an easy comparison
    if not Exists(rc_mm_freq):
        Statistics_analysis(rc_merged_msag, rc_mm_freq, [["COMPARE", "COUNT"]], "COMPARE")
    if not Exists(msag_mm_freq):
        Statistics_analysis(msag_merged_msag, msag_mm_freq, [["COMPARE", "COUNT"]], "COMPARE")

    #next step: join the two frequency tables and select the records where both counts = 1
    r1 = "r"
    m = "m"
    MakeTableView_management(rc_mm_freq, r1)
    MakeTableView_management(msag_mm_freq, m)
    AddJoin_management(r1, "COMPARE", m, "COMPARE", "KEEP_COMMON")

    #compare the segments
    with SearchCursor(r1, (basename(rc_mm_freq) + ".COMPARE")) as rows:
        for row in rows:
            wc = "COMPARE = '" + row[0] + "'"

            roadnumbers = []
            with SearchCursor(rc_merged_msag, ("LOW", "HIGH"), wc) as r_rows:
                for r_row in r_rows:
                    road_range = list(range(int(r_row[0]), int(r_row[1]) + 1))
                    for rr in road_range:
                        roadnumbers.append(rr)
            msagNumbers = []
            with SearchCursor(msag_merged_msag, ("LOW", "HIGH"), wc) as m_rows:
                for m_row in m_rows:
                    msag_range = list(range(int(m_row[0]), int(m_row[1]) + 1))
                    for mm in msag_range:
                        msagNumbers.append(mm)

            if roadnumbers == msagNumbers:
                insertReports(msag_object.workingGDB, "Exact MSAG match", [row[0]], '', '')

            else:
                #this is where we do further investigation, probably with ranges as a tool
                msag_outliers = list(set(roadnumbers) - set(msagNumbers))
                msag_outliers.sort()
                reporting = getRanges(msag_outliers)
                if reporting != []:
                    friendly_reporting = makeFriendlyRangeMsg(reporting)
                    insertReports(msag_object.workingGDB, "Not in MSAG- " + friendly_reporting, [row[0]], '', '')

                road_outliers = list(set(msagNumbers) - set(roadnumbers))
                road_outliers.sort()
                reporting2 = getRanges(road_outliers)
                if reporting2 != []:
                    friendly_reporting2 = makeFriendlyRangeMsg(reporting2)
                    insertReports(msag_object.workingGDB, "Not in NG911 road- " + friendly_reporting2, [row[0]], '', '')

    del row, rows, r_row, r_rows, m_row, m_rows

def main():

    #set variables
    msag = GetParameterAsText(0)
    gdb = GetParameterAsText(1)
##    provider = GetParameterAsText(2)
    today = strftime('%Y%m%d')
    field = "COMPARE"

    msag_object = getMSAGObject(gdb, today)

    #create workspaces- folder
    workspaceFolder = msag_object.workspace_folder
    if not exists(workspaceFolder):
        mkdir(workspaceFolder)

    #create workspaces - gdb in folder
    workingGDB = msag_object.workingGDB
    if not Exists(workingGDB):
        CreateFileGDB_management(workspaceFolder, basename(workingGDB))

    #copy over road centerline
    prepRoads(msag_object, gdb, field)
    consolidateMSAG(msag_object.workingRoads, "COMPARE_L", ("L_F_ADD", "L_T_ADD", "R_F_ADD", "R_T_ADD"))

    #prep msag table
    prepMSAG(msag_object, msag, field)
    consolidateMSAG(msag_object.msag_table, "COMPARE", ("Low","High"))

    #compare msag names
    userMessage("Comparing MSAG segment names...")
    compareMSAGnames(msag_object)

    #compare msag ranges
    compareMSAGranges(msag_object)

    #add reporting
    workingRoads = msag_object.workingRoads
    wr = "wr"
    MakeFeatureLayer_management(workingRoads, wr)

    msag = msag_object.msag_table
    mr = "mr"
    MakeTableView_management(msag, mr)

    #add reporting fields
    f_list = ["REPORT_R", "REPORT_L"]
    for f in f_list:
        if not fieldExists(workingRoads, f):
            AddField_management(workingRoads, f, "TEXT", "", "", 255)

    if not fieldExists(msag, "REPORT"):
        AddField_management(msag, "REPORT", "TEXT", "", "", 255)

    #set up where clauses
    wc_roads = "REPORT not like '%in MSAG%'"
    wc_msag = "REPORT not like '%in NG911%'"

    report_roads = "rr"
    report_msag = "rm"

    reporting = join(workingGDB, "MSAG_reporting")

    #report roads first
    MakeTableView_management(reporting, report_roads, wc_roads)

    #run a join on the road centerline based on the R
    AddJoin_management(wr, "COMPARE_R", report_roads, "COMPARISON")
    CalculateField_management(wr, "RoadCenterline.REPORT_R", "!MSAG_reporting.REPORT!", "PYTHON")
    RemoveJoin_management(wr)

    #run a join on the road centerline based on the L
    AddJoin_management(wr, "COMPARE_L", report_roads, "COMPARISON")
    CalculateField_management(wr, "RoadCenterline.REPORT_L", "!MSAG_reporting.REPORT!", "PYTHON")
    RemoveJoin_management(wr)

    # refresh the layer
    Delete_management(wr)
    wr = "wr"
    MakeFeatureLayer_management(workingRoads, wr)

    SelectLayerByAttribute_management(wr, "NEW_SELECTION", "REPORT_R IS NULL")
    CalculateField_management(wr, "REPORT_R", "'Issue with corresponding MSAG range'", "PYTHON")
    SelectLayerByAttribute_management(wr, "NEW_SELECTION", "REPORT_L IS NULL")
    CalculateField_management(wr, "REPORT_L", "'Issue with corresponding MSAG range'", "PYTHON")

    #run a join on the MSAG
    MakeTableView_management(reporting, report_msag, wc_msag)
    AddJoin_management(mr, "COMPARE", report_msag, "COMPARISON")
    CalculateField_management(mr, "MSAG_" + today + ".REPORT", "!MSAG_reporting.REPORT!", "PYTHON")
    RemoveJoin_management(mr)

    SelectLayerByAttribute_management(mr, "NEW_SELECTION", "REPORT IS NULL")
    CalculateField_management(mr, "REPORT", "'Issue with corresponding road centerline range'", "PYTHON")

    #notes- basically the MSAG needs to be fully represented in road centerline
    #my email example is fine
    #flag "inconsistent range"
    #bigger issue is with inconsistent communities and ESN's
    #report what doesn't match, community or ESN or if everything is a mess, inconsistent street names?


if __name__ == '__main__':
    main()
