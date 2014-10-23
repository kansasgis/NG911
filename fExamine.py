#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      kyleg
#
# Created:     02/10/2014
# Copyright:   (c) kyleg 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from NG911_Config import gdb

def ExamineGDB(gdb):
    import ntpath, re
    reviewpath=ntpath.basename(gdb)

    from arcpy import env, ListWorkspaces, ListDatasets, ListTables, ListFeatureClasses, GetCount_management, Compact_management, ListFields
    #set the workspace from the config file
    env.workspace = ntpath.dirname(gdb)
    ng911 = gdb
    print "geodatabases"
    print ng911
    env.workspace = ng911
    datasets = ListDatasets()
    print "Datasets:"
    for dataset in datasets:
        print "     "+ str(dataset)
    tables = ListTables()
    print " tables:"
    for table in tables:
        fcc = GetCount_management(table)
        print "     "+str(table)
    fd = datasets[0]
    fcs = ListFeatureClasses("", "", fd)
    for fc in fcs:
        fields = ListFields(fc)
        fcc = GetCount_management(fc)
        print fc +", " + str(fcc) + " features"
        for field in fields:
            print "        "+str(field.name)+", "+str(field.type)
    checkfile = reviewpath+"/"+ntpath.basename(ng911)
    topo= fd+"/NG911_Topology"
    Compact_management(ng911)