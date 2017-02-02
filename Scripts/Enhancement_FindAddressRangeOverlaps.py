#-------------------------------------------------------------------------------
# Name:        Enhancement_FindAddressRangeOverlaps.py
# Purpose:     This script finds and marks address range overlaps in a road centerline file.
#
#Original script written by Matt Francis
#Original script downloaded by Kristen Jordan-Koenig on Sept. 9, 2015
#http://arcscripts.esri.com/details.asp?dbid=15082

# This script searches an input feature class finding and marking
# address range overlaps.  It would also do a parity check, and a check for mismatched
# ranges, but the results aren't used, so that's currently disabled
# A table view of the unique street names having a count > 1 are compared for
# overlapping address ranges.  Records are loaded into a python dictionary of lists like this:
# ... {STOVER CREEK: [241, 3700, 3713, 214, 3800, 3809] ... }
# The list[] contains a repeating pattern of a record's ObjectID, LOW address value and HIGH address value
# It is in no particular order, so it must be sorted before comparison.
# I have implemented a reverse "bubble" sort routine that isn't the most efficient
# however, my implementation will run through 25,000 records and generate an output file in 1 minute.
# (on my laptop with 1.8ghz processer, 1gig RAM, Python 2.4, ArcGIS 9.2)

#Updating and improvements by Kristen Jordan-Koenig with the Kansas Data Access and Support Center, kristen@kgs.ku.edu
#-------------------------------------------------------------------------------

# Import modules
##from arcpy import (env, GetParameterAsText, ListFields, MakeTableView_management,
##        MakeFeatureLayer_management, SelectLayerByAttribute_management, Delete_management,
##        CopyFeatures_management, Exists, Append_management, AddWarning, Dissolve_management)
##from arcpy.da import SearchCursor
##from os.path import join
##from NG911_GDB_Objects import getFCObject, getGDBObject
##from NG911_arcpy_shortcuts import fieldExists
##from time import strftime
from arcpy import GetParameterAsText
from NG911_DataCheck import FindOverlaps

def main():
    # Set important parameters here
    working_gdb = GetParameterAsText(0)
    FindOverlaps(working_gdb)

if __name__ == '__main__':
    main()
