#-------------------------------------------------------------------------------
# Name:        NG911_ClearOldResults
# Purpose:     Delete rows indicating past errors
#
# Author:      kristen
#
# Created:     09/12/2014
#-------------------------------------------------------------------------------
from arcpy import GetParameterAsText, DeleteRows_management, Exists, AddMessage
from os.path import join

def main():

    gdb = GetParameterAsText(0)
    templateTableClear = GetParameterAsText(1)
    fieldValuesTableClear = GetParameterAsText(2)

    ClearOldResults(gdb, templateTableClear, fieldValuesTableClear)

def ClearOldResults(gdb, templateTableClear, fieldValuesTableClear):

    if templateTableClear == "true":
        templateTable = join(gdb, "TemplateCheckResults")
        if Exists(templateTable):
            DeleteRows_management(templateTable)
            AddMessage("TemplateCheckResults cleared")
            print("TemplateCheckResults cleared")

    if fieldValuesTableClear == "true":
        fieldValuesTable = join(gdb,"FieldValuesCheckResults")
        if Exists(fieldValuesTable):
            DeleteRows_management(fieldValuesTable)
            AddMessage("FieldValuesCheckResults cleared")
            print("FieldValuesCheckResults cleared")

if __name__ == '__main__':
    main()
