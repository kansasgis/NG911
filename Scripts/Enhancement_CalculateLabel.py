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
from NG911_GDB_Objects import getDefaultNG911AddressObject, getDefaultNG911RoadCenterlineObject

def main():
    layer = GetParameterAsText(0)
    updateBlanksOnly = GetParameterAsText(1)

    expression = ""
    a = ""
    field_list = []

    #define object & field list
    if basename(layer) == "RoadCenterline":
        a = getDefaultNG911RoadCenterlineObject()
        field_list = a.LABEL_FIELDS
    elif basename(layer) == "AddressPoints":
        a = getDefaultNG911AddressObject()
        field_list = a.LABEL_FIELDS
    else:
        userMessage(layer + " does not work with this tool. Please select the NG911 road centerline or address point file.")

    #make sure the object is something
    if a != "":
        #start at 1 since 0 is the label field itself
        i = 1

        #create the expression
        while i < len(field_list):
            #since the house number needs a string conversion, we need to have a slightly different expression for the first piece
            if i == 1:
                if basename(layer) == "AddressPoints":
                    expression = 'str(!' +  field_list[i] + '!) + " " + !'
                else:
                    expression = '!' + field_list[i] + '! + " " + !'

            else:
                expression = expression + field_list[i] + '! + " " + !'

            i += 1

        expression = expression[:-10]

    userMessage(expression)

    labelField = a.LABEL

    userMessage(labelField)

    if expression != "":
        lyr = "lyr"
        MakeFeatureLayer_management(layer, lyr)

        qry = labelField + " is null or " + labelField + " = '' or " + labelField + " = ' '"

        #select only the blank ones to update if that's what the user wanted
        if updateBlanksOnly == "true":
            SelectLayerByAttribute_management(lyr, "NEW_SELECTION", qry)

        userMessage("Calculating label...")
        CalculateField_management(lyr, labelField, expression, "PYTHON_9.3")

        #make sure no records were left behind
        SelectLayerByAttribute_management(lyr, "NEW_SELECTION", qry)
        result = GetCount_management(lyr)
        count = int(result.getOutput(0))

        #if the count is higher than 0, it means the table had null values in some of the concatonated fields
        if count > 0:
            gdb = dirname(dirname(layer))
            fields = tuple(field_list)

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
                            if row[start_int] not in ("", " "):
                                label = label + " " + str(row[start_int])
                        start_int = start_int + 1

                    row[0] = label
                    rows.updateRow(row)

            edit.stopEditing(True)


        #clean up all labels
        trim_expression = '" ".join(!' + labelField + '!.split())'
        CalculateField_management(layer, labelField, trim_expression, "PYTHON_9.3")

if __name__ == '__main__':
    main()
