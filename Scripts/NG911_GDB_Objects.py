#-------------------------------------------------------------------------------
# Name:        NG911_GDB_Objects
# Purpose:     Objects representing NG911 fields
#
# Author:      kristen
#
# Created:     April 13, 2016
#-------------------------------------------------------------------------------
# This is a class used represent the NG911 geodatabase
from os.path import join, basename
from NG911_arcpy_shortcuts import fieldExists
from arcpy import Exists

class NG911_RoadCenterline_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_SEGID, u_STATE_L, u_STATE_R, u_COUNTY_L, u_COUNTY_R, u_MUNI_L,
                    u_MUNI_R, u_L_F_ADD, u_L_T_ADD, u_R_F_ADD, u_R_T_ADD, u_PARITY_L, u_PARITY_R, u_POSTCO_L, u_POSTCO_R, u_ZIP_L, u_ZIP_R,
                    u_ESN_L, u_ESN_R, u_MSAGCO_L, u_MSAGCO_R, u_PRD, u_STP, u_RD, u_STS, u_POD, u_POM, u_SPDLIMIT, u_ONEWAY, u_RDCLASS,
                    u_UPDATEBY,  u_LABEL, u_ELEV_F, u_ELEV_T, u_ESN_C, u_SURFACE, u_STATUS, u_TRAVEL, u_LRSKEY, u_EXCEPTION, u_SUBMIT,
                    u_NOTES, u_UNINC_L, u_UNINC_R, u_KSSEGID):

        self.STEWARD = u_STEWARD
        self.L_UPDATE = u_L_UPDATE
        self.EFF_DATE = u_EFF_DATE
        self.EXP_DATE = u_EXP_DATE
        self.SEGID = u_SEGID
        self.UNIQUEID = self.SEGID
        self.STATE_L = u_STATE_L
        self.STATE_R = u_STATE_R
        self.COUNTY_L = u_COUNTY_L
        self.COUNTY_R = u_COUNTY_R
        self.MUNI_L = u_MUNI_L
        self.MUNI_R = u_MUNI_R
        self.L_F_ADD = u_L_F_ADD
        self.L_T_ADD = u_L_T_ADD
        self.R_F_ADD = u_R_F_ADD
        self.R_T_ADD = u_R_T_ADD
        self.PARITY_L = u_PARITY_L
        self.PARITY_R = u_PARITY_R
        self.POSTCO_L = u_POSTCO_L
        self.POSTCO_R = u_POSTCO_R
        self.ZIP_L = u_ZIP_L
        self.ZIP_R = u_ZIP_R
        self.ESN_L = u_ESN_L
        self.ESN_R = u_ESN_R
        self.MSAGCO_L = u_MSAGCO_L
        self.MSAGCO_R = u_MSAGCO_R
        self.PRD = u_PRD
        self.STP = u_STP
        self.RD = u_RD
        self.STS = u_STS
        self.POD = u_POD
        self.POM = u_POM
        self.SPDLIMIT = u_SPDLIMIT
        self.ONEWAY = u_ONEWAY
        self.RDCLASS = u_RDCLASS
        self.UPDATEBY = u_UPDATEBY
        self.LABEL = u_LABEL
        self.ELEV_F = u_ELEV_F
        self.ELEV_T = u_ELEV_T
        self.ESN_C = u_ESN_C
        self.SURFACE = u_SURFACE
        self.STATUS = u_STATUS
        self.TRAVEL = u_TRAVEL
        self.LRSKEY = u_LRSKEY
        self.EXCEPTION = u_EXCEPTION
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.UNINC_L = u_UNINC_L
        self.UNINC_R = u_UNINC_R
        self.KSSEGID = u_KSSEGID
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.STATE_L, self.STATE_R, self.COUNTY_L, self.COUNTY_R,
                                self.MUNI_L, self.MUNI_R, self.L_F_ADD, self.L_T_ADD, self.R_F_ADD, self.R_T_ADD, self.PARITY_L, self.PARITY_R,
                                self.MSAGCO_L, self.MSAGCO_R, self.RD, self.LABEL, self.UPDATEBY, self.STATUS, self.ELEV_F, self.ELEV_T, self.EXCEPTION]
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.STATE_L, self.STATE_R, self.COUNTY_L, self.COUNTY_R, self.MUNI_L,
                    self.MUNI_R, self.L_F_ADD, self.L_T_ADD, self.R_F_ADD, self.R_T_ADD, self.PARITY_L, self.PARITY_R, self.POSTCO_L, self.POSTCO_R, self.ZIP_L, self.ZIP_R,
                    self.ESN_L, self.ESN_R, self.MSAGCO_L, self.MSAGCO_R, self.PRD, self.STP, self.RD, self.STS, self.POD, self.POM, self.SPDLIMIT, self.ONEWAY, self.RDCLASS,
                    self.UPDATEBY,  self.LABEL, self.ELEV_F, self.ELEV_T, self.ESN_C, self.SURFACE, self.STATUS, self.TRAVEL, self.LRSKEY, self.EXCEPTION, self.SUBMIT,
                    self.NOTES, self.UNINC_L, self.UNINC_R]
        self.LABEL_FIELDS = [self.LABEL, self.PRD, self.STP, self.RD, self.STS, self.POD, self.POM]
        self.FIELDS_WITH_DOMAINS = [self.STEWARD, self.STATE_L, self.STATE_R, self.COUNTY_L, self.COUNTY_R, self.MUNI_L, self.MUNI_R, self.PARITY_L, self.PARITY_R,
                                self.POSTCO_L, self.POSTCO_R, self.ZIP_L, self.ZIP_R, self.PRD, self.STS, self.POD, self.ONEWAY, self.RDCLASS, self.SURFACE, self.STATUS,
                                self.EXCEPTION, self.SUBMIT]
        self.FREQUENCY_FIELDS = [self.STATE_L,self.STATE_R,self.COUNTY_L,self.COUNTY_R,self.MUNI_L,self.MUNI_R,self.L_F_ADD,self.L_T_ADD,self.R_F_ADD,self.R_T_ADD,
                                self.PARITY_L,self.PARITY_R,self.POSTCO_L,self.POSTCO_R,self.ZIP_L,self.ZIP_R,self.ESN_L,self.ESN_R,self.MSAGCO_L,self.MSAGCO_R,
                                self.PRD,self.STP,self.RD,self.STS,self.POD,self.POM,self.SPDLIMIT,self.ONEWAY,self.RDCLASS,self.LABEL,self.ELEV_F,self.ELEV_T,
                                self.ESN_C,self.SURFACE,self.STATUS,self.TRAVEL,self.LRSKEY]
        self.FREQUENCY_FIELDS_STRING = ";".join(self.FREQUENCY_FIELDS)

