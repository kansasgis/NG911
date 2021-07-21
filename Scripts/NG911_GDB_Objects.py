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
from arcpy import Exists

class NG911_RoadCenterline_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_SEGID, u_STATE_L, u_STATE_R, u_COUNTY_L, u_COUNTY_R, u_MUNI_L,
                    u_MUNI_R, u_L_F_ADD, u_L_T_ADD, u_R_F_ADD, u_R_T_ADD, u_PARITY_L, u_PARITY_R, u_POSTCO_L, u_POSTCO_R, u_ZIP_L, u_ZIP_R,
                    u_ESN_L, u_ESN_R, u_MSAGCO_L, u_MSAGCO_R, u_PRD, u_STP, u_RD, u_STS, u_POD, u_POM, u_SPDLIMIT, u_ONEWAY, u_RDCLASS,
                    u_UPDATEBY,  u_LABEL, u_ELEV_F, u_ELEV_T, u_SURFACE, u_STATUS, u_TRAVEL, u_LRSKEY, u_EXCEPTION, u_SUBMIT,
                    u_NOTES, u_UNINC_L, u_UNINC_R, u_KSSEGID, u_AUTH_L, u_AUTH_R, u_GEOMSAGL, u_GEOMSAGR, u_gdb_version):

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
        self.AUTH_L = u_AUTH_L
        self.AUTH_R = u_AUTH_R
        self.GEOMSAGL = u_GEOMSAGL
        self.GEOMSAGR = u_GEOMSAGR
        self.GDB_VERSION = u_gdb_version
        self.LABEL_FIELDS = [self.LABEL, self.PRD, self.STP, self.RD, self.STS, self.POD, self.POM]

        reqFields = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.STATE_L, self.STATE_R, self.COUNTY_L, self.COUNTY_R,
                    self.MUNI_L, self.MUNI_R, self.L_F_ADD, self.L_T_ADD, self.R_F_ADD, self.R_T_ADD, self.PARITY_L, self.PARITY_R,
                    self.MSAGCO_L, self.MSAGCO_R, self.RD, self.LABEL, self.UPDATEBY, self.STATUS, self.ELEV_F, self.ELEV_T, self.EXCEPTION]
        fieldMap = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.STATE_L, self.STATE_R, self.COUNTY_L, self.COUNTY_R, self.MUNI_L,
                    self.MUNI_R, self.L_F_ADD, self.L_T_ADD, self.R_F_ADD, self.R_T_ADD, self.PARITY_L, self.PARITY_R, self.POSTCO_L, self.POSTCO_R, self.ZIP_L, self.ZIP_R,
                    self.ESN_L, self.ESN_R, self.MSAGCO_L, self.MSAGCO_R, self.PRD, self.STP, self.RD, self.STS, self.POD, self.POM, self.SPDLIMIT, self.ONEWAY, self.RDCLASS,
                    self.UPDATEBY,  self.LABEL, self.ELEV_F, self.ELEV_T, self.SURFACE, self.STATUS, self.TRAVEL, self.LRSKEY, self.EXCEPTION, self.SUBMIT,
                    self.NOTES, self.UNINC_L, self.UNINC_R]
        fieldsWithDomains = {self.STEWARD: "STEWARD", self.STATE_L: "STATE", self.STATE_R: "STATE", self.COUNTY_L: "COUNTY", self.COUNTY_R: "COUNTY",
                         self.MUNI_L: "MUNI", self.MUNI_R: "MUNI", self.PARITY_L: "PARITY", self.PARITY_R: "PARITY",
                            self.POSTCO_L: "POSTCO", self.POSTCO_R: "POSTCO", self.ZIP_L: "ZIP", self.ZIP_R: "ZIP",
                            self.PRD: "PRD", self.STS: "STS", self.POD: "POD", self.ONEWAY: "ONEWAY", self.RDCLASS: "RDCLASS",
                            self.SURFACE: "SURFACE", self.STATUS: "STATUS", self.EXCEPTION: "EXCEPTION", self.SUBMIT: "YN"}
        frequencyFields = [self.STATE_L,self.STATE_R,self.COUNTY_L,self.COUNTY_R,self.MUNI_L,self.MUNI_R,self.L_F_ADD,self.L_T_ADD,self.R_F_ADD,self.R_T_ADD,
                            self.PARITY_L,self.PARITY_R,self.POSTCO_L,self.POSTCO_R,self.ZIP_L,self.ZIP_R,self.ESN_L,self.ESN_R,self.MSAGCO_L,self.MSAGCO_R,
                            self.PRD,self.STP,self.RD,self.STS,self.POD,self.POM,self.SPDLIMIT,self.ONEWAY,self.RDCLASS,self.LABEL,self.ELEV_F,self.ELEV_T,
                            self.SURFACE,self.STATUS,self.TRAVEL,self.LRSKEY]

        setList = [reqFields, fieldMap, fieldsWithDomains, frequencyFields]

        # add additional field values and domains for new 2.1 fields
        if self.GDB_VERSION == "21":
            for sL in setList:
                for rf in [self.AUTH_L, self.AUTH_R, self.GEOMSAGL, self.GEOMSAGR]:
                    if type(sL) == list:
                        sL.append(rf)
                    elif type(sL) == dict:
                        sL[rf] = "YN"

        self.REQUIRED_FIELDS = reqFields
        self.FIELD_MAP = fieldMap
        self.FIELDS_WITH_DOMAINS = fieldsWithDomains
        self.FREQUENCY_FIELDS = frequencyFields
        self.FREQUENCY_FIELDS_STRING = ";".join(self.FREQUENCY_FIELDS)


