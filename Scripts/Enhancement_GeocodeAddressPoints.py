#-------------------------------------------------------------------------------
# Name:        Enhancement_GeocodeAddressPoints
# Purpose:     Geocodes address points against road centerline
#
# Author:      kristen
#
# Created:     26/07/2016, Edited 10/28/2016, Edited 12/13/2016, edited 5/12/2017
# Copyright:   (c) kristen 2016
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, Exists, CopyFeatures_management, DisableEditorTracking_management,
            EnableEditorTracking_management, AddJoin_management, RemoveJoin_management, CalculateField_management,
            Delete_management, MakeFeatureLayer_management, AddIndex_management, ListFields, AddMessage, ListIndexes)
from MSAG_DBComparison import launch_compare
from NG911_GDB_Objects import getFCObject
from NG911_arcpy_shortcuts import fieldExists, ListFieldNames
from os.path import join


def getIndexNames(lyr):
    names = map(lambda x: x.name, ListIndexes(lyr))
    return names


def geocompare(gdb, version, emptyOnly):
    addy_fc = join(gdb, "NG911", "AddressPoints")
    rd_fc = join(gdb, "NG911", "RoadCenterline")
    addy_object = getFCObject(addy_fc)
    rd_object = getFCObject(rd_fc)
    addy_field_list = ["NAME_COMPARE", "PRD", "STP", "RD", "STS", "POD", "POM"]

    a_id = addy_object.UNIQUEID

    # create output results
    out_name = "AddressPt_GC_Results"
    output_table = join(gdb, out_name)
    wc = "SUBMIT = 'Y'"
    fl = "fl"

    # set up where clause if the user only wants empty records done
    if emptyOnly == "true":
        wc = wc + " AND (" + addy_object.RCLMATCH + " is null or " + addy_object.RCLMATCH + " in ('', ' ','TIES','NO_MATCH','NULL_ID'))"

    # make sure we're dealing with a clean output table
    if Exists(output_table):
        Delete_management(output_table)

    # create output table
    MakeFeatureLayer_management(addy_fc, fl, wc)
    CopyFeatures_management(fl, output_table)
    Delete_management(fl)

    # turn off editor tracking
    DisableEditorTracking_management(addy_fc, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")
    DisableEditorTracking_management(rd_fc, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")

    launch_compare(gdb, output_table, addy_object.HNO, addy_object.MSAGCO, addy_field_list, False)

    # if the version is 2.1...
    if version == "21":
        indexName = "kristen"

        MakeFeatureLayer_management(addy_fc, fl)

        # check to see if MY index exists on NGADDID
        addy_fc_index = getIndexNames(fl)

        if indexName not in addy_fc_index:
            # add an index on NGADDID
            AddIndex_management(fl, a_id, indexName)

        # create a feature layer from the results
        ot_fl = "ot_fl"
        MakeFeatureLayer_management(output_table, ot_fl)

        # double check to see if the kristen index exists on the outpu
        output_index = getIndexNames(ot_fl)

        if indexName not in output_index:
            AddIndex_management(ot_fl, a_id, indexName)

        # join the output table to the address point file
        AddJoin_management(fl, a_id, ot_fl, a_id, "KEEP_COMMON")

        # make a list of the field names in upper case
        uc_fieldNames = []
        flds = ListFields(fl)
        for fld in flds:
            uc_fieldNames.append(fld.name.upper())

        # define fields to be calculated
        rclmatch = "AddressPoints.RCLMATCH"
        rclside = "AddressPoints.RCLSIDE"
        ngsegid_exp = "!AddressPt_GC_Results.NGSEGID!"
        rclside_exp = "!AddressPt_GC_Results.RCLSIDE!"

        # fix for Butler County if those fields don't exist
        if rclmatch.upper() not in uc_fieldNames:
            rclmatch = "KSNG911S.DBO." + rclmatch
            ngsegid_exp = "!KSNG911S.DBO.AddressPt_GC_Results.NGSEGID!"
        if rclside.upper() not in uc_fieldNames:
            rclside = "KSNG911S.DBO." + rclside
            rclside_exp = "!KSNG911S.DBO.AddressPt_GC_Results.RCLSIDE!"

        # calculate field
        CalculateField_management(fl, rclmatch, ngsegid_exp, "PYTHON_9.3", "")
        CalculateField_management(fl, rclside, rclside_exp, "PYTHON_9.3", "")

        # remove the join
        RemoveJoin_management(fl)

        Delete_management(fl)
        Delete_management(ot_fl)

    # turn editor tracking back on
    EnableEditorTracking_management(addy_fc, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")
    EnableEditorTracking_management(rd_fc, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")


def main():
    gdb = GetParameterAsText(0)
    emptyOnly = GetParameterAsText(1)
    version = "20"

    # see what version we're working with
    ap = join(gdb, "NG911", "AddressPoints")
    if fieldExists(ap, "RCLMATCH"):
        version = "21"

    if version == "20" and emptyOnly == "true":
        emptyOnly = "false"
    geocompare(gdb, version, emptyOnly)

if __name__ == '__main__':
    main()
