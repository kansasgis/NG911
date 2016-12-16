#-------------------------------------------------------------------------------
# Name:        Conversion_GDB11to20
# Purpose:     Migrates a county's 1.1 GDB to the new and fancy 2.0 template
#
# Author:      kristen
#
# Created:     October 18.2016
# Copyright:   (c) Kristen Jordan Koenig 2016
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, env, Append_management, ListFeatureClasses,
    AssignDefaultToField_management, Exists, Copy_management, AddField_management,
    CalculateField_management, ListFields, DeleteField_management, Delete_management)
from os.path import join, basename
from NG911_GDB_Objects import getGDBObject, getFCObject
from NG911_arcpy_shortcuts import ListFieldNames, fieldExists, hasRecords
from NG911_DataCheck import userMessage

def forceCommonFields(fc11, fc20):

    #migrate other user fields
    fields11 = ListFields(fc11)
    fields20 = ListFields(fc20)

##    fieldTypeList = ["TEXT","FLOAT","DOUBLE","SHORT","LONG","DATE","BLOB","RASTER","GUID"]

    #if the proprietary field doesn't exist, add it
    for field20 in fields20:
        if not fieldExists(fc11, field20.name):
            if "SHAPE" not in field20.name.upper():
##                if field20.type.upper() in fieldTypeList:
                if "OBJECTID" not in field20.name.upper():
                    try:
                        AddField_management(fc11, field20.name, field20.type, "", "", field20.length)
                    except Exception as e:
                        userMessage(str(e) + ": Attempting to add column " + field20.name + " to the 1.1 goedatabase.")

    #if the proprietary field doesn't exist, add it
    for field11 in fields11:
        if not fieldExists(fc20, field11.name):
            if "SHAPE" not in field11.name.upper():
##                if field11.type.upper() in fieldTypeList:
                if "OBJECTID" not in field11.name.upper():
                    try:
                        AddField_management(fc20, field11.name, field11.type, "", "", field11.length)
                    except Exception as e:
                        userMessage(str(e) + ": Attempting to add column " + field11.name + " to the 2.0 goedatabase.")


def main():

    gdb11 = GetParameterAsText(0)
    gdb20 = GetParameterAsText(1)

    #get the gdb object
    gdb11object = getGDBObject(gdb11)
    gdb20object = getGDBObject(gdb20)

    #get the feature class dictionary for each gdb
    gdb11fcDict = gdb11object.fcDict
    gdb20fcDict = gdb20object.fcDict

    #get copies of ESB layers in the 2.0 geodatabase
    esb11 = gdb11object.esbList

    if len(esb11) > 1:
        ESB20 = gdb20object.ESB
        target = ''
        for esb_fc in esb11:
            if "LAW" in esb_fc.upper():
                target = gdb20object.LAW
            elif "EMS" in esb_fc.upper():
                target = gdb20object.EMS
            elif "FIRE" in esb_fc.upper():
                target = gdb20object.FIRE
            elif "PSAP" in esb_fc.upper():
                target = gdb20object.PSAP

            if target != '':
                if not Exists(target):
                    Copy_management(ESB20, target)

    #set up the conversion
    conversionDict = {}

    for key in gdb11fcDict:
        #only copy over the layers that exist
        if Exists(gdb11fcDict[key]) and Exists(gdb20fcDict[key]):
            conversionDict[key] = [gdb11fcDict[key], gdb20fcDict[key]]

    #loop through all layers in the conversion dictionary
    for layerType in conversionDict:
        userMessage("Converting " + layerType)
        convList = conversionDict[layerType]

        #set variables
        item11 = convList[0]
        item20 = convList[1]
        obj20 = getFCObject(item20)
        obj11 = getFCObject(item11)

        #force common fields so the field mapping will only be unique IDs
        forceCommonFields(item11, item20)

        #copy over unique IDs
        CalculateField_management(item11, obj20.UNIQUEID, '!' + obj11.UNIQUEID + '!', "PYTHON_9.3")

        removeFields = [obj11.UNIQUEID]

        #copy over segid's if this is the road alias table
        if basename(item20) == "RoadAlias":
            CalculateField_management(item11, obj20.SEGID, '!' + obj11.SEGID + '!', "PYTHON_9.3")
            removeFields.append(obj11.SEGID)

        #copy over road alias table
        Append_management(item11, item20, "NO_TEST")

        #remove added unique ID fields
        if basename(item20).upper() not in ["PARCELS", "HYDRANTS", "GATES", "CELL_SECTOR"]:
            for rF in removeFields:
##                userMessage("Going to delete " + rF + " from " + item20)
                if rF != 'NGKSPID':
                    DeleteField_management(item20, rF)

            #delete NGUNIQUID from the 1.1 template layer
            if obj20.UNIQUEID != 'NGKSPID':
##                userMessage("Going to delete " + obj20.UNIQUEID + " from " + item11)
                DeleteField_management(item11, obj20.UNIQUEID)

        userMessage(layerType + " done")

if __name__ == '__main__':
    main()
