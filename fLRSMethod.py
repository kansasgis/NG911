#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      kyleg
#
# Created:     02/10/2014
# Copyright:   (c) kyleg 2014
# Licence:     <your licence>
# Modified:    11/05/2014 by dirktall04
# KMG           12/9/2014 Add Function to take in MSAG and linear reference the results
#               PER Aggregation meetings December 2014:
#               Modify LRS Key to use KDOT LRS Key, and use ADMO from KDOT North and West Road
#               "Clear previous errors table"
#               Create Intersections using Geometric Network
#               Check valid highway names
#               Create some Layer Files
#               Consider Including Layer files (in Kristen's package) for mapping errors and cleanup
#-------------------------------------------------------------------------------


try:
    from NG911_Config import gdb, DOTRoads, soundexNameExclusions, ordinalNumberEndings, currentPathSettings
except:
    "Go ahead, debug this in ArcMap... but you will have to copy and paste the NG911_Config file first"
import re
"""functions that add several administrative fields and calculate coded values for a NG911 attribute based LRS_Key field"""
import os, ntpath
checkfile = gdb
thelayer = checkfile+"/RoadCenterline"
thealias = checkfile+"/RoadAlias"
from arcpy import (
    MakeFeatureLayer_management,
    Sort_management,
    Exists,
    GetMessages,
    FeatureClassToFeatureClass_conversion,
    SelectLayerByLocation_management,
    DisableEditorTracking_management)
from arcpy import (
    CalculateField_management as CalcField,
    MakeTableView_management as TableView,
    AddJoin_management as JoinTbl,
    RemoveJoin_management as removeJoin,
    AddField_management as addField,
    AddIndex_management as AddIndex,
    SelectLayerByAttribute_management as Select,
    Delete_management as Delete
    )


from arcpy.da import (
    SearchCursor as daSearchCursor,
    UpdateCursor as daUpdateCursor,
    Editor as daEditor)


from arcpy import env
env.overwriteOutput = 1
env.workspace = checkfile


MakeFeatureLayer_management(thelayer,"RoadCenterline","#","#","#")
lyr = "RoadCenterline"
TableView(thealias, "RoadAlias","#","#","#")
Alias = "RoadAlias"
Kdotdbfp = DOTRoads


try:
    DisableEditorTracking_management(thelayer ,"DISABLE_CREATOR","DISABLE_CREATION_DATE","DISABLE_LAST_EDITOR","DISABLE_LAST_EDIT_DATE")
    DisableEditorTracking_management(thealias ,"DISABLE_CREATOR","DISABLE_CREATION_DATE","DISABLE_LAST_EDITOR","DISABLE_LAST_EDIT_DATE")
except:
    print "WARNING: could not Disable editor tracking, it has either already been disabled, or there is a lock on the database"


"""
This module encodes a string using Soundex, as described by
http://en.wikipedia.org/w/index.php?title=Soundex&oldid=466065377

Only strings with the letters A-Z and of length >= 2 are supported.
"""
invalid_re = re.compile("[AEHIOUWY\.]|[^A-Z]")
numerical_re = re.compile("[A-Z]")
charsubs = {'B': '1', 'F': '1', 'P': '1', 'V': '1',
            'C': '2', 'G': '2', 'J': '2', 'K': '2',
            'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
            'D': '3', 'T': '3', 'L': '4', 'M': '5',
            'N': '5', 'R': '6', '.':''}


def normalize(s):
    """ Returns a copy of s without invalid chars and repeated letters. """
    first = s[0].upper()
    s = re.sub(invalid_re, "", s.upper()[1:])

    # remove repeated chars
    char = None
    s_clean = first
    for c in s:
        if char != c:
            s_clean += c
        char = c
    return s_clean


def soundex(s):
    """ Encode a string using Soundex. Takes a string and returns its Soundex representation."""
    replacementString = ""
    replacementDict = {"A":"1", "E":"2", "H":"3", "I":"4", "O":"5", "U":"6", "W":"7", "Y":"8"}

    if len(s) == 2:
        if s[0] == s[1]:# Only affects one very specific road name type. Kind of a narrow fix.
            for keyName in replacementDict:
                if keyName == str(s[1].upper()):
                    replacementString = replacementDict[keyName]
                    enc = str(str(s[0]) + replacementString).zfill(4)
                    return enc
                else:
                    pass
        else:
            pass

    elif len(s) == 1:
        enc = str(s[0]).zfill(4)
        return enc
    elif len(s) == 0:
        enc = str("X").zfill(4)
        return enc
    else:
        pass

    s = normalize(s)
    last = None

    enc = s[0]
    for c in s[1:]:
        if len(enc) == 4:
            break
        if charsubs[c] != last:
            enc += charsubs[c]
        last = charsubs[c]
    while len(enc) < 4:
        enc += '0'
    return enc


