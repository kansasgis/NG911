#-------------------------------------------------------------------------------
# Name:        Conversion_NENA
# Purpose:     Converts address point file into NENA standard
#
# Author:      kristen
#
# Created:     September 30, 2019
# Based on standard found at:
# https://cdn.ymaws.com/www.nena.org/resource/resmgr/standards/nena-sta-006_ng9-1-1_gis_dat.pdf
#-------------------------------------------------------------------------------
from arcpy import (GetParameterAsText, CreateFeatureclass_management, 
                   AddField_management, Describe, CopyFeatures_management,
                   Delete_management, CalculateField_management,
                   Append_management, Exists, DeleteField_management)
from arcpy.da import UpdateCursor
from os.path import basename, dirname, join, realpath
from NG911_DataCheck import userMessage, getFieldDomain
from NG911_arcpy_shortcuts import fieldExists
from NG911_GDB_Objects import getFCObject

def addFields(out_fc):
    
    field_dict = [["DiscrpAgID", "TEXT", "Discrepancy Agency ID", 75],
                  ["DateUpdate", "DATE", "Date Updated"],
                  ["Effective", "DATE", "Effective Date"],
                  ["Expire", "DATE", "Expiration Date"],
                  ["Site_NGUID", "TEXT", "Site NENA Globally Unique ID", 254],
                  ["Country", "TEXT", "Country", 2],
                  ["State", "TEXT", "State", 2], 
                  ["County", "TEXT", "County", 40],
                  ["AddCode", "TEXT", "Additional Code", 6],
                  ["AddDataURI", "TEXT", "Additional Data URI", 254],
                  ["Inc_Muni", "TEXT", "Incorporated Municipality", 100],
                  ["Uninc_Comm", "TEXT", "Unincorporated Community", 100],
                  ["Nbrhd_Comm", "TEXT", "Neighborhood Community", 100],
                  ["AddNum_Pre", "TEXT", "Address Number Prefix", 15],
                  ["Add_Number", "LONG", "Address Number"],
                  ["AddNum_Suf", "TEXT", "Address Number Suffix", 15],
                  ["St_PreMod", "TEXT", "Street Name Pre Modifier",  15],
                  ["St_PreDir", "TEXT", "Street Name Pre Directional", 9],
                  ["St_PreTyp", "TEXT", "Street Name Pre Type", 50],
                  ["St_PreSep", "TEXT", "Street Name Pre Type Separator", 20],
                  ["St_Name", "TEXT", "Street Name", 60],
                  ["St_PosTyp", "TEXT", "Street Name Post Type", 50],
                  ["St_PosDir", "TEXT", "Street Name Post Directional", 9],
                  ["St_PosMod", "TEXT", "Street Name Post Modifier", 25],
                  ["ESN", "TEXT", "ESN", 5],
                  ["MSAGComm", "TEXT", "MSAG Community Name", 30],
                  ["Post_Comm", "TEXT", "Postal Community Name", 40],
                  ["Post_Code", "TEXT", "Postal Code", 7],
                  ["Post_Code4", "TEXT", "Zip Plus 4", 7],
                  ["Building", "TEXT", "Building", 75],
                  ["Floor", "TEXT", "Floor", 75],
                  ["Unit", "TEXT", "Unit", 75],
                  ["Room", "TEXT", "Room", 75],
                  ["Seat", "TEXT", "Seat", 75],
                  ["Addtl_Loc", "TEXT", "Additional Location Information", 225],
                  ["LandmkName", "TEXT", "Complete Landmark Name", 150],
                  ["Milepost", "TEXT", "Mile Post", 150],
                  ["Place_Type", "TEXT", "Place Type", 50],
                  ["Placement", "TEXT", "Placement Method", 25],
                  ["Long", "FLOAT", "Longitude"],
                  ["Lat", "FLOAT", "Latitude"],
                  ["Elev", "FLOAT", "Elevation"]]
            
    
    # loop through field dictionary
    for fld_info in field_dict:
        
        field_name = fld_info[0]
        fld_type = fld_info[1]
        alias = fld_info[2]
        
        # grab field into
        userMessage("Adding %s" % field_name)
       
        if len(fld_info) > 3:
            length = fld_info[3]
        else:
            length = ""
        
        # add field
        AddField_management(out_fc, field_name, fld_type, "", "", length, alias)
    
    # report back
    userMessage("Added all fields")
    
    
