# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 11:21:03 2019

@author: kristen
"""
from arcpy import (GetParameterAsText, Delete_management, Describe, Exists,
                   CreateFeatureDataset_management, env, ListFeatureClasses,
                   CopyFeatures_management, Rename_management, DeleteField_management)
from os.path import join, basename
from Enhancement_AddTopology import add_topology

def main():
    # get variables
    gdb = GetParameterAsText(0)
    ng911 = join(gdb, "NG911")
    optional = join(gdb, "OptionalLayers")
    
    # delete topology
    topology = join(ng911, 'NG911_Topology')
    Delete_management(topology)
    
    # get spatial reference
    addy_pt = join(ng911, "AddressPoints")
    desc = Describe(addy_pt)
    sr = desc.spatialReference
    
    # create feature dataset, NG911_local
    CreateFeatureDataset_management(gdb, "NG911_local", sr)
    ds = join(gdb, "NG911_local")
    
    adjusted_list = []
    
    # list _NEW feature classes, loop through datasets
    for fds in [gdb, ng911, optional]:
        env.workspace = fds
        fcs = ListFeatureClasses("*_NEW")
        
        # create full path to feature class
        for fc in fcs:
            fp = join(fds, fc)
            adjusted_list.append(fp)
            
    # move esbs, append local to name
    for full_path_new in adjusted_list:
        
        full_path = full_path_new.replace("_NEW", "")

        # move the features to the new dataset
        name = basename(full_path)
        out = join(ds, name + "_local")
        CopyFeatures_management(full_path, out)
        
        # remove old file
        if Exists(out):
            Delete_management(full_path)
        
        # clean up extra fields while we're here
        if "ESB" in full_path_new:
            df = """FID_SU;FID_ESB_EMS;FID_ESB_LAW;FID_ESB_FIRE;FID_ESB_PSAP;FID_ESB;FID_PSAP_temp;STEWARD_1;L_UPDATE_1;
                EFF_DATE_1;EXP_DATE_1;AGENCYID_1;DISPLAY_1;UPDATEBY_1;SUBMIT_1;NOTES_1;DATAMAINT;DM_EMAIL;NGABID"""
        elif "ESZ" in full_path_new:
            df = """FID_SU;FID_ESZ;FID_PSAP_temp;STEWARD_1;L_UPDATE_1;DISPLAY;DISPLAY_1;STATE;
                EFF_DATE_1;EXP_DATE_1;AGENCYID_1;UPDATEBY_1;SUBMIT_1;NOTES_1;DATAMAINT;DM_EMAIL;NGABID"""
        else:
            df = """FID_SU;STEWARD_1;FID_PSAP_temp;L_UPDATE_1;EFF_DATE_1;EXP_DATE_1;AGENCYID_1;DISPLAY_1;UPDATEBY_1;
            SUBMIT_1;NOTES_1;DATAMAINT;DM_EMAIL;NGABID"""
                
        DeleteField_management(full_path_new, df)
    
        # see if new file exists
        if Exists(full_path_new):
            # rename if it does
            Rename_management(full_path_new, full_path)   
                    
        
    # do some magic to get psap_temp into the authoritative boundary data schema
    
    # see if authoritative boundary already exists
    ab = join(ng911, "AuthoritativeBoundary")
    flag_ab = Exists(ab)
    
    if flag_ab:
        # make a copy of the authoritative boundary
        out_ab = join(ds, "AuthoritativeBoundary_local")
        CopyFeatures_management(ab, out_ab)
        
        # remove existing authoritative boundary
        Delete_management(ab)
    
    # copy psap_temp to be the new authoritative boundary
    psap_temp = join(ng911, "PSAP_temp")
    CopyFeatures_management(psap_temp, ab)
    
    # delete unnecessary fields for authoritative boundary
    DeleteField_management(ab, "DATAMAINT;DM_EMAIL")
    
    # delete PSAP_temp
    Delete_management(psap_temp)
    
    # add topology back in
    add_topology(gdb, "true")

if __name__ == '__main__':
    main()