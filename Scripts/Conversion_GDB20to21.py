#-------------------------------------------------------------------------------
# Name:        Conversion_GDB20to21
# Purpose:     Migrates a county's 2.0 GDB to the new and fancy 2.1 template
#
# Author:      kristen
#
# Created:     October 10, 2017
# Copyright:   (c) Kristen Jordan Koenig 2017
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, env, Append_management, ListFeatureClasses,
    AssignDefaultToField_management, Exists, Copy_management, AddField_management,
    CalculateField_management, ListFields, DeleteField_management, Delete_management,
    Describe, DisableEditorTracking_management, EnableEditorTracking_management,
    ExportMetadata_conversion, ImportMetadata_conversion, GetInstallInfo, MakeFeatureLayer_management,
    MakeTableView_management, RemoveFeatureClassFromTopology_management, AddRuleToTopology_management,
    ValidateTopology_management, AddFeatureClassToTopology_management, RemoveRuleFromTopology_management)
from os.path import join, basename, dirname, exists
from os import remove
from NG911_GDB_Objects import getGDBObject, getFCObject
from NG911_arcpy_shortcuts import ListFieldNames, fieldExists, hasRecords
from NG911_DataCheck import userMessage
import xml.etree.ElementTree as etree
from xml.etree.ElementTree import parse
from xml.dom import minidom


def editMetadata(metadataFile, xmlNode, current, replace):
    xml_parse = parse(metadataFile)
    fixItems = xml_parse.getiterator(xmlNode)
    for fixItem in fixItems:
        if current in fixItem.text:
            text = fixItem.text
            new = text.replace(current, replace)
            fixItem.text = new

    xml_parse.write(metadataFile)
    etree.dump(xml_parse)

def forceCommonFields(current, future):

    #migrate other user fields
    fieldsC = ListFields(current)
    fieldsF = ListFields(future)

    #if the proprietary field doesn't exist, add it
    for fieldF in fieldsF:
        if not fieldExists(current, fieldF.name):
            if "SHAPE" not in fieldF.name.upper():
                if "OBJECTID" not in fieldF.name.upper():
                    try:
                        AddField_management(current, fieldF.name, fieldF.type, "", "", fieldF.length)
                    except Exception as e:
                        userMessage(str(e) + ": Attempting to add column " + fieldF.name + " to the current goedatabase.")

    #if the proprietary field doesn't exist, add it
    for fieldC in fieldsC:
        if not fieldExists(future, fieldC.name):
            if "SHAPE" not in fieldC.name.upper():
                if "OBJECTID" not in fieldC.name.upper():
                    try:
                        AddField_management(future, fieldC.name, fieldC.type, "", "", fieldC.length)
                    except Exception as e:
                        userMessage(str(e) + ": Attempting to add column " + fieldC.name + " to the 2.0 goedatabase.")