def getDefaultNG911RoadCenterlineObject(gdb_version):

    NG911_RoadCenterline_Default = NG911_RoadCenterline_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGSEGID", "STATE_L", "STATE_R", "COUNTY_L", "COUNTY_R", "MUNI_L",
                    "MUNI_R", "L_F_ADD", "L_T_ADD", "R_F_ADD", "R_T_ADD", "PARITY_L", "PARITY_R", "POSTCO_L", "POSTCO_R", "ZIP_L", "ZIP_R",
                    "ESN_L", "ESN_R", "MSAGCO_L", "MSAGCO_R", "PRD", "STP", "RD", "STS", "POD", "POM", "SPDLIMIT", "ONEWAY", "RDCLASS",
                    "UPDATEBY", "LABEL", "ELEV_F", "ELEV_T", "SURFACE", "STATUS", "TRAVEL", "LRSKEY", "EXCEPTION", "SUBMIT",
                    "NOTES", "UNINC_L", "UNINC_R", "NGKSSEGID", "AUTH_L", "AUTH_R", "GEOMSAGL", "GEOMSAGR", gdb_version)

    return NG911_RoadCenterline_Default


class NG911_RoadAlias_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_ALIASID, u_SEGID, u_A_PRD, u_A_STP, u_A_RD, u_A_STS, u_A_POD, u_A_POM, u_A_L_FROM, u_A_L_TO,
                    u_A_R_FROM, u_A_R_TO, u_LABEL, u_UPDATEBY, u_SUBMIT, u_NOTES, u_KSSEGID, u_NGKSALIASID, u_gdb_version):

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
        self.NGKSALIASID = u_NGKSALIASID
        self.GDB_VERSION = u_gdb_version
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.SEGID, self.LABEL, self.UPDATEBY]
        self.FIELDS_WITH_DOMAINS = {self.STEWARD: "STEWARD", self.A_PRD: "PRD", self.A_STS: "STS",
                             self.A_POD: "POD", self.SUBMIT: "YN"}
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.SEGID, self.A_PRD,
                            self.A_STP, self.A_RD, self.A_STS, self.A_POD, self.A_POM, self.A_L_FROM, self.A_L_TO,
                            self.A_R_FROM, self.A_R_TO, self.LABEL, self.UPDATEBY, self.SUBMIT, self.NOTES]


def getDefaultNG911RoadAliasObject(gdb_version):

    NG911_RoadAlias_Default = NG911_RoadAlias_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGALIASID", "NGSEGID", "A_PRD", "A_STP", "A_RD", "A_STS", "A_POD",
                    "A_POM", "A_L_FROM", "A_L_TO", "A_R_FROM", "A_R_TO", "LABEL", "UPDATEBY", "SUBMIT", "NOTES", "NGKSSEGID", "NGKSALIASID", gdb_version)

    return NG911_RoadAlias_Default