def getDefaultNG911RoadCenterlineObject():

    NG911_RoadCenterline_Default = NG911_RoadCenterline_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "SEGID", "STATE_L", "STATE_R", "COUNTY_L", "COUNTY_R", "MUNI_L",
                    "MUNI_R", "L_F_ADD", "L_T_ADD", "R_F_ADD", "R_T_ADD", "PARITY_L", "PARITY_R", "POSTCO_L", "POSTCO_R", "ZIP_L", "ZIP_R",
                    "ESN_L", "ESN_R", "MSAGCO_L", "MSAGCO_R", "PRD", "STP", "RD", "STS", "POD", "POM", "SPDLIMIT", "ONEWAY", "RDCLASS",
                    "UPDATEBY", "LABEL", "ELEV_F", "ELEV_T", "ESN_C", "SURFACE", "STATUS", "TRAVEL", "LRSKEY", "EXCEPTION", "SUBMIT",
                    "NOTES", "UNINC_L", "UNINC_R", "KSSEGID")

    return NG911_RoadCenterline_Default

def getDefault20NG911RoadCenterlineObject():

    NG911_RoadCenterline_Default = NG911_RoadCenterline_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGSEGID", "STATE_L", "STATE_R", "COUNTY_L", "COUNTY_R", "MUNI_L",
                    "MUNI_R", "L_F_ADD", "L_T_ADD", "R_F_ADD", "R_T_ADD", "PARITY_L", "PARITY_R", "POSTCO_L", "POSTCO_R", "ZIP_L", "ZIP_R",
                    "ESN_L", "ESN_R", "MSAGCO_L", "MSAGCO_R", "PRD", "STP", "RD", "STS", "POD", "POM", "SPDLIMIT", "ONEWAY", "RDCLASS",
                    "UPDATEBY", "LABEL", "ELEV_F", "ELEV_T", "", "SURFACE", "STATUS", "TRAVEL", "LRSKEY", "EXCEPTION", "SUBMIT",
                    "NOTES", "UNINC_L", "UNINC_R", "KSSEGID")

    return NG911_RoadCenterline_Default

class NG911_RoadAlias_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_ALIASID, u_SEGID, u_A_PRD, u_A_STP, u_A_RD, u_A_STS, u_A_POD, u_A_POM, u_A_L_FROM, u_A_L_TO,
                    u_A_R_FROM, u_A_R_TO, u_LABEL, u_UPDATEBY, u_SUBMIT, u_NOTES, u_KSSEGID):

        self.STEWARD = u_STEWARD
        self.L_UPDATE = u_L_UPDATE
        self.EFF_DATE = u_EFF_DATE
        self.EXP_DATE = u_EXP_DATE
        self.ALIASID = u_ALIASID
        self.SEGID = u_SEGID
        self.UNIQUEID = self.ALIASID
        self.A_PRD = u_A_PRD
        self.A_STP = u_A_STP
        self.A_RD = u_A_RD
        self.A_STS = u_A_STS
        self.A_POD = u_A_POD
        self.A_POM = u_A_POM
        self.A_L_FROM = u_A_L_FROM
        self.A_L_TO = u_A_L_TO
        self.A_R_FROM = u_A_R_FROM
        self.A_R_TO = u_A_R_TO
        self.LABEL = u_LABEL
        self.UPDATEBY = u_UPDATEBY
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.KSSEGID = u_KSSEGID
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.SEGID, self.LABEL, self.UPDATEBY]
        self.FIELDS_WITH_DOMAINS = [self.STEWARD, self.A_PRD, self.A_STS, self.A_POD, self.SUBMIT]
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.SEGID, self.A_PRD,
                            self.A_STP, self.A_RD, self.A_STS, self.A_POD, self.A_POM, self.A_L_FROM, self.A_L_TO,
                            self.A_R_FROM, self.A_R_TO, self.LABEL, self.UPDATEBY, self.SUBMIT, self.NOTES]


def getDefaultNG911RoadAliasObject():

    NG911_RoadAlias_Default = NG911_RoadAlias_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "ALIASID", "SEGID", "A_PRD", "A_STP", "A_RD", "A_STS", "A_POD",
                    "A_POM", "A_L_FROM", "A_L_TO", "A_R_FROM", "A_R_TO", "LABEL", "UPDATEBY", "SUBMIT", "NOTES", "KSSEGID")

    return NG911_RoadAlias_Default

def getDefault20NG911RoadAliasObject():

    NG911_RoadAlias_Default = NG911_RoadAlias_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGALIASID", "NGSEGID", "A_PRD", "A_STP", "A_RD", "A_STS", "A_POD",
                    "A_POM", "A_L_FROM", "A_L_TO", "A_R_FROM", "A_R_TO", "LABEL", "UPDATEBY", "SUBMIT", "NOTES", "KSSEGID")

    return NG911_RoadAlias_Default

