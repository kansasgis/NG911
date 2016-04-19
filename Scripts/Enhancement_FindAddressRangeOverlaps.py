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
from arcpy import env, GetParameterAsText, ListFields, MakeTableView_management, MakeFeatureLayer_management, SelectLayerByAttribute_management, CopyFeatures_management, Exists, Append_management
from arcpy.da import SearchCursor
from NG911_Config import getGDBObject
from NG911_DataCheck import userMessage
from os.path import join
from NG911_GDB_Objects import getDefaultNG911RoadCenterlineObject

# Set important parameters here
working_gdb = GetParameterAsText(0)

#get gdb object
gdb_object = getGDBObject(working_gdb)

env.workspace = working_gdb
input_fc = gdb_object.RoadCenterline         # Our street centerline feature class
output_fc = join(gdb_object.gdbPath, "AddressRange_Overlap")
a = getDefaultNG911RoadCenterlineObject()
name_field = a.LABEL   # Should be concatenated with pre/post directionals and type
left_from = a.L_F_ADD         # The left from address field
left_to = a.L_T_ADD            # The left to address field
right_from = a.R_F_ADD        # The right from address field
right_to = a.R_T_ADD            # The right to address field
OID_field = "OBJECTID"

try:
    # Allow arcpy to overwrite something if it's already there
    env.overwriteOutput = True

    parityList = ["('E','B')", "('O','B')"]

    for parity in parityList:

        # --- Parity check ---
    ##    parity_sql = left_from + " <> " + left_to + " or " + right_from +" <> " + right_to
        parity_sql = a.PARITY_L + " in " + parity + " AND " + a.PARITY_R + " in " + parity

        # Create search cursor to loop through unique road names
        overlap_list = []   # List to store the OIDs of overlapping segments
        overlap_error_count = 0
        overlap_error_total = 0
        overlap_string = ""
        o_string = ""
        overlap_sql = ""
        dictionary = {}     # Place to store data before heavy lifting

        #set up data for search cursor
        fields = (name_field, OID_field, left_from, left_to, right_from, right_to, a.MUNI_L, a.MUNI_R)
        userMessage("Loading data into a dictionary")

        with SearchCursor(input_fc, fields, parity_sql) as segments:
            for segment in segments:

                # get the highest and lowest values from the four address values
                addresses = [segment[2],segment[3],segment[4],segment[5]]

                cur_road_HIGH = 0
                # print "Summary for segment: "str(segment.GetValue(name_field)), str(addresses)
                for a in range(4):
                    curaddr = addresses[a]
                    if (curaddr > cur_road_HIGH and curaddr <> 0):
                        cur_road_HIGH = curaddr
                    lowval = cur_road_HIGH
                for a in range(4):
                    curaddr = addresses[a]
                    if (curaddr < lowval and curaddr <> 0):
                        lowval = curaddr
                        cur_road_LOW = lowval
                cur_road_name = segment[0] + segment[6] + segment[7]
                cur_road_OID = segment[1]
                # print cur_road_name, cur_road_LOW, cur_road_HIGH
                if cur_road_HIGH > 0:   # drop dumb record that fouls up things anyways :)
                    append_list = []    # clear out the list
                    # check if dictionary key exists
                    if dictionary.has_key (str(cur_road_name)) == 0:
                        # add the dictionary key and populate it with values
                        cur_road_list = [cur_road_OID, cur_road_LOW, cur_road_HIGH]
                        dictionary[cur_road_name] = cur_road_list
                    else:   # append the values to the list
                        cur_road_list = dictionary[cur_road_name]
                        cur_road_list.append(cur_road_OID)
                        cur_road_list.append(cur_road_LOW)
                        cur_road_list.append(cur_road_HIGH)
                        dictionary[cur_road_name] = cur_road_list

        userMessage("Sorting address ranges")
        lyr = "lyr"
        MakeFeatureLayer_management(input_fc, lyr, parity_sql)
        for key, value in dictionary.iteritems():
            # dictionary {} is structured thusly:
            # ... {STOVER CREEK: [241, 3700, 3713, 214, 3800, 3809] ... }
            # therefore, the logic is to step through each dictionary entry (STOVER CREEK) and
            # 1) sort the list
            # 2) compare high and low items
            list_length = len(value)
            if list_length > 3: # disregarding single-segment roads
                loop = list_length/3
                #
                # Sort!
                # This is Matt's braindead sort routine.
                # If value[1] < value[4] (Low of record 1 is greater than the low of record 2)
                #    then pop it out of the list, and append it to the end of the stack.
                # Keep popping and the lowest record gravitates to the front.
                # Skip and pop until the highest record gravitates to the end.
                # This is NOT an efficient routine, but since I'm sorting on
                # average something like six records, it can't get much faster
                #
                # For reference:
                # {key: [OID_element1, low_element1, high_element1, OID_element2, low_element2, high_element2, ... ]
                # OID_element1 = ((i+1)*3-3)
                # low_element1 = ((i+1)*3-2)
                # high_element1 = ((i+1)*3-1)
                # OID_element2 = ((i+1)*3)
                # low_element2 = ((i+1)*3+1)
                # high_element2 = ((i+1)*3+2)
                #
                i = 0
                while i < loop - 1:
                    if value[((i+1)*3-2)] > value[((i+1)*3+1)]:
                        value.append(value.pop(((i+1)*3-3))) # first item in sequence is (objectID)--stick it at the end
                        value.append(value.pop(((i+1)*3-3))) # first item in sequence is now (LOW)--stick it at the end
                        value.append(value.pop(((i+1)*3-3))) # first item in sequence is now (HIGH)--stick it at the end
                        i = 0 # since we had to re-order, redo the whole comparison from the beginning.
                    else: i = i + 1
                # loop through the records searching for discrepancies
                for k in range(loop - 1):
                    if value[((k+1)*3+1)] < value[((k+1)*3-1)]:
                        # print k, key, value[((k+1)*3-1)], "should be smaller than ", value[((k+1)*3+1)]
                        overlap_list.append(value[((k+1)*3-3)])
                        overlap_list.append(value[((k+1)*3)])
                        overlap_error_count = overlap_error_count + 1
                        overlap_error_total = overlap_error_total + 1
                    # PLACEHOLDER should you want to search for gaps, here's where you would put the loop
                if overlap_error_count > 500: # a tad arbitrary here
                    # My first idea was to create a Select * from Roads where ObjectID in (...) query.  Unfortunately,
                    # it could be quite long, and needs to be broken into a more manageable size.
                    for x in overlap_list:
                        o_string = o_string + str(x) +", "              # constructing a comma-seperated list of OIDs
                    overlap_string = o_string[0:-2]
                    overlap_sql = OID_field +" in (" + overlap_string + ")" # constructing the complete SQL statement

                    overlap_error_total = overlap_error_total + overlap_error_count
                    userMessage("The number of errors exceeds " +str(overlap_error_total))
                    userMessage("Adding these features to a feature layer")

                    SelectLayerByAttribute_management(lyr, "ADD_TO_SELECTION", str(overlap_sql))
                    overlap_error_count = 0
                    overlap_list = []
        # above logic breaks the sql into smaller chunks
        # deal with the remainders outside the while loop here
        if len(overlap_list) > 0:
            for x in overlap_list:
                o_string = o_string + str(x) +", "       # constructing a comma-seperated list of OIDs
            overlap_string = o_string[0:-2]     # the last character added is a problematic trailling comma
            overlap_sql = OID_field + " in (" + overlap_string + ")" # constructing the complete SQL statement

            # print overlap_sql
            userMessage("The final count of errors processed is "+str(overlap_error_total))
            userMessage("Adding the remaining features to a feature layer")

            SelectLayerByAttribute_management(lyr, "ADD_TO_SELECTION", overlap_sql)

            userMessage("Exporting data into a new feature class")
            if not Exists(output_fc):
                CopyFeatures_management(lyr, str(output_fc))
            else:
                Append_management(lyr, output_fc, "NO_TEST")
            userMessage("Overlapping address ranges in: " + output_fc)

        else:
            userMessage("No overlaps found. Good job!")

except "FieldError":
    userMessage("Fields in the input table: " + input_fc + " do not exist")
