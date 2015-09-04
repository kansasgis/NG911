#-------------------------------------------------------------------------------
# Name:        Conversion_ZipNG911Geodatabase
# Purpose:     Zip an NG911 geodatabase to prepare for submission.
#
# Author:      kristen
#
# Created:     04/09/2015
#-------------------------------------------------------------------------------
import zipfile
from os import listdir, remove
from os.path import basename, join, exists
from NG911_DataCheck import userMessage
from arcpy import GetParameterAsText

def createNG911Zip(gdb, path):
    #path = resulting zip file
    #toZip = file intended to be zipped
    #mode- 'w' for write, 'a' for append
    #from http://www.doughellmann.com/PyMOTW/zipfile/

    folder = basename(gdb)

    if exists(path):
        remove(path)

    #get all files in geodatabase
    files = listdir(gdb)

    #loop through files and zip
    i = 0 #for the first file, this flag will make the zip file write, the zip file will append for subsequent files

    #flag for issues
    issue_flag = 0
    for f in files:
        if f[-4:] != "lock":
            #append if the zip file already exists, write if it's new
            mode = "a"
            if i == 0:
                mode = "w"

            #create full path to the file to zip
            toZip = join(gdb, f)

            file = zipfile.ZipFile(path, mode, zipfile.ZIP_DEFLATED)
            try:
                #file.write(full pathname, rename, compression type)
                file.write(toZip, join(folder, basename(toZip)))
            except:
                userMessage("Issue zipping " + toZip)
                issue_flag = 1
            finally:
                file.close()

            i = i + 1

    if issue_flag == 0:
        userMessage("Successfully zipped geodatabase")
    else:
        if exists(path):
            remove(path)
        userMessage("Issue zipping geodatabase. No zip file created.")

def main():
    gdb = GetParameterAsText(0)
    path = GetParameterAsText(1)

    if path[-3:] != "zip":
        userMessage("Output zip file is not valid. Please try again.")

    else:
        createNG911Zip(gdb, path)

if __name__ == '__main__':
    main()