class NG911_Adddress_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_ADDID, u_STATE, u_COUNTY, u_MUNI, u_HNO, u_HNS, u_PRD, u_STP,
                    u_RD, u_STS, u_POD, u_POM, u_ESN, u_MSAGCO, u_POSTCO, u_ZIP, u_ZIP4, u_BLD, u_FLR, u_UNIT, u_ROOM, u_SEAT, u_LMK,
                    u_LOC, u_PLC, u_LONG, u_LAT, u_ELEV, u_LABEL, u_UPDATEBY, u_LOCTYPE, u_USNGRID, u_KSPID, u_MILEPOST, u_ADDURI,
                    u_UNINC, u_SUBMIT, u_NOTES, u_PRM):

        self.STEWARD = u_STEWARD
        self.L_UPDATE = u_L_UPDATE
        self.EFF_DATE = u_EFF_DATE
        self.EXP_DATE = u_EXP_DATE
        self.ADDID = u_ADDID
        self.UNIQUEID = self.ADDID
        self.STATE = u_STATE
        self.COUNTY = u_COUNTY
        self.MUNI = u_MUNI
        self.HNO = u_HNO
        self.HNS = u_HNS
        self.PRD = u_PRD
        self.STP = u_STP
        self.RD = u_RD
        self.STS = u_STS
        self.POD = u_POD
        self.POM = u_POM
        self.ESN = u_ESN
        self.MSAGCO = u_MSAGCO
        self.POSTCO = u_POSTCO
        self.ZIP = u_ZIP
        self.ZIP4 = u_ZIP4
        self.BLD = u_BLD
        self.FLR = u_FLR
        self.UNIT = u_UNIT
        self.ROOM = u_ROOM
        self.SEAT = u_SEAT
        self.LMK = u_LMK
        self.LOC = u_LOC
        self.PLC = u_PLC
        self.LONG = u_LONG
        self.X = self.LONG
        self.LAT = u_LAT
        self.Y = self.LAT
        self.ELEV = u_ELEV
        self.LABEL = u_LABEL
        self.UPDATEBY = u_UPDATEBY
        self.LOCTYPE = u_LOCTYPE
        self.USNGRID = u_USNGRID
        self.KSPID = u_KSPID
        self.MILEPOST = u_MILEPOST
        self.ADDURI = u_ADDURI
        self.UNINC = u_UNINC
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.PRM = u_PRM
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.STATE, self.COUNTY, self.MUNI, self.HNO,
                                self.RD, self.MSAGCO, self.LABEL, self.UPDATEBY, self.LOCTYPE]
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.STATE, self.COUNTY, self.MUNI, self.HNO, self.HNS, self.PRD, self.STP,
                    self.RD, self.STS, self.POD, self.POM, self.ESN, self.MSAGCO, self.POSTCO, self.ZIP, self.ZIP4, self.BLD, self.FLR, self.UNIT, self.ROOM, self.SEAT, self.LMK,
                    self.LOC, self.PLC, self.LONG, self.LAT, self.ELEV, self.LABEL, self.UPDATEBY, self.LOCTYPE, self.USNGRID, self.KSPID, self.MILEPOST, self.ADDURI,
                    self.UNINC, self.SUBMIT, self.NOTES]
        self.LABEL_FIELDS = [self.LABEL, self.HNO, self.HNS, self.PRD, self.STP, self.RD, self.STS, self.POD, self.POM, self.BLD, self.FLR, self.UNIT, self.ROOM, self.SEAT]
        self.FIELDS_WITH_DOMAINS = [self.STEWARD, self.STATE, self.COUNTY, self.MUNI, self.PRD, self.STS, self.POD, self.POSTCO, self.ZIP,
                                    self.PLC, self.LOCTYPE, self.SUBMIT]
        self.FREQUENCY_FIELDS = [self.MUNI,self.HNO,self.HNS,self.PRD,self.STP,self.RD,self.STS,self.POD,self.POM,self.ZIP,self.BLD,self.FLR,self.UNIT,self.ROOM,
                                    self.SEAT,self.LOC,self.LOCTYPE,self.MSAGCO]
        self.FREQUENCY_FIELDS_STRING = ";".join(self.FREQUENCY_FIELDS)
        self.GEOCODE_LABEL_FIELDS = [self.HNO, self.PRD, self.STP, self.RD, self.STS, self.POD, self.POM]

def getDefaultNG911AddressObject():

    NG911_Address_Default = NG911_Adddress_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "ADDID", "STATE", "COUNTY", "MUNI", "HNO", "HNS", "PRD", "STP",
                    "RD", "STS", "POD", "POM", "ESN", "MSAGCO", "POSTCO", "ZIP", "ZIP4", "BLD", "FLR", "UNIT", "ROOM", "SEAT", "LMK",
                    "LOC", "PLC", "LONG", "LAT", "ELEV", "LABEL", "UPDATEBY", "LOCTYPE", "USNGRID", "KSPID", "MILEPOST", "ADDURI",
                    "UNINC", "SUBMIT", "NOTES", "")

    return NG911_Address_Default

def getDefault20NG911AddressObject():

    NG911_Address_Default = NG911_Adddress_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGADDID", "STATE", "COUNTY", "MUNI", "HNO", "HNS", "PRD", "STP",
                    "RD", "STS", "POD", "POM", "ESN", "MSAGCO", "POSTCO", "ZIP", "ZIP4", "BLD", "FLR", "UNIT", "ROOM", "SEAT", "LMK",
                    "LOC", "PLC", "LONG", "LAT", "ELEV", "LABEL", "UPDATEBY", "LOCTYPE", "USNGRID", "KSPID", "MILEPOST", "ADDURI",
                    "UNINC", "SUBMIT", "NOTES", "PRM")

    return NG911_Address_Default

class NG911_GeocodeExceptions_Object(object):

    def __init__(self, u_ADDID, u_LABEL, u_NOTES):

        self.ADDID = u_ADDID
        self.UNIQUEID = u_ADDID
        self.LABEL = u_LABEL
        self.NOTES = u_NOTES


def getDefaultNG911GeocodeExceptionsObject():

    NG911_GeocodeExceptions_Default = NG911_GeocodeExceptions_Object("ADDID", "LABEL", "NOTES")

    return NG911_GeocodeExceptions_Default

def getDefaul20NG911GeocodeExceptionsObject():

    NG911_GeocodeExceptions_Default = NG911_GeocodeExceptions_Object("NGADDID", "LABEL", "NOTES")

    return NG911_GeocodeExceptions_Default

class NG911_FieldValuesCheckResults_Object(object):

    def __init__(self, u_DATEFLAGGED, u_DESCRIPTION, u_LAYER, u_FIELD, u_FEATUREID):

        self.DATEFLAGGED = u_DATEFLAGGED
        self.DESCRIPTION = u_DESCRIPTION
        self.LAYER = u_LAYER
        self.FIELD = u_FIELD
        self.FEATUREID = u_FEATUREID


def getDefaultNG911FieldValuesCheckResultsObject():

    NG911_FieldValuesCheckResults_Default = NG911_FieldValuesCheckResults_Object("DATEFLAGGED", "DESCRIPTION", "LAYER", "FIELD", "FEATUREID")

    return NG911_FieldValuesCheckResults_Default

class NG911_TemplateCheckResults_Object(object):

    def __init__(self, u_DATEFLAGGED, u_DESCRIPTION, u_CATEGORY):

        self.DATEFLAGGED = u_DATEFLAGGED
        self.DESCRIPTION = u_DESCRIPTION
        self.CATEGORY = u_CATEGORY


def getDefaultNG911TemplateCheckResultsObject():

    NG911_TemplateCheckResults_Default = NG911_TemplateCheckResults_Object("DATEFLAGGED", "DESCRIPTION", "CATEGORY")

    return NG911_TemplateCheckResults_Default

