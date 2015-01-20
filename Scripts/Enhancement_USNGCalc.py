#-------------------------------------------------------------------------------
# Name:        USNG Field Calculator
# Purpose:      Calculate USNG field based on DD X and Y fields
#
# Author:       Sherry Massey with assist from Kristen Jordan
#
# Created:     01/04/2014
# Copyright:   (c) SMassey 2014
# Licence:     Subject to Creative Commons Attribution-ShareAlike 4.0 International Public License
#-------------------------------------------------------------------------------

def main():

    import CoordConvertor
    from arcpy import GetParameterAsText, AddMessage
    from arcpy.da import Editor, UpdateCursor
    from os.path import dirname

    ct = CoordConvertor.CoordTranslator()

    #declare parameter variables for feature class and
    #X and Y fields and the National Grid field
    fc = GetParameterAsText(0)
    xField = GetParameterAsText(1)
    yField = GetParameterAsText(2)
    NG = GetParameterAsText(3)

    #establish workspace
    path = dirname(fc)

    if '.gdb' in path:
        place = path.find('.gdb') + 4
    else:
        if '.mdb' in path:
            place = path.find('.mdb') + 4
        else:
            if '.sde' in path:
                place = path.find('.sde') + 4
            else:
                place = len(path) - 1

    workspace = path[:place]

    AddMessage(workspace)

    #Start an edit session
    edit = Editor(workspace)

    # Edit session is started without an undo/redo stack for versioned data
    #  (for second argument, use False for unversioned data)
    edit.startEditing(False, True)

    # Start an edit operation
    edit.startOperation()

    #define the field list
    fields = (xField, yField, NG)

    #calculate the NG coordinate for each row
    try:
        with UpdateCursor(fc, fields) as cursor:
            for row in cursor:
                x = row[0]
                y = row[1]
                if x is not None:
                    if y is not None:
                        row[2] = ct.AsMGRS([y,x], 5, False)
                cursor.updateRow(row)

        #release the locks on the data
        del row
        del cursor

    except:
        AddMessage("USNG coordinates could not be updated.")

    finally:
        # Stop the edit operation.
        edit.stopOperation()

        # Stop the edit session and save the changes
        edit.stopEditing(True)

if __name__ == '__main__':
    main()