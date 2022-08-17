# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 12:31:34 2022

@author: kristen
"""
from arcpy import (GetParameterAsText)
from NG911_GDB_Objects import getGDBObject
from NG911_DataCheck import checkGEOMSAG
    

def main():
    
    # get geodatabase
    gdb = GetParameterAsText(0)
    
    # get geodatabase object
    gdb_obj = getGDBObject(gdb)
    
    # check the geomsag
    checkGEOMSAG(gdb_obj)
        
if __name__ == '__main__':
    main()