class NG911_ESB_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_ESBID, u_STATE, u_AGENCYID, u_SERV_NUM, u_DISPLAY, u_ESB_TYPE, u_LAW,
                u_FIRE, u_EMS, u_UPDATEBY, u_PSAP, u_SUBMIT, u_NOTES):

        self.STEWARD = u_STEWARD
        self.L_UPDATE = u_L_UPDATE
        self.EFF_DATE = u_EFF_DATE
        self.EXP_DATE = u_EXP_DATE
        self.ESBID = u_ESBID
        self.UNIQUEID = self.ESBID
        self.STATE = u_STATE
        self.AGENCYID = u_AGENCYID
        self.SERV_NUM = u_SERV_NUM
        self.DISPLAY = u_DISPLAY
        self.ESB_TYPE = u_ESB_TYPE
        self.LAW = u_LAW
        self.FIRE = u_FIRE
        self.EMS = u_EMS
        self.UPDATEBY = u_UPDATEBY
        self.PSAP = u_PSAP
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.STATE, self.AGENCYID, self.DISPLAY, self.ESB_TYPE, self.UPDATEBY]
        self.FIELDS_WITH_DOMAINS = [self.STEWARD, self.STATE, self.AGENCYID, self.SUBMIT]
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.STATE, self.AGENCYID,
                            self.SERV_NUM, self.DISPLAY, self.ESB_TYPE, self.LAW, self.FIRE, self.EMS, self.UPDATEBY, self.PSAP,
                            self.SUBMIT, self.NOTES]


def getDefaultNG911ESBObject():

    NG911_ESB_Default = NG911_ESB_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "ESBID", "STATE", "AGENCYID", "SERV_NUM", "DISPLAY", "ESB_TYPE",
                    "LAW", "FIRE", "EMS", "UPDATEBY", "PSAP", "SUBMIT", "NOTES")

    return NG911_ESB_Default

def getDefault20NG911ESBObject():

    NG911_ESB_Default = NG911_ESB_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGESBID", "STATE", "AGENCYID", "SERV_NUM", "DISPLAY", "ESB_TYPE",
                    "LAW", "FIRE", "EMS", "UPDATEBY", "PSAP", "SUBMIT", "NOTES")

    return NG911_ESB_Default

class NG911_ESZ_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_ESZID, u_STATE, u_AGENCYID, u_ESN, u_UPDATEBY, u_SUBMIT, u_NOTES):

        self.STEWARD = u_STEWARD
        self.L_UPDATE = u_L_UPDATE
        self.EFF_DATE = u_EFF_DATE
        self.EXP_DATE = u_EXP_DATE
        self.ESZID = u_ESZID
        self.UNIQUEID = self.ESZID
        self.STATE = u_STATE
        self.AGENCYID = u_AGENCYID
        self.ESN = u_ESN
        self.UPDATEBY = u_UPDATEBY
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.AGENCYID, self.ESN, self.UPDATEBY]
        self.FIELDS_WITH_DOMAINS = [self.STEWARD, self.AGENCYID, self.SUBMIT]
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.AGENCYID,
                            self.ESN, self.UPDATEBY, self.SUBMIT, self.NOTES]


def getDefaultNG911ESZObject():

    NG911_ESZ_Default = NG911_ESZ_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "ESZID", "STATE", "AGENCYID", "ESN", "UPDATEBY", "SUBMIT", "NOTES")

    return NG911_ESZ_Default

def getDefault20NG911ESZObject():

    NG911_ESZ_Default = NG911_ESZ_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGESZID", "STATE", "AGENCYID", "ESN", "UPDATEBY", "SUBMIT", "NOTES")

    return NG911_ESZ_Default

class NG911_CountyBoundary_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_COUNTYID, u_STATE, u_COUNTY, u_UPDATEBY, u_SUBMIT, u_NOTES):

        self.STEWARD = u_STEWARD
        self.L_UPDATE = u_L_UPDATE
        self.COUNTYID = u_COUNTYID
        self.UNIQUEID = self.COUNTYID
        self.STATE = u_STATE
        self.COUNTY = u_COUNTY
        self.UPDATEBY = u_UPDATEBY
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.UNIQUEID, self.STATE, self.COUNTY, self.UPDATEBY]
        self.FIELDS_WITH_DOMAINS = [self.STEWARD, self.STATE, self.COUNTY]
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.UNIQUEID, self.STATE, self.COUNTY, self.UPDATEBY, self.SUBMIT, self.NOTES]


def getDefaultNG911CountyBoundaryObject():

    NG911_CountyBoundary_Default = NG911_CountyBoundary_Object("STEWARD", "L_UPDATE", "COUNTYID", "STATE", "COUNTY", "UPDATEBY", "SUBMIT", "NOTES")

    return NG911_CountyBoundary_Default

def getDefault20NG911CountyBoundaryObject():

    NG911_CountyBoundary_Default = NG911_CountyBoundary_Object("STEWARD", "L_UPDATE", "NGCOUNTYID", "STATE", "COUNTY", "UPDATEBY", "SUBMIT", "NOTES")

    return NG911_CountyBoundary_Default

class NG911_AuthoritativeBoundary_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_ABID, u_STATE, u_AGENCYID, u_DISPLAY, u_UPDATEBY, u_SUBMIT, u_NOTES):

        self.STEWARD = u_STEWARD
        self.L_UPDATE = u_L_UPDATE
        self.EFF_DATE = u_EFF_DATE
        self.EXP_DATE = u_EXP_DATE
        self.ABID = u_ABID
        self.UNIQUEID = self.ABID
        self.STATE = u_STATE
        self.AGENCYID = u_AGENCYID
        self.DISPLAY = u_DISPLAY
        self.UPDATEBY = u_UPDATEBY
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.AGENCYID, self.DISPLAY, self.UPDATEBY]
        self.FIELDS_WITH_DOMAINS = [self.STEWARD, self.AGENCYID, self.SUBMIT]
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.AGENCYID, self.DISPLAY,
                            self.UPDATEBY, self.SUBMIT, self.NOTES]


def getDefaultNG911AuthoritativeBoundaryObject():

    NG911_AuthoritativeBoundary_Default = NG911_AuthoritativeBoundary_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "ABID", "STATE", "AGENCYID",
                        "DISPLAY", "UPDATEBY", "SUBMIT", "NOTES")

    return NG911_AuthoritativeBoundary_Default

def getDefault20NG911AuthoritativeBoundaryObject():

    NG911_AuthoritativeBoundary_Default = NG911_AuthoritativeBoundary_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGABID", "STATE", "AGENCYID",
                        "DISPLAY", "UPDATEBY", "SUBMIT", "NOTES")

    return NG911_AuthoritativeBoundary_Default


