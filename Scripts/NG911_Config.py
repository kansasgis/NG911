#-------------------------------------------------------------------------------
# Name:        NG911_config
# Purpose:      Configuration variables for the NG911 Data Check
#
# Author:      kristen
#
# Created:     24/09/2014
# Modified:    31/10/2014 by dirktall04
#-------------------------------------------------------------------------------
from os.path import join

esb = ["EMS", "FIRE", "LAW"] #list of layers that are emergency services boundaries
gdb = r"R:\BigDrives\internal\internal1\NG911_Pilot_Agg\Final_GIS_Data\Region1_PR_Final_KJ.gdb" #full path of the NG911 geodatabase
folder = r"E:\Kristen\Data\NG911\NG911_Metadata_Fix\Domains" #folder containing the magical text files
DOTRoads = r"\\gisdata\arcgis\GISdata\DASC\NG911\KDOTReview\KDOT_Roads.gdb"

# These soundexNameExclusions entries are already checked for a space immediately following them.
# There is no need to add a trailing space as in "RD ". Use "RD" instead.
# Also, this means that "CR" will only be matched to road names like "CR 2500",
# it will not be matched to road names like "CRAFT".

soundexNameExclusions = ["ROAD", "US HIGHWAY", "RD", "CO RD", "CR", "RS", "R", "STATE HIGHWAY", "STATE ROAD", "BUSINESS US HIGHWAY"]
ordinalNumberEndings = ["ST", "ND", "RD", "TH"]

currentLayerList = ["RoadAlias", "AddressPoints", "RoadCenterline", "AuthoritativeBoundary", "CountyBoundary", "ESZ", "PSAP", "MunicipalBoundary"]
nonDisplayFields = ["ObjectID", "Shape", "Shape_Area", "Shape_Length"]

# This is a class used to pass information to the Data Check functions.
class pathInformationClass():
    def __init__(self):
        self.gdbPath = gdb
        self.domainsFolderPath = folder
        self.addressPointsPath = ""
        self.fieldNames = ""
        self.otherPath = ""
        self.esbList = esb
        self.DOTRoads = DOTRoads
        self.checkList = []
        self.fcList = []
        self.gdbVersion = "11"
        self.ESZ = ""

currentPathSettings = pathInformationClass()

def getGDBObject(gdb):

    # This is a class used represent the NG911 geodatabase
    class NG911_GDB_Object():
        def __init__(self):
            self.gdbPath = gdb
            self.AddressPoints = join(gdb, "NG911", "AddressPoints")
            self.RoadCenterline = join(gdb, "NG911", "RoadCenterline")
            self.RoadAlias = join(gdb, "RoadAlias")
            self.AuthoritativeBoundary = join(gdb, "NG911", "AuthoritativeBoundary")
            self.MunicipalBoundary = join(gdb, "NG911", "MunicipalBoundary")
            self.ESZ = join(gdb, "NG911", "ESZ")
            self.Topology = join(gdb, "NG911", "NG911_Topology")
            self.Locator = join(gdb, "Locator")
            self.gc_test = join(gdb, "gc_test")
            self.GeocodeTable = join(gdb, "GeocodeTable")
            self.FieldValuesCheckResults = join(gdb, "FieldValuesCheckResults")
            self.TemplateCheckResults = join(gdb, "TemplateCheckResults")
            self.ProjectionFile = r"\\stewie\c$\hp\ftp\ftp2\ftp_users\GISSubcommittee_NG911\KDOTprojectionfile\KDOT_Lambert.prj"

    NG911_GDB = NG911_GDB_Object()

    return NG911_GDB
