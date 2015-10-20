#-------------------------------------------------------------------------------
# Name:        NG911_ClearOldResults
# Purpose:     Delete rows indicating past errors
#
# Author:      kristen
#
# Created:     09/12/2014
#-------------------------------------------------------------------------------
from arcpy import GetParameterAsText, DeleteRows_management, Exists
from NG911_DataCheck import userMessage
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
            userMessage("TemplateCheckResults cleared")

    if fieldValuesTableClear == "true":
        fieldValuesTable = join(gdb,"FieldValuesCheckResults")
        if Exists(fieldValuesTable):
            DeleteRows_management(fieldValuesTable)
            userMessage("FieldValuesCheckResults cleared")

if __name__ == '__main__':
    main()
