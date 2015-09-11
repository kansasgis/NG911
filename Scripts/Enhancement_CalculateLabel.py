#-------------------------------------------------------------------------------
# Name:        Enhancement_CalculateLabel
# Purpose:     Calculates the label field for input
#
# Author:      kristen
#
# Created:     11/09/2015
#-------------------------------------------------------------------------------

#import modules
from arcpy import GetParameterAsText, Exists, CalculateField_management, MakeFeatureLayer_management, SelectLayerByAttribute_management, GetCount_management
from arcpy.da import UpdateCursor, Editor
from os.path import basename, dirname
from NG911_DataCheck import userMessage

def main():
    layer = GetParameterAsText(0)
    updateBlanksOnly = GetParameterAsText(1)

    expression = ""

    #define the expression
    if basename(layer) == "RoadCenterline":
        expression = '!PRD! + " " + !STP! + " " + !RD! + " " + !STS! + " " + !POD! + " " + !POM!'
    elif basename(layer) == "AddressPoints":
        expression = '!HNO! + " " + !HNS! + " " + !PRD! + " " + !STP! + " " + !RD! + " " + !STS! + " " + !POD! + " " + !POM!'

    else:
        userMessage(layer + " does not work with this tool. Please select the NG911 road centerline or address point file.")

    if expression != "":
        lyr = "lyr"
        MakeFeatureLayer_management(layer, lyr)

        #select only the blank ones to update if that's what the user wanted
        if updateBlanksOnly == "true":
            qry = "LABEL is null or LABEL = '' or LABEL = ' '"
            SelectLayerByAttribute_management(lyr, "NEW_SELECTION", qry)

        userMessage("Calculating label...")
        CalculateField_management(lyr, "LABEL", expression, "PYTHON_9.3")

        #make sure no records were left behind
        SelectLayerByAttribute_management(lyr, "NEW_SELECTION", qry)
        result = GetCount_management(lyr)
        count = int(result.getOutput(0))

        #if the count is higher than 0, it means the table had null values in some of the concatonated fields
        if count > 0:
            gdb = dirname(dirname(layer))
            if basename(layer) == "RoadCenterline":
                fields = ("LABEL", "PRD", "STP", "RD", "STS", "POD", "POM")
            elif basename(layer) == "AddressPoints":
                fields = ("LABEL", "HNO", "HNS","PRD","STP","RD","STS","POD","POM")

            #start edit session
            edit = Editor(gdb)
            edit.startEditing(False, False)

            #run update cursor
            with UpdateCursor(layer, fields, qry) as rows:
                for row in rows:
                    field_count = len(fields)
                    start_int = 1
                    label = ""

                    #loop through the fields to see what's null & skip it
                    while start_int < field_count:
                        if row[start_int] is not None:
                            label = label + " " + row[start_int]
                        start_int = start_int + 1

                    row[0] = label
                    rows.updateRow(row)

            edit.stopEditing(True)


        #clean up all labels
        trim_expression = '" ".join(!LABEL!.split())'
        CalculateField_management(layer, "LABEL", trim_expression, "PYTHON_9.3")

if __name__ == '__main__':
    main()
