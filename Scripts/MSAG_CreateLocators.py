#-------------------------------------------------------------------------------
# Name:        MSAG_CreateLocators
# Purpose:     Create composite locator using MSAG info from address points
#               and road centerlines
#
# Author:      kristen
#
# Created:     01/08/2016
#-------------------------------------------------------------------------------
# Creates a composite locator from the address points and road centerlines based on the MSAG field information

from os import mkdir
from os.path import exists, dirname, join, basename
from arcpy import (CreateFileGDB_management, Exists,
CreateAddressLocator_geocoding,
CreateCompositeAddressLocator_geocoding)
from arcpy import GetParameterAsText
from NG911_GDB_Objects import getGDBObject, getFCObject
from NG911_DataCheck import userMessage

def createLocators(gdb_object):
    addressPointPath = gdb_object.AddressPoints
    streetPath = gdb_object.RoadCenterline
    roadAliasPath = gdb_object.RoadAlias

    rc_obj = getFCObject(streetPath)
    ra_obj = getFCObject(roadAliasPath)

    tn_object = getTNObject(gdb_object.gdbPath)
    tn_gdb = tn_object.tn_gdb

    LocatorFolder = tn_object.LocatorFolder

    if not exists(LocatorFolder):
        mkdir(LocatorFolder)

    if not Exists(tn_gdb):
        CreateFileGDB_management(dirname(tn_gdb), basename(tn_gdb))

    AL1 = tn_object.AddressLocator
    AL2 = tn_object.RoadLocator
    AL3 = tn_object.CompositeLocator

    if not Exists(AL1):
        #Create address locator from NG911 Address points AL1, 10.3 - 10.4.1
        addyFieldMap = """'Feature ID' OBJECTID VISIBLE NONE;'*House Number' HNO VISIBLE NONE;Side <None> VISIBLE NONE;'Prefix Direction' PRD VISIBLE NONE;
            'Prefix Type' STP VISIBLE NONE;'*Street Name' RD VISIBLE NONE;'Suffix Type' STS VISIBLE NONE;'Suffix Direction' POD VISIBLE NONE;
            'City or Place' MSAGCO VISIBLE NONE;'ZIP Code' ZIP VISIBLE NONE;State STATE VISIBLE NONE;'Street ID' <None> VISIBLE NONE;'Display X' <None> VISIBLE NONE;
            'Display Y' <None> VISIBLE NONE;'Min X value for extent' <None> VISIBLE NONE;'Max X value for extent' <None> VISIBLE NONE;'Min Y value for extent' <None> VISIBLE NONE;
            'Max Y value for extent' <None> VISIBLE NONE;'Additional Field' <None> VISIBLE NONE;'Altname JoinID' <None> VISIBLE NONE"""

        # detect ArcGIS Version?
        # 10.5 addy field map
        addyFieldMap105 = """'Point Address ID' OBJECTID VISIBLE NONE;'Street ID' <None> VISIBLE NONE;'*House Number' HNO VISIBLE NONE;Side <None> VISIBLE NONE;
        'Full Street Name' LABEL VISIBLE NONE;'Prefix Direction' PRD VISIBLE NONE;'Prefix Type' STP VISIBLE NONE;'*Street Name' RD VISIBLE NONE;
        'Suffix Type' STS VISIBLE NONE;'Suffix Direction' POD VISIBLE NONE;'City or Place' MSAGCO VISIBLE NONE;County COUNTY VISIBLE NONE;State STATE VISIBLE NONE;
        'State Abbreviation' STATE VISIBLE NONE;'ZIP Code' ZIP VISIBLE NONE;'Country Code' <None> VISIBLE NONE;'3-Digit Language Code' <None> VISIBLE NONE;
        '2-Digit Language Code' <None> VISIBLE NONE;'Admin Language Code' <None> VISIBLE NONE;'Block ID' <None> VISIBLE NONE;'Street Rank' <None> VISIBLE NONE;
        'Display X' <None> VISIBLE NONE;'Display Y' <None> VISIBLE NONE;'Min X value for extent' <None> VISIBLE NONE;'Max X value for extent' <None> VISIBLE NONE;
        'Min Y value for extent' <None> VISIBLE NONE;'Max Y value for extent' <None> VISIBLE NONE;'Additional Field' <None> VISIBLE NONE;'Altname JoinID' <None> VISIBLE NONE;
        'City Altname JoinID' <None> VISIBLE NONE"""


        userMessage("Creating locator from address points...")

        try:
            CreateAddressLocator_geocoding("US Address - Single House", addressPointPath + " 'Primary Table'", addyFieldMap, AL1, "", "DISABLED")
        except:
            try:
                # use the 10.5 field map syntax
                CreateAddressLocator_geocoding("US Address - Single House", addressPointPath + " 'Primary Table'", addyFieldMap105, AL1, "", "DISABLED")
            except:
                try:
                    CreateAddressLocator_geocoding("US Address - Single House", addressPointPath + " 'Primary Table'", addyFieldMap, AL1, "")
                except:
                    userMessage("Could not create locator from address points.")

        #report on locator status and edit minimum match score down to 75
        if Exists(AL1):
            userMessage("Created locator from address points.")

        if not Exists(AL2):
            #Create address locator from NG911 Road centerline AL2
             #generate locator
            fieldMap = """'Primary Table:Feature ID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
            '*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;
            '*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;
            'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;
            'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;
            'Primary Table:Left City or Place' RoadCenterline:MSAGCO_L VISIBLE NONE;
            'Primary Table:Right City or Place' RoadCenterline:MSAGCO_R VISIBLE NONE;
            'Primary Table:Left ZIP Code' RoadCenterline:ZIP_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:ZIP_R VISIBLE NONE;
            'Primary Table:Left State' RoadCenterline:STATE_L VISIBLE NONE;'Primary Table:Right State' RoadCenterline:STATE_R VISIBLE NONE;
            'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;
            'Primary Table:Display X' <None> VISIBLE NONE;'Primary Table:Display Y' <None> VISIBLE NONE;
            'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;
            'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;
            'Primary Table:Left parity' <None> VISIBLE NONE;'Primary Table:Right parity' <None> VISIBLE NONE;
            'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;
            '*Primary Table:Altname JoinID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:""" + ra_obj.SEGID + """ VISIBLE NONE;
            'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' RoadAlias:A_STP VISIBLE NONE;
            'Alternate Name Table:Street Name' RoadAlias:A_RD VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;
            'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"""

            userMessage("Creating locator from road centerlines...")

            try:
                CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, AL2, "", "DISABLED")
            except:
                try:
                    fieldMap = """'Primary Table:Feature ID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
                        '*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;
                        '*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;
                        'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;
                        'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;
                        'Primary Table:Left City or Place' RoadCenterline:MSAGCO_L VISIBLE NONE;
                        'Primary Table:Right City or Place' RoadCenterline:MSAGCO_R VISIBLE NONE;
                        'Primary Table:Left ZIP Code' RoadCenterline:ZIP_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:ZIP_R VISIBLE NONE;
                        'Primary Table:Left State' RoadCenterline:STATE_L VISIBLE NONE;'Primary Table:Right State' RoadCenterline:STATE_R VISIBLE NONE;
                        'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;
                        'Primary Table:Display X' <None> VISIBLE NONE;'Primary Table:Display Y' <None> VISIBLE NONE;
                        'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;
                        'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;
                        'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;
                        '*Primary Table:Altname JoinID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:""" + ra_obj.SEGID + """ VISIBLE NONE;
                        'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' <None> VISIBLE NONE;
                        'Alternate Name Table:Street Name' RoadAlias:A_RD VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;
                        'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"""
                    CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, AL2, "", "DISABLED")
                except:
                    try:
                        fieldMap = """'Primary Table:Feature ID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
                            '*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;
                            '*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;
                            'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;
                            'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;
                            'Primary Table:Left City or Place' RoadCenterline:MSAGCO_L VISIBLE NONE;
                            'Primary Table:Right City or Place' RoadCenterline:MSAGCO_R VISIBLE NONE;
                            'Primary Table:Left ZIP Code' RoadCenterline:ZIP_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:ZIP_R VISIBLE NONE;
                            'Primary Table:Left State' RoadCenterline:STATE_L VISIBLE NONE;'Primary Table:Right State' RoadCenterline:STATE_R VISIBLE NONE;
                            'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;
                            'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;
                            'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;
                            'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;
                            'Primary Table:Altname JoinID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:""" + ra_obj.SEGID + """ VISIBLE NONE;
                            'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' <None> VISIBLE NONE;
                            'Alternate Name Table:Street Name' RoadAlias:A_RD VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;
                            'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"""
                        CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, AL2, "", "DISABLED")
                    except Exception as e:
                        try:
                            #10.3.x field map
                            fieldMap = """'Primary Table:Feature ID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
                            '*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;
                            '*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;
                            'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;'*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;
                            'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;
                            'Primary Table:Left City or Place' RoadCenterline:MSAGCO_L VISIBLE NONE;
                            'Primary Table:Right City or Place' RoadCenterline:MSAGCO_R VISIBLE NONE;
                            'Primary Table:Left ZIP Code' RoadCenterline:ZIP_L VISIBLE NONE;'Primary Table:Right ZIP Code' RoadCenterline:ZIP_R VISIBLE NONE;
                            'Primary Table:Left State' RoadCenterline:STATE_L VISIBLE NONE;'Primary Table:Right State' RoadCenterline:STATE_R VISIBLE NONE;
                            'Primary Table:Left Street ID' <None> VISIBLE NONE;'Primary Table:Right Street ID' <None> VISIBLE NONE;
                            'Primary Table:Display X' <None> VISIBLE NONE;'Primary Table:Display Y' <None> VISIBLE NONE;
                            'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;
                            'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;
                            'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;
                            'Primary Table:Altname JoinID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Alternate Name Table:JoinID' RoadAlias:""" + ra_obj.SEGID + """ VISIBLE NONE;
                            'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' RoadAlias:A_STP VISIBLE NONE;
                            'Alternate Name Table:Street Name' RoadAlias:A_RD VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;
                            'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"""
                            CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, AL2, "", "DISABLED")
                        except:
                            try:
                                # 10.5 field map
                                fieldMap = """'Primary Table:Feature ID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'*Primary Table:From Left' RoadCenterline:L_F_ADD VISIBLE NONE;
                                '*Primary Table:To Left' RoadCenterline:L_T_ADD VISIBLE NONE;'*Primary Table:From Right' RoadCenterline:R_F_ADD VISIBLE NONE;
                                '*Primary Table:To Right' RoadCenterline:R_T_ADD VISIBLE NONE;'Primary Table:Left Parity' RoadCenterline:PARITY_L VISIBLE NONE;
                                'Primary Table:Right Parity' RoadCenterline:PARITY_R VISIBLE NONE;'Primary Table:Full Street Name' RoadCenterline:LABEL VISIBLE NONE;
                                'Primary Table:Prefix Direction' RoadCenterline:PRD VISIBLE NONE;'Primary Table:Prefix Type' RoadCenterline:STP VISIBLE NONE;
                                '*Primary Table:Street Name' RoadCenterline:RD VISIBLE NONE;'Primary Table:Suffix Type' RoadCenterline:STS VISIBLE NONE;
                                'Primary Table:Suffix Direction' RoadCenterline:POD VISIBLE NONE;'Primary Table:Left City or Place' RoadCenterline:MSAGCO_L VISIBLE NONE;
                                'Primary Table:Right City or Place' RoadCenterline:MSAGCO_R VISIBLE NONE;'Primary Table:Left County' RoadCenterline:COUNTY_L VISIBLE NONE;
                                'Primary Table:Right County' RoadCenterline:COUNTY_R VISIBLE NONE;'Primary Table:Left State' RoadCenterline:STATE_L VISIBLE NONE;
                                'Primary Table:Right State' RoadCenterline:STATE_R VISIBLE NONE;'Primary Table:Left State Abbreviation' RoadCenterline:STATE_L VISIBLE NONE;
                                'Primary Table:Right State Abbreviation' RoadCenterline:STATE_R VISIBLE NONE;'Primary Table:Left ZIP Code' RoadCenterline:ZIP_L VISIBLE NONE;
                                'Primary Table:Right ZIP Code' RoadCenterline:ZIP_R VISIBLE NONE;'Primary Table:Country Code' <None> VISIBLE NONE;
                                'Primary Table:3-Digit Language Code' <None> VISIBLE NONE;'Primary Table:2-Digit Language Code' <None> VISIBLE NONE;
                                'Primary Table:Admin Language Code' <None> VISIBLE NONE;'Primary Table:Left Block ID' <None> VISIBLE NONE;
                                'Primary Table:Right Block ID' <None> VISIBLE NONE;'Primary Table:Left Street ID' <None> VISIBLE NONE;
                                'Primary Table:Right Street ID' <None> VISIBLE NONE;'Primary Table:Street Rank' <None> VISIBLE NONE;
                                'Primary Table:Min X value for extent' <None> VISIBLE NONE;'Primary Table:Max X value for extent' <None> VISIBLE NONE;
                                'Primary Table:Min Y value for extent' <None> VISIBLE NONE;'Primary Table:Max Y value for extent' <None> VISIBLE NONE;
                                'Primary Table:Left Additional Field' <None> VISIBLE NONE;'Primary Table:Right Additional Field' <None> VISIBLE NONE;
                                '*Primary Table:Altname JoinID' RoadCenterline:""" + rc_obj.UNIQUEID + """ VISIBLE NONE;'Primary Table:City Altname JoinID' <None> VISIBLE NONE;
                                '*Alternate Name Table:JoinID' RoadAlias:""" + ra_obj.SEGID + """ VISIBLE NONE;'Alternate Name Table:Full Street Name' RoadAlias:LABEL VISIBLE NONE;
                                'Alternate Name Table:Prefix Direction' RoadAlias:A_PRD VISIBLE NONE;'Alternate Name Table:Prefix Type' RoadAlias:A_STP VISIBLE NONE;
                                'Alternate Name Table:Street Name' RoadAlias:A_RD VISIBLE NONE;'Alternate Name Table:Suffix Type' RoadAlias:A_STS VISIBLE NONE;
                                'Alternate Name Table:Suffix Direction' RoadAlias:A_POD VISIBLE NONE"""
                                CreateAddressLocator_geocoding("US Address - Dual Ranges", streetPath + " 'Primary Table';" + roadAliasPath + " 'Alternate Name Table'", fieldMap, AL2, "", "DISABLED")
                            except:
                                userMessage("Could not create locator from road data. " + str(e))

            if Exists(AL2):
                userMessage("Created road centerline locator")

        #Create composite address locator from addresspoints/road centerline AL3
        if not Exists(AL3):
            if Exists(AL1) and Exists(AL2):
                userMessage("Creating composite address locator...")
                #address point locator first
