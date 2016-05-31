#-------------------------------------------------------------------------------
# Name:        NG911_GDB_Objects
# Purpose:     Objects representing NG911 fields
#
# Author:      kristen
#
# Created:     April 13, 2016
#-------------------------------------------------------------------------------
# This is a class used represent the NG911 geodatabase
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

class NG911_Adddress_Object(object):

    def __init__(self, u_STEWARD, u_L_UPDATE, u_EFF_DATE, u_EXP_DATE, u_ADDID, u_STATE, u_COUNTY, u_MUNI, u_HNO, u_HNS, u_PRD, u_STP,
                    u_RD, u_STS, u_POD, u_POM, u_ESN, u_MSAGCO, u_POSTCO, u_ZIP, u_ZIP4, u_BLD, u_FLR, u_UNIT, u_ROOM, u_SEAT, u_LMK,
                    u_LOC, u_PLC, u_LONG, u_LAT, u_ELEV, u_LABEL, u_UPDATEBY, u_LOCTYPE, u_USNGRID, u_KSPID, u_MILEPOST, u_ADDURI,
                    u_UNINC, u_SUBMIT, u_NOTES):

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

def getDefaultNG911AddressObject():

    NG911_Address_Default = NG911_Adddress_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "ADDID", "STATE", "COUNTY", "MUNI", "HNO", "HNS", "PRD", "STP",
                    "RD", "STS", "POD", "POM", "ESN", "MSAGCO", "POSTCO", "ZIP", "ZIP4", "BLD", "FLR", "UNIT", "ROOM", "SEAT", "LMK",
                    "LOC", "PLC", "LONG", "LAT", "ELEV", "LABEL", "UPDATEBY", "LOCTYPE", "USNGRID", "KSPID", "MILEPOST", "ADDURI",
                    "UNINC", "SUBMIT", "NOTES")

    return NG911_Address_Default

class NG911_GeocodeExceptions_Object(object):

    def __init__(self, u_ADDID, u_LABEL, u_NOTES):

        self.ADDID = u_ADDID
        self.LABEL = u_LABEL
        self.NOTES = u_NOTES


def getDefaultNG911GeocodeExceptionsObject():

    NG911_GeocodeExceptions_Default = NG911_GeocodeExceptions_Object("ADDID", "LABEL", "NOTES")

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