class NG911_MunicipalBoundary_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_MUNI_ID, u_STATE, u_COUNTY, u_MUNI, u_UPDATEBY, u_SUBMIT, u_NOTES):

        self.STEWARD = u_STEWARD
        self.L_UPDATE = u_L_UPDATE
        self.EFF_DATE = u_EFF_DATE
        self.EXP_DATE = u_EXP_DATE
        self.MUNI_ID = u_MUNI_ID
        self.UNIQUEID = self.MUNI_ID
        self.STATE = u_STATE
        self.COUNTY = u_COUNTY
        self.MUNI = u_MUNI
        self.UPDATEBY = u_UPDATEBY
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.STATE, self.COUNTY, self.MUNI, self.UPDATEBY]
        self.FIELDS_WITH_DOMAINS = [self.STEWARD, self.STATE, self.COUNTY, self.MUNI, self.SUBMIT]
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.STATE, self.COUNTY, self.MUNI,
                            self.UPDATEBY, self.SUBMIT, self.NOTES]


def getDefaultNG911MunicipalBoundaryObject():

    NG911_MunicipalBoundary_Default = NG911_MunicipalBoundary_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "MUNI_ID", "STATE", "COUNTY", "MUNI",
                        "UPDATEBY", "SUBMIT", "NOTES")

    return NG911_MunicipalBoundary_Default

def getDefault20NG911MunicipalBoundaryObject():

    NG911_MunicipalBoundary_Default = NG911_MunicipalBoundary_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGMUNI_ID", "STATE", "COUNTY", "MUNI",
                        "UPDATEBY", "SUBMIT", "NOTES")

    return NG911_MunicipalBoundary_Default

class NG911_Hydrant_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_HYDID, u_HYDTYPE, u_PROVIDER, u_STATUS, u_PRIVATE, u_UPDATEBY, u_SUBMIT, u_NOTES):

        self.STEWARD = u_STEWARD
        self.L_UPDATE = u_L_UPDATE
        self.EFF_DATE = u_EFF_DATE
        self.EXP_DATE = u_EXP_DATE
        self.NGHYDID = u_HYDID
        self.UNIQUEID = self.NGHYDID
        self.HYDTYPE = u_HYDTYPE
        self.PROVIDER = u_PROVIDER
        self.STATUS = u_STATUS
        self.UPDATEBY = u_UPDATEBY
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.PRIVATE = u_PRIVATE
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.HYDTYPE, self.STATUS, self.PRIVATE, self.UPDATEBY]
        self.FIELDS_WITH_DOMAINS = [self.STEWARD, self.SUBMIT, self.HYDTYPE, self.STATUS, self.PRIVATE]
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.HYDTYPE, self.PROVIDER, self.STATUS,
                            self.UPDATEBY, self.SUBMIT, self.NOTES, self.PRIVATE]


def getDefault20NG911HydrantObject():

    NG911_Hydrant_Default = NG911_Hydrant_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGHYDID", "HYDTYPE", "PROVIDER", "STATUS",
                        "PRIVATE", "UPDATEBY", "SUBMIT", "NOTES")

    return NG911_Hydrant_Default

class NG911_Parcel_Object(object):

    def __init__(self, u_STEWARD, u_KSPID, u_SUBMIT, u_NOTES):

        self.STEWARD = u_STEWARD
        self.NGKSPID = u_KSPID
        self.UNIQUEID = self.NGKSPID
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.REQUIRED_FIELDS = [self.STEWARD, self.UNIQUEID]
        self.FIELDS_WITH_DOMAINS = [self.STEWARD, self.SUBMIT]
        self.FIELD_MAP = [self.STEWARD, self.UNIQUEID, self.SUBMIT, self.NOTES]


def getDefault20NG911ParcelObject():

    NG911_Parcel_Default = NG911_Parcel_Object("STEWARD", "NGKSPID", "SUBMIT", "NOTES")

    return NG911_Parcel_Default

class NG911_Gate_Object(object):

    def __init__(self, u_STEWARD, u_NGGATEID, u_GATE_TYPE, u_SIREN, u_RF_OP, u_KNOXBOX, u_KEYPAD,
                    u_MAN_OPEN, u_GATEOPEN, u_G_OWNER, u_SUBMIT, u_NOTES):

        self.STEWARD = u_STEWARD
        self.NGGATEID = u_NGGATEID
        self.UNIQUEID = self.NGGATEID
        self.GATE_TYPE = u_GATE_TYPE
        self.SIREN = u_SIREN
        self.RF_OP = u_RF_OP
        self.KNOXBOX = u_KNOXBOX
        self.KEYPAD = u_KEYPAD
        self.MAN_OPEN = u_MAN_OPEN
        self.GATEOPEN = u_GATEOPEN
        self.G_OWNER = u_G_OWNER
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.REQUIRED_FIELDS = [self.STEWARD, self.UNIQUEID, self.GATE_TYPE, self.SIREN, self.RF_OP, self.KNOXBOX, self.KEYPAD, self.MAN_OPEN, self.GATEOPEN]
        self.FIELDS_WITH_DOMAINS = [self.STEWARD, self.SUBMIT, self.GATE_TYPE, self.SIREN, self.RF_OP, self.KNOXBOX, self.KEYPAD, self.KEYPAD, self.MAN_OPEN, self.GATEOPEN]
        self.FIELD_MAP = [self.STEWARD, self.UNIQUEID, self.GATE_TYPE, self.SIREN, self.RF_OP, self.KNOXBOX, self.KEYPAD, self.MAN_OPEN,
                            self.GATEOPEN, self.G_OWNER, self.SUBMIT, self.NOTES]


def getDefault20NG911GateObject():

    NG911_Gate_Default = NG911_Gate_Object("STEWARD", "NGGATEID", "GATE_TYPE", "SIREN", "RF_OP", "KNOXBOX", "KEYPAD",
                    "MAN_OPEN", "GATEOPEN", "G_OWNER", "SUBMIT", "NOTES")

    return NG911_Gate_Default

class NG911_CellSector_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_NGCELLID, u_STATE, u_COUNTY, u_SITEID, u_SECTORID, u_SWITCHID,
                u_C_SITEID, u_ESRD, u_LASTESRK, u_SECORN, u_TECH, u_UPDATEBY, u_SUBMIT, u_NOTES):

        self.STEWARD = u_STEWARD
        self.L_UPDATE = u_L_UPDATE
        self.EFF_DATE = u_EFF_DATE
        self.EXP_DATE = u_EXP_DATE
        self.NGCELLID = u_NGCELLID
        self.UNIQUEID = self.NGCELLID
        self.STATE = u_STATE
        self.COUNTY = u_COUNTY
        self.SITEID = u_SITEID
        self.SECTORID = u_SECTORID
        self.SWITCHID = u_SWITCHID
        self.C_SITEID = u_C_SITEID
        self.ESRD = u_ESRD
        self.LASTESRK = u_LASTESRK
        self.SECORN = u_SECORN
        self.TECH = u_TECH
        self.UPDATEBY = u_UPDATEBY
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.STATE, self.COUNTY, self.SECTORID,
                            self.SECORN, self.UPDATEBY]
        self.FIELDS_WITH_DOMAINS = [self.STATE, self.COUNTY, self.SUBMIT, self.STEWARD]
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.STATE, self.COUNTY, self.SITEID,
                            self.SECTORID, self.SWITCHID, self.C_SITEID, self.ESRD, self.LASTESRK, self.SECORN, self.TECH,
                             self.UPDATEBY, self.SUBMIT, self.NOTES]