class NG911_Adddress_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_ADDID, u_STATE, u_COUNTY, u_MUNI, u_HNO, u_HNS, u_PRD, u_STP,
                    u_RD, u_STS, u_POD, u_POM, u_ESN, u_MSAGCO, u_POSTCO, u_ZIP, u_ZIP4, u_BLD, u_FLR, u_UNIT, u_ROOM, u_SEAT, u_LMK,
                    u_LOC, u_PLC, u_LONG, u_LAT, u_ELEV, u_LABEL, u_UPDATEBY, u_LOCTYPE, u_USNGRID, u_KSPID, u_MILEPOST, u_ADDURI,
                    u_UNINC, u_SUBMIT, u_NOTES, u_PRM, u_RCLMATCH, u_GEOMSAG, u_RCLSIDE, u_gdb_version):

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
        self.RCLMATCH = u_RCLMATCH
        self.GEOMSAG = u_GEOMSAG
        self.RCLSIDE = u_RCLSIDE
        self.GDB_VERSION = u_gdb_version
        self.LABEL_FIELDS = [self.LABEL, self.HNO, self.HNS, self.PRD, self.STP, self.RD, self.STS, self.POD, self.POM, self.BLD,
                            self.FLR, self.UNIT, self.ROOM, self.SEAT]
        self.GEOCODE_LABEL_FIELDS = [self.HNO, self.PRD, self.STP, self.RD, self.STS, self.POD, self.POM]

        reqFields = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.STATE, self.COUNTY, self.MUNI, self.HNO,
                    self.RD, self.LABEL, self.UPDATEBY, self.LOCTYPE]
        fieldMap = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.STATE, self.COUNTY, self.MUNI, self.HNO, self.HNS, self.PRD, self.STP,
                    self.RD, self.STS, self.POD, self.POM, self.ESN, self.MSAGCO, self.POSTCO, self.ZIP, self.ZIP4, self.BLD, self.FLR, self.UNIT, self.ROOM, self.SEAT, self.LMK,
                    self.LOC, self.PLC, self.LONG, self.LAT, self.ELEV, self.LABEL, self.UPDATEBY, self.LOCTYPE, self.USNGRID, self.KSPID, self.MILEPOST, self.ADDURI,
                    self.UNINC, self.SUBMIT, self.NOTES]
        fieldsWithDomains = {self.STEWARD: "STEWARD", self.STATE: "STATE", self.COUNTY: "COUNTY", self.MUNI: "MUNI", self.HNO: "HNO", self.PRD: "PRD",
                     self.STS: "STS", self.POD: "POD", self.POSTCO: "POSTCO", self.ZIP: "ZIP",
                    self.PLC: "PLC", self.LOCTYPE: "LOCTYPE", self.SUBMIT: "YN"}
        frequencyFields = [self.HNO,self.HNS,self.PRD,self.STP,self.RD,self.STS,self.POD,self.POM,self.BLD,self.FLR,self.UNIT,self.ROOM,
                                    self.SEAT,self.LOC,self.LOCTYPE,self.MSAGCO]

        setList = [reqFields, fieldMap, frequencyFields]

        if self.GDB_VERSION == "21":
            # only geomsag has a domain of the new 2.1 fields
            fieldsWithDomains[self.GEOMSAG] = "YN"
            fieldsWithDomains[self.RCLSIDE] = "RCLSIDE"

            for sL in setList:
                for rf in [self.RCLMATCH, self.GEOMSAG, self.RCLSIDE]:
                    sL.append(rf)

        self.REQUIRED_FIELDS = reqFields
        self.FIELD_MAP = fieldMap
        self.FIELDS_WITH_DOMAINS = fieldsWithDomains
        self.FREQUENCY_FIELDS = frequencyFields
        self.FREQUENCY_FIELDS_STRING = ";".join(self.FREQUENCY_FIELDS)


def getDefaultNG911AddressObject(gdb_version):

    NG911_Address_Default = NG911_Adddress_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGADDID", "STATE", "COUNTY", "MUNI", "HNO", "HNS", "PRD", "STP",
                    "RD", "STS", "POD", "POM", "ESN", "MSAGCO", "POSTCO", "ZIP", "ZIP4", "BLD", "FLR", "UNIT", "ROOM", "SEAT", "LMK",
                    "LOC", "PLC", "LONG", "LAT", "ELEV", "LABEL", "UPDATEBY", "LOCTYPE", "USNGRID", "KSPID", "MILEPOST", "ADDURI",
                    "UNINC", "SUBMIT", "NOTES", "PRM", "RCLMATCH", "GEOMSAG", "RCLSIDE", gdb_version)

    return NG911_Address_Default


class NG911_FieldValuesCheckResults_Object(object):

    def __init__(self, u_DATEFLAGGED, u_DESCRIPTION, u_LAYER, u_FIELD, u_FEATUREID, u_CHECK, u_NOTES):

        self.DATEFLAGGED = u_DATEFLAGGED
        self.DESCRIPTION = u_DESCRIPTION
        self.LAYER = u_LAYER
        self.FIELD = u_FIELD
        self.FEATUREID = u_FEATUREID
        self.CHECK = u_CHECK
        self.NOTES = u_NOTES


def getDefaultNG911FieldValuesCheckResultsObject():

    NG911_FieldValuesCheckResults_Default = NG911_FieldValuesCheckResults_Object("DATEFLAGGED", "DESCRIPTION", "LAYER", "FIELD", "FEATUREID", "CHECK", "NOTES")

    return NG911_FieldValuesCheckResults_Default


class NG911_TemplateCheckResults_Object(object):

    def __init__(self, u_DATEFLAGGED, u_DESCRIPTION, u_CATEGORY, u_CHECK):

        self.DATEFLAGGED = u_DATEFLAGGED
        self.DESCRIPTION = u_DESCRIPTION
        self.CATEGORY = u_CATEGORY
        self.CHECK = u_CHECK


def getDefaultNG911TemplateCheckResultsObject():

    NG911_TemplateCheckResults_Default = NG911_TemplateCheckResults_Object("DATEFLAGGED", "DESCRIPTION", "CATEGORY", "CHECK")

    return NG911_TemplateCheckResults_Default