def convertFields(working_ap, a_obj):
    
    # ---------add fields & calculate full values for translating values
    leg_dict = {a_obj.PRD:["St_PreDir", 9, "PRD"],
                a_obj.STS:["St_PosTyp", 50, "STS"],
                a_obj.POD:["St_PosDir", 9, "POD"],
                a_obj.LOCTYPE:["Placement", 25, "NENA_LOCTYPE"]}

    # loop through the dictionary
    for field in leg_dict.keys():

        # set values for the new field
        new_field = leg_dict[field][0]
        length = leg_dict[field][1]

        # add the field
        AddField_management(working_ap, new_field, "TEXT", "", "", length)

        # get the domain as a dictionary
        domain_folder = join(dirname(dirname(realpath(__file__))), "Domains")
        domain = leg_dict[field][2]
        domain_dict = getFieldDomain(domain, domain_folder)
#        userMessage(domain_dict)

        wc = field + " not in ('', ' ') and " + field + " is not null"
        
        # update cursor to populate the new field
        with UpdateCursor(working_ap, (field, new_field), wc) as rows:
            for row in rows:

                # get the fully spelled out value from the domain, set to upper
                row[1] = domain_dict[row[0]].upper()
                rows.updateRow(row)

        try:
            del row, rows
        except:
            pass
        
    # create & populate field for site NGUID
    AddField_management(working_ap, "Site_NGUID", "TEXT", "", "", 254)
    CalculateField_management(working_ap, "Site_NGUID", "!STATE! + !STEWARD! + !NGADDID!", "PYTHON_9.3")
    