def getDefault20NG911CellSectorObject():

    NG911_CellSector_Default = NG911_CellSector_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGCELLID", "STATE", "COUNT", "SITEID",
                        "SECTORID", "SWITCHID", "C_SITEID", "ESRD", "LASTESRK", "SECORN", "TECH", "UPDATEBY", "SUBMIT", "NOTES")

    return NG911_CellSector_Default

class TN_Object(object):

    def __init__(self, u_LocatorFolder, u_AddressLocator, u_RoadLocator, u_CompositeLocator, u_TN_List, u_ResultsFC, u_ResultsTable, u_UNIQUEID,
            u_defaultFullAddress, u_tn_gdb):

        self.LocatorFolder = u_LocatorFolder
        self.AddressLocator = u_AddressLocator
        self.RoadLocator = u_RoadLocator
        self.CompositeLocator = u_CompositeLocator
        self.TN_List = u_TN_List
        self.ResultsFC = u_ResultsFC
        self.ResultsTable = u_ResultsTable
        self.UNIQUEID = u_UNIQUEID
        self.DefaultFullAddress = u_defaultFullAddress
        self.tn_gdb = u_tn_gdb


def getTNObject(gdb):
    from os.path import join,dirname,basename
    from time import strftime

    LocatorFolder = join(dirname(gdb), basename(gdb).replace(".gdb","") + "_TN")
    today = strftime('%Y%m%d')
    tn_gdb = join(LocatorFolder, "TN_Working.gdb")
    tname = join(tn_gdb, "TN_List_" + today)
    output_fc = join(tn_gdb, "TN_GC_Output_" + today)
    resultsTable = join(tn_gdb, "TN_Geocode_Results_" + today)


    NG911_TN_Default = TN_Object(LocatorFolder, join(LocatorFolder, "AddressLocator"), join(LocatorFolder, "RoadLocator"),
                                join(LocatorFolder, "CompositeLoc"), tname, output_fc, resultsTable, "NGTNID", "SingleLineInput",
                                tn_gdb)

    return NG911_TN_Default


class NG911_Session_obj(object):
    def __init__(self, gdb, folder, gdbObject, a_obj, rc_obj, esb_obj, ab_obj, ra_obj, cb_obj, mb_obj, esz_obj, psap_obj,
                fvcr_obj, tcr_obj, cell_obj, parc_obj, gate_obj, hyd_obj, layer_obj_dict):
        self.gdbPath = gdb
        self.domainsFolderPath = folder
        self.gdbObject = gdbObject #contains fcList & esbList
        self.a_obj = a_obj
        self.rc_obj = rc_obj
        self.esb_obj = esb_obj
        self.ab_obj = ab_obj
        self.ra_obj = ra_obj
        self.cb_obj = cb_obj
        self.mb_obj = mb_obj
        self.esz_obj = esz_obj
        self.psap_obj = psap_obj
        self.fvcr_obj = fvcr_obj
        self.tcr_obj = tcr_obj
        self.cell_obj = cell_obj
        self.parc_obj = parc_obj
        self.gate_obj = gate_obj
        self.hyd_obj = hyd_obj
        self.layer_obj_dict = layer_obj_dict
        self.checkList = ""

def getProjectionFile():
    prj = r"\\vesta\d$\NG911_Pilot_Agg\KDOT_Lambert.prj"
    return prj

def NG911_Session(gdb):
    from arcpy import Exists
    from NG911_arcpy_shortcuts import fieldExists
    from os.path import dirname, join, realpath

    folder = join(dirname(dirname(realpath(__file__))), "Domains")

    #get geodatabase object set up
    gdbObject = getGDBObject(gdb)

    #set feature class list
    fcList = gdbObject.fcList
    #set esb list
    esbList = gdbObject.esbList

    #make sure feature class list only contains the layers that exist
    for fc in fcList:
        if not Exists(fc):
            fcList.remove(fc)

    #remove any esb entries that don't exist
    for esb in esbList:
        if not Exists(esb):
            esbList.remove(esb)
        else:
            #add esb's to the feature class list
            fcList.append(esb)

    #reset the gdbObject's fcList & esbList since now both show the layers that really exist
    gdbObject.fcList = fcList
    gdbObject.esbList = esbList

    addressPoints = gdbObject.AddressPoints

    if addressPoints in fcList:
        a_obj = getFCObject(addressPoints)
    else:
        a_obj = ""
    if gdbObject.RoadCenterline in fcList:
        rc_obj = getFCObject(gdbObject.RoadCenterline)
    else:
        rc_obj = ""
    if gdbObject.ESB in fcList:
        esb_obj = getFCObject(gdbObject.ESB)
    elif gdbObject.EMS in fcList:
        esb_obj = getFCObject(gdbObject.EMS)
    else:
        esb_obj = ''
    if gdbObject.ESZ in fcList:
        esz_obj = getFCObject(gdbObject.ESZ)
    else:
        esz_obj = ''
    if gdbObject.AuthoritativeBoundary in fcList:
        ab_obj = getFCObject(gdbObject.AuthoritativeBoundary)
    else:
        ab_obj = ""
    if gdbObject.RoadAlias in fcList:
        ra_obj = getFCObject(gdbObject.RoadAlias)
    else:
        ra_obj = ""
    if gdbObject.CountyBoundary in fcList:
        cb_obj = getFCObject(gdbObject.CountyBoundary)
    else:
        cb_obj = ""
    if gdbObject.MunicipalBoundary in fcList:
        mb_obj = getFCObject(gdbObject.MunicipalBoundary)
    else:
        mb_obj = ""

    psap_obj = esb_obj
    tcr_obj = getDefaultNG911TemplateCheckResultsObject()
    fvcr_obj = getDefaultNG911FieldValuesCheckResultsObject()

    if gdbObject.CELL_SECTOR != "" and gdbObject.CELL_SECTOR in fcList:
        cell_obj = getFCObject(gdbObject.CELL_SECTOR)
    else:
        cell_obj = ""

    if gdbObject.PARCELS != "" and gdbObject.PARCELS in fcList:
        parc_obj = getFCObject(gdbObject.PARCELS)
    else:
        parc_obj = ""

    if gdbObject.GATES != "" and gdbObject.GATES in fcList:
        gate_obj = getFCObject(gdbObject.GATES)
    else:
        gate_obj = ""

    if gdbObject.HYDRANTS != "" and gdbObject.HYDRANTS in fcList:
        hyd_obj = getFCObject(gdbObject.HYDRANTS)
    else:
        hyd_obj = ""

    layer_obj_dict = {"ADDRESSPOINTS": a_obj, "ROADCENTERLINE": rc_obj, "ESB": esb_obj, "AUTHORITATIVEBOUNDARY": ab_obj,
                    "ROADALIAS": ra_obj, "COUNTYBOUNDARY": cb_obj, "MUNICIPALBOUNDARY":mb_obj, "ESZ": esz_obj,
                    "PSAP": esb_obj, "FieldValuesCheckResults":fvcr_obj, "TemplateCheckResults":tcr_obj,
                    "CELL_SITES": cell_obj, "PARCELS": parc_obj, "GATES": gate_obj, "HYDRANTS": hyd_obj}

    NG911_obj = NG911_Session_obj(gdb, folder, gdbObject, a_obj, rc_obj, esb_obj, ab_obj, ra_obj, cb_obj, mb_obj, esz_obj, psap_obj,
                fvcr_obj, tcr_obj, cell_obj, parc_obj, gate_obj, hyd_obj, layer_obj_dict)

    return NG911_obj


