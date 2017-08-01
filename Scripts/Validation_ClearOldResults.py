#-------------------------------------------------------------------------------
# Name:        NG911_ClearOldResults
# Purpose:     Delete rows indicating past errors
#
# Author:      kristen
#
# Created:     09/12/2014
#-------------------------------------------------------------------------------
from arcpy import GetParameterAsText, DeleteRows_management, Exists, AddMessage
from os.path import join, basename
from NG911_GDB_Objects import getGDBObject

def main():

    gdb = GetParameterAsText(0)
    templateTableClear = GetParameterAsText(1)
    fieldValuesTableClear = GetParameterAsText(2)

    ClearOldResults(gdb, templateTableClear, fieldValuesTableClear)

def ClearOldResults(gdb, templateTableClear, fieldValuesTableClear):

    gdbObject = getGDBObject(gdb)

    if templateTableClear == "true":
        templateTable = gdbObject.TemplateCheckResults
        if Exists(templateTable):
            DeleteRows_management(templateTable)
            AddMessage(basename(templateTable) + " cleared")
            print((basename(templateTable) + " cleared"))

    if fieldValuesTableClear == "true":
        fieldValuesTable = gdbObject.FieldValuesCheckResults
        if Exists(fieldValuesTable):
            DeleteRows_management(fieldValuesTable)
            AddMessage(basename(fieldValuesTable) + " cleared")
            print((basename(fieldValuesTable) + " cleared"))

if __name__ == '__main__':
    main()