def numdex(s):
    """this module applies soundex to named streets, and pads the numbered streets with zeros, keeping the numbering system intact"""
    if s[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
        numerical_re = re.compile("[A-Z]|[^0-9][^0-9][^0-9][^0-9]")
        # ^^ I don't think this is working as intended.
        # As written, it would match a single alpha anywhere in the string -OR- 4 characters anywhere
        # in the string which are NOT 0 through 9. That does not seem to be the intent, or if
        # it is, it is at odds with trying to make something like Road 17A soundex to R17A.
        # As it will replace the A with "", removing it from the string.
        # Where the string is 3 or less, if it consists of two letters and a number,
        # two numbers and a letter, one number and one letter, two letters, two numbers,
        # one number, or one letter, treat it differently than other strings.

        # Redo in dt_Regex.
        s = s.replace(" ", "")
        s=re.sub(numerical_re,"", s.zfill(4))
        return s.zfill(4)

    else:
        return soundex(s)


def StreetNetworkCheck(gdb):
    """removes street centerlines from the topology and creates geometric network, then checks geometric network connectivity"""
    from arcpy import ListDatasets, VerifyAndRepairGeometricNetworkConnectivity_management, RemoveFeatureClassFromTopology_management, CreateGeometricNetwork_management, FindDisconnectedFeaturesInGeometricNetwork_management
    print gdb
    env.workspace= gdb
    fd =  ListDatasets("*", "Feature")
    fdNG = fd[0]
    print fd[0]
    topo = gdb+"/"+fdNG+"/NG911_Topology"
    #topo = ListDatasets("*") #TOPO CANNOT GET TO WORK BY LIST FUNCTOINS in V10.2.2
    geonet =gdb+"/"+fdNG+"/RoadCenterlineGeoNet"
    print topo
    if Exists(geonet):
        print "Street Geometric Network Already Exists"
    else:
        try:
            RemoveFeatureClassFromTopology_management(topo, "RoadCenterline")
        except:
            print "could not remove road centerlines from topology"
        CreateGeometricNetwork_management(gdb+"/"+fdNG, "RoadCenterlineGeoNet", "RoadCenterline SIMPLE_EDGE NO", "#", "#", "#", "#", "#")
    FindDisconnectedFeaturesInGeometricNetwork_management(gdb+"/"+fdNG+"/RoadCenterline", "Roads_Disconnected")
    StreetLogfile = os.path.join(os.path.dirname(currentPathSettings.gdbPath), os.path.basename(currentPathSettings.gdbPath)[:-4]+"_Centerline.log")
    VerifyAndRepairGeometricNetworkConnectivity_management(geonet, StreetLogfile, "VERIFY_ONLY", "EXHAUSTIVE_CHECK", "0, 0, 10000000, 10000000")

def IntersectionMaker(currentPathSettings):
    print "this is in another code set"

def ReturnStreetstoTopology(gdb):
    from arcpy import Delete_management, AddFeatureClassToTopology_management, ListDatasets, AddRuleToTopology_management
    env.workspace =currentPathSettings.gdbPath
    fd =  ListDatasets("*", "Feature")
    gdbw =os.path.join(currentPathSettings.gdbPath, fd[0])
    env.workspace = gdbw
    topoDatasetList =  arcpy.ListDatasets("*", "TOPOLOGY")
    geonetDatasetList = arcpy.ListDatasets("*", "GeometricNetwork")
    authbnd =os.path.join(gdbw, "AuthoritativeBoundary")
    ESZBnd =os.path.join(gdbw, "ESZ")
    if geonetDatasetList == []:
        print "no geometric network created yet"
    else:
        Delete_management(geonetDatasetList)
    desc = arcpy.Describe(topoDatasetList[0])
    print "%-27s %s" % ("FeatureClassNames:", desc.featureClassNames)
    if lyr in desc.featureClassNames:
        print "Road Centerlines already exist in topology dataset"
    else:
        print "adding road centerlines to topology"
        inputTopology = os.path.join(gdbw, topoDatasetList[0])
        inputRoadCenterline =os.path.join(gdbw, "RoadCenterline")
        AddFeatureClassToTopology_management(inputTopology, inputRoadCenterline, "1", "1")
        AddRuleToTopology_management(inputTopology, "Must Not Overlap (line)", inputRoadCenterline, "", "", "")
        AddRuleToTopology_management(inputTopology, "Must Not Intersect (line)", inputRoadCenterline, "", "", "")
        AddRuleToTopology_management(inputTopology, "Must Not Have Dangles (Line)", inputRoadCenterline, "", "", "")
        AddRuleToTopology_management(inputTopology, "Must Not Self-Overlap (Line)", inputRoadCenterline, "", "", "")
        AddRuleToTopology_management(inputTopology, "Must Not Self-Intersect (Line)", inputRoadCenterline, "", "", "")
        AddRuleToTopology_management(inputTopology, "Must Be Single Part (Line)", inputRoadCenterline, "", "", "")
        AddRuleToTopology_management(inputTopology, "Must Not Intersect Or Touch Interior (Line)", inputRoadCenterline, "", "", "")
        AddRuleToTopology_management(inputTopology, "Must Not Intersect Or Touch Interior (Line)", inputRoadCenterline, "", "", "")
        AddRuleToTopology_management(inputTopology, "Must Be Inside (Line-Area)", inputRoadCenterline, "", authbnd, "")
#write for loop - must be inside ESZ boundaries
        AddRuleToTopology_management(inputTopology, "Boundary Must Be Covered By (Area-Line)", authbnd, "", inputRoadCenterline, "")
        AddRuleToTopology_management(inputTopology, "Boundary Must Be Covered By (Area-Line)", ESZBnd, "", inputRoadCenterline, "")
#write for loop - Boundary Must Be Covered By ESZ boundaries


'''Available Topology rules for python:
Must Not Have Gaps (Area)
Must Not Overlap (Area)
Must Be Covered By Feature Class Of (Area-Area)
Must Cover Each Other (Area-Area)
Must Be Covered By (Area-Area)
Must Not Overlap With (Area-Area)
Must Be Covered By Boundary Of (Line-Area)
Must Be Covered By Boundary Of (Point-Area)
Must Be Properly Inside (Point-Area)
Must Not Overlap (Line)
Must Not Intersect (Line)
Must Not Have Dangles (Line) |
Must Not Have Pseudo-Nodes (Line) |
Must Be Covered By Feature Class Of (Line-Line) |
Must Not Overlap With (Line-Line) |
Must Be Covered By (Point-Line) |
Must Be Covered By Endpoint Of (Point-Line) |
Boundary Must Be Covered By (Area-Line) |
Boundary Must Be Covered By Boundary Of (Area-Area) |
Must Not Self-Overlap (Line) |
Must Not Self-Intersect (Line) |
Must Not Intersect Or Touch Interior (Line)
Endpoint Must Be Covered By (Line-Point) |
Contains Point (Area-Point) |
Must Be Single Part (Line) |
Must Coincide With (Point-Point) |
Must Be Disjoint (Point) |
Must Not Intersect With (Line-Line) |
Must Not Intersect or Touch Interior With (Line-Line) |
Must Be Inside (Line-Area)
Contains One Point (Area-Point).
Failed to execute (AddRuleToTopology)
'''


def ConflateKDOTrestart(gdb, DOTRoads):
    """Conflation restart for selecting KDOT roads to conflate to the NG911 Network"""
    MakeFeatureLayer_management(DOTRoads+"/KDOT_HPMS_2012","KDOT_Roads","#","#","#")
    MakeFeatureLayer_management(checkfile+"/RoadCenterline","RoadCenterline","#","#","#")
    SelectLayerByLocation_management("KDOT_Roads","INTERSECT","RoadCenterline","60 Feet","NEW_SELECTION")
    FeatureClassToFeatureClass_conversion("KDOT_Roads",checkfile+r"/NG911","KDOT_Roads_Review","#","#","#")


def ConflateKDOT(gdb, DOTRoads):
    """detects road centerline changes and transfers the HPMS key field from the KDOT roads via ESRI conflation tools"""
    from arcpy import TransferAttributes_edit, DetectFeatureChanges_management, RubbersheetFeatures_edit, GenerateRubbersheetLinks_edit, RubbersheetFeatures_edit
    checkfile = gdb
    spatialtolerance = "20 feet"
    MakeFeatureLayer_management(DOTRoads+"/KDOT_HPMS_2012","KDOT_Roads","#","#","#")
    MakeFeatureLayer_management(checkfile+"/RoadCenterline","RoadCenterline","#","#","#")
    if Exists(checkfile+r"/NG911/KDOT_Roads_Review"):
        print "selection of KDOT roads for conflation already exists"
    else:
        SelectLayerByLocation_management("KDOT_Roads","INTERSECT","RoadCenterline","60 Feet","NEW_SELECTION")
        FeatureClassToFeatureClass_conversion("KDOT_Roads",checkfile+r"/NG911","KDOT_Roads_Review","#","#","#")
    MakeFeatureLayer_management(checkfile+"/KDOT_Roads_Review","KDOT_Roads_Review","#","#","#")
    GenerateRubbersheetLinks_edit("KDOT_Roads_Review","RoadCenterline",checkfile+r"/NG911/RoadLinks",spatialtolerance,"ROUTE_ID LRSKEY",checkfile+r"/RoadMatchTbl")
    MakeFeatureLayer_management(checkfile+"/NG911/RoadLinks","RoadLinks","#","#","#")
    MakeFeatureLayer_management(checkfile+"/NG911/RoadLinks_pnt","RoadLinks_pnt","#","#","#")
    RubbersheetFeatures_edit("KDOT_Roads_Review","RoadLinks","RoadLinks_pnt","LINEAR")
    DetectFeatureChanges_management("KDOT_Roads_Review","RoadCenterline",checkfile+r"/NG911/RoadDifference",spatialtolerance,"#",checkfile+r"/RoadDifTbl",spatialtolerance,"#")
    MakeFeatureLayer_management(checkfile+"/NG911/RoadDifference","RoadDifference","#","#","#")
    TransferAttributes_edit("KDOT_Roads_Review","RoadCenterline","YEAR_RECORD;ROUTE_ID",spatialtolerance,"#",checkfile+r"/LRS_MATCH")


#Add checks here to see if these exist prior to creating them. Should prevent RID_1, RID_2, RID_3, etc.
def addAdminFields(lyr, Alias):
    try:
        AddIndex(lyr,"SEGID;COUNTY_L;COUNTY_R;MUNI_L;MUNI_R","RCL_INDEX","NON_UNIQUE","NON_ASCENDING")
    except:
        print "indexed"
    FieldList3=("KDOT_COUNTY_R", "KDOT_COUNTY_L","KDOT_CITY_R", "KDOT_CITY_L", 'UniqueNo' )
    for field in FieldList3:
        addField(lyr, field, "TEXT", "#", "#", "3")
    FieldList1=('KDOT_ADMO', 'KDOTPreType', 'PreCode', 'SuffCode', 'TDirCode')
    for field in FieldList1:
        addField(lyr, field, "TEXT", "#", "#", "1")
    addField(lyr, "Soundex", "TEXT", "#", "#", "5")
    addField(lyr, "RID", "TEXT", "#", "#", "26")
    addField(lyr, "KDOT_START_DATE", "DATE")
    addField(lyr, "KDOT_END_DATE", "DATE")
    addField(lyr, "SHAPE_MILES", "Double", "#", "#", "#" )
    addField(Alias, "KDOT_PREFIX", "TEXT", "#", "#", "1" )
    addField(Alias, "KDOT_CODE", "LONG" )
    addField(Alias, "KDOT_ROUTENAME", "TEXT", "#", "#", "3" )


def CalcAdminFields(lyr, Kdotdbfp):
    """Populate Admin Fields with Default or Derived values"""
    CalcField(lyr,"UniqueNo",'000',"PYTHON_9.3","#")
    CalcField(lyr,"KDOT_START_DATE","1/1/1901","PYTHON_9.3","#")
    CalcField(lyr,"KDOTPreType","!ROUTE_ID![3]","PYTHON_9.3","#") #PreType is a conflated field, consider changing this to calculate from NENA fields
    TableView(lyr, "NewPretype", "KDOTPreType is Null")
    CalcField("NewPretype","KDOTPreType","'L'","PYTHON_9.3","#")
    CalcField(lyr,"KDOT_ADMO","'X'","PYTHON_9.3","#")
    CalcField(lyr,"PreCode","0","PYTHON_9.3","#")
    CalcField(lyr,"KDOT_CITY_L","999","PYTHON_9.3","#")
    CalcField(lyr,"KDOT_CITY_R","999","PYTHON_9.3","#")
    CalcField(lyr,"TDirCode","0","PYTHON_9.3","#")
    CalcField(lyr,"SHAPE_MILES","!Shape_Length!/5280.010560021","PYTHON_9.3","#")  #There are slightly more than 5280 miles per US Survey foot
    TableView(Kdotdbfp+"\\NG911_RdDir", "NG911_RdDir")
    JoinTbl(lyr,"PRD","NG911_RdDir", "RoadDir", "KEEP_COMMON")
    CalcField(lyr,"PreCode","!NG911_RdDir.RdDirCode!","PYTHON_9.3","#")
    removeJoin(lyr)
    TableView(Kdotdbfp+"\NG911_RdTypes", "NG911_RdTypes")
    CalcField(lyr,"SuffCode","0","PYTHON_9.3","#")
    JoinTbl(lyr,"STS","NG911_RdTypes", "RoadTypes", "KEEP_COMMON")
    CalcField(lyr,"SuffCode","!NG911_RdTypes.LRS_CODE_TXT!","PYTHON_9.3","#")
    removeJoin(lyr)


def CountyCode(lyr):
    """Codify the County number for LRS (based on right side of street based on addressing direction, calculated for LEFT and RIGHT from NG911)"""
    TableView(Kdotdbfp+"\NG911_County", "NG911_County")
    JoinTbl(lyr,"COUNTY_L","NG911_County", "CountyName", "KEEP_COMMON")
    CalcField(lyr,"KDOT_COUNTY_L","!NG911_County.CountyNumber!","PYTHON_9.3","#")
    removeJoin(lyr)
    JoinTbl(lyr,"COUNTY_R","NG911_County", "CountyName", "KEEP_COMMON")
    CalcField(lyr,"KDOT_COUNTY_R","!NG911_County.CountyNumber!","PYTHON_9.3","#")
    removeJoin(lyr)


def CityCodes(lyr, Kdotdbfp):
    """Codify the City Limit\city number for LRS , calculated for LEFT and RIGHT from NG911)"""
    TableView(Kdotdbfp+"\City_Limits", "City_Limits")
    JoinTbl(lyr,"MUNI_R","City_Limits", "CITY", "KEEP_COMMON")
    CalcField(lyr,"KDOT_CITY_R","str(!City_Limits.CITY_CD!).zfill(3)","PYTHON_9.3","#")
    removeJoin(lyr)
    JoinTbl(lyr,"MUNI_L","City_Limits", "CITY", "KEEP_COMMON")
    CalcField(lyr,"KDOT_CITY_L","str(!City_Limits.CITY_CD!).zfill(3)","PYTHON_9.3","#")
    removeJoin(lyr)
    TableView(lyr, "CityRoads", "KDOT_CITY_R = KDOT_CITY_L AND KDOT_CITY_R not like '999'")
    CalcField("CityRoads","KDOT_ADMO","'W'","PYTHON_9.3","#")


def RoadinName1(lyr):
    """This module corrects the road names in the soundex code where the road is named like Road A or Road 12 """
    TableView(lyr,"ROAD_NAME","RD LIKE 'ROAD %'")
    CalcField("ROAD_NAME","Soundex",""""R"+!RD![5:].zfill(3)""","PYTHON_9.3","#")

    TableView(lyr,"RD_NAME","RD LIKE 'RD %'")
    CalcField(lyr,"Soundex","""("R"+!RD![1:5]).zfill(3)""","PYTHON_9.3","#")


def RoadinName(roadFeatures, nameExclusions):
    """This module corrects the road names in the soundex code where the road is named like Road A or Road 12 """
    # Need to add logic to remove the ST from roads like 3RD ST and make sure that this translates to 0003
    # and not 003.
    fieldList = ['OBJECTID', 'RD', 'Soundex']
    #Placeholder. Recompiled in nameExclusions for loop.
    listMatchString = re.compile(r'^WEST', re.IGNORECASE)
    roadNameString = ''
    roadPreSoundexString = ''
    roadSoundexString = ''
    holderList = list()

    testMatch0 = None
    testMatch1 = None
    testMatch2 = None
    testMatch3 = None

    # Get the data from the geodatabase so that it can be used in the next part of the function.
    cursor = daSearchCursor(roadFeatures, fieldList)  # @UndefinedVariable
    for row in cursor:
        listRow = list(row)
        holderList.append(listRow)

    # Clean up
    if "cursor" in locals():
        del cursor
    else:
        pass
    if "row" in locals():
        del row
    else:
        pass

    # Matches any group of 3 alpha characters in the string, ignoring case.
    tripleAlphaMatchString = re.compile(r'[A-Z][A-Z][A-Z]', re.IGNORECASE)
    # Matches 1 or 2 alpha characters at the start of a string, ignoring case.
    singleOrDoubleAlphaMatchString = re.compile(r'^[A-Z]$|^[A-Z][A-Z]$', re.IGNORECASE)
    # Matches 1 to 4 digits at the start of a string, probably no reason to ignore case in the check.
    singleToQuadNumberMatchString = re.compile(r'^[0-9]$|^[0-9][0-9]$|^[0-9][0-9][0-9]$|^[0-9][0-9][0-9][0-9]$')
    anyNumberMatchString = re.compile(r'[0-9]', re.IGNORECASE)

    # For roads that don't match a name exclusion:
    singleOrDoubleNumberThenAlphaMatchString = re.compile(r'^[0-9][0-9][A-Z]$|^[0-9][A-Z]$', re.IGNORECASE)
    # For roads that don't match a name exclusion and should be normally Numdexed.
    firstCharacterNumberString = re.compile(r'^[0-9]')

    ## Significant structure change here 2014-11-05.
    ## Watch for possible bugs.
    ##
    ## Added Numdex logic to this part, which
    ## caused some issues.
    ##
    ## Flattened the loops out here so that it only
    ## does a run through the
    ## <for heldRow in holderList>
    ## loop once instead of doing it once per
    ## entry in the nameExclusions list via
    ## <for excludedText in nameExclusions>
    ##
    ## Runs faster now. After changing the regex string
    ## to be dynamically generated prior to compilation
    ## and using \b{0}\b as part of the pattern,
    ## errors *seem* to be gone.

    stringToCompile = ""

    # Perform some regex on the strings to produce a new soundex in certain cases.
    for i, excludedText in enumerate(nameExclusions): #shift left start
        excludedText = str(excludedText)
        excludedText = excludedText.upper()
        #listMatchString = re.compile(r'^{0}\s'.format(re.escape(excludedText)), re.IGNORECASE) ## Old version, pre-dynamic generation.
        if i == 0:
            stringToCompile = r'^\b{0}\b\ '.format(re.escape(excludedText))
        else:
            stringToCompile = stringToCompile + r'|^\b{0}\b\ '.format(re.escape(excludedText))
        print i
        listMatchString = re.compile(stringToCompile, re.IGNORECASE)

    print "stringToCompile = " + str(stringToCompile)

    for heldRow in holderList:
        roadNameString = ''
        roadPreSoundexString = ''
        roadSoundexString = ''

        roadNameString = str(heldRow[1])
        roadNameString = roadNameString.upper()
        roadNameString = roadNameString.replace(".", "")

        exclusionMatch = listMatchString.search(roadNameString)
        if exclusionMatch != None: # Testing for excluded Road Names such as "Road" and "CR" in "Road 25" and "CR 2500".
            # Get the characters from the end of the testMatch to the end of the string.
            # Should return a string that starts with a space.

            roadPreSoundexString = roadNameString[exclusionMatch.end():]

            # Replace with a search for " " by group in regex.
            roadPreSoundexString = roadPreSoundexString.replace(" ", "")
            roadPreSoundexString = roadPreSoundexString.replace(" ", "")
            # then loop through the groups to replace with "" so that any number
            # of spaces can be removed.

            print "roadNameString = " + str(roadNameString)
            print "roadPreSoundexString = " + str(roadPreSoundexString)

            # Do subbing for #ST, #ND, #RD, #TH etc...
            for numberEnding in ordinalNumberEndings:
                nonsensitiveReplace = re.compile(r'[0-9]{0}'.format(re.escape(numberEnding), re.IGNORECASE))
                replaceMatch = nonsensitiveReplace.search(roadNameString)
                if replaceMatch != None:
                    roadPreSoundexString = re.sub(replaceMatch.group(0), "", roadPreSoundexString)
                else:
                    pass

            # Replace with regex string that matches spaces as groups, then loop through groups to replace.
            roadPreSoundexString = roadPreSoundexString.replace(" ", "")
            roadPreSoundexString = roadPreSoundexString.replace(" ", "")

            testMatch0 = None
            testMatch0 = tripleAlphaMatchString.search(roadPreSoundexString)
            testMatch1 = None
            testMatch1 = singleOrDoubleAlphaMatchString.search(roadPreSoundexString)
            testMatch2 = None
            testMatch2 = singleToQuadNumberMatchString.search(roadPreSoundexString)
            testMatch3 = None
            testMatch3 = anyNumberMatchString.search(roadPreSoundexString)

            if testMatch0 != None:
                roadSoundexString = soundex(roadPreSoundexString)
                # Slice the roadSoundexString to remove the first character, but keep the rest.
                if len(roadSoundexString) >= 4:
                    roadSoundexString = roadSoundexString[1:4]
                    # The next line looks complicated, but exclusionMatch.group(0)[0:1]
                    # is actually just getting the first letter of the first matched pattern.
                    roadSoundexString = exclusionMatch.group(0)[0:1] + roadSoundexString
                elif len(roadSoundexString) == 3:
                    roadSoundexString = exclusionMatch.group(0)[0:1] + roadSoundexString
                elif len(roadSoundexString) == 2 or len(roadSoundexString) == 1:
                    roadSoundexString = roadSoundexString.zfill(3)
                    roadSoundexString = exclusionMatch.group(0)[0:1] + roadSoundexString
                else:
                    pass

                heldRow[2] = roadSoundexString

            elif testMatch1 != None: # Road A, Road BB, or similar.
                roadPreSoundexString = roadPreSoundexString[testMatch1.start():testMatch1.end()]
                if len(roadPreSoundexString) > 2:
                    pass
                elif len(roadPreSoundexString) == 2:
                    roadSoundexString = "0" + roadPreSoundexString
                    roadSoundexString = exclusionMatch.group(0)[0:1] + roadSoundexString
                    heldRow[2] = roadSoundexString
                elif len(roadPreSoundexString) == 1:
                    roadSoundexString = "00" + roadPreSoundexString
                    roadSoundexString = exclusionMatch.group(0)[0:1] + roadSoundexString
                    heldRow[2] = roadSoundexString
                else:
                    pass

            elif testMatch2 != None:
                roadPreSoundexString = roadPreSoundexString[testMatch2.start():testMatch2.end()]
                if len(roadPreSoundexString) > 4:
                    pass
                elif len(roadPreSoundexString) == 4:
                    # Slice the string to include only the first 3 characters, as slice end is non-inclusive.
                    roadSoundexString = roadPreSoundexString[:4]
                    roadSoundexString = exclusionMatch.group(0)[0:1] + roadSoundexString
                    heldRow[2] = roadSoundexString
                elif len(roadPreSoundexString) == 3:
                    roadSoundexString = roadPreSoundexString
                    roadSoundexString = exclusionMatch.group(0)[0:1] + roadSoundexString
                    heldRow[2] = roadSoundexString
                elif len(roadPreSoundexString) == 2:
                    roadSoundexString = "0" + roadPreSoundexString
                    roadSoundexString = exclusionMatch.group(0)[0:1] + roadSoundexString
                    heldRow[2] = roadSoundexString
                elif len(roadPreSoundexString) == 1:
                    roadSoundexString = "00" + roadPreSoundexString
                    roadSoundexString = exclusionMatch.group(0)[0:1] + roadSoundexString
                    heldRow[2] = roadSoundexString
                else:
                    pass
            else:
                pass

        else:
            roadNameString = heldRow[1]
            testMatch4 = None
            testMatch4 = singleOrDoubleNumberThenAlphaMatchString.search(roadNameString)
            testMatch5 = None
            testMatch5 = firstCharacterNumberString.search(roadNameString)

            # Numdex with one or two numbers, then alpha.
            if testMatch4 != None:
                roadPreSoundexString = roadNameString[testMatch4.start():]
                roadSoundexString = roadPreSoundexString.zfill(4)
                heldRow[2] = roadSoundexString
            # Normal Numdex if there were not one or two numbers, then alpha, but the string starts with a number.
            elif testMatch5 != None:
                numerical_re = re.compile("[A-Z]|[^0-9][^0-9][^0-9][^0-9]")

                roadPreSoundexString = roadNameString.replace(" ", "")
                roadSoundexString = re.sub(numerical_re,"", roadPreSoundexString.zfill(4))

                if len(roadSoundexString) > 4:
                    roadSoundexString = roadSoundexString[:5]
                else:
                    pass

                roadSoundexString = roadSoundexString.zfill(4)

                heldRow[2] = roadSoundexString

            else: # Check for AA, BB, EE, etc without an excluded name in front of it
                if len(roadNameString) == 2:
                    if roadNameString[0] == roadNameString[1]:
                        roadPreSoundexString = roadNameString
                        roadSoundexString = roadPreSoundexString.zfill(4)
                else: # Normal Soundex
                    roadPreSoundexString = roadNameString
                    roadSoundexString = soundex(roadPreSoundexString)

                heldRow[2] = roadSoundexString # shift left end


    try:
        # Start an edit session for this workspace because the centerline
        # feature class participates in a topology.
        editSession = daEditor(gdb)
        editSession.startEditing(False, False)
        editSession.startOperation()

        print "Editing started."

        cursor = daUpdateCursor(roadFeatures, fieldList)  # @UndefinedVariable
        for row in cursor:
            for heldRow in holderList: # N^2 looping, try not to place print statements inside this block.
                if str(row[0]) == str(heldRow[0]):
                    cursor.updateRow(heldRow)
                else:
                    pass

        editSession.stopOperation()
        editSession.stopEditing(True)

        print "Editing complete."

    except Exception as e:
        print "Failed to update the Soundex values."
        print e.message
        print GetMessages(2)

    finally:
        # Clean up
        if "cursor" in locals():
            del cursor
        else:
            pass
        if "row" in locals():
            del row
        else:
            pass


def RouteCalc(lyr, soundexNameExclusions):
    """calculate what should be a nearly unique LRS Route key based on the decoding and street name soundex/numdex function"""
    # Trying to make the CalcField call unnecessary as RoadinName includes the functionality
    # of numdex.
    # Instead of calling numdex here, rewrite and incorporate numdex and soundex functionality into the RoadinName function.
    #CalcField(lyr,"Soundex","numdex(!RD!)","PYTHON_9.3","#")
    RoadinName(lyr, soundexNameExclusions)
    CalcField(lyr, "RID", "str(!KDOT_COUNTY_R!)+str(!KDOT_COUNTY_L!)+str(!KDOT_CITY_R!)+str(!KDOT_CITY_L!)+str(!PreCode!) + !Soundex! + str(!SuffCode!)+str(!UniqueNo!)+str(!TDirCode!)","PYTHON_9.3","#")


def AliasCalc(Alias, DOTRoads):
    CalcField(Alias, "KDOT_PREFIX", "!LABEL![0]","PYTHON_9.3","#")
    CalcField(Alias,"KDOT_ROUTENAME","""!A_RD![1:].replace("S","").zfill(3)""","PYTHON_9.3","#")
    TableView(DOTRoads+"\KDOT_RoutePre", "KDOT_RoutePre")
    JoinTbl("RoadAlias", "KDOT_PREFIX", "KDOT_RoutePre", "LRSPrefix", "KEEP_COMMON")
    CalcField("RoadAlias","RoadAlias.KDOT_CODE","!KDOT_RoutePre.PreCode!","PYTHON_9.3","#")
    removeJoin("RoadAlias")


def HighwayCalc(lyr, gdb, Alias):
    """Pull out State Highways to preserve KDOT LRS Key (CANSYS FORMAT - non directional CRAD)"""
    if Exists(gdb+"\RoadAlias_Sort"):
        Delete(gdb+"\RoadAlias_Sort")
    else:
        pass
    Sort_management(Alias,gdb+"\RoadAlias_Sort","KDOT_CODE ASCENDING;KDOT_ROUTENAME ASCENDING","UR")

    #Heiarchy did not sort or calc correctly for Cheyenne County, US36 over K161 1st
    #Sot and join doesnt accomplish primary route key designsation... but calculaing over hte heirarchy should...
    #Remember to check the primary route heirarchy calculates correctly where US rides US and I rides I
    Heriarchy = ["K", "U", "I"]
    for routeClass in Heriarchy:
        rideselect =  "KDOT_PREFIX LIKE '"+routeClass+"%'"
        print rideselect, routeClass
        TableView(gdb+"\RoadAlias_Sort", "RoadAlias_Sort", rideselect)
        JoinTbl(lyr,"SEGID","RoadAlias_Sort", "SEGID", "KEEP_COMMON")
        CalcField(lyr,lyr+".KDOTPreType","!RoadAlias_Sort.KDOT_PREFIX!","PYTHON_9.3","#")
        CalcField(lyr,lyr+".Soundex","!RoadAlias_Sort.KDOT_PREFIX!+!RoadAlias_Sort.KDOT_ROUTENAME!","PYTHON_9.3","#")
        CalcField(lyr,"KDOT_ADMO","'S'","PYTHON_9.3","#")
        CalcField(lyr,"PreCode","0","PYTHON_9.3","#")
        removeJoin(lyr)
    CalcField(lyr, "RID", "str(!KDOT_COUNTY_R!)+str(!KDOT_COUNTY_L!)+str(!KDOT_CITY_R!)+str(!KDOT_CITY_L!)+str(!PreCode!) + !Soundex! + str(!SuffCode!)+str(!UniqueNo!)+str(!TDirCode!)","PYTHON_9.3","#")
    CalcField(lyr, "LRSKEY", "str(!RID!)", "PYTHON_9.3","#")


def ScratchCalcs():
    CalcField("RoadCenterline","RoadCenterline.Soundex","""!RoadAlias.A_RD![0]  +  !RoadAlias.A_RD![1:].replace("S","").zfill(3)""","PYTHON_9.3","#")
    CalcField(in_table="RoadCenterline",field="RoadCenterline.KDOTPreType",expression="!RoadAlias.A_RD![0]  ",expression_type="PYTHON_9.3",code_block="#")
    CalcField(in_table="RoadCenterline",field="RoadCenterline.PreCode",expression="'0'",expression_type="PYTHON_9.3",code_block="#")
    CalcField(in_table="RoadCenterline",field="RoadCenterline.KDOT_ADMO",expression="'S'",expression_type="PYTHON_9.3",code_block="#")


def LRS_Tester():
    """makes the LRS route layer and dissolves the NG911 fields to LRS event tables"""
    # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
    # The following inputs are layers or table views: "RoadCenterline"
    from arcpy import Dissolve_management as dissolve
    CalcField(lyr, "LRSKEY", "str(!KDOT_COUNTY_R!)+str(!KDOT_COUNTY_L!)+str(!KDOT_CITY_R!)+str(!KDOT_CITY_L!)+str(!PreCode!) + !Soundex! + str(!SuffCode!)+str(!UniqueNo!)+str(!TDirCode!)","PYTHON_9.3","#")
    CalcField(lyr, "RID", "str(!KDOT_COUNTY_R!)+str(!KDOT_COUNTY_L!)+str(!KDOT_CITY_R!)+str(!KDOT_CITY_L!)+str(!PreCode!) + !Soundex! + str(!SuffCode!)+str(!UniqueNo!)+str(!TDirCode!)","PYTHON_9.3","#")


    env.overwriteOutput = 1
    dissolve(lyr,gdb+"/NG911/RCLD1","LRSKEY","SEGID COUNT;L_F_ADD MIN;L_T_ADD MAX;L_F_ADD RANGE;L_T_ADD RANGE;SHAPE_MILES SUM","MULTI_PART","DISSOLVE_LINES")
    dissolve(lyr,gdb+"/NG911/RCLD2","LRSKEY","SEGID COUNT;L_F_ADD MIN;L_T_ADD MAX;L_F_ADD RANGE;L_T_ADD RANGE;SHAPE_MILES SUM","MULTI_PART","UNSPLIT_LINES")

    #MakeRouteLayer_na()
    pass


uniqueIdInFields = ["OBJECTID", "COUNTY_L", "COUNTY_R", "STATE_L", "STATE_R", "L_F_ADD", "L_T_ADD", "R_F_ADD", "R_T_ADD", "UniqueNo", "LRSKEY", "SHAPE_MILES"]
uniqueIdOutFields = ["OBJECTID", "UniqueNo", "LRSKEY"]


def createUniqueIdentifier(gdb, lyr, inFieldNamesList, outFieldNamesList):
    '''filters through records and calculates an incremental Unique Identifier for routes that are not border routes, to handle Y's, eyebrows, and splits that would cause complex routes'''
    workspaceLocation = gdb
    #MakeFeatureLayer_management(lyr,"RCL_Particles",where_clause="COUNTY_L = COUNTY_R AND STATE_L = STATE_R AND ( L_F_ADD =0 OR L_T_ADD =0 OR R_F_ADD =0 OR R_T_ADD =0)")
    featureClassName = lyr
    from arcpy.da import SearchCursor as daSearchCursor, UpdateCursor as daUpdateCursor, Editor as daEditor
    alphabetListForConversion = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    newCursor = daSearchCursor(featureClassName, inFieldNamesList)
    searchList = list()
    for searchRow in newCursor:
        searchList.append(list(searchRow)) # Transforms the row tuple into a list so it can be edited.

    if "newCursor" in locals():
        del newCursor
    else:
        pass

    matchCount = 0
    matchList = list()

    for testRow in searchList:
        if (testRow[1] == testRow[2] and testRow[3] == testRow[4] and (str(testRow[5]) == "0" or str(testRow[6]) == "0" or str(testRow[7]) == "0" or str(testRow[8]) == "0")):
            matchCount += 1
            matchList.append(testRow)

    matchedRowDictionary = dict()

    for matchedRow in matchList:
        matchedRowContainer = list()
        # If the key already exists, assign the previous list of lists
        # to the list container, then append the new list
        # before updating the new value to that key in the dictionary.
        if matchedRow[10] in matchedRowDictionary:
            matchedRowContainer = matchedRowDictionary[matchedRow[10]]
            matchedRowContainer.append(matchedRow)
            matchedRowDictionary[matchedRow[10]] = matchedRowContainer
        # Otherwise, the key needs to be created
        # with the value, the list container, having only
        # one list contained within it for now.
        else:
            matchedRowContainer.append(matchedRow)
            matchedRowDictionary[matchedRow[10]] = matchedRowContainer

    for LRSKey in matchedRowDictionary:
        outRowContainer = matchedRowDictionary[LRSKey]
        # Sort based on length
        outRowContainer = sorted(outRowContainer, key = lambda sortingRow: sortingRow[11])
        countVariable = 0 # Start at 0 for unique values
        LRSVariable = ""
        for outRowIndex, outRow in enumerate(outRowContainer):
            # Is this the first list/row in the key's list container?
            # If so, then set the Resolution_Order to 0
            if outRowIndex == 0:
                outRow[9] = 0
            else:
                countVariable += 1
                if countVariable in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                    outRow[9] = countVariable
                elif countVariable >= 10 and countVariable <= 34:
                    outRow[9] = alphabetListForConversion[countVariable - 10] # Converts countVariable to an alpha character, without the letter "O".
                else:
                    print "The count Variable is above 34. Ran out of numbers and letters to use as unique values."

            LRSVariable = outRow[10]
            LRSVariableShortened = str(LRSVariable[:-1]) # Returns the LRSVariable without the last character.
            LRSVariable = LRSVariableShortened + str(outRow[9])
            outRow[10] = LRSVariable

            outRowString = ""

            for outRowElement in outRow:
                outRowString = outRowString + str(outRowElement) + " "

            print outRowString

            outRowContainer[outRowIndex] = outRow

        matchedRowDictionary[LRSKey] = outRowContainer

    newEditingSession = daEditor(workspaceLocation)
    newEditingSession.startEditing()
    newEditingSession.startOperation()

    newCursor = daUpdateCursor(featureClassName, outFieldNamesList)  # @UndefinedVariable
    for existingRow in newCursor:
        formattedOutRow = list()
        if existingRow[2] in matchedRowDictionary.keys():
            outRowContainer = matchedRowDictionary[existingRow[2]]
            for outRow in outRowContainer:
                if existingRow[0] == outRow[0]: # Test for matching OBJECTID fields.
                    formattedOutRow.append(outRow[0])
                    formattedOutRow.append(outRow[9])
                    formattedOutRow.append(outRow[10])
                    newCursor.updateRow(formattedOutRow)
                else:
                    pass

        else:
            pass

    newEditingSession.stopOperation()
    newEditingSession.stopEditing(True)

    if "newCursor" in locals():
        del newCursor
    else:
        pass


#ConflateKDOT(gdb, DOTRoads)
#addAdminFields(lyr, Alias)
#CalcAdminFields(lyr, Kdotdbfp)
#CountyCode(lyr)
#CityCodes(lyr, Kdotdbfp)
#RouteCalc(lyr, soundexNameExclusions)
#AliasCalc(Alias, DOTRoads)
#HighwayCalc(lyr, gdb, Alias)
#StreetNetworkCheck(gdb)
#createUniqueIdentifier(gdb, lyr, uniqueIdInFields, uniqueIdOutFields)
#LRS_Tester()