def getGDBObject(gdb):
    addyPtTest = join(gdb, "NG911", "AddressPoints")

    if fieldExists(addyPtTest, "NGADDID"):
        gdbObject = get20GDBObject(gdb)
    else:
        gdbObject = get11GDBObject(gdb)

    return gdbObject

def get11GDBObject(gdb):
    from NG911_arcpy_shortcuts import fieldExists
    from arcpy import ListFeatureClasses, env

    #determine (hopefully) which layers are the esb layers
    fds = join(gdb, "NG911")
    env.workspace = fds
    fcs = ListFeatureClasses()
    ems, law, fire, psap, esb = "", "", "", "", ""
    for f in fcs:
        f = f.upper()
        if "EMS" in f:
            ems = join(fds, f)
        if "LAW" in f:
            law = join(fds, f)
        if "FIRE" in f:
            fire = join(fds, f)
        if "PSAP" in f:
            psap = join(fds, f)
        if "ESB" in f and "EMS" not in f and "LAW" not in f and "FIRE" not in f:
            esb = join(fds, f)

    esbList = []
    for e in [ems, law, fire, psap, esb]:
        if Exists(e):
            if e not in esbList:
                esbList.append(e)

    prj = getProjectionFile()

    # This is a class used represent the NG911 geodatabase
    class NG911_GDB_Object():
        def __init__(self):
            self.gdbPath = gdb
            self.ProjectionFile = prj
            self.NG911_FeatureDataset = join(gdb, "NG911")
            self.AddressPoints = join(self.NG911_FeatureDataset, "AddressPoints")
            self.RoadCenterline = join(self.NG911_FeatureDataset, "RoadCenterline")
            self.RoadAlias = join(gdb, "RoadAlias")
            self.AuthoritativeBoundary = join(self.NG911_FeatureDataset, "AuthoritativeBoundary")
            self.MunicipalBoundary = join(self.NG911_FeatureDataset, "MunicipalBoundary")
            self.CountyBoundary = join(self.NG911_FeatureDataset, "CountyBoundary")
            self.ESZ = join(self.NG911_FeatureDataset, "ESZ")
            self.PSAP = psap
            self.EMS = ems
            self.LAW = law
            self.FIRE = fire
            self.ESB = esb
            self.Topology = join(self.NG911_FeatureDataset, "NG911_Topology")
            self.Locator = join(gdb, "Locator")
            self.gc_test = join(gdb, "gc_test")
            self.GeocodeTable = join(gdb, "GeocodeTable")
            self.GeocodeExceptions = join(gdb, "GeocodeExceptions")
            self.AddressPointFrequency = join(gdb, "AP_Freq")
            self.RoadCenterlineFrequency = join(gdb, "Road_Freq")
            self.FieldValuesCheckResults = join(gdb, "FieldValuesCheckResults")
            self.TemplateCheckResults = join(gdb, "TemplateCheckResults")
            self.HYDRANTS = join(gdb, "HYDRANTS")
            self.PARCELS = join(gdb, "PARCELS")
            self.GATES = join(gdb, "GATES")
            self.CELL_SECTOR = join(gdb, "Cell_Sector")
            self.AdminBoundaryList = [self.AuthoritativeBoundary, self.CountyBoundary, self.MunicipalBoundary,
                                    self.ESZ, self.PSAP]
            self.fcList = [self.AddressPoints, self.RoadCenterline, self.RoadAlias, self.AuthoritativeBoundary, self.MunicipalBoundary,
                        self.CountyBoundary, self.ESZ, self.PSAP, self.HYDRANTS, self.PARCELS, self.GATES, self.CELL_SECTOR]
            self.esbList = esbList
            self.otherLayers = [self.HYDRANTS, self.PARCELS, self.GATES, self.CELL_SECTOR]
            self.requiredLayers = [self.RoadAlias, self.AddressPoints, self.RoadCenterline, self.AuthoritativeBoundary, self.ESZ] + esbList
            self.fcDict = {"AuthoritativeBoundary": self.AuthoritativeBoundary, "MunicipalBoundary": self.MunicipalBoundary, "CountyBoundary":
                            self.CountyBoundary, "ESZ": self.ESZ, "PSAP": self.PSAP, "EMS": self.EMS, "LAW": self.LAW, "FIRE": self.FIRE,
                            "ESB": self.ESB, "HYDRANTS": self.HYDRANTS, "PARCELS": self.PARCELS, "GATES": self.GATES, "CELL_SECTOR": self.CELL_SECTOR,
                            "AddressPoints": self.AddressPoints, "RoadCenterline": self.RoadCenterline, "RoadAlias": self.RoadAlias}

    NG911_GDB = NG911_GDB_Object()

    return NG911_GDB