##                compositeFieldMap = "Street \"Street or Intersection\" true true true 100 Text 0 0 ,First,#," + AL1 + ",Street,0,0," + AL2 + ",Street,0,0;City \"City or Placename\" true true false 40 Text 0 0 ,First,#,"  + \
##                    AL1 + ",City,0,0," + AL2 + ",City,0,0;State \"State\" true true false 20 Text 0 0 ,First,#," + AL1 + ",State,0,0," + AL2 + ",State,0,0;ZIP \"ZIP Code\" true true false 10 Text 0 0 ,First,#," + \
##                    AL1 + ",ZIP,0,0," + AL2 + ",ZIP,0,0"
##
##                CreateCompositeAddressLocator_geocoding(AL1 + " AddyPt;" + AL2 + " Roads", compositeFieldMap, "AddyPt #;Roads #", AL3)
                #road locator first
                compositeFieldMap = "Street \"Street or Intersection\" true true true 100 Text 0 0 ,First,#," + AL1 + ",Street,0,0," + AL2 + ",Street,0,0;City \"City or Placename\" true true false 40 Text 0 0 ,First,#,"  + \
                    AL1 + ",City,0,0," + AL2 + ",City,0,0;State \"State\" true true false 20 Text 0 0 ,First,#," + AL1 + ",State,0,0," + AL2 + ",State,0,0;ZIP \"ZIP Code\" true true false 10 Text 0 0 ,First,#," + \
                    AL1 + ",ZIP,0,0," + AL2 + ",ZIP,0,0"

                CreateCompositeAddressLocator_geocoding(AL2 + " Roads;" + AL1 + " AddyPt", compositeFieldMap, "Roads #;AddyPt #", AL3)

def main():

    gdb = GetParameterAsText(0)
    gdb_object = getGDBObject(gdb)

    createLocators(gdb_object)

if __name__ == '__main__':
    main()