class NG911_ESB_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_ESBID, u_STATE, u_AGENCYID, u_SERV_NUM, u_DISPLAY, u_ESB_TYPE, u_LAW,
                u_FIRE, u_EMS, u_UPDATEBY, u_PSAP, u_SUBMIT, u_NOTES, u_gdb_version):

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
        self.GDB_VERSION = u_gdb_version
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.STATE, self.AGENCYID, self.DISPLAY, self.ESB_TYPE, self.UPDATEBY]
        self.FIELDS_WITH_DOMAINS = {self.STEWARD: "STEWARD", self.STATE: "STATE", self.AGENCYID: "AGENCYID", self.SUBMIT: "YN"}
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.STATE, self.AGENCYID,
                            self.SERV_NUM, self.DISPLAY, self.ESB_TYPE, self.LAW, self.FIRE, self.EMS, self.UPDATEBY, self.PSAP,
                            self.SUBMIT, self.NOTES]


def getDefaultNG911ESBObject(gdb_version):

    NG911_ESB_Default = NG911_ESB_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGESBID", "STATE", "AGENCYID", "SERV_NUM", "DISPLAY", "ESB_TYPE",
                    "LAW", "FIRE", "EMS", "UPDATEBY", "PSAP", "SUBMIT", "NOTES", gdb_version)

    return NG911_ESB_Default


class NG911_ESZ_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_ESZID, u_STATE, u_AGENCYID, u_ESN, u_UPDATEBY, u_SUBMIT, u_NOTES, u_gdb_version):

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
        self.GDB_VERSION = u_gdb_version
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.AGENCYID, self.ESN, self.UPDATEBY]
        self.FIELDS_WITH_DOMAINS = {self.STEWARD: "STEWARD", self.AGENCYID: "AGENCYID", self.SUBMIT: "YN"}
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.AGENCYID,
                            self.ESN, self.UPDATEBY, self.SUBMIT, self.NOTES]


def getDefaultNG911ESZObject(gdb_version):

    NG911_ESZ_Default = NG911_ESZ_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGESZID", "STATE", "AGENCYID", "ESN",
                "UPDATEBY", "SUBMIT", "NOTES", gdb_version)

    return NG911_ESZ_Default


class NG911_CountyBoundary_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_COUNTYID, u_STATE, u_COUNTY, u_UPDATEBY, u_SUBMIT, u_NOTES, u_gdb_version):

        self.STEWARD = u_STEWARD
        self.L_UPDATE = u_L_UPDATE
        self.COUNTYID = u_COUNTYID
        self.UNIQUEID = self.COUNTYID
        self.STATE = u_STATE
        self.COUNTY = u_COUNTY
        self.UPDATEBY = u_UPDATEBY
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.GDB_VERSION = u_gdb_version
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.UNIQUEID, self.STATE, self.COUNTY, self.UPDATEBY]
        self.FIELDS_WITH_DOMAINS = {self.STEWARD: "STEWARD", self.STATE: 'STATE', self.COUNTY: "COUNTY"}
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.UNIQUEID, self.STATE, self.COUNTY, self.UPDATEBY, self.SUBMIT, self.NOTES]


def getDefaultNG911CountyBoundaryObject(gdb_version):

    NG911_CountyBoundary_Default = NG911_CountyBoundary_Object("STEWARD", "L_UPDATE", "NGCOUNTYID", "STATE", "COUNTY", "UPDATEBY",
                "SUBMIT", "NOTES", gdb_version)

    return NG911_CountyBoundary_Default


class NG911_AuthoritativeBoundary_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_ABID, u_STATE, u_AGENCYID, u_DISPLAY, u_UPDATEBY, u_SUBMIT, u_NOTES, u_gdb_version):

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
        self.GDB_VERSION = u_gdb_version
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.AGENCYID, self.DISPLAY, self.UPDATEBY]
        self.FIELDS_WITH_DOMAINS = {self.STEWARD: "STEWARD", self.AGENCYID: "AGENCYID", self.SUBMIT: "YN"}
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.AGENCYID, self.DISPLAY,
                            self.UPDATEBY, self.SUBMIT, self.NOTES]


def getDefaultNG911AuthoritativeBoundaryObject(gdb_version):

    NG911_AuthoritativeBoundary_Default = NG911_AuthoritativeBoundary_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGABID", "STATE", "AGENCYID",
                        "DISPLAY", "UPDATEBY", "SUBMIT", "NOTES", gdb_version)

    return NG911_AuthoritativeBoundary_Default


class NG911_MunicipalBoundary_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_MUNI_ID, u_STATE, u_COUNTY, u_MUNI, u_UPDATEBY, u_SUBMIT, u_NOTES, u_gdb_version):

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
        self.GDB_VERSION = u_gdb_version
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.STATE, self.COUNTY, self.MUNI, self.UPDATEBY]
        self.FIELDS_WITH_DOMAINS = {self.STEWARD: "STEWARD", self.STATE: "STATE", self.COUNTY: "COUNTY", self.MUNI: "MUNI", self.SUBMIT: "YN"}
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.STATE, self.COUNTY, self.MUNI,
                            self.UPDATEBY, self.SUBMIT, self.NOTES]


