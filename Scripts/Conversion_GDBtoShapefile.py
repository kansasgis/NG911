#-------------------------------------------------------------------------------
# Name:        Conversion_GDBtoShapefile
# Purpose:     Converts all geodatabase tables and feature classes to dbf's and shapefiles
#
# Author:      kristen
#
# Created:     09/02/2015
#-------------------------------------------------------------------------------

def main():
    from arcpy import GetParameterAsText, ListFeatureClasses, CopyFeatures_management, CopyRows_management, env
    from os.path import join

    #get variables
    gdb = GetParameterAsText(0)
    outputFolder = GetParameterAsText(1)

    #set workspace
    env.workspace = join(gdb, "NG911")

    #list all feature classes
    fcs = ListFeatureClasses()

    #loop through feature classes
    for fc in fcs:
        #create output name
        outFC = join(outputFolder, fc + ".shp")
        #copy features
        CopyFeatures_management(fc, outFC)

    #set variabes for road alias table
    roadAliasTable = join(gdb, "RoadAlias")
    outRoadAliasTable = join(outputFolder, "RoadAlias.dbf")

    #copy road alias table
    CopyRows_management(roadAliasTable, outRoadAliasTable)

if __name__ == '__main__':
    main()
