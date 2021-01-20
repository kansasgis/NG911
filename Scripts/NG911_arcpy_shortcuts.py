#-------------------------------------------------------------------------------
# Name:        NG911_arcpy_shortcuts
# Purpose:     Short cuts for repetitive arcpy coding
#
# Author:      kristen
#
# Created:     13/05/2016
#-------------------------------------------------------------------------------
def addItemIfUnique(item, mList):
    if item not in mList:
        mList.append(item)
    return mList

def countQueryResults(fc, wc):
    from arcpy import Delete_management
    lyr = MakeLayer(fc, "lyrSelectStuff", wc)
    count = getFastCount(lyr)
    Delete_management(lyr)
    return count

def countLayersGetSize(folder):
    from os import walk
    from os.path import getsize, join

    size = 0
    for root, dirs, files in walk(folder):
        for name in files:
            ##get full pathname
            if name[-4:] != 'lock':
                filename = join(root, name)
                fSize = getsize(filename)
                size = size + fSize

    #add piece to calculate the size in MB or GB, whatever is better
    sizeReport = ""
    if size < 1048576:
        kb = round(size/1024.00, 2)
        sizeReport = str(kb) + " KB"
    elif size >= 1048576 and size < 1073741824:
        mb = round(size/1048576.00, 2)
        sizeReport = str(mb) + " MB"
    elif size >= 1073741824:
        gb = round(size/1073741824.00, 2)
        sizeReport = str(gb) + " GB"

    count = countLayers(folder)

    return {"size":sizeReport, "count":count}

def hasRecords(fc):
    records = False
    count = getFastCount(fc)
    if count > 0:
        records = True

    return records

def AddFieldAndCalculate(fc, field, fieldType, length, expression, exp_lang):
    from arcpy import AddField_management, CalculateField_management
    if length != "":
        AddField_management(fc, field, fieldType, "", "", length)
    else:
        AddField_management(fc, field, fieldType)
    CalculateField_management(fc, field, expression, exp_lang)


def cleanUp(listOfItems):
    for item in listOfItems:
        deleteExisting(item)

def deleteExisting(item):
    from arcpy import Exists, Delete_management
    if Exists(item):
        Delete_management(item)

def getFastCount(lyr):
    from arcpy import GetCount_management
    result = GetCount_management(lyr)
    count = int(result.getOutput(0))
    return count

def ExistsAndHasData(item):
    result = False
    from arcpy import Exists
    if Exists(item):
        if getFastCount(item) > 0:
            result = True
    return result

def countLayers(folder):
    from arcpy import ListFeatureClasses, env
    env.workspace = folder
    fcs = ListFeatureClasses()
    count = len(fcs)
    return count

def ListFieldNames(item):
    #create a list of field names
    from arcpy import ListFields
    fieldList = map(lambda x: x.name.upper(), ListFields(item))
    return fieldList

def fieldExists(fc, fieldName):
    exists = False
    fields = ListFieldNames(fc)
    if fieldName in fields:
        exists = True
    return exists

def indexExists(fc, indexName):
    exists = False
    indexList = ListIndexNames(fc)
    if indexName in indexList:
        exists = True
    return exists

def hasIndex(fc):
    exists = False
    indexes = ListIndexNames
    if indexes != []:
        exists = True
    return exists


def ListIndexNames(fc):
    from arcpy import ListIndexes
    names = map(lambda x: x.name, ListIndexes(fc))
    return names


def MakeLayer(item, lyrName, wc):
    from arcpy import Describe, MakeFeatureLayer_management, MakeTableView_management
    #get data type
    dataType = Describe(item).dataType
    #based on data type, create the right kind of layer or table view
    if dataType == "FeatureClass":
        if wc != "":
            MakeFeatureLayer_management(item, lyrName, wc)
        else:
            MakeFeatureLayer_management(item, lyrName)
    else:
        if wc != "":
            MakeTableView_management(item, lyrName, wc)
        else:
            MakeTableView_management(item, lyrName)
    return lyrName


def CalcWithWC(fc, fld, val, wc):
    from arcpy import MakeFeatureLayer_management, CalculateField_management, Delete_management
    fl_calc = "fl_calc"
    MakeFeatureLayer_management(fc, fl_calc, wc)
    CalculateField_management(fl_calc, fld, val, "PYTHON_9.3", "")
    Delete_management(fl_calc)
    
    