# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 14:31:19 2019

@author: kristen
"""

from arcpy import (GetParameterAsText, MakeFeatureLayer_management, 
                   CalculateField_management, Delete_management, Exists)
from arcpy.da import SearchCursor
from os.path import join

def main():
    
    # set variables
    gdb = GetParameterAsText(0)
    fvcr = join(gdb, "FieldValuesCheckResults")
    roads = join(gdb, 'NG911', 'RoadCenterline')
    
    # look for all records still reporting outside authoritative boundary
    wc = "DESCRIPTION in ('Error: Feature not inside authoritative boundary', 'Error: Topology issue- Must Be Inside')"
    id_list = []
    
    if Exists(fvcr):
    
        # make NGSEGID list
        with SearchCursor(fvcr, ["FEATUREID"], wc) as rows:
            for row in rows:
                id_list.append(row[0])
                
        # get road features with those IDs
        id_str = "','".join(id_list)
        rd_wc = "NGSEGID in ('%s')" % id_str
        rd_fl = "rd_fl"
        
        # make feature layer
        MakeFeatureLayer_management(roads, rd_fl, rd_wc)
        
        # calculate field to add exception
        CalculateField_management(rd_fl, "EXCEPTION", '"EXCEPTION INSIDE"', "PYTHON_9.3")

        # clean up
        Delete_management(rd_fl)
        
        
if __name__ == '__main__':
    main()