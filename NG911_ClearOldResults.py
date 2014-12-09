#-------------------------------------------------------------------------------
# Name:        NG911_ClearOldResults
# Purpose:     Delete rows indicating past errors
#
# Author:      kristen
#
# Created:     09/12/2014
#-------------------------------------------------------------------------------

def main():
    from arcpy import GetParameterAsText, DeleteRows_management
    from NG911_DataCheck import userMessage
    from os.path import join

    gdb = GetParameterAsText(0)
    templateTableClear = GetParameterAsText(1)
    fieldValuesTableClear = GetParameterAsText(2)

    if templateTableClear == "true":
        templateTable = join(gdb, "TemplateCheckResults")
        DeleteRows_management(templateTable)
        userMessage("TemplateCheckResults cleared")

    if fieldValuesTableClear == "true":
        fieldValuesTable = join(gdb,"FieldValuesCheckResults")
        DeleteRows_management(fieldValuesTable)
        userMessage("FieldValuesCheckResults cleared")

if __name__ == '__main__':
    main()
