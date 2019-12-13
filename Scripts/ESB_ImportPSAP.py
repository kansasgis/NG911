# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 13:35:03 2019

@author: kristen
"""
from arcpy import (GetParameterAsText, MakeFeatureLayer_management, 
                   CopyFeatures_management, Exists, Delete_management,
                   Statistics_analysis, Describe, AddError)
from arcpy.da import SearchCursor
from os.path import join, abspath, dirname
from inspect import getsourcefile
from ESB_AdjustESB import userMessage


def getStewardWC(fc):
    steward_wc = ""

    output = r"in_memory\Summary"
    field = "STEWARD"

    if Exists(output):
        Delete_management(output)

    wc_submit = "SUBMIT = 'Y'"
    fl_submit = "fl_submit"

    MakeFeatureLayer_management(fc, fl_submit, wc_submit)

    #run frequency to get unique list in "STEWARD" field
    Statistics_analysis(fl_submit, output, field + " COUNT", field)
#    Frequency_analysis(fl_submit, output, field, "")

    #set up empty variables to hold list of stewards
    stewardList = []

    #run search cursor to get list of stewards
    with SearchCursor(output, (field)) as rows:
        for row in rows:
            if row[0] is not None:
                stewardList.append("'" + row[0] + "'")

    if stewardList != []:
        stewards = "(" + ",".join(stewardList) + ")"
        steward_wc = "STEWARD in %s" % stewards

    Delete_management(output)
    Delete_management(fl_submit)
    return steward_wc
    del stewards, stewardList, wc_submit, steward_wc
    

def main():
    
    # copy psap boundary into geodatabase
    gdb = GetParameterAsText(0)
    
    # use address points as a baseline for extra info
    addy_pt = join(gdb, "NG911", "AddressPoints")
    
    # get spatial reference of address points
    desc = Describe(addy_pt)
    sr = desc.spatialReference
    factoryCode = str(sr.factoryCode)
    
    # use factoryCode to get the correct psap
    # get the ng911 folder, then navigate to the psap folder
    ng911_folder = dirname(dirname(abspath(getsourcefile(lambda:0))))
    psap_gdb = join(ng911_folder, "PSAP_Data", "PSAP_Data.gdb")
    psap_big = join(psap_gdb, "PSAP_%s" % factoryCode)
    
    # make sure the psap data exists
    if Exists(psap_big):
        userMessage("Preparing PSAP data...")
        # get stewards from address points
        steward_wc = getStewardWC(addy_pt)
    
        # make psap feature layer
        p = "p"
        MakeFeatureLayer_management(psap_big, p, steward_wc)
    
        # copy psap into the geodatabase
        psap = join(gdb, "NG911", "PSAP_temp")
        userMessage("Copying PSAP data...")
        CopyFeatures_management(p, psap)
        
        userMessage("Copied data into %s" % psap)
        
        userMessage("-----Please manually inspect data before running the next tool.-----")
        
    else:
        AddError(psap_big + " does not exist. Cannot complete operation. Please contact Kristen- kristen@kgs.ku.edu")


if __name__ == '__main__':
    main()