def getDefaultNG911MunicipalBoundaryObject(gdb_version):

    NG911_MunicipalBoundary_Default = NG911_MunicipalBoundary_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGMUNI_ID", "STATE", "COUNTY", "MUNI",
                        "UPDATEBY", "SUBMIT", "NOTES", gdb_version)

    return NG911_MunicipalBoundary_Default


class NG911_Hydrant_Object(object):

    def __init__(self, u_STEWARD, u_HYDID, u_HYDTYPE, u_PROVIDER, u_STATUS, u_PRIVATE,
            u_SUBMIT, u_NOTES, u_gdb_version):

        self.STEWARD = u_STEWARD
        self.NGHYDID = u_HYDID
        self.UNIQUEID = self.NGHYDID
        self.HYDTYPE = u_HYDTYPE
        self.PROVIDER = u_PROVIDER
        self.STATUS = u_STATUS
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.PRIVATE = u_PRIVATE
        self.GDB_VERSION = u_gdb_version
        self.REQUIRED_FIELDS = [self.STEWARD, self.UNIQUEID, self.HYDTYPE, self.STATUS, self.PRIVATE, self.SUBMIT]
        self.FIELDS_WITH_DOMAINS = {self.STEWARD: "STEWARD", self.SUBMIT: "YN", self.HYDTYPE: "HYDTYPE",
                                self.STATUS: "HYDSTATUS", self.PRIVATE: "PRIVATE"}
        self.FIELD_MAP = [self.STEWARD, self.UNIQUEID, self.HYDTYPE, self.PROVIDER, self.STATUS,
                            self.SUBMIT, self.NOTES, self.PRIVATE]


def getDefaultNG911HydrantObject(gdb_version):

    NG911_Hydrant_Default = NG911_Hydrant_Object("STEWARD", "NGHYDID", "HYDTYPE", "PROVIDER", "HYDSTATUS",
                        "PRIVATE", "SUBMIT", "NOTES", gdb_version)

    return NG911_Hydrant_Default


class NG911_Parcel_Object(object):

    def __init__(self, u_STEWARD, u_KSPID, u_SUBMIT, u_NOTES, u_gdb_version):

        self.STEWARD = u_STEWARD
        self.NGKSPID = u_KSPID
        self.UNIQUEID = self.NGKSPID
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.GDB_VERSION = u_gdb_version
        self.REQUIRED_FIELDS = [self.STEWARD, self.UNIQUEID]
        self.FIELDS_WITH_DOMAINS = {self.STEWARD: "STEWARD", self.SUBMIT: "YN"}
        self.FIELD_MAP = [self.STEWARD, self.UNIQUEID, self.SUBMIT, self.NOTES]


def getDefaultNG911ParcelObject(gdb_version):

    NG911_Parcel_Default = NG911_Parcel_Object("STEWARD", "NGKSPID", "SUBMIT", "NOTES", gdb_version)

    return NG911_Parcel_Default


class NG911_Gate_Object(object):

    def __init__(self, u_STEWARD, u_NGGATEID, u_GATE_TYPE, u_SIREN, u_RF_OP, u_KNOXBOX, u_KEYPAD,
                    u_MAN_OPEN, u_GATEOPEN, u_G_OWNER, u_SUBMIT, u_NOTES, u_gdb_version):

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
        self.GDB_VERSION = u_gdb_version
        self.REQUIRED_FIELDS = [self.STEWARD, self.UNIQUEID, self.GATE_TYPE, self.SIREN, self.RF_OP, self.KNOXBOX, self.KEYPAD, self.MAN_OPEN, self.GATEOPEN]
        self.FIELDS_WITH_DOMAINS = {self.STEWARD: "STEWARD", self.SUBMIT: "YN", self.GATE_TYPE: "GATE_TYPE", self.SIREN: "YNU",
                            self.RF_OP: "YNU", self.KNOXBOX: "YNU", self.KEYPAD: "YNU", self.KEYPAD: "YNU", self.MAN_OPEN: "YNU", self.GATEOPEN: "YNU"}
        self.FIELD_MAP = [self.STEWARD, self.UNIQUEID, self.GATE_TYPE, self.SIREN, self.RF_OP, self.KNOXBOX, self.KEYPAD, self.MAN_OPEN,
                            self.GATEOPEN, self.G_OWNER, self.SUBMIT, self.NOTES]


def getDefaultNG911GateObject(gdb_version):

    NG911_Gate_Default = NG911_Gate_Object("STEWARD", "NGGATEID", "GATE_TYPE", "SIREN", "RF_OP", "KNOXBOX", "KEYPAD",
                    "MAN_OPEN", "GATEOPEN", "G_OWNER", "SUBMIT", "NOTES", gdb_version)

    return NG911_Gate_Default


