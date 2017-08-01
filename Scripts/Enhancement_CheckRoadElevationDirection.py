#-------------------------------------------------------------------------------
# Name:        Enhancement_CheckRoadElevationDirection
# Purpose:     Looks at roads to see if the elevation/bridge attributes are assigned correctly
#
# Author:      kristen
#
# Created:     10/09/2015
#-------------------------------------------------------------------------------
#import modules
from arcpy import MakeFeatureLayer_management, GetParameterAsText
from arcpy.da import SearchCursor
from NG911_arcpy_shortcuts import fieldExists
from NG911_DataCheck import RecordResults, userMessage
from os.path import join
from time import strftime
from NG911_GDB_Objects import getFCObject, getGDBObject

def main():
    gdb = GetParameterAsText(0)

    #set variables
    gdb_object = getGDBObject(gdb)
    roads = gdb_object.RoadCenterline
    a_obj = getFCObject(roads)

    #userMessage
    userMessage("Comparing elevation indicators...")

    #limit records to those with elevation flags
    qry = a_obj.ELEV_F + " = 1 or " + a_obj.ELEV_T + " = 1"

    #set up search cursor
    roadFullDict = {}
    fields = (a_obj.UNIQUEID, a_obj.LABEL, a_obj.ELEV_F, a_obj.ELEV_T, a_obj.L_F_ADD)

    with SearchCursor(roads, fields, qry) as rows:
        for row in rows:
            label = row[1]

            #create a list from the segID and a string concatonation of the elev_f & elev_t
            f_t = [row[0], str(row[2]) + str(row[3])]

            #KJK theory, get the lowest left address point to sort addresses based on range
            leftFrom = row[4]

            #see if label is already a key in the dictionary
            if label not in roadFullDict:

                #if it isn't, create new sub dictionary
                subDict = {leftFrom:f_t}
                roadFullDict[label] = subDict

            #if it is in the dictionary already, add the new info
            else:
                subDict = roadFullDict[label]
                subDict[leftFrom] = f_t

    badSegs = []

    #loop through the road labels
    for label in roadFullDict:
        elevInfo = roadFullDict[label]

        elevString = ""
        segIDlist = []
        ftelevList = []
        stringsum = 0

        #sort elevInfo based on the keys (keys are the left from address)
        for l_from in sorted(elevInfo):

            ftList = elevInfo[l_from]
            segIDlist.append(ftList[0])
            ftelevList.append(ftList[1])
            #calculate the string sum (why? see below for notes)
            stringsum = stringsum + int(ftList[1][0]) + int(ftList[1][1])

        #KJK theory, based on the number of segments, we can get info about what the concatonated elevation string should look like
        #for example, with two segments, the elevation string should look ideally like "0110", for three segments "011110", for four segments "01111110", etc.
        #each of those segments have a total sum of digits. Two segments = 2, three segments = 4, four segments = 6
        #basically the ideal count is 2 times the number of segments minus 2
        #if the real count doesn't match the ideal count, it's a trigger that something is wrong
        #for example for two segments: real segment = "0111", count = 3, doesn't match ideal count of 2, something is wrong
        #example for three segments: real segment = "011010", count = 3, doesn't match ideal count of 4, something is wrong
        count = len(segIDlist)
        idealStringSum = (2 * count) - 2

        if count == 1:
            #get segID and report to table
            badSegs.append(segIDlist[0])
        else:
            #complete the check here to see if the real string sum doesn't match the ideal string sum
            if stringsum != idealStringSum:
                #create a full concatonated real string
                ftelev = "".join(ftelevList)
                length = len(ftelev)
                #flag if the first digit is wrong (should be 0)
                if ftelev[0] == "1":
                    badSegs.append(segIDlist[0])

                #flag if the last digit is wrong (should be 0)
                if ftelev[-1] == "1":
                    badSegs.append(segIDlist[-1])

                #here's the check to see about the inside 1's (not applicable to two segment comparisons)
                if length > 4:
                    #need to use multiple counter loops to later link the error location back to the original segment ID
                    looper = 2
                    index = 1

                    while looper < length:
                        #compare digits in sets
                        if ftelev[looper:looper+2] != "11":
                            badSegs.append(segIDlist[index])
                        looper = looper + 2
                        index = index + 1

    #record issues if any exist
    values = []
    resultType = "fieldValues"
    today = strftime("%m/%d/%y")
    fc = "RoadCenterline"
    report = a_obj.ELEV_F + " and:or " + a_obj.ELEV_T + " are not consistent with neighboring road segments"

    if len(badSegs) > 0:
        for badSeg in badSegs:
            val = (today, report, fc, a_obj.ELEV_F + " " + a_obj.ELEV_T, badSeg, "Check Road Elevation Direction")
            values.append(val)

    if values != []:
        RecordResults(resultType, values, gdb)
        userMessage("Check complete. " + str(len(badSegs)) + " issues found. See table FieldValuesCheckResults for results.")
    else:
        userMessage("Check complete. Elevation indicators matched correctly.")


if __name__ == '__main__':
    main()