def get20GDBObject(gdb):

    featureDataset = "NG911"

    ESB = join(gdb, featureDataset, "ESB")
    EMS = join(gdb, featureDataset, "ESB_EMS")
    FIRE = join(gdb, featureDataset, "ESB_FIRE")
    LAW = join(gdb, featureDataset, "ESB_LAW")
    PSAP = join(gdb, featureDataset, "ESB_PSAP")

    esbList = []
    for e in [ESB, EMS, FIRE, LAW, PSAP]:
        if Exists(e):
            if e not in esbList:
                esbList.append(e)

    prj = getProjectionFile()

    # This is a class used represent the NG911 geodatabase
    class NG911_20GDB_Object():
        def __init__(self):
            self.gdbPath = gdb
            self.ProjectionFile = prj
            self.NG911_FeatureDataset = join(gdb, "NG911")
            self.AddressPoints = join(self.NG911_FeatureDataset, "AddressPoints")
            self.RoadCenterline = join(self.NG911_FeatureDataset, "RoadCenterline")
            self.RoadAlias = join(gdb, "RoadAlias")
            self.AuthoritativeBoundary = join(self.NG911_FeatureDataset, "AuthoritativeBoundary")
            self.MunicipalBoundary = join(self.NG911_FeatureDataset, "MunicipalBoundary")
            self.CountyBoundary = join(self.NG911_FeatureDataset, "CountyBoundary")
            self.ESZ = join(self.NG911_FeatureDataset, "ESZ")
            self.PSAP = PSAP
            self.Topology = join(self.NG911_FeatureDataset, "NG911_Topology")
            self.Locator = join(gdb, "Locator")
            self.gc_test = join(gdb, "gc_test")
            self.GeocodeTable = join(gdb, "GeocodeTable")
            self.GeocodeExceptions = join(gdb, "GeocodeExceptions")
            self.AddressPointFrequency = join(gdb, "AP_Freq")
            self.RoadCenterlineFrequency = join(gdb, "Road_Freq")
            self.FieldValuesCheckResults = join(gdb, "FieldValuesCheckResults")
            self.TemplateCheckResults = join(gdb, "TemplateCheckResults")
            self.ESB = ESB
            self.EMS = EMS
            self.FIRE = FIRE
            self.LAW = LAW
            self.HYDRANTS = join(gdb, "Hydrants")
            self.PARCELS = join(gdb, "Parcels")
            self.GATES = join(gdb, "Gates")
            self.CELL_SECTOR = join(gdb, "Cell_Sector")
            self.AdminBoundaryList = [basename(self.AuthoritativeBoundary), basename(self.CountyBoundary), basename(self.MunicipalBoundary),
                                    basename(self.ESZ), basename(self.PSAP)]
            self.fcList = [self.AddressPoints, self.RoadCenterline, self.RoadAlias, self.AuthoritativeBoundary, self.MunicipalBoundary,
                        self.CountyBoundary, self.ESZ, self.PSAP, self.HYDRANTS, self.PARCELS, self.GATES, self.CELL_SECTOR]
            self.esbList = esbList
            self.otherLayers = [self.HYDRANTS, self.PARCELS, self.GATES, self.CELL_SECTOR]
            self.requiredLayers = [self.RoadAlias, self.AddressPoints, self.RoadCenterline, self.AuthoritativeBoundary, self.ESZ] + esbList
            self.fcDict = {"AuthoritativeBoundary": self.AuthoritativeBoundary, "MunicipalBoundary": self.MunicipalBoundary, "CountyBoundary":
                self.CountyBoundary, "ESZ": self.ESZ, "PSAP": self.PSAP, "EMS": self.EMS, "LAW": self.LAW, "FIRE": self.FIRE,
                "ESB": self.ESB, "HYDRANTS": self.HYDRANTS, "PARCELS": self.PARCELS, "GATES": self.GATES, "CELL_SECTOR": self.CELL_SECTOR,
                "AddressPoints": self.AddressPoints, "RoadCenterline": self.RoadCenterline, "RoadAlias": self.RoadAlias}

    NG911_GDB = NG911_20GDB_Object()

    return NG911_GDB

def getFCObject(fc):
    from NG911_arcpy_shortcuts import fieldExists
    from os.path import basename

    word = basename(fc).upper()

    obj = object

    if word == "ROADCENTERLINE":
        if fieldExists(fc, "NGSEGID"):
            #2.0 geodatabase
            obj = getDefault20NG911RoadCenterlineObject()
        else:
            obj = getDefaultNG911RoadCenterlineObject()

    elif word == "ADDRESSPOINTS":
        if fieldExists(fc, "NGADDID"):
            #2.0 geodatabase
            obj = getDefault20NG911AddressObject()
        else:
            obj = getDefaultNG911AddressObject()
    elif word == "ROADALIAS":
        if fieldExists(fc, "NGALIASID"):
            #2.0 geodatabase
            obj = getDefault20NG911RoadAliasObject()
        else:
            obj = getDefaultNG911RoadAliasObject()
    elif word == "AUTHORITATIVEBOUNDARY":
        if fieldExists(fc, "NGABID"):
            #2.0 geodatabase
            obj = getDefault20NG911AuthoritativeBoundaryObject()
        else:
            obj = getDefaultNG911AuthoritativeBoundaryObject()
    elif word == "MUNICIPALBOUNDARY":
        if fieldExists(fc, "NGMUNI_ID"):
            obj = getDefault20NG911MunicipalBoundaryObject()
        else:
            obj = getDefaultNG911MunicipalBoundaryObject()
    elif word == "COUNTYBOUNDARY":
        if fieldExists(fc, "NGCOUNTYID"):
            obj = getDefault20NG911CountyBoundaryObject()
        else:
            obj = getDefaultNG911CountyBoundaryObject()
    elif word == "ESZ":
        if fieldExists(fc, "NGESZID"):
            obj = getDefault20NG911ESZObject()
        else:
            obj = getDefaultNG911ESZObject()
    elif word == "PARCELS":
        obj = getDefault20NG911ParcelObject()
    elif word == "GATES":
        obj = getDefault20NG911GateObject()
    elif word == "HYDRANTS":
        obj = getDefault20NG911HydrantObject()
    elif word == "CELL_SECTOR":
        obj = getDefault20NG911CellSectorObject()
    elif word == "FIELDVALUESCHECKRESULTS":
        obj = getDefaultNG911FieldValuesCheckResultsObject()
    elif word == "TEMPLATECHECKRESULTS":
        obj = getDefaultNG911TemplateCheckResultsObject()
    elif word == "GEOCODEEXCEPTIONS":
        if fieldExists(fc, "NGADDID"):
            obj = getDefaul20NG911GeocodeExceptionsObject()
        else:
            obj = getDefaultNG911GeocodeExceptionsObject()
    elif "ESB" in word or "PSAP" in word or "EMS" in word or "LAW" in word or "FIRE" in word:
        if fieldExists(fc, "NGESBID"):
            obj = getDefault20NG911ESBObject()
        else:
            obj = getDefaultNG911ESBObject()

    return obj



