# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 14:33:05 2019

@author: kristen
"""

#-------------------------------------------------------------------------------
# Name:        Enhancement_AddFVCRNotes
# Purpose:     Add notes to FVCR table
#
# Author:      kristen
#
# Created:     December 6, 2019
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, AddField_management, AddMessage,
                   Statistics_analysis, Exists, Delete_management)
from arcpy.da import SearchCursor, UpdateCursor
from os.path import join
from NG911_arcpy_shortcuts import fieldExists
from NG911_GDB_Objects import getFCObject

def userMessage(msg):
    print(msg)
    AddMessage(msg)


def main():
    
    gdb = GetParameterAsText(0)
    addFVCRNotes(gdb)
    
def addFVCRNotes(gdb):
    
    # get fieldvaluescheckresults table & object
    fvcr = join(gdb, "FieldValuesCheckResults")
    fvcr_obj = getFCObject(fvcr)
    LAYER = fvcr_obj.LAYER
    
    # make sure fvcr table exists
    if Exists(fvcr):
        
        # if the NOTES field doesn't exist, add it
        if not fieldExists(fvcr, "NOTES"):
            userMessage("Adding NOTES field to FVCR...")
            AddField_management(fvcr, "NOTES", 'TEXT', "", "", 255)
            
        # get a list of the layers represented in fvcr
        fvcr_stat = fvcr + "_Stat"
        if Exists(fvcr_stat):
            Delete_management(fvcr_stat)
            
        userMessage("Seeing which layers are in FVCR...")
        Statistics_analysis(fvcr, fvcr_stat, LAYER + " COUNT", LAYER)
        
        # create list of layer names
        layers = []
        with SearchCursor(fvcr_stat, (LAYER)) as rows:
            for row in rows:
                layers.append(row[0])
                
        # clean up
        try:
            Delete_management(fvcr_stat)
            del rows, row
        except:
            pass
        
        # loop through the layer names
        userMessage("Importing NOTES...")
        for layer in layers:
            
            # get layer's full path
            full_path = join(gdb, "NG911", layer)
            continueRunning = True
            
            # make sure the layer exists
            if not Exists(full_path):
                full_path = join(gdb, "OptionalLayers", layer)
                
                if not Exists(full_path):
                    continueRunning = False
            
            if continueRunning:
                fc_obj = getFCObject(full_path)
                
                # query out the UNIQUE IDS in FVCR
                fvcr_wc = "%s = '%s'" % (LAYER, layer)
                
                with UpdateCursor(fvcr, (fvcr_obj.FEATUREID, "NOTES"), fvcr_wc) as rows:
                    for row in rows:
                        note = ''
                        uniqueID = row[0]
                        
                        wc = "%s = '%s'" % (fc_obj.UNIQUEID, uniqueID)
                
                        # query out the notes for that feature
                        with SearchCursor(full_path, ("NOTES"), wc) as s_rows:
                            for s_row in s_rows:
                                try:
                                    note = s_row[0]
                                except:
                                    note = ''
    
                        # update the NOTES field in FVCR with the NOTES value from the feature class
                        if note not in ('', ' '):
                            row[1] = note
                            rows.updateRow(row)
                    
                # clean up
                try:
                    del rows, row, s_rows, s_row
                except:
                    pass
                
        userMessage("Done adding NOTES.")
    
if __name__ == '__main__':
    main()