class NG911_Utility_Object(object):

    def __init__(self, u_STEWARD, u_NGUSERVID, u_UTIL_NAME, u_PHONENUM, u_SUBMIT, u_NOTES, u_gdb_version):

        self.STEWARD = u_STEWARD
        self.NGUSERVID = u_NGUSERVID
        self.UNIQUEID = self.NGUSERVID
        self.UTIL_NAME = u_UTIL_NAME
        self.PHONENUM = u_PHONENUM
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.GDB_VERSION = u_gdb_version
        self.REQUIRED_FIELDS = [self.STEWARD, self.UNIQUEID, self.UTIL_NAME, self.PHONENUM]
        self.FIELDS_WITH_DOMAINS = {self.STEWARD: "STEWARD"}
        self.FIELD_MAP = [self.STEWARD, self.UNIQUEID, self.UTIL_NAME, self.PHONENUM, self.SUBMIT, self.NOTES]


def getDefaultNG911UtilityObject(gdb_version):

    NG911_Utility_Default = NG911_Utility_Object("STEWARD", "NGUSERVID", "UTIL_NAME", "PHONENUM", "SUBMIT", "NOTES", gdb_version)

    return NG911_Utility_Default


class NG911_Bridge_Object(object):

    def __init__(self, u_STEWARD, u_NGBRIDGE, u_LPA_NAME, u_STRUCT_NO, u_WEIGHT_L, u_OVERUNDER, u_STATUS, u_SUBMIT, u_NOTES, u_gdb_version):

        self.STEWARD = u_STEWARD
        self.NGBRIDGE = u_NGBRIDGE
        self.UNIQUEID = self.NGBRIDGE
        self.LPA_NAME = u_LPA_NAME
        self.STRUCT_NO = u_STRUCT_NO
        self.WEIGHT_L = u_WEIGHT_L
        self.OVERUNDER = u_OVERUNDER
        self.STATUS = u_STATUS
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.GDB_VERSION = u_gdb_version
        self.REQUIRED_FIELDS = [self.STEWARD, self.UNIQUEID]
        self.FIELDS_WITH_DOMAINS= {self.STEWARD: "STEWARD", self.STATUS: "BRIDGESTATUS", self.OVERUNDER: "OVERUNDER"}
        self.FIELD_MAP = [self.STEWARD, self.UNIQUEID, self.LPA_NAME, self.STRUCT_NO, self.WEIGHT_L, self.OVERUNDER, self.STATUS,
                     self.SUBMIT, self.NOTES]


def getDefaultNG911BridgeObject(gdb_version):

    NG911_Bridge_Default = NG911_Bridge_Object("STEWARD", "NGBRIDGE", "LPA_NAME", "STRUCT_NO", "WEIGHT_L",
            "OVERUNDER", "STATUS", "SUBMIT", "NOTES", gdb_version)

    return NG911_Bridge_Default


class NG911_CellSite_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_NGCELLID, u_EFF_DATE, u_EXP_DATE, u_STATE, u_COUNTY, u_HEIGHT,
                    u_TWR_TYP, u_UPDATEBY, u_SUBMIT, u_NOTES, u_gdb_version):

        self.STEWARD = u_STEWARD
        self.L_UPDATE = u_L_UPDATE
        self.NGCELLID = u_NGCELLID
        self.UNIQUEID = self.NGCELLID
        self.EFF_DATE = u_EFF_DATE
        self.EXP_DATE = u_EXP_DATE
        self.STATE = u_STATE
        self.COUNTY = u_COUNTY
        self.HEIGHT = u_HEIGHT
        self.TWR_TYP = u_TWR_TYP
        self.UPDATEBY = u_UPDATEBY
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.GDB_VERSION = u_gdb_version
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.UNIQUEID, self.EFF_DATE, self.STATE, self.COUNTY, self.UPDATEBY]
        self.FIELDS_WITH_DOMAINS= {self.STEWARD: "STEWARD", self.TWR_TYP: "TWR_TYP"}
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.UNIQUEID, self.EFF_DATE, self.EXP_DATE, self.STATE, self.COUNTY,
                    self.HEIGHT, self.TWR_TYP, self.UPDATEBY, self.SUBMIT, self.NOTES]


def getDefaultNG911CellSiteObject(gdb_version):

    NG911_CellSite_Default = NG911_CellSite_Object("STEWARD", "L_UPDATE", "NGCELLID", "EFF_DATE", "EXP_DATE", "STATE", "COUNTY",
            "HEIGHT", "TWR_TYP", "UPDATEBY", "SUBMIT", "NOTES", gdb_version)

    return NG911_CellSite_Default


