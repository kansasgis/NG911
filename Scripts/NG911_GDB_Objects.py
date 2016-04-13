#-------------------------------------------------------------------------------
# Name:        NG911_GDB_Objects
# Purpose:     Objects representing NG911 fields
#
# Author:      kristen
#
# Created:     April 13, 2016
#-------------------------------------------------------------------------------
# This is a class used represent the NG911 geodatabase
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
        self.FIELD_MAP = [self.STEWARD, self.L_UPDATE, self.EFF_DATE, self.EXP_DATE, self.ADDID, self.STATE, self.COUNTY, self.MUNI, self.HNO, self.HNS, self.PRD, self.STP,
                    self.RD, self.STS, self.POD, self.POM, self.ESN, self.MSAGCO, self.POSTCO, self.ZIP, self.ZIP4, self.BLD, self.FLR, self.UNIT, self.ROOM, self.SEAT, self.LMK,
                    self.LOC, self.PLC, self.LONG, self.LAT, self.ELEV, self.LABEL, self.UPDATEBY, self.LOCTYPE, self.USNGRID, self.KSPID, self.MILEPOST, self.ADDURI,
                    self.UNINC, self.SUBMIT, self.NOTES]


def getDefaultNG911AddressObject():

    NG911_Address_Default = NG911_Adddress_Object("STEWARD", "L_UPDATE", "EFF_DATE", "EXP_DATE", "ADDID", "STATE", "COUNTY", "MUNI", "HNO", "HNS", "PRD", "STP",
                    "RD", "STS", "POD", "POM", "ESN", "MSAGCO", "POSTCO", "ZIP", "ZIP4", "BLD", "FLR", "UNIT", "ROOM", "SEAT", "LMK",
                    "LOC", "PLC", "LONG", "LAT", "ELEV", "LABEL", "UPDATEBY", "LOCTYPE", "USNGRID", "KSPID", "MILEPOST", "ADDURI",
                    "UNINC", "SUBMIT", "NOTES")

    return NG911_Address_Default



