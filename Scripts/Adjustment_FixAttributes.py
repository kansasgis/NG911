# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name: Adjustment_FixAttributes
# Purpose: Fixes random attributes flagged in FieldValuesCheckResults
#
# Author: Kristen Jordan Koenig, Kansas Data Access and Support Center
# kristen.kgs@ku.edu
#
# Created: 5/26/2021
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, MakeTableView_management, Delete_management,
                   CalculateField_management, Exists, MakeFeatureLayer_management,
                   AddMessage)
from arcpy.da import SearchCursor
from NG911_arcpy_shortcuts import getFastCount
from NG911_GDB_Objects import getFCObject, getGDBObject
from os.path import basename


def userMessage(txt):
    print(txt)
    AddMessage(txt)


def fixAttributes(fc, fld, char):
            
    # set up where clause
    wc = fld + " like '%" + char + "%'"
    
    # make a feature layer
    fl = "fl"
    if Exists(fl):
        Delete_management(fl)
    MakeFeatureLayer_management(fc, fl, wc)
    
    # if the count is higher than 0, identify the features
    if getFastCount(fl) > 0:
        print("Fixing %s in %s" % (char, fld))
        
        try:
            CalculateField_management(fl, fld, "!%s!.replace('%s', '').strip(' ')" % (fld, char), "PYTHON_9.3")
        except:
            CalculateField_management(fl, fld, "!%s!.replace('\%s', '').strip(' ')" % (fld, char), "PYTHON_9.3")
            
        # recalculate LABEL field
        
        # get label fields
        a = getFCObject(fc)
        field_list = a.LABEL_FIELDS
        labelField = a.LABEL
        
        # get gdb object
        gdb_obj = getGDBObject(fc.split(".gdb")[0] + ".gdb")
        
        # make sure the object is something
        if a != "":
            # start at 1 since 0 is the label field itself
            i = 1
    
            # create the expression
            while i < len(field_list):
                #since the house number needs a string conversion, we need to have a slightly different expression for the first piece
                if i == 1:
                    if fc == gdb_obj.AddressPoints:
                        expression = 'str(!' +  field_list[i] + '!) + " " + !'
                    else:
                        expression = '!' + field_list[i] + '! + " " + !'
                        
                    # add in a pound sign in front of the unit
                    unit = a.UNIT
                    expression.replace(' + " " + !%s!' % unit, ' + " #" + !%s!' % unit)
    
                else:
                    expression = expression + field_list[i] + '! + " " + !'
    
                i += 1
    
            expression = expression[:-10]
            
            CalculateField_management(fl, labelField, expression, "PYTHON_9.3")
        
    # clean up
    Delete_management(fl)


def fixAttributesAll(gdb):
    
    userMessage("Fixing characters...")
    
    # get gdb object
    gdb_obj = getGDBObject(gdb)
    
    # fixing any out-of-character values
    fvcr = gdb_obj.FieldValuesCheckResults
    fvcr_obj = getFCObject(fvcr)
    
    for fc in [gdb_obj.RoadCenterline, gdb_obj.AddressPoints]:
        
        # get basename of feature class
        name = basename(fc)
    
        wc = "%s = 'Check Attributes' AND %s = '%s'" % (fvcr_obj.CHECK, fvcr_obj.LAYER, name)
        tbl = "tbl"
        MakeTableView_management(fvcr, tbl, wc)
        
        if getFastCount(tbl) > 0:
            
            userMessage("Fixing characters in %s..." % name)
            
            fixes = {}
            
            # get the fields & values that need updating
            with SearchCursor(tbl, [fvcr_obj.FEATUREID, fvcr_obj.DESCRIPTION]) as rows:
                for row in rows:
                    issuePhraseList = row[1].split(' ')
                    issueFld = issuePhraseList[1]
                    issueChar = issuePhraseList[4]
                    
                    feat_id = row[0]
                    
                    if feat_id not in fixes:
                        # add a dictionary entry that is a list of lists
                        fixes[feat_id] = [[issueFld, issueChar]]
                    else:
                        fixes[feat_id].append([issueFld, issueChar])
                        
            # loop through the dictionary that was created
            for feat_id in fixes:
                
                userMessage("Fixing characters for ID %s..." % feat_id)
                issue_list = fixes[feat_id]
                
                for issue in issue_list:
                    field = issue[0]
                    char = issue[1]
                    
                    fixAttributes(fc, field, char)
                    
            userMessage("Done fixing features in %s." % name)
                
        # clean up
        Delete_management(tbl)

def main():
    
    gdb = GetParameterAsText(0)
    
    fixAttributesAll(gdb)

if __name__ == '__main__':
    main()