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
from os.path import join

def userMessage(msg):
    print(msg)
    AddMessage(msg)

def main():
    gdb = GetParameterAsText(0)
    validate_topology = GetParameterAsText(1)
    add_topology(gdb, validate_topology)

def add_topology(gdb, validate_topology):

    ds = join(gdb, "NG911")
    topology_name ="NG911_Topology"
    topology = join(ds, topology_name)

    # see if topology exists
    if not Exists(topology):
        CreateTopology_management(ds, topology_name)
        userMessage("Created NG911 topology")

    # list feature classes already in the topology
    # check out http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-functions/topology-properties.htm
    topology_desc = Describe(topology)
    fc_topology = topology_desc.featureClassNames

    # userMessage(fc_topology)

    # list of feature classes to be added to the topology
    fc_list= ["RoadCenterline", "AddressPoints", "ESB", "ESB_LAW", "ESB_EMS", "ESB_FIRE", "AuthoritativeBoundary",
                "ESZ", "ESB_PSAP", "ESB_RESCUE", "ESB_FIREAUTOAID"]

    esb_list = ["ESB", "ESB_EMS", "ESB_FIRE", "ESB_LAW", "ESB_PSAP", "ESZ", "ESB_RESCUE", "ESB_FIREAUTOAID"]

    # add all feature classes that exist to the topology
    for fc in fc_list:
        fc_full = join(ds, fc)

        if Exists(fc_full):

            present = False
            # if the feature class isn't in the topology, add it
            if fc not in fc_topology:
                AddFeatureClassToTopology_management(topology, fc_full)
            else:
                present = True

            # if it's a polygon, add the no overlap rule
            if fc not in ["RoadCenterline", "AddressPoints"]:
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
    road = join(ds, "RoadCenterline")

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
    auth_bnd = join(ds, "AuthoritativeBoundary")
    addy_pt = join(ds, "AddressPoints")

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
