#-------------------------------------------------------------------------------
# Name:        NG911_config
# Purpose:      Configuration variables for the NG911 Data Check
#
# Author:      kristen
#
# Created:     24/09/2014
# Modified:    29/10/2014 by dirktall04
#-------------------------------------------------------------------------------

esb = ["EMS", "FIRE", "LAW"]
gdb = r"\\gisdata\arcgis\GISdata\DASC\NG911\KDOTReview\RSDigital_GY_NG911.gdb" #r"\\gisdata\arcgis\GISdata\DASC\NG911\KDOTReview\RSDigital_CN_NG911.gdb" ##r"R:\BigDrives\internal\internal1\NG911_Pilot_Agg\Final_GIS_Data\Region1_KW_Final.gdb"
folder = r"E:\Kristen\Data\NG911\NG911_Metadata_Fix\Domains"
DOTRoads = r"\\gisdata\arcgis\GISdata\DASC\NG911\KDOTReview\KDOT_Roads.gdb"

# These soundexNameExclusions entries are already checked for a space immediately following them.
# There is no need to add a trailing space as in "RD ". Use "RD" instead.
# Also, this means that "CR" will only be matched to road names like "CR 2500",
# it will not be matched to road names like "CRAFT".

soundexNameExclusions = ["ROAD", "RD", "CO RD", "CR", "RS", "STATE HIGHWAY", "R"]
ordinalNumberEndings = ["ST", "ND", "RD", "TH"]

currentLayerList = ["RoadAlias", "AddressPoints", "RoadCenterline", "AuthoritativeBoundary", "CountyBoundary", "ESZ", "PSAP", "MunicipalBoundary"]
nonDisplayFields = ["ObjectID", "Shape", "Shape_Area", "Shape_Length"]
