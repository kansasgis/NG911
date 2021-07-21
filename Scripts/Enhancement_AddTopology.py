#-------------------------------------------------------------------------------
# Name:        Enhancement_AddTopology
# Purpose:     Makes sure that the NG911 topology has all current rules
#
# Author:      kristen
#
# Created:     10/12/2018
# Copyright:   (c) kristen 2018
#-------------------------------------------------------------------------------
from arcpy import (AddRuleToTopology_management, ValidateTopology_management,
                AddFeatureClassToTopology_management, Exists, CreateTopology_management,
                GetParameterAsText, AddMessage, Describe)
from os.path import join, basename
from NG911_GDB_Objects import getGDBObject

def userMessage(msg):
    print(msg)
    AddMessage(msg)

def main():
    gdb = GetParameterAsText(0)
    validate_topology = GetParameterAsText(1)
    add_topology(gdb, validate_topology)

def add_topology(gdb, validate_topology):
    
    gdb_obj = getGDBObject(gdb)

    ds = gdb_obj.NG911_FeatureDataset
    topology = gdb_obj.Topology
    topology_name = basename(topology)

    # see if topology exists
    if not Exists(topology):
        CreateTopology_management(ds, topology_name)
        userMessage("Created NG911 topology")

    # list feature classes already in the topology
    # check out http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-functions/topology-properties.htm
    topology_desc = Describe(topology)
    fc_topology = topology_desc.featureClassNames

#    userMessage(fc_topology)

    # list of feature classes to be added to the topology
    fc_list= [gdb_obj.RoadCenterline, gdb_obj.AddressPoints, gdb_obj.ESB,
              gdb_obj.LAW, gdb_obj.EMS, gdb_obj.FIRE, gdb_obj.AuthoritativeBoundary,
              gdb_obj.ESZ, gdb_obj.PSAP, gdb_obj.RESCUE, gdb_obj.FIREAUTOAID]

    esb_list = [gdb_obj.ESB, gdb_obj.EMS, gdb_obj.FIRE, gdb_obj.LAW,
                gdb_obj.PSAP, gdb_obj.ESZ, gdb_obj.RESCUE, gdb_obj.FIREAUTOAID]

    # add all feature classes that exist to the topology
    for fc_full in fc_list:
        fc = basename(fc_full)

        if Exists(fc_full):
            userMessage(fc)

            present = False
            # if the feature class isn't in the topology, add it
            if fc not in fc_topology:
                AddFeatureClassToTopology_management(topology, fc_full)
            else:
                present = True

            # if it's a polygon, add the no overlap rule
            if fc_full not in [gdb_obj.RoadCenterline, gdb_obj.AddressPoints]:
                AddRuleToTopology_management(topology, "Must Not Overlap (Area)", fc_full)

            # add no gaps rule to ESB layers
            if "ESB" in fc and present == False:
                AddRuleToTopology_management(topology, "Must Not Have Gaps (Area)", fc_full)

    userMessage("All feature classes present in or added to topology")


    # start adding rules based on layers that exist
    # start adding single-fc stuff

    # add road rules
    road_rules = ["Must Not Overlap (Line)", "Must Not Intersect (Line)", "Must Not Have Dangles (Line)",
                    "Must Not Self-Overlap (Line)", "Must Not Self-Intersect (Line)", "Must Be Single Part (Line)",
                    "Must Not Intersect Or Touch Interior (Line)"]
    road = gdb_obj.RoadCenterline

    if Exists(road):
        # add all individual road rules
        for road_rule in road_rules:
            AddRuleToTopology_management(topology, road_rule, road)

##        # make sure roads are inside all ESB & ESZ layers
##        for esb in esb_list:
##            esb_full = join(ds, esb)
##            if Exists(esb_full):
##                AddRuleToTopology_management(topology, "Must Be Inside (Line-Area)", road, "", esb_full)

    # make sure authoritative boundary covers everything
    auth_bnd = gdb_obj.AuthoritativeBoundary
    addy_pt = gdb_obj.AddressPoints

    if Exists(auth_bnd):
        # points
        if Exists(addy_pt):
            AddRuleToTopology_management(topology, "Must Be Properly Inside (Point-Area)", addy_pt, "", auth_bnd)

        # lines
        if Exists(road):
            AddRuleToTopology_management(topology, "Must Be Inside (Line-Area)", road, "", auth_bnd)

        # polygons
        for esb in esb_list:
            full_esb = join(ds, esb)
            if Exists(full_esb):
                AddRuleToTopology_management(topology, "Must Cover Each Other (Area-Area)", auth_bnd, "", full_esb)

    userMessage("All validation rules verified or added")

    if validate_topology == "true":
        userMessage("Validating topology...")
        ValidateTopology_management(topology)
        userMessage("Topology validated")

    return "Done"


if __name__ == '__main__':
    main()
