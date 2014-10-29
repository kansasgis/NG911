#-------------------------------------------------------------------------------
# Name:        NG911_config
# Purpose:      Configuration variables for the NG911 Data Check
#
# Author:      kristen
#
# Created:     24/09/2014
# Modified:    29/10/2014 by dirktall04
#-------------------------------------------------------------------------------

esb = ["EMS", "FIRE", "LAW"] #list of layers that are emergency services boundaries
gdb = r"R:\BigDrives\internal\internal1\NG911_Pilot_Agg\Final_GIS_Data\Region1_PR_Final_KJ.gdb" #full path of the NG911 geodatabase
folder = r"E:\Kristen\Data\NG911\NG911_Metadata_Fix\Domains" #folder containing the magical text files
DOTRoads = r"\\gisdata\arcgis\GISdata\DASC\NG911\KDOTReview\KDOT_Roads.gdb"

soundexNameExclusions = ["ROAD", "RD", "CO RD", "CR", "RS", "STATE HIGHWAY"]
ordinalNumberEndings = ["ST", "ND", "RD", "TH"]

currentLayerList = ["RoadAlias", "AddressPoints", "RoadCenterline", "AuthoritativeBoundary", "CountyBoundary", "ESZ", "PSAP", "MunicipalBoundary"]
nonDisplayFields = ["ObjectID", "Shape", "Shape_Area", "Shape_Length"]
