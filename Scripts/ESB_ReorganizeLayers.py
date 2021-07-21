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
from NG911_GDB_Objects import getGDBObject


def main():
    
    # get variables
    gdb = GetParameterAsText(0)
    gdb_obj = getGDBObject(gdb)
    ng911 = gdb_obj.NG911_FeatureDataset
    optional = gdb_obj.OPTIONAL_LAYERS_FD
    
    # delete topology
    topology = gdb_obj.Topology
    Delete_management(topology)
    
    # get spatial reference
    addy_pt = gdb_obj.AddressPoints
    desc = Describe(addy_pt)
    sr = desc.spatialReference
    
    # create feature dataset, NG911_local
    CreateFeatureDataset_management(gdb, "%s_local" % basename(ng911), sr)
    ds = join(gdb, "%s_local" % basename(ng911))
    
    adjusted_list = []
    
    # list _NEW feature classes, loop through datasets
    for fds in [gdb, ng911, optional]:
        env.workspace = fds
        fcs = ListFeatureClasses("*_NEW")
        
        try:
            # create full path to feature class
            for fc in fcs:
                fp = join(fds, fc)
                adjusted_list.append(fp)
        except:
            pass
            
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
    ab = gdb_obj.AuthoritativeBoundary
    flag_ab = Exists(ab)
    
    if flag_ab:
        # make a copy of the authoritative boundary
        out_ab = ab + "_local"
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