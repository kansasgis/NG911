#-------------------------------------------------------------------------------
# Name:        Enhancement_CheckESNAttribute
# Purpose:     Checks address points to make sure they are attributed with the correct ESN zone
#
# Author:      kristen
#
# Created:     10/09/2015
#-------------------------------------------------------------------------------

#import modules
from arcpy import GetParameterAsText, SelectLayerByLocation_management, MakeFeatureLayer_management, Delete_management
from arcpy.da import SearchCursor
from NG911_Config import getGDBObject
from NG911_DataCheck import RecordResults, userMessage
from time import strftime

def main():
    NG911gdb = GetParameterAsText(0)
    esz = GetParameterAsText(1)

    gdb_object = getGDBObject(NG911gdb)

    address_points = gdb_object.AddressPoints

    addy_lyr = "addy_lyr"
    MakeFeatureLayer_management(address_points, addy_lyr)

    values = []
    recordType = "fieldValues"
    today = strftime("%m/%d/%y")
    filename = "AddressPoints"

    with SearchCursor(esz, ("ESN", "OBJECTID")) as polys:
        for poly in polys:
            esn = poly[0]

            #make feature layer
            esz_lyr = "esz_lyr"
            qry = "OBJECTID = " + str(poly[1])
            MakeFeatureLayer_management(esz, esz_lyr, qry)

            #select by location
            SelectLayerByLocation_management(addy_lyr, "INTERSECT", esz_lyr)

            #loop through address points
            with SearchCursor(addy_lyr, ("ESN", "ADDID")) as rows:
                for row in rows:
                    #get ESN
                    esn_addy = row[0]

                    #see if the esns match
                    if esn_addy != esn:
                        segID = row[1]

                        report = "Address point ESN does not match ESN in ESZ layer"
                        val = (today, report, filename, "", segID)
                        values.append(val)


            Delete_management(esz_lyr)

    #report records
    if values != []:
        RecordResults(recordType, values, NG911gdb)
        userMessage("Check complete. " + str(len(values)) + " issues found. Results are in the FieldValuesCheckResults table.")
    else:
        userMessage("Check complete. No issues found.")


if __name__ == '__main__':
    main()
