#-------------------------------------------------------------------------------
# Name:        Enhancement_SplitSingleESBLayer
# Purpose:     Splits a single ESB layer into separate EMS, Fire and Law boundaries
#
# Author:      kristen
#
# Created:     11/10/2016

#-------------------------------------------------------------------------------
from NG911_DataCheck import userMessage
from arcpy import (CopyFeatures_management, MakeFeatureLayer_management, GetParameterAsText, Exists,
        CalculateField_management, Dissolve_management, Delete_management, env,
        AddField_management, Statistics_analysis)
from arcpy.da import SearchCursor
from os.path import join
from NG911_GDB_Objects import getFCObject
from NG911_arcpy_shortcuts import fieldExists
from datetime import datetime

def splitESB(inputESB, output_workspace):

    #completely prepares a single-input ESB layer
    #splits up ESB layers
    userMessage("Preparing ESBs...")

    esb_obj = getFCObject(inputESB)

    working_dir = output_workspace

    env.workspace = working_dir
    env.overwriteOutput = True

    #if copies already exists, archive them
    EMSOutput = join(working_dir, "ESB_EMS")
    FireOutput = join(working_dir, "ESB_FIRE")
    LawOutput = join(working_dir, "ESB_LAW")

    outputDict = {"FIRE":FireOutput, "EMS":EMSOutput, "LAW": LawOutput}

    #create working paths
    fire = join(working_dir, "ESB_FIRE_wk")
    ems = join(working_dir, "ESB_EMS_wk")
    law = join(working_dir, "ESB_Law_wk")

    esbworkDict = {"FIRE":fire, "EMS":ems, "LAW":law}

    #limit records to only those for submission
    lyrESB = "lyrESB"
    if not fieldExists(inputESB, "SUBMIT"):
        MakeFeatureLayer_management(inputESB, lyrESB)
    else:
        wc = esb_obj.SUBMIT + " NOT IN ('N')"
        MakeFeatureLayer_management(inputESB, lyrESB, wc)

    #get the most common eff_date
    stats_eff_date = join("in_memory", "eff_date")
    Statistics_analysis(lyrESB, stats_eff_date, [["EFF_DATE", "COUNT"]], "EFF_DATE")

    eff_date = ""
    high_count = 0
    with SearchCursor(stats_eff_date, ("EFF_DATE", "COUNT_EFF_DATE")) as rows:
        for row in rows:
            if row[1] > high_count:
                high_count = row[1]
                eff_date = datetime.strftime(row[0], "%m/%d/%Y %H:%M:%S")

    Delete_management(stats_eff_date)

    for key in esbworkDict:
        layer = esbworkDict[key]
        other1 = ""
        other2 = ""
        letter = ""

        #delete working layer if it exists already
        if Exists(layer):
            Delete_management(layer)

        #copy to shapefile so it can be reprojected
        CopyFeatures_management(lyrESB, layer)

        if key == "FIRE":
            other1 = "LAW"
            other2 = "EMS"
            letter = "F"
        elif key == "EMS":
            other1 = "LAW"
            other2 = "FIRE"
            letter = "E"
        elif key == "LAW":
            other1 = "FIRE"
            other2 = "EMS"
            letter = "L"

        #edit other features
        CalculateField_management(layer, other1, '""', "VB", "")
        CalculateField_management(layer, other2, '""', "VB", "")
        CalculateField_management(layer, esb_obj.DISPLAY, "[" + key + "]", "VB", "")
        CalculateField_management(layer, esb_obj.UNIQUEID, '""', "VB", "")
        CalculateField_management(layer, esb_obj.ESB_TYPE, '"' + key + '"', "VB", "")

        #get final output
        output = outputDict[key]

        #dissolve features into final output
        Dissolve_management(layer, output, [esb_obj.STEWARD, esb_obj.UNIQUEID, esb_obj.STATE, esb_obj.AGENCYID,
                                                esb_obj.SERV_NUM, esb_obj.DISPLAY, esb_obj.ESB_TYPE, esb_obj.LAW, esb_obj.FIRE, esb_obj.EMS,
                                                esb_obj.PSAP], "", "MULTI_PART", "DISSOLVE_LINES")

        #calculate new ESBID
        fld = ""
        if fieldExists(output, "OBJECTID"):
            fld = "OBJECTID"
        elif fieldExists(output, "FID"):
            fld = "FID"
        CalculateField_management(output, esb_obj.UNIQUEID, '"' + letter + '" & [' + fld + ']', "VB", "")

        #add and calculate other required fields
        fieldsDict = {"L_UPDATE": ["DATE"], "EFF_DATE": ["DATE"], "EXP_DATE": ["DATE"], "UPDATEBY": ["TEXT", 50], "SUBMIT": ["TEXT", 1, "SUBMIT"], "NOTES": ["TEXT", 255]}

        for f in fieldsDict:
            parameters = fieldsDict[f]
            fieldType = parameters[0]
            if len(parameters) == 1:
                AddField_management(output, f, fieldType)
                if f == "L_UPDATE":
                    #set last update to now
                    CalculateField_management(output, f, 'datetime.datetime.now()', 'PYTHON_9.3')
                elif f == "EFF_DATE":
                    #set to common eff_date
                    CalculateField_management(output, f, '"' + eff_date + '"', "PYTHON_9.3")

            if len(parameters) > 1:
                fieldLength = parameters[1]
                fieldDomain = ""
                if len(parameters) > 2:
                    fieldDomain = parameters[2]

                AddField_management(output, f, fieldType, "", "", fieldLength, "", "", "", fieldDomain)


                if f == "UPDATEBY":
                    CalculateField_management(output, f, "os.getenv('username')", 'PYTHON_9.3', 'import os')

                elif f == "SUBMIT":
                    CalculateField_management(output, f, '"Y"', 'PYTHON_9.3')



        #clean up
        Delete_management(layer)

    Delete_management(lyrESB)

    if Exists(EMSOutput) and Exists(FireOutput) and Exists(LawOutput):
        userMessage("ESBs split. NOTE: the EFF_DATE was filled in with the MOST COMMON EFF_DATE from the ESB layer. Please check individual data pieces for accuracy.")
    else:
        userMessage("There was an issue splitting the ESB boundaries. Please contact kristen@kgs.ku.edu.")

def main():
    inputESB = GetParameterAsText(0)
    output_workspace = GetParameterAsText(1)
    splitESB(inputESB, output_workspace)

if __name__ == '__main__':
    main()
