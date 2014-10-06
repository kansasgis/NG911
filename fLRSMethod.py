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

from NG911_Config import gdb, DOTRoads
import re

"""
This module encodes a string using Soundex, as described by
http://en.wikipedia.org/w/index.php?title=Soundex&oldid=466065377

Only strings with the letters A-Z and of length >= 2 are supported.
"""
invalid_re = re.compile("[AEHIOUWY]|[^A-Z]")
numerical_re = re.compile("[A-Z]")
charsubs = {'B': '1', 'F': '1', 'P': '1', 'V': '1',
            'C': '2', 'G': '2', 'J': '2', 'K': '2',
            'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
            'D': '3', 'T': '3', 'L': '4', 'M': '5',
            'N': '5', 'R': '6'}
def normalize(s):
    """ Returns a copy of s without invalid chars and repeated letters. """
    #s = re.sub(r'\ROAD ', '', s, flags=re.IGNORECASE)
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
    if len(s) < 2:
        return None
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
        s=re.sub(numerical_re,"", s.zfill(4))
        return s.zfill(4)
    else:
        return soundex(s)

def RoadinName(lyr):
    """This module corrects the road names in the soundex code where the road is named like Road A or Road 12 """
    from arcpy import SelectLayerByAttribute_management, CalculateField_management
    SelectLayerByAttribute_management(lyr,"NEW_SELECTION","RD LIKE 'ROAD %'")
    CalculateField_management(lyr,"Soundex",""""R"+!RD![5:].zfill(3)""","PYTHON_9.3","#")
    SelectLayerByAttribute_management(lyr,"CLEAR_SELECTION","#")


def StreetNetworkCheck(gdb):
    """removes street centerlines from the topology and creates geometric network, then checks geometric network connectivity"""
    from arcpy import env, Exists, VerifyAndRepairGeometricNetworkConnectivity_management, RemoveFeatureClassFromTopology_management, CreateGeometricNetwork_management, FindDisconnectedFeaturesInGeometricNetwork_management
    checkfile = gdb
    env.workspace = checkfile
    print topo
    fd = arcpy.ListDatasests
    geonet = fd+"\Street_Network"
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
    from arcpy import SelectLayerByLocation_management, FeatureClassToFeatureClass_conversion
    from arcpy import env
    env.overwriteOutput = 1
    checkfile = gdb
    MakeFeatureLayer_management(DOTRoads+"/KDOT_HPMS_2012","KDOT_Roads","#","#","#")
    MakeFeatureLayer_management(checkfile+"/RoadCenterline","RoadCenterline","#","#","#")
    SelectLayerByLocation_management("KDOT_Roads","INTERSECT","RoadCenterline","60 Feet","NEW_SELECTION")
    FeatureClassToFeatureClass_conversion("KDOT_Roads",checkfile+r"/NG911","KDOT_Roads_Review","#","#","#")

def ConflateKDOT(gdb, DOTRoads):
    """detects road centerline changes and transfers the HPMS key field from the KDOT roads via ESRI conflation tools"""
    from arcpy import MakeFeatureLayer_management, Exists, TransferAttributes_edit, DetectFeatureChanges_management, RubbersheetFeatures_edit, SelectLayerByLocation_management, FeatureClassToFeatureClass_conversion, GenerateRubbersheetLinks_edit, RubbersheetFeatures_edit
    from arcpy import env
    env.overwriteOutput = 1
    checkfile = gdb
    spatialtolerance = "20 feet"
    #MakeFeatureLayer_management(checkfile+"/AuthoritativeBoundary","AuthoritativeBoundary_Layer","#","#","#")
    #MakeFeatureLayer_management(checkfile+"/CountyBoundary","CountyBoundary_Layer","#","#","#")
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