class NG911_CellSector_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_NGCELLID, u_STATE, u_COUNTY, u_SITEID, u_SECTORID, u_SWITCHID,
                u_MARKETID, u_C_SITEID, u_ESRD, u_LASTESRK, u_SECORN, u_UPDATEBY, u_SUBMIT, u_NOTES, u_gdb_version):

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
        self.MARKETID = u_MARKETID
        self.C_SITEID = u_C_SITEID
        self.ESRD = u_ESRD
        self.LASTESRK = u_LASTESRK
        self.SECORN = u_SECORN
        self.UPDATEBY = u_UPDATEBY
        self.SUBMIT = u_SUBMIT
        self.NOTES = u_NOTES
        self.GDB_VERSION = u_gdb_version
        self.REQUIRED_FIELDS = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.UNIQUEID, self.STATE, self.COUNTY, self.SECTORID,
                            self.SECORN, self.UPDATEBY]
        self.FIELDS_WITH_DOMAINS = {self.STATE: "STATE", self.COUNTY: "COUNTY", self.SUBMIT: "YN", self.STEWARD: "STEWARD"}
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.UNIQUEID, self.STATE, self.COUNTY, self.SITEID,
                        self.SECTORID, self.SWITCHID, self.MARKETID, self.C_SITEID, self.ESRD, self.LASTESRK, self.SECORN,
                            self.UPDATEBY, self.SUBMIT, self.NOTES]


def getDefaultNG911CellSectorObject(gdb_version):

    NG911_CellSector_Default = NG911_CellSector_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "NGCELLID", "STATE", "COUNTY", "SITEID",
                        "SECTORID", "SWITCHID", "MARKETID", "C_SITEID", "ESRD", "LASTESRK", "SECORN", "UPDATEBY", "SUBMIT", "NOTES", gdb_version)

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
    def __init__(self, gdb, folder, gdbObject):
        self.gdbPath = gdb
        self.domainsFolderPath = folder
        self.gdbObject = gdbObject #contains fcList & esbList
        self.checkList = ""

def getProjectionFile():
    prj = r"\\vesta\d$\NG911_Pilot_Agg\KDOT_Lambert.prj"
    return prj

def NG911_Session(gdb):
    from os.path import dirname, join, realpath

    folder = join(dirname(dirname(realpath(__file__))), "Domains")

    #get geodatabase object set up
    gdbObject = getGDBObject(gdb)
    NG911_obj = NG911_Session_obj(gdb, folder, gdbObject)

    return NG911_obj


def getGDBObject(gdb):
    from NG911_arcpy_shortcuts import fieldExists, hasRecords

    featureDataset = "NG911"

    # see what version of the database we're working with
    ap = join(gdb, featureDataset, "AddressPoints")
    if fieldExists(ap, "RCLMATCH"):
        version = "21"
    else:
        version = "20"

    # prep potential ESB list
    ESB = join(gdb, featureDataset, "ESB")
    EMS = join(gdb, featureDataset, "ESB_EMS")
    FIRE = join(gdb, featureDataset, "ESB_FIRE")
    LAW = join(gdb, featureDataset, "ESB_LAW")
    PSAP = join(gdb, featureDataset, "ESB_PSAP")
    RESCUE = join(gdb, featureDataset, "ESB_RESCUE")
    FIREAUTOAID = join(gdb, featureDataset, "ESB_FIREAUTOAID")

    # test to see what should be included in the for-real ESB list
    esbList = []
    for e in [ESB, EMS, FIRE, LAW, PSAP, RESCUE, FIREAUTOAID]:
        if Exists(e): # make sure the layer exists
            if hasRecords(e): # make sure the layer has records
                if e not in esbList:
                    esbList.append(e)

    # get the path to the projection file
    prj = getProjectionFile()

    # This is a class used represent the NG911 geodatabase
    class NG911_GDB_Object():
        def __init__(self):
            self.gdbPath = gdb
            self.GDB_VERSION = version
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
            self.gc_test = join(gdb, "gc_test")
            self.GeocodeTable = join(gdb, "GeocodeTable")
            self.AddressPointFrequency = join(gdb, "AP_Freq")
            self.RoadCenterlineFrequency = join(gdb, "Road_Freq")
            self.FieldValuesCheckResults = join(gdb, "FieldValuesCheckResults")
            self.TemplateCheckResults = join(gdb, "TemplateCheckResults")
            self.ESB = ESB
            self.EMS = EMS
            self.FIRE = FIRE
            self.LAW = LAW
            self.RESCUE = RESCUE
            self.FIREAUTOAID = FIREAUTOAID
            self.myState = "KS"

            if self.GDB_VERSION == "20":
                self.HYDRANTS = join(gdb, "Hydrants")
                self.PARCELS = join(gdb, "Parcels")
                self.GATES = join(gdb, "Gates")
                self.CELLSECTORS = join(gdb, "Cell_Sector")
                self.CELLSITES = ""
                self.BRIDGES = ""
                self.UT_ELECTRIC = ""
                self.UT_GAS = ""
                self.UT_SEWER = ""
                self.UT_WATER = ""

            elif self.GDB_VERSION == "21":
                self.OPTIONAL_LAYERS_FD = join(gdb, "OptionalLayers")
                self.HYDRANTS = join(self.OPTIONAL_LAYERS_FD, "HYDRANTS")
                self.PARCELS = join(self.OPTIONAL_LAYERS_FD, "PARCELS")
                self.GATES = join(self.OPTIONAL_LAYERS_FD, "GATES")
                self.CELLSECTORS = join(self.OPTIONAL_LAYERS_FD, "CELLSECTORS")
                self.CELLSITES = join(self.OPTIONAL_LAYERS_FD, "CELLSITES")
                self.BRIDGES = join(self.OPTIONAL_LAYERS_FD, "BRIDGES")
                self.UT_ELECTRIC = join(self.OPTIONAL_LAYERS_FD, "UT_ELECTRIC")
                self.UT_GAS = join(self.OPTIONAL_LAYERS_FD, "UT_GAS")
                self.UT_SEWER = join(self.OPTIONAL_LAYERS_FD, "UT_SEWER")
                self.UT_WATER = join(self.OPTIONAL_LAYERS_FD, "UT_WATER")

            # populate the utility list
            utList = [self.UT_ELECTRIC, self.UT_GAS, self.UT_SEWER, self.UT_WATER]

            # standard lists
            self.AdminBoundaryList = [basename(self.AuthoritativeBoundary), basename(self.CountyBoundary), basename(self.MunicipalBoundary),
                                    basename(self.ESZ), basename(self.PSAP)]
            self.AdminBoundaryFullPathList = [self.AuthoritativeBoundary, self.CountyBoundary, self.MunicipalBoundary,
                                    self.ESZ, self.PSAP]
            self.esbList = esbList
            self.requiredLayers = [self.RoadAlias, self.AddressPoints, self.RoadCenterline, self.AuthoritativeBoundary, self.ESZ] + esbList

            # variable lists
            featureClasses = [self.AddressPoints, self.RoadCenterline, self.RoadAlias, self.AuthoritativeBoundary, self.MunicipalBoundary,
                        self.CountyBoundary, self.ESZ, self.PSAP, self.HYDRANTS, self.PARCELS, self.GATES, self.CELLSECTORS]
            otherLayers = [self.HYDRANTS, self.PARCELS, self.GATES, self.CELLSECTORS]

            # make sure a 2.1 object contains the right information
            setList = [featureClasses, otherLayers]

            if version == "21":
                for sl in setList:
                    for rf in utList + [self.BRIDGES, self.CELLSITES]:
                        sl.append(rf)

            # add all esb layers to fcList
            for esb in esbList:
                featureClasses.append(esb)

            self.fcList = featureClasses
            self.otherLayers = otherLayers

    NG911_GDB = NG911_GDB_Object()

    return NG911_GDB

