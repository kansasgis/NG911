#-------------------------------------------------------------------------------
# Name:        Enhancement_VerifyRoadAlias
# Purpose:     See if the road alias values for highways are the approved names
#
# Author:      kristen
#
# Created:     21/12/2015
#-------------------------------------------------------------------------------
from arcpy import GetParameterAsText, AddMessage
from arcpy.da import SearchCursor
from os.path import join, exists
from NG911_DataCheck import RecordResults, userMessage
from time import strftime

def getNumbers():
    numbers = "0123456789"
    return numbers


def main():
    gdb = GetParameterAsText(0)
    domainFolder = GetParameterAsText(1)

    #set up variables for search cursor
    roadAlias = join(gdb, "RoadAlias")
    fieldList = ('A_RD', 'ALIASID')

    #get highway values
    hwy_text = join(domainFolder, "KS_HWY.txt")

    hwy_dict = {}

    #make sure file path exists
    if exists(hwy_text):
        fieldDefDoc = open(hwy_text, "r")

        #get the header information
        headerLine = fieldDefDoc.readline()
        valueList = headerLine.split("|")
        ## print valueList

        #get field indexes
        rNameIndex = valueList.index("ROUTENAME")
        rNumIndex = valueList.index("ROUTENUM\n")

        #parse the text to populate the field definition dictionary
        for line in fieldDefDoc.readlines():
            stuffList = line.split("|")

            #set up values
            route_num = stuffList[1].rstrip()
            route_name = stuffList[0]

            #see if the road list already exists in the hwy dictionary
            if route_num not in hwy_dict:
                nameList = [route_name]
            else:
                nameList = hwy_dict[route_num]
                nameList.append(route_name)

            #set dictionary value to name list
            hwy_dict[route_num] = nameList

    #get variables set up
    #where clause for the search cursor
    wc = "A_STS is null or A_STS in ('HWY', '', ' ')"

    #variables for error reporting
    errorList = []
    values = []
    filename = "RoadAlias"
    field = "A_RD"
    recordType = "fieldValues"
    today = strftime("%m/%d/%y")

    #get a list of numbers
    numbers = getNumbers()

    #start search cursor to examine records
    with SearchCursor(roadAlias, fieldList, wc) as rows:
        for row in rows:

            road = row[0]
            first_char = road[0]

            #see if first character indicates a highway
            if first_char in "IUK0123456789":

                for n in numbers:

                    #see if the road name has numbers in it
                    if n in road:

                        roadNum = road #working variable to strip out all alphabet characters
                        fID = row[1] #road alias ID for reporting

                        #get just the road number with no other characters
                        for r in roadNum:
                            if r not in numbers:
                                roadNum = roadNum.replace(r, "")

                        #see if the road number is in the highway dictionary
                        if roadNum in hwy_dict:
                            if road not in hwy_dict[roadNum]:
                                if road not in errorList:
                                    report = road + " is not in the approved highway name list"
                                    val = (today, report, filename, field, fID)
                                    values.append(val)
                                    errorList.append(road)


    #report records
    if values != []:
        #set up custom error count message
        count = len(errorList)
        if count > 1:
            countReport = "There were " + str(count) + " issues. "
        else:
            countReport = "There was 1 issue. "

        RecordResults(recordType, values, gdb)
        userMessage("Checked highways in the road alias table. " + countReport + "Results are in table FieldValuesCheckResults")
    else:
        userMessage("Checked highways in the road alias table. No errors were found.")

if __name__ == '__main__':
    main()