def LRSRoutePrep(gdb, DOTroads):
    """functions that add several administrative fields and calculate coded values for a NG911 attribute based LRS_Key field"""
    checkfile = gdb
    thelayer = checkfile+"/RoadCenterline"
    alias = gdb+"/RoadAlias"
    from arcpy import MakeFeatureLayer_management, SelectLayerByAttribute_management, AddField_management, CalculateField_management, AddJoin_management, MakeTableView_management, RemoveJoin_management
    #MakeFeatureLayer_management(checkfile+"/RoadCenterline","RoadCenterline","#","#","#")
    lyr =MakeFeatureLayer_management(thelayer,"RoadCenterline","#","#","#")
    Alias = MakeTableView_management(alias, "RoadAlias")
    Kdotdbfp = DOTRoads
    def addAdminFields(lyr, Alias):
        from arcpy import AddField_management as addField, AddIndex_management as AddIndex
        AddIndex(lyr,"SEGID;COUNTY_L;COUNTY_R;MUNI_L;MUNI_R","RCL_INDEX","NON_UNIQUE","NON_ASCENDING")
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
        addField(Alias, "KDOT_PREFIX", "TEXT", "#", "#", "1" )
        addField(Alias, "KDOT_CODE", "LONG" )
        addField(Alias, "KDOT_ROUTENAME", "TEXT", "#", "#", "3" )

    def CalcAdminFields(lyr, Kdotdbfp):
        from arcpy import CalculateField_management as CalcField
        from arcpy import MakeTableView_management as TableView
        from arcpy import AddJoin_management as JoinTbl, RemoveJoin_management as removeJoin
        CalcField(lyr,"UniqueNo",'000',"PYTHON_9.3","#")
        CalcField(lyr,"KDOT_START_DATE","1/1/1901","PYTHON_9.3","#")
        CalcField(lyr,"KDOTPreType","!ROUTE_ID![3]","PYTHON_9.3","#")
        TableView(lyr, "NewLocal", "KDOT_ADMO is null")
        CalcField("NewLocal","KDOT_ADMO","'L'","PYTHON_9.3","#")
        CalcField(lyr,"PreCode","0","PYTHON_9.3","#")
        CalcField(lyr,"KDOT_CITY_L","999","PYTHON_9.3","#")
        CalcField(lyr,"KDOT_CITY_R","999","PYTHON_9.3","#")
        TableView(Kdotdbfp+"\\NG911_RdDir", "NG911_RdDir")
        CalcField(lyr,"PreCode","0","PYTHON_9.3","#")
        JoinTbl(lyr,"PRD","NG911_RdDir", "RoadDir", "KEEP_COMMON")
        CalcField(lyr,"PreCode","!NG911_RdDir.RdDirCode!","PYTHON_9.3","#")
        removeJoin(lyr)
        TableView(Kdotdbfp+"\NG911_RdTypes", "NG911_RdTypes")
        CalcField(lyr,"SuffCode","0","PYTHON_9.3","#")
        JoinTbl(lyr,"STS","NG911_RdTypes", "RoadTypes", "KEEP_COMMON")
        CalcField(lyr,"SuffCode","!NG911_RdTypes.LRS_CODE_TXT!","PYTHON_9.3","#")
        removeJoin(lyr)

    #Codify the County number for LRS (based on right side of street based on addressing direction, calculated for LEFT and RIGHT from NG911)
    def CountyCode(lyr):
        MakeTableView_management(Kdotdbfp+"\NG911_County", "NG911_County")
        AddJoin_management(lyr,"COUNTY_L","NG911_County", "CountyName", "KEEP_COMMON")
        CalculateField_management(lyr,"KDOT_COUNTY_L","!NG911_County.CountyNumber!","PYTHON_9.3","#")
        RemoveJoin_management(lyr)
        AddJoin_management(lyr,"COUNTY_R","NG911_County", "CountyName", "KEEP_COMMON")
        CalculateField_management(lyr,"KDOT_COUNTY_R","!NG911_County.CountyNumber!","PYTHON_9.3","#")
        RemoveJoin_management(lyr)

    def CityCodes(lyr, Kdotdbfp):
        #Codify the City Limit\city number for LRS , calculated for LEFT and RIGHT from NG911)
        MakeTableView_management(Kdotdbfp+"\City_Limits", "City_Limits")
        AddJoin_management(lyr,"MUNI_R","City_Limits", "CITY", "KEEP_COMMON")
        CalculateField_management(lyr,"KDOT_CITY_R","str(!City_Limits.CITY_CD!).zfill(3)","PYTHON_9.3","#")
        RemoveJoin_management(lyr)
        AddJoin_management(lyr,"MUNI_L","City_Limits", "CITY", "KEEP_COMMON")
        CalculateField_management(lyr,"KDOT_CITY_L","str(!City_Limits.CITY_CD!).zfill(3)","PYTHON_9.3","#")
        RemoveJoin_management(lyr)

    def RouteCalc(lyr):
        from arcpy import CalculateField_management
        #calculate what should be a nearly unique LRS Route key based on the decoding and street name soundex/numdex function
        CalculateField_management(lyr,"Soundex","numdex(!RD!)","PYTHON_9.3","#")

    def HighwayCalc(lyr, gdb):
        #Pull out State Highways to preserve KDOT LRS Key (CANSYS FORMAT - non directional CRAD)
        MakeTableView_management(gdb+"\RoadAlias", "RoadAlias")
        from arcpy import CalculateField_management as CalcField, Sort_management
        from arcpy import MakeTableView_management as TableView, SelectLayerByAttribute_management as Select
        from arcpy import AddJoin_management as JoinTbl, RemoveJoin_management as removeJoin
        Select(lyr,"NEW_SELECTION","ROUTE_ID LIKE '%X0'")
        CalcField(in_table="RoadCenterline",field="KDOT_ADMO",expression="'X'",expression_type="PYTHON_9.3",code_block="#")
        Sort_management("RoadAlias",gdb+"/AliasSort1","LABEL ASCENDING","UR")
        TableView(Kdotdbfp+"\AliasSort1", "AliasSort1")
        JoinTbl(lyr,"SEGID","AliasSort1", "SEGID")
        Select(lyr, "NEW_SELECTION", "AliasSort1.LABEL LIKE 'US %' OR AliasSort1.LABEL LIKE 'I %' OR AliasSort1.LABEL LIKE 'K %'" )
        removeJoin(lyr)
        CalcField(lyr,"RID","!ROUTE_ID![:11]","PYTHON_9.3","#")
        Select(lyr, "REMOVE_FROM_SELECTION", "TRAVEL is null" )
        CalcField(lyr,"RID","!ROUTE_ID![:11]+!TRAVEL!","PYTHON_9.3","#")

    def ScratchCalcs():
        CalculateField_management("RoadCenterline","RoadCenterline.Soundex","""!RoadAlias.A_RD![0]  +  !RoadAlias.A_RD![1:].replace("S","").zfill(3)""","PYTHON_9.3","#")
        CalculateField_management(in_table="RoadCenterline",field="RoadCenterline.KDOTPreType",expression="!RoadAlias.A_RD![0]  ",expression_type="PYTHON_9.3",code_block="#")
        CalculateField_management(in_table="RoadCenterline",field="RoadCenterline.PreCode",expression="'0'",expression_type="PYTHON_9.3",code_block="#")
        CalculateField_management(in_table="RoadCenterline",field="RoadCenterline.KDOT_ADMO",expression="'S'",expression_type="PYTHON_9.3",code_block="#")

    addAdminFields(lyr)
    CalcAdminFields(lyr, Kdotdbfp)
    CountyCode(lyr)
    CityCodes(lyr, Kdotdbfp)
    RouteCalc(lyr)
    RoadinName(lyr)
    HighwayCalc(lyr,Kdotdbfp)
    #CalculateField_management(lyr, "RID", "str(!KDOT_COUNTY_R!)+str(!KDOT_COUNTY_L!)+str(!KDOT_CITY_R!)+str(!KDOT_CITY_L!)+str(!PreCode!) + !Soundex! + str(!SuffCode!)+!TRAVEL!+str(!UniqueNo!)","PYTHON_9.3","#")

def LRSIt():
    """makes the LRS route layer and dissolves the NG911 fields to LRS event tables"""
    MakeRouteLayer_na()
    pass

#ConflateKDOT(gdb, DOTRoads)
LRSRoutePrep(gdb, DOTRoads)