def main():

    gdbCurrent = GetParameterAsText(0)
    gdbFuture = GetParameterAsText(1)

    # get the gdb object
    gdbCurrentobject = getGDBObject(gdbCurrent)
    gdbFutureobject = getGDBObject(gdbFuture)

    # copy over the gdb metadata
    # export to an xml
    installDir = GetInstallInfo()["InstallDir"]
    fgdcTranslator = join(installDir, "Metadata", "Translator", "ARCGIS2FGDC.xml")
    gdb_out_xml = join(dirname(gdbFuture), "GDB_20Metadata.xml")
    if exists(gdb_out_xml):
        remove(gdb_out_xml)
    ExportMetadata_conversion(gdbCurrent, fgdcTranslator, gdb_out_xml)

    # edit the xml to show the 2.1 version
    for node in ["title", "purpose"]:
        editMetadata(gdb_out_xml, node, "2.0", "2.1")

    # import into the new geodatabase
    ImportMetadata_conversion(gdb_out_xml, "FROM_FGDC", gdbFuture, "ENABLED")

    #get the feature class dictionary for each gdb
    gdbCurrentfcDict = {"AuthoritativeBoundary": gdbCurrentobject.AuthoritativeBoundary, "MunicipalBoundary": gdbCurrentobject.MunicipalBoundary, "CountyBoundary":
                gdbCurrentobject.CountyBoundary, "ESZ": gdbCurrentobject.ESZ, "PSAP": gdbCurrentobject.PSAP, "EMS": gdbCurrentobject.EMS,
                "LAW": gdbCurrentobject.LAW, "FIRE": gdbCurrentobject.FIRE,
                "ESB": gdbCurrentobject.ESB, "HYDRANTS": gdbCurrentobject.HYDRANTS, "PARCELS": gdbCurrentobject.PARCELS, "GATES": gdbCurrentobject.GATES,
                "CELL_SECTOR": gdbCurrentobject.CELL_SECTOR,
                "AddressPoints": gdbCurrentobject.AddressPoints, "RoadCenterline": gdbCurrentobject.RoadCenterline, "RoadAlias": gdbCurrentobject.RoadAlias}

    gdbFuturefcDict = {"AuthoritativeBoundary": gdbFutureobject.AuthoritativeBoundary, "MunicipalBoundary": gdbFutureobject.MunicipalBoundary, "CountyBoundary":
                gdbFutureobject.CountyBoundary, "ESZ": gdbFutureobject.ESZ, "PSAP": gdbFutureobject.PSAP, "EMS": gdbFutureobject.EMS,
                "LAW": gdbFutureobject.LAW, "FIRE": gdbFutureobject.FIRE,
                "ESB": gdbFutureobject.ESB, "HYDRANTS": gdbFutureobject.HYDRANTS, "PARCELS": gdbFutureobject.PARCELS, "GATES": gdbFutureobject.GATES,
                "CELL_SECTOR": gdbFutureobject.CELL_SECTOR,
                "AddressPoints": gdbFutureobject.AddressPoints, "RoadCenterline": gdbFutureobject.RoadCenterline, "RoadAlias": gdbFutureobject.RoadAlias}

    #get copies of ESB layers in the 2.0 geodatabase
    esbCurrent = gdbCurrentobject.esbList
    multiple_ESB = 0
    esbFuture = []

    if len(esbCurrent) > 1:
        multiple_ESB = 1
        ESB_Future = gdbFutureobject.ESB
        target = ''
        for esb_fc in esbCurrent:
            if "LAW" in esb_fc.upper():
                target = gdbFutureobject.LAW
            elif "EMS" in esb_fc.upper():
                target = gdbFutureobject.EMS
            elif "FIRE" in esb_fc.upper():
                target = gdbFutureobject.FIRE
            elif "PSAP" in esb_fc.upper():
                target = gdbFutureobject.PSAP

            if target != '':
                if not Exists(target):
                    Copy_management(ESB_Future, target)
                    esbFuture.append(target)

    #set up the conversion
    conversionDict = {}

    for key in gdbCurrentfcDict:
        #only copy over the layers that exist
        if Exists(gdbCurrentfcDict[key]) and Exists(gdbFuturefcDict[key]):
            conversionDict[key] = [gdbCurrentfcDict[key], gdbFuturefcDict[key]]
        else:
            message = True
            if key in ["GATES", "HYDRANTS", "PARCELS", "CELL_SECTOR", "LAW", "FIRE", "EMS"]:
                message = False
            if message:
                userMessage("Please check that " + gdbCurrentfcDict[key] + " and " + gdbFuturefcDict[key] + " exist. Data will not be migrated.")

    #loop through all layers in the conversion dictionary
    for layerType in conversionDict.keys():
        userMessage("Converting " + layerType)
        convList = conversionDict[layerType]

        #set variables
        itemC = convList[0]
        itemF = convList[1]

        editorC = Describe(itemC).editorTrackingEnabled
        editorF = Describe(itemF).editorTrackingEnabled

        # disable editor tracking on both feature classes
        if editorC:
            DisableEditorTracking_management(itemC, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")
        if editorF:
            DisableEditorTracking_management(itemF, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")

        # records can just be appended over NO_TEST for the most part
        Append_management(itemC, itemF, "NO_TEST")

        # import previous metadata
        if "RoadCenterline" in itemF:
            road_out_xml = join(dirname(gdbFuture), "Road_20Metadata.xml")
            if exists(road_out_xml):
                remove(road_out_xml)
            ExportMetadata_conversion(itemC, fgdcTranslator, road_out_xml)

            # edit the xml to show the 2.1 version
            for version_val in ["1.1", "2.0"]:
                editMetadata(road_out_xml, "abstract", version_val, "2.1")

            # import into the new geodatabase
            ImportMetadata_conversion(road_out_xml, "FROM_FGDC", itemF, "ENABLED")
        else:
            ImportMetadata_conversion(itemC, "FROM_ARCGIS", itemF, "ENABLED")

        # see if the SUBMIT field exists
        if fieldExists(itemF, "SUBMIT"):
            wc = "SUBMIT not in ('N')"

            fl = "fl"
            if "RoadAlias" in itemF:
                MakeTableView_management(itemF, fl, wc)
            else:
                MakeFeatureLayer_management(itemF, fl, wc)

            # autopopulate any blank/null records with "y"
            CalculateField_management(fl, "SUBMIT", '"Y"', "PYTHON", "")

            Delete_management(fl)

        # turn editor tracking back on
        if editorC:
            EnableEditorTracking_management(itemC, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")
        if editorF:
            EnableEditorTracking_management(itemF, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")

        userMessage(layerType + " done")

    # adjust topology if there are multiple ESB layers
    env.workspace = join(gdbFuture, "NG911")
    topology = join(gdbFuture, "NG911", "NG911_Topology")
    if multiple_ESB == 1:
        userMessage("Updating topology...")

        # set variables
        ESB_Future = gdbFutureobject.ESB
        rc = join(gdbFuture, "NG911", "RoadCenterline")
        ab = join(gdbFuture, "NG911", "AuthoritativeBoundary")
        fixTopology = 0

        # remove the existing topology references to the ESB layer
        if Exists(ESB_Future) and not hasRecords(ESB_Future):
            esb_dsid = str(Describe(ESB_Future).DSID)
            rc_dsid = str(Describe(rc).DSID)
            ab_dsid = str(Describe(ab).DSID)

            # remove specific ESB rules
            rulesToRemove = ['Must Not Overlap (' + esb_dsid + ")",
                             "Must Be Inside (" + rc_dsid + "-" + esb_dsid + ")",
                             "Must Cover Each Other (" + ab_dsid + "-" + esb_dsid + ")"]
            for rule in rulesToRemove:
                RemoveRuleFromTopology_management(topology, rule)

            # remove the feature class from the topology
            RemoveFeatureClassFromTopology_management(topology, "ESB")
            fixTopology = 1 # set flag so the rest of the topology is edited

        else:
            if hasRecords(ESB_Future):
                userMessage("Layer named ESB has features, but additional ESB layers are present. Topology will not be automatically updated.")

        if fixTopology == 1:
            # validate the topology after removing the feature class
            ValidateTopology_management(topology)


            # test existence, just to be on the safe side
            for esb in esbFuture:
                if Exists(esb) and hasRecords(esb):

                    # add feature class to topology
                    AddFeatureClassToTopology_management(topology, esb, 2, 1)

                    # add topology rules
                    AddRuleToTopology_management(topology, "Must Not Overlap (Area)", esb)
                    AddRuleToTopology_management(topology, "Must Not Have Gaps (Area)", esb)
                    AddRuleToTopology_management(topology, "Must Be Inside (Line-Area)", rc, "", esb, "")
                    AddRuleToTopology_management(topology, "Must Cover Each Other (Area-Area)", ab, "", esb, "")

            # delete the ESB layer since we don't need it
            Delete_management(ESB_Future)

    # clean up lingering metadata conversion files
    cleanUpList = [gdb_out_xml, road_out_xml, join(dirname(gdbFuture), "GDB_20Metadata_xslttransform.log"),
                    join(dirname(gdbFuture), "Road_20Metadata_xslttransfor.log")]
    for cu in cleanUpList:
        if exists(cu):
            remove(cu)

if __name__ == '__main__':
    main()
