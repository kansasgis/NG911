#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      kyleg
#
# Created:     02/10/2014
# Copyright:   (c) kyleg 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------


try:
    from NG911_Config import gdb, DOTRoads, soundexNameExclusions, ordinalNumberEndings
except:
    "Go ahead, debug this in ArcMap... but you will have to copy and paste the NG911_Config file first"
import re
"""functions that add several administrative fields and calculate coded values for a NG911 attribute based LRS_Key field"""
checkfile = gdb
thelayer = checkfile+"/RoadCenterline"
thealias = checkfile+"/RoadAlias"
from arcpy import (
    MakeFeatureLayer_management,
    Sort_management,
    Exists,
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
holderList = list()


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
invalid_re = re.compile("[AEHIOUWY.]|[^A-Z]")
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
    #Added a "." here, should replace correctly now.
    replacementDict = {"A":"1", "E":"2", "H":"3", "I":"4", "O":"5", "U":"6", "W":"7", "Y":"8", ".":""} 
    
    if len(s) == 2: 
        if s[0] == s[1]:# Only affects one very specific road name type. Kind of a narrow fix.
            for keyName in replacementDict:
                if keyName == str(s[1].upper():
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
        enc = str("x").zfill(4)
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
    if s[0] in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.']:
        # I don't think having a '.' here will do anything unless the road name is ".SomeName" since it
        # only checks the first character of the string.
        numerical_re = re.compile("[A-Z]|[^0-9][^0-9][^0-9][^0-9]")
        s=re.sub(numerical_re,"", s.zfill(4))
        return s.zfill(4)

    else:
        return soundex(s)


def StreetNetworkCheck(gdb):
    """removes street centerlines from the topology and creates geometric network, then checks geometric network connectivity"""
    from arcpy import ListDatasets, VerifyAndRepairGeometricNetworkConnectivity_management, RemoveFeatureClassFromTopology_management, CreateGeometricNetwork_management, FindDisconnectedFeaturesInGeometricNetwork_management
    #print topo
    fd = ListDatasets(gdb)
    print fd[0]
    geonet = fd[0]+"\Street_Network"
    #print geonet
    if Exists(geonet):
        print "Street Geometric Network Already Exists"
    else:
        RemoveFeatureClassFromTopology_management(topo, "RoadCenterline")
        CreateGeometricNetwork_management(fd, "Street_Network", "RoadCenterline SIMPLE_EDGE NO", "#", "#", "#", "#", "#")
    FindDisconnectedFeaturesInGeometricNetwork_management(fd+"/RoadCenterline", "Roads_Disconnected")
    StreetLogfile = reviewpath+"/KDOTReview/"+ntpath.basename(ng911)+".log"
    VerifyAndRepairGeometricNetworkConnectivity_management(geonet, StreetLogfile, "VERIFY_ONLY", "EXHAUSTIVE_CHECK", "0, 0, 10000000, 10000000")


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
    fieldList = ['OBJECTID', 'RD', 'Soundex']
    listMatchString = re.compile(r'^WEST', re.IGNORECASE)
    roadNameString = ''
    roadPreSoundexString = ''
    roadSoundexString = ''
    testMatch = None
    testMatch1 = None
    testMatch2 = None

    # Get the data from the geodatabase so that it can be used in the next part of the function.
    cursor = daSearchCursor(roadFeatures, fieldList)  # @UndefinedVariable
    for row in cursor:
        listRow = list(row)
        holderList.append(listRow)

    # Clean up
    if cursor:
        del cursor
    else:
        pass
    if row:
        del row
    else:
        pass

    # Perform some regex on the strings to produce a new soundex in certain cases.
    for excludedText in nameExclusions:
        excludedText = str(excludedText)
        excludedText = excludedText.upper()
        listMatchString = re.compile(r'^{0}\s'.format(re.escape(excludedText)), re.IGNORECASE)

        # Matches 1 or 2 alpha characters at the start of a string, ignoring case.
        singleOrDoubleAlphaMatchString = re.compile(r'^[a-z]$|^[a-z][a-z]$', re.IGNORECASE)
        # Matches 1 to 4 digits at the start of a string, probably no reason to ignore case in the check.
        singleToQuadNumberMatchString = re.compile(r'^[0-9]$|^[0-9][0-9]$|^[0-9][0-9][0-9]$|^[0-9][0-9][0-9][0-9]$')

        for heldRow in holderList:
            roadNameString = str(heldRow[1])
            roadNameString = roadNameString.upper()
            testMatch = listMatchString.search(roadNameString)
            if testMatch != None:
                roadPreSoundexString = roadNameString[testMatch.end():]
                roadPreSoundexString = roadPreSoundexString.replace(" ", "")

                # Do subbing for #ST, #ND, #RD, #TH etc...
                for numberEnding in ordinalNumberEndings:
                    nonsensitiveReplace = re.compile(r'[0-9]{0}'.format(re.escape(numberEnding), re.IGNORECASE))
                    replaceMatch = nonsensitiveReplace.search(roadNameString)
                    if replaceMatch != None:
                        roadPreSoundexString = re.sub(replaceMatch.group(0), replaceMatch.group(0)[0:1], roadPreSoundexString)
                    else:
                        pass
                
                # Test for the following conditions:
                # A, AA as in Road A, RD AA
                testMatch1 = None
                testMatch1 = singleOrDoubleAlphaMatchString.search(roadPreSoundexString)
                # Test for the following conditions:
                # 1, 10, 100, 1000 as in Road 1, RD 10, Road 100, CR1000
                testMatch2 = None
                testMatch2 = singleToQuadNumberMatchString.search(roadPreSoundexString)
                if testMatch1 != None: # Road A, Road BB, or similar.
                    roadPreSoundexString = roadPreSoundexString[testMatch1.start():testMatch1.end()]
                    if len(roadPreSoundexString) > 2:
                        pass
                    elif len(roadPreSoundexString) == 2:
                        roadSoundexString = "0" + roadPreSoundexString
                        # Adds the first letter from the excluded text to the start of the Soundex string.
                        roadSoundexString = excludedText[0:1] + roadSoundexString
                    elif len(roadPreSoundexString) == 1:
                        roadSoundexString = "00" + roadPreSoundexString
                        roadSoundexString = excludedText[0:1] + roadSoundexString
                    else:
                        pass
                
                elif(testMatch2 != None):
                    roadPreSoundexString = roadPreSoundexString[testMatch2.start():testMatch2.end()]
                    if len(roadPreSoundexString) > 4:
                        pass
                    elif len(roadPreSoundexString) == 4:
                        # Slice the string to include only the first 3 characters.
                        roadSoundexString = roadPreSoundexString[:4]
                        # Add the first letter from the excluded text to the start of the Soundex string.
                        roadSoundexString = excludedText[0:1] + roadSoundexString
                    elif len(roadPreSoundexString) == 3:
                        roadSoundexString = roadPreSoundexString
                        roadSoundexString = excludedText[0:1] + roadSoundexString
                    elif len(roadPreSoundexString) == 2:
                        roadSoundexString = "0" + roadPreSoundexString
                        roadSoundexString = excludedText[0:1] + roadSoundexString
                    elif len(roadPreSoundexString) == 1:
                        roadSoundexString = "00" + roadPreSoundexString
                        roadSoundexString = excludedText[0:1] + roadSoundexString
                    else:
                        pass
                
                # One of the excluded texts was found at the start of the name, but it was not followed by
                # A, AA, 1, 20, 340, 5670, etc...
                # Instead something like "Road Hitch" or "RD Empire"
                # Do soundex normally, but replace the first character with the first character from the
                # excluded text.
                else:
                    roadSoundexString = soundex(roadPreSoundexString)
                    # Slice the roadSoundexString to remove the first character, but keep the rest.
                    roadSoundexString = roadSoundexString[1:]
                    # Add the first letter from the excluded text to the start of the Soundex string.
                    roadSoundexString = excludedText[0:1] + roadSoundexString

                # Assign the new road soundex string to the held row's third slot, heldRow[2],
                # to be used in an update cursor to update the data in the geodatabase.
                heldRow[2] = roadSoundexString
            else:
                pass

    # Start an edit session for this workspace because the centerline
    # feature class participates in a topology.
    editSession = daEditor(gdb)
    editSession.startEditing(False, False)
    editSession.startOperation()

    cursor = daUpdateCursor(roadFeatures, fieldList)  # @UndefinedVariable
    for row in cursor:
        for heldRow in holderList:
            if row[0] == heldRow[0]:
                cursor.updateRow(heldRow)
            else:
                pass

    # Clean up
    if cursor:
        del cursor
    else:
        pass
    if row:
        del row
    else:
        pass

    editSession.stopOperation()
    editSession.stopEditing(True)


def RouteCalc(lyr, soundexNameExclusions):
    """calculate what should be a nearly unique LRS Route key based on the decoding and street name soundex/numdex function"""
    #CalcField(lyr,"Soundex","numdex(!RD!)","PYTHON_9.3","#")
    RoadinName(lyr, soundexNameExclusions)
    CalcField(lyr, "RID", "str(!KDOT_COUNTY_R!)+str(!KDOT_COUNTY_L!)+str(!KDOT_CITY_R!)+str(!KDOT_CITY_L!)+str(!PreCode!) + !Soundex! + str(!SuffCode!)+str(!UniqueNo!)+str(!TDirCode!)","PYTHON_9.3","#")

# Instead of calling numdex here, rewrite and incorporate numdex and soundex functionality into the RoadinName function.

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
RouteCalc(lyr, soundexNameExclusions)
#AliasCalc(Alias, DOTRoads)
#HighwayCalc(lyr, gdb, Alias)
#StreetNetworkCheck(gdb)
#createUniqueIdentifier(gdb, lyr, uniqueIdInFields, uniqueIdOutFields)
#LRS_Tester()