def main():

    # get variables
    ap = GetParameterAsText(0)
    out_fc = GetParameterAsText(1)
    working_ap = ap + "_working"
    
    a_obj = getFCObject(ap)
    
    # create working copy of the data
    if Exists(working_ap):
        Delete_management(working_ap)
    CopyFeatures_management(ap, working_ap)
    userMessage("Created working copy of the data.")
    
    # get the input spatial reference
    desc = Describe(ap)
    sr = desc.spatialReference
    
    userMessage("Creating NENA address points...")
    
    # create the output feature class
    if Exists(out_fc):
        Delete_management(out_fc)
    CreateFeatureclass_management(dirname(out_fc), basename(out_fc), "POINT", "", "", "", sr)
    addFields(out_fc)
    
    if fieldExists(out_fc, "Id"):
        DeleteField_management(out_fc, "Id")
    
    userMessage("Converting data to NENA format...")
    convertFields(working_ap, a_obj)
    
    # append data
    field_map = '''DiscrpAgID "Discrepancy Agency ID" true true false 75 Text 0 0 ,First,#;
        DateUpdate "Date Updated" true true false 8 Date 0 0 ,First,#,%s,L_UPDATE,-1,-1;
        Effective "Effective Date" true true false 8 Date 0 0 ,First,#,%s,EFF_DATE,-1,-1;
        Expire "Expiration Date" true true false 8 Date 0 0 ,First,#,%s,EXP_DATE,-1,-1;
        Site_NGUID "Site NENA Globally Unique ID" true true false 254 Text 0 0 ,First,#,%s,Site_NGUID,-1,-1;
        Country "Country" true true false 2 Text 0 0 ,First,#;
        State "State" true true false 2 Text 0 0 ,First,#,%s,STATE,-1,-1;
        County "County" true true false 40 Text 0 0 ,First,#,%s,COUNTY,-1,-1;
        AddCode "Additional Code" true true false 6 Text 0 0 ,First,#;
        AddDataURI "Additional Data URI" true true false 254 Text 0 0 ,First,#;
        Inc_Muni "Incorporated Municipality" true true false 100 Text 0 0 ,First,#,%s,MUNI,-1,-1;
        Uninc_Comm "Unincorporated Community" true true false 100 Text 0 0 ,First,#;
        Nbrhd_Comm "Neighborhood Community" true true false 100 Text 0 0 ,First,#;
        AddNum_Pre "Address Number Prefix" true true false 15 Text 0 0 ,First,#;
        Add_Number "Address Number" true true false 4 Long 0 0 ,First,#,%s,HNO,-1,-1;
        AddNum_Suf "Address Number Suffix" true true false 15 Text 0 0 ,First,#,%s,HNS,-1,-1;
        St_PreMod "Street Name Pre Modifier" true true false 15 Text 0 0 ,First,#;
        St_PreDir "Street Name Pre Directional" true true false 9 Text 0 0 ,First,#,%s,St_PreDir,-1,-1;
        St_PreTyp "Street Name Pre Type" true true false 50 Text 0 0 ,First,#,%s,STP,-1,-1;
        St_PreSep "Street Name Pre Type Separator" true true false 20 Text 0 0 ,First,#;
        St_Name "Street Name" true true false 60 Text 0 0 ,First,#,%s,RD,-1,-1;
        St_PosTyp "Street Name Post Type" true true false 50 Text 0 0 ,First,#,%s,St_PosTyp,-1,-1;
        St_PosDir "Street Name Post Directional" true true false 9 Text 0 0 ,First,#,%s,St_PosDir,-1,-1;
        St_PosMod "Street Name Post Modifier" true true false 25 Text 0 0 ,First,#,%s,POM,-1,-1;
        ESN "ESN" true true false 5 Text 0 0 ,First,#,%s,ESN,-1,-1;
        MSAGComm "MSAG Community Name" true true false 30 Text 0 0 ,First,#,%s,MSAGCO,-1,-1;
        Post_Comm "Postal Community Name" true true false 40 Text 0 0 ,First,#,%s,POSTCO,-1,-1;
        Post_Code "Postal Code" true true false 7 Text 0 0 ,First,#,%s,ZIP,-1,-1;
        Post_Code4 "Zip Plus 4" true true false 7 Text 0 0 ,First,#,%s,ZIP4,-1,-1;
        Building "Building" true true false 75 Text 0 0 ,First,#,%s,BLD,-1,-1;
        Floor "Floor" true true false 75 Text 0 0 ,First,#,%s,FLR,-1,-1;
        Unit "Unit" true true false 75 Text 0 0 ,First,#,%s,UNIT,-1,-1;
        Room "Room" true true false 75 Text 0 0 ,First,#,%s,ROOM,-1,-1;
        Seat "Seat" true true false 75 Text 0 0 ,First,#,%s,SEAT,-1,-1;
        Addtl_Loc "Additional Location Information" true true false 225 Text 0 0 ,First,#;
        LandmkName "Complete Landmark Name" true true false 150 Text 0 0 ,First,#;
        Milepost "Mile Post" true true false 150 Text 0 0 ,First,#,%s,MILEPOST,-1,-1;
        Place_Type "Place Type" true true false 50 Text 0 0 ,First,#;
        Placement "Placement Method" true true false 25 Text 0 0 ,First,#,%s,Placement,-1,-1;
        Long "Longitude" true true false 4 Float 0 0 ,First,#,%s,LONG,-1,-1;
        Lat "Latitude" true true false 4 Float 0 0 ,First,#,%s,LAT,-1,-1;
        Elev "Elevation" true true false 4 Float 0 0 ,First,#,%s,ELEV,-1,-1''' % (working_ap, working_ap, working_ap, working_ap, working_ap, working_ap, working_ap, working_ap, working_ap, working_ap,
     working_ap, working_ap, working_ap, working_ap, working_ap, working_ap, working_ap, working_ap, working_ap, working_ap,
     working_ap, working_ap, working_ap, working_ap, working_ap, working_ap, working_ap, working_ap, working_ap, working_ap)
    Append_management(working_ap, out_fc, "NO_TEST", field_map)
    
    # calculate country
    CalculateField_management(out_fc, "COUNTRY", '"US"', "PYTHON_9.3")
    
    # clean up
    Delete_management(working_ap)
    

if __name__ == '__main__':
    main()
    