#-------------------------------------------------------------------------------
# Name:        Validation_UpdateDomains
# Purpose:     Updates domain files from master copies on GitHub
#
# Author:      kristen
#
# Created:     11/02/2015
# Copyright:   (c) kristen 2015
#-------------------------------------------------------------------------------
def getApprovedDomains():
    dList = ["AGENCYID_Domains.txt", "COUNTRY_Domains.txt", "COUNTY_Domains.txt", "LOCTYPE_Domains.txt", "MUNI_Domains.txt",
    "NG911_FieldDefinitions.txt", "NG911_RequiredFields.txt","ONEWAY_Domains.txt", "PARITY_Domains.txt", "PLC_Domains.txt",
    "POSTCO_Domains.txt", "PRD_Domains.txt", "RDCLASS_Domains.txt", "STATE_Domains.txt", "STATUS_Domains.txt", "STEWARD_Domains.txt",
    "STS_Domains.txt", "SURFACE_Domains.txt", "ZIP_Domains.txt"]

    return dList

def main():
    from arcpy import GetParameterAsText
    try:
        from urllib import urlretrieve
    except:
        from urllib.request import urlretrieve
    from os import listdir
    from os.path import basename, join, dirname, realpath

    #get domain folder
    domainFolder = join(dirname(dirname(realpath(__file__))), "Domains")

    rootURL = r'https://raw.githubusercontent.com/kansasgis/NG911/master/Domains/'

    #list current domain files
    files = listdir(domainFolder)
    approvedDomains = getApprovedDomains()

    #loop through domain files
    for file1 in files:
        #make sure file is a text file
        if file1[-3:] == "txt":

            #make sure this is a file we want to work with
            if file1 in approvedDomains:
                #create full path name
                fullfile = join(domainFolder, file1)

                #build url
                url = rootURL + file1

                #save copy of new file
                try:
                    urlretrieve(url, fullfile)
                except:
                    "Error updating domain " + file1

if __name__ == '__main__':
    main()
