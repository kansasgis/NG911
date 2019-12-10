# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 13:18:38 2019

@author: kristen
"""
from arcpy import (GetParameterAsText, MakeFeatureLayer_management, Exists,
                   Delete_management, Union_analysis, DeleteIdentical_management,
                   AddMessage, Clip_analysis, AddError, env, ListFeatureClasses)
from os.path import join, basename
from NG911_arcpy_shortcuts import hasRecords

def userMessage(msg):
    print(msg)
    AddMessage(msg)

    
def adjustBoundaries(gdb, fcs):
    psap = join(gdb, "NG911", "PSAP_temp")
    
    if not Exists(psap):
        AddError("PSAP import does not exist. You must import the PSAP layer.")

    else:
        # create psap feature layer
        l_psap = "l_psap"
        MakeFeatureLayer_management(psap, l_psap)
        
        # create the list of ESBs, ESZ, & utilities
        if fcs == "":
        
            # get list of features classes that start with ESB
            ds = join(gdb, "NG911")
            env.workspace = ds
            
            esb_list = ListFeatureClasses("ESB*")
            
            # and add in the ESZ layer
            esb_list.append("ESZ")
            
            adjust_list = [join(ds, esb) for esb in esb_list]
            
            # add in any utility layers that have records
            ds_other = join(gdb, "OptionalLayers")
            env.workspace = ds_other
            ut_list = ListFeatureClasses("UT*")
            
            for ut in ut_list:
                fp_ut = join(ds_other, ut)
                if hasRecords(fp_ut):
                    adjust_list.append(fp_ut)
        
        else:
            # use the adjustment list provided by the user
            adjust_list = [a_fc for a_fc in fcs if Exists(a_fc) and not Exists(a_fc + "_NEW")]
                
        # create reporting list
        fixed_list = []
    
        # loop through full paths
        for fc in adjust_list:

            userMessage("Processing %s" % basename(fc))
            
            esb_final = fc + "_NEW"
    
            # do a self-union first
            self_union = join(gdb, "SU")
            if Exists(self_union):
                Delete_management(self_union)
            userMessage("Running the self-union")
            Union_analysis(fc, self_union, "ALL", "0.01 Feet", "NO_GAPS")
        
            # then run a delete identical on Shape_Length & Shape_Area
            userMessage("Deleting identical shapes")
            DeleteIdentical_management(self_union, "Shape_Length;Shape_Area", "", "0")
        
            # run another union between the ESB & PSAP
            psap_union = join(gdb, "PU")
            if Exists(psap_union):
                Delete_management(psap_union)
            userMessage("Running the ESB/PSAP union")
            Union_analysis([self_union, l_psap], psap_union, "ALL", "0.01 Feet", "NO_GAPS")
            
            # clean up
            Delete_management(self_union)            
            
            # clip by the inital psap boundary
            # make sure final name doesn't exist yet
            if Exists(esb_final):
                Delete_management(esb_final)
            userMessage("Clipping to PSAP boundary...")
            Clip_analysis(psap_union, l_psap, esb_final)
            
            # clean up
            Delete_management(psap_union)
            
            userMessage("Completed %s" % basename(fc))
            fixed_list.append(basename(fc))
                
        # report back to user all what layers were adjusted
        userMessage("Layers adjusted: " + ", ".join(fixed_list))
        
        # clean up
        Delete_management(l_psap)
        
def main():

    gdb = GetParameterAsText(0)
    
    try:
        fcs = GetParameterAsText(1).split(";")
    except:
        fcs = ""
        
    adjustBoundaries(gdb, fcs)

if __name__ == '__main__':
    main()