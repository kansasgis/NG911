#-------------------------------------------------------------------------------
# Name:        Conversion_CopyToTemplate
# Purpose:     Copies an existing GDB into a clean template
#
# Author:      kristen
#
# Created:     March 19, 2019
# Copyright:   (c) Kristen Jordan Koenig 2019
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, env, Append_management, ListFeatureClasses,
    Exists, Copy_management, AddField_management, ListFields, Delete_management,
    Describe, DisableEditorTracking_management, EnableEditorTracking_management,
    ExportMetadata_conversion, ImportMetadata_conversion, GetInstallInfo,
    ListTables, CopyRows_management, CopyFeatures_management)
from os.path import join, basename, dirname, exists
from os import remove
from NG911_GDB_Objects import getGDBObject
from NG911_arcpy_shortcuts import fieldExists, hasRecords
from NG911_DataCheck import userMessage
from Enhancement_AddTopology import add_topology
import xml.etree.ElementTree as etree
from xml.etree.ElementTree import parse


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
    copy_gdb(gdbCurrent, gdbFuture)


def copy_gdb(gdbCurrent, gdbFuture):

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

    #get copies of ESB layers in the 2.0 geodatabase
    esbCurrent = gdbCurrentobject.esbList
    esbFuture = []

    if len(esbCurrent) > 1:

        # delete the topology
        topology = gdbFutureobject.Topology
        Delete_management(topology)

        # copy ESB layer into varieties
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

        # remove ESB layer
        Delete_management(ESB_Future)

    # set up the conversion dictionary
    conversionDict = {}

    # set up lists of workspaces
    ws_list = [gdbCurrentobject.NG911_FeatureDataset, gdbCurrent]
    try:
        ws_list.append(gdbCurrentobject.OPTIONAL_LAYERS_FD)
    except:
        pass

    # loop through workspaces
    for ws in ws_list:

        if Exists(ws):

            # set workspace
            env.workspace = ws

            # list feature classes and tables
            fcs = ListFeatureClasses()
            tbls = ListTables()

            # put all data items into a workspace dictionary according to data type
            ws_dict = {"fc": fcs, "tbl": tbls}

            # loop through the data types
            for item_type in ws_dict:
                data_items = ws_dict[item_type]

                # loop through data list
                for data in data_items:
                    currentData = join(ws, data)

                    # only copy it over if the data has records
                    if hasRecords(currentData):
                        futureData = currentData.replace(gdbCurrent, gdbFuture)

                        # see if the other layer exists
                        if Exists(futureData):
                            # if it does, append the layer
                            method = "append"

                        else:
                            # if not, copy
                            method = "copy"

                        # add the data item to the conversion dictionary
                        conversionDict[currentData] = [futureData, item_type, method]

                    else:
                        userMessage(currentData + " has no records and will not be copied.")


    #loop through all layers in the conversion dictionary
    for data_item in conversionDict.keys():
        userMessage("Converting " + basename(data_item))
        convList = conversionDict[data_item]

        #set variables
        itemC = data_item
        itemF = convList[0]
        item_type = convList[1]
        method = convList[2]

        editorC = Describe(itemC).editorTrackingEnabled
        if Exists(itemF):
            editorF = Describe(itemF).editorTrackingEnabled
        else:
            editorF = False

        # disable editor tracking on both feature classes
        if editorC:
            DisableEditorTracking_management(itemC, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")
        if editorF:
            DisableEditorTracking_management(itemF, "DISABLE_CREATOR", "DISABLE_CREATION_DATE", "DISABLE_LAST_EDITOR", "DISABLE_LAST_EDIT_DATE")

        # force common fields
        if Exists(itemF):
            forceCommonFields(itemC, itemF)

        # move records according to how they need to move
        if method == "append":
            Append_management(itemC, itemF, "NO_TEST")
        elif method == "copy" and item_type == "fc":
            CopyFeatures_management(itemC, itemF)
        elif method == "copy" and item_type == "tbl":
            CopyRows_management(itemC, itemF)

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

        # turn editor tracking back on
        if editorC:
            EnableEditorTracking_management(itemC, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")
        if editorF:
            EnableEditorTracking_management(itemF, "", "", "UPDATEBY", "L_UPDATE", "NO_ADD_FIELDS", "UTC")

        userMessage(data_item + " done")

    # adjust topology if there are multiple ESB layers
    add_topology(gdbFuture, "true")

    # clean up lingering metadata conversion files
    cleanUpList = [gdb_out_xml, road_out_xml, join(dirname(gdbFuture), "GDB_20Metadata_xslttransform.log"),
                    join(dirname(gdbFuture), "Road_20Metadata_xslttransfor.log")]
    for cu in cleanUpList:
        if exists(cu):
            remove(cu)

if __name__ == '__main__':
    main()
