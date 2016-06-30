#-------------------------------------------------------------------------------
# Name:        NG911_config
# Purpose:      Configuration variables for the NG911 Data Check
#
# Author:      kristen
#
# Created:     24/09/2014
# Modified:    31/10/2014 by dirktall04
#-------------------------------------------------------------------------------
from os.path import join, basename

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
##        self.gdbVersion = "11"
        self.ESZ = ""

currentPathSettings = pathInformationClass()

def getGDBObject(gdb):

    # This is a class used represent the NG911 geodatabase
    class NG911_GDB_Object():
        def __init__(self):
            self.gdbPath = gdb
            self.NG911_FeatureDataset = join(gdb, "NG911")
            self.AddressPoints = join(self.NG911_FeatureDataset, "AddressPoints")
            self.RoadCenterline = join(self.NG911_FeatureDataset, "RoadCenterline")
            self.RoadAlias = join(gdb, "RoadAlias")
            self.AuthoritativeBoundary = join(self.NG911_FeatureDataset, "AuthoritativeBoundary")
            self.MunicipalBoundary = join(self.NG911_FeatureDataset, "MunicipalBoundary")
            self.CountyBoundary = join(self.NG911_FeatureDataset, "CountyBoundary")
            self.ESZ = join(self.NG911_FeatureDataset, "ESZ")
            self.PSAP = join(self.NG911_FeatureDataset, "PSAP")
            self.Topology = join(self.NG911_FeatureDataset, "NG911_Topology")
            self.Locator = join(gdb, "Locator")
            self.gc_test = join(gdb, "gc_test")
            self.GeocodeTable = join(gdb, "GeocodeTable")
            self.GeocodeExceptions = join(gdb, "GeocodeExceptions")
            self.AddressPointFrequency = join(gdb, "AP_Freq")
            self.RoadCenterlineFrequency = join(gdb, "Road_Freq")
            self.FieldValuesCheckResults = join(gdb, "FieldValuesCheckResults")
            self.TemplateCheckResults = join(gdb, "TemplateCheckResults")
            self.ProjectionFile = r"\\stewie\c$\hp\ftp\ftp2\ftp_users\GISSubcommittee_NG911\KDOTprojectionfile\KDOT_Lambert.prj"
            self.AdminBoundaryList = [basename(self.AuthoritativeBoundary), basename(self.CountyBoundary), basename(self.MunicipalBoundary),
                                    basename(self.ESZ), basename(self.PSAP)]

    NG911_GDB = NG911_GDB_Object()

    return NG911_GDB

def checkToolboxVersion():
    import json, urllib
    from inspect import getsourcefile
    from os.path import abspath, dirname, join, exists
    from arcpy import AddMessage

    #set lots of variables
    message, toolData, toolVersion, response, mostRecentVersion = "", "", "0", "", "X"

    #get version in the .json file that is already present
    me_folder = dirname(abspath(getsourcefile(lambda:0)))
    jsonFile = join(me_folder, "ToolboxVersion.json")

    #make sure the local json file exists
    if exists(jsonFile):
        toolData = json.loads(open(jsonFile).read())
        toolVersion = toolData["toolboxVersion"]["version"]
        AddMessage(toolVersion)

    #get version of toolbox live online
    url = "https://raw.githubusercontent.com/kansasgis/NG911/master/Scripts/ToolboxVersion.json"

    #Error trapping in case the computer is offline or can't get to the internet
    try:
        response = urllib.urlopen(url)
        mostRecentData = json.loads(response.read())
        mostRecentVersion = mostRecentData["toolboxVersion"]["version"]
        AddMessage(mostRecentVersion)
    except:
        message("Unable to check toolbox version at this time.")

    #compare the two
    if toolVersion == mostRecentVersion:
        message = "Your NG911 toolbox version is up-to-date."
    else:
        if mostRecentVersion != "X":
            message = """Your version of the NG911 toolbox is not the most recent version available.
            Your results might be different than results received upon data submission. Please
            download an up-to-date copy of the toolbox at
            https://github.com/kansasgis/NG911/raw/master/KansasNG911GISTools.zip"""

    #report back to the user
    return message