def getFCObject(fc):
    from NG911_arcpy_shortcuts import fieldExists
    from os.path import basename

    word = basename(fc).upper()

    obj = object

    if "ROADCENTERLINE" in word:
        if fieldExists(fc, "AUTH_L"):
            # 2.1 indicator
            version = "21"
        else:
            version = "20"
        obj = getDefaultNG911RoadCenterlineObject(version)

    elif "ADDRESS" in word:
        if fieldExists(fc, "RCLMATCH"):
            # 2.1 indicator
            version = "21"
        else:
            version = "20"
        obj = getDefaultNG911AddressObject(version)

    elif "ROADALIAS" in word:
        # 2.1 & 2.0 are the same
        obj = getDefaultNG911RoadAliasObject("x")

    elif "AUTHORITATIVEBOUNDARY" in word:
        # 2.1 & 2.0 are the same
        obj = getDefaultNG911AuthoritativeBoundaryObject("x")

    elif "MUNICIPALBOUNDARY" in word:
       # 2.1 & 2.0 are the same
       obj = getDefaultNG911MunicipalBoundaryObject("x")

    elif "COUNTYBOUNDARY" in word:
        # 2.1 & 2.0 are the same
        obj = getDefaultNG911CountyBoundaryObject("x")

    elif "ESZ" in word:
        # 2.1 & 2.0 are the same
        obj = getDefaultNG911ESZObject("x")

    elif "ESB" in word:
        # 2.1 & 2.0 are the same
        obj = getDefaultNG911ESBObject("x")

    # get various optional layers
    elif "PARCELS" in word:
        obj = getDefaultNG911ParcelObject("x")
    elif "GATES" in word:
        obj = getDefaultNG911GateObject("x")
    elif "HYDRANTS" in word:
        obj = getDefaultNG911HydrantObject("x")
    elif "CELL_SECTOR" in word or "CELLSECTORS" in word:
        obj = getDefaultNG911CellSectorObject("x")
    elif "BRIDGES" in word:
        obj = getDefaultNG911BridgeObject("x")
    elif "CELLSITE" in word:
        obj = getDefaultNG911CellSiteObject("x")
    elif word[0:3] == "UT_":
        obj = getDefaultNG911UtilityObject("x")

    elif word == "FIELDVALUESCHECKRESULTS":
        obj = getDefaultNG911FieldValuesCheckResultsObject()
    elif word == "TEMPLATECHECKRESULTS":
        obj = getDefaultNG911TemplateCheckResultsObject()

    return obj
