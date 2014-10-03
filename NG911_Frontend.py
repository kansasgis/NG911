#-------------------------------------------------------------------------------
# Name:        NG911_Frontend
# Purpose:     Allows the user to define the feature
#              class and field mapping/crosswalk.
#              Allows the user to select
#              processes to run and view results.
#              Use a scrollable canvas object to display output.
#
# Author:      Dirk Talley, Kansas Department of Transportation
#               dtalley@ksdot.org
#
# Created:     26/09/2014
# Modified:    03/10/2014
# Version:     0.17a
#-------------------------------------------------------------------------------
import Tkinter as tk
from Tkinter import *  # @UnusedWildImport
from ttk import *  # @UnusedWildImport
import tkFont
import os  # @UnusedImport
import datetime

from arcpy import env, ListWorkspaces, ListDatasets, ListFeatureClasses, CreateTable_management, Exists as arcpyExists
from arcpy.da import (InsertCursor as daInsertCursor, SearchCursor as daSearchCursor, # @UnresolvedImport @UnusedImport
                       UpdateCursor as daUpdateCursor)  # @UnresolvedImport @UnusedImport
from arcpy.management import AddField
#import NG911_DataCheck
from NG911_DataCheck import getRequiredFields

env.workspace = os.getcwd()
defaultLayers = ["RoadAlias", "AddressPoints", "RoadCenterline", "AuthoritativeBoundary", "CountyBoundary", "ESZ", "PSAP", "MunicipalBoundary", "EMS", "FIRE", "LAW"]

for i, listItem in enumerate(defaultLayers):
    defaultLayers[i] = str(os.path.join("NG911", listItem))
 
class Application(Frame):              
    def __init__(self, master=None):
        Frame.__init__(self, master)   
        self.grid()                       
        
        self.listLocalGDBs()
        
        self.createWidgets()
        fonts = tkFont.families()
        if 'Calibri' in fonts:
            pass
            #print 'Calibri'
        else:
            pass
            #print 'No Calibri. =('
        
    def listFcsInGDB(self):
        ''' Set arcpy.env.workspace to a GDB before calling '''
        self.FcsList = list()
        for fds in ListDatasets('',''):
            for fc in ListFeatureClasses('','',fds):
                self.FcsHold1 = str(fds)
                self.FcsHold2 = str(fc)
                self.FcsJoin1 = self.FcsHold1 + os.path.sep + self.FcsHold2
                self.FcsList.append(self.FcsJoin1)
        for fc in ListFeatureClasses('',''):
            self.FcsList.append(str(fc))
            self.FcsList = sorted(self.FcsList)
        return self.FcsList
                #print self.FcsJoin1
        #print self.FcsList
        
    def listLocalGDBs(self):
        self.gdbList1 = list()
        
        self.gdbList1 = ListWorkspaces('', 'FileGDB')
        print 'List of local GDBs: '
        for gdbLocation in self.gdbList1:
            print gdbLocation
        '''
        for fName in os.listdir(os.getcwd()):  # @ReservedAssignment
            if fName.endswith(".gdb"):
                self.gdbList1.append(str(fName))
        if len(self.gdbList1) <= 0:
            print "No gdb files found!" # Change to label.
        elif len(self.gdbList1) == 1:
            env.workspace = os.getcwd()+'\\'+ self.gdbList1[0]
            print "Using " + str(env.workspace) + " as the default workspace."  # @UndefinedVariable
        else:
            print "More than one gdb found. Select one to use."
        '''
        # Set
        
    def getDefaultClassesAndFields(self):
        self.currentWorkingDirectory = os.getcwd()
        self.domainDirectory = self.currentWorkingDirectory + os.path.sep + "Domains"
        
        self.requiredFieldsDict = getRequiredFields(self.domainDirectory)
        
        for dictKey in self.requiredFieldsDict:
            valuesList = self.requiredFieldsDict[dictKey]
            for eachValue in valuesList:
                print dictKey + os.path.sep + eachValue
                
        # Make a modified dictionary that includes the remapped feature classes
        # instead of the default feature classes for each feature class
        # that was previously remapped.
        
        # Write that to the gdb.
        # Then, display the remappedFeatureClass in box3a
        # with the defaultFieldNames that correspond to it in box3b
        # to be remapped to one of the field names in box4a that were
        # found by listfields on the <remappedFeatureClass> selection
        # from box3a.

        # Then, save the outputs to gdb and reload
        # them next time that the script is called.
        # Also use them as the basis for running the
        # data check scripts further down the line.
    
    def listFeatureClassesForFields(self):
        self.FeatureClassesForFields = list()
        self.listFcsInGDB()
        self.featureClassLookupExists = 0
        self.featureClassMapping = dict()
        #self.mappedFeatureClasses = list()
        for featureClass in self.FcsList:
            if str(featureClass).find('FeatureClassLookup') >= 0:
                self.featureClassLookupExists = 1
        if self.featureClassLookupExists == 1:
            newCursor = daSearchCursor(env.workspace + '\\FeatureClassLookup', ['OBJECTID', 'DefaultFeatureClass', 'MappedFeatureClass', 'LastModified'])  # @UnusedVariable @UndefinedVariable
            for cursorRow in newCursor:
                self.featureClassMapping[cursorRow[1]] = cursorRow[2]
        else:
            pass
        for layerItem in defaultLayers:
            if layerItem not in self.FeatureClassMapping.keys():
                self.featureClassMapping[layerItem] = layerItem
            else:
                pass
        
    def createWidgets(self):
        # Make a gdb selection widget here after the basic fc/field mapping is complete.
        # Also, make a selection for using defaults which will skip the rest of this
        # up to the point of where the user can start running tests.
        top=self.winfo_toplevel()               
        top.rowconfigure(8, weight=1)           
        top.columnconfigure(3, weight=1)
        top.geometry('600x800-20+20')         
        self.rowconfigure(8, weight=1)           
        self.columnconfigure(3, weight=1)        
        self.quitButton = tk.Button(self, text='Quit', font=('Calibri', 10, 'normal'), command=self.quit)
        self.quitButton.grid(row=8, column=1,        
            sticky=tk.S)
        
        # Label to prompt user to select a geodatabase.
        # Combobox showing all available geodatabases, with the first
        # geodatabase found being the first option/starting off preselected.
        
        self.gdbSelectLabel = Label(self, text="Select the GDB to use: ")
        self.gdbSelectLabel.grid(row=0, column=1, sticky=tk.S)
        #self.gdbSelectLabel.grid_remove()
        
        self.comboBoxList0 = sorted(self.gdbList1)
        
        self.comboBox0 = Combobox(self, width=70, height=5, justify="left", state="readonly")
        self.comboBox0.config(values = self.comboBoxList0)
        self.comboBox0.grid(row=1, column=1)
        self.comboBox0.config(values = self.comboBoxList0)
        self.comboBox0.bind("<<ComboboxSelected>>", self.comboBox0Selection)
        self.comboBox0.focus_set()
        
        self.selectGDBButton = tk.Button(self, text='Use this GDB and continue.', font=('Calibri', 10, 'normal'), 
                                    command=self.selectGDBToUse)
        self.selectGDBButton.grid(row=2, column=1,        
            sticky=tk.N+tk.S+tk.E+tk.W)
        
        # Check to make sure that a gdb was found.
        if len(self.comboBoxList0) >= 1:
            self.comboBox0.current(0)
        else:
            self.gdbSelectLabel.config(text ="GDB not found. Please make sure there is a .gdb file in the same folder as this script.")
            self.comboBox0.grid_remove()
            self.selectGDBButton.grid_remove()
        
        
        '''
        # Add in the "Use Defaults/Modify Defaults/Reset Modified Defaults" choice.
        # Radio button for the Use Defaults/Modify Defaults choice.
        # Label to prompt user to select a radio button.
        self.defaultsRadioChoice = ''
        self.radioButton1 = Radiobutton(self, text="Use Defaults", Variable=self.defaultsRadioChoice, value='1', height=1)
        self.radioButton1.grid()
        self.radioButton2 = Radiobutton(self, text="Modify Defaults", Variable=self.defaultsRadioChoice, value='2', height=1)
        self.radioButton3 = Radiobutton(self, text="Reset Modified Defaults", Variable=self.defaultsRadioChoice, value='3', height=1)
        # Button to continue after radio button selection.
        '''
        self.labelBox1 = Label(self, text="Default Feature Class: ")
        self.labelBox1.grid(row=2, column=0, sticky=tk.E)
        self.labelBox1.grid_remove()
        
        self.labelBox2 = Label(self, text="Mapped Feature Class: ")
        self.labelBox2.grid(row=3, column=0, sticky=tk.E)
        self.labelBox2.grid_remove()
        
        self.featureClassButton = tk.Button(self, text='Change Feature Class Mapping', font=('Calibri', 10, 'normal'), 
                                    command=self.changeFeatureClassMapping)
        self.featureClassButton.grid(row=1, column=1,        
            sticky=tk.N+tk.S+tk.E+tk.W)
        self.featureClassButton.grid_remove()
        
        self.updateFeatureClassButton = tk.Button(self, text='Update Feature Class Mapping', font=('Calibri', 10, 'normal'), 
                                    command=self.updateFeatureClassMapping)
        self.updateFeatureClassButton.grid(row=4, column=1,        
            sticky=tk.N+tk.S+tk.E+tk.W)
        self.updateFeatureClassButton.grid_remove()
        
        self.labelBox3 = Label(self, text="Default Field Name: ")
        self.labelBox3.grid(row=2, column=1, sticky=tk.E)
        self.labelBox3.grid_remove()
        
        self.labelBox4 = Label(self, text="Mapped Field Name: ")
        self.labelBox4.grid(row=3, column=1, sticky=tk.E)
        self.labelBox4.grid_remove() 
        
        self.fieldNameButton = tk.Button(self, text='Change Field Name Mapping', font=('Calibri', 10, 'normal'), 
                                    command=self.changeFieldNameMapping)
        self.fieldNameButton.grid(row=1, column=2,        
            sticky=tk.N+tk.S+tk.E)
        self.fieldNameButton.grid_remove()
        
        self.updateFieldNameButton = tk.Button(self, text='Update Field Name Mapping', font=('Calibri', 10, 'normal'), 
                                    command=self.updateFieldNameMapping)
        self.updateFieldNameButton.grid(row=5, column=2,        
            sticky=tk.N+tk.S+tk.W)
        self.updateFieldNameButton.grid_remove()
        
        
        
        self.comboBox1 = Combobox(self, width=30, height=5, justify="left", state="readonly")
        comboBoxList1 = sorted(defaultLayers)
        self.comboBox1.config(values = comboBoxList1)
        self.comboBox1.grid(row=2, column=1)
        self.comboBox1.grid_remove()
        comboBoxList1.insert(0, 'Choose the Default Feature Class')
        self.comboBox1.config(values = comboBoxList1)
        self.comboBox1.current(0)
        self.comboBox1.bind("<<ComboboxSelected>>", self.comboBox1Selection)
        
        self.comboBox2 = Combobox(self, width=30, height=5, justify="left", values = "", state="readonly")
        self.comboBox2.grid(row=3, column=1)
        self.comboBox2.grid_remove()
        self.comboBox2.bind("<<ComboboxSelected>>", self.comboBox2Selection)
        
        self.comboBox3a = Combobox(self, width=40, height=5, justify="left", state="readonly")
        self.comboBox3a.grid(row=2, column=2)
        self.comboBox3a.grid_remove()
        self.comboBox3a.bind("<<ComboboxSelected>>", self.comboBox3aSelection)
        comboBoxList3a = ['1', '2', '3', '4', '5', '6', '7', '8']
        self.comboBox3a.config(values = comboBoxList3a)
        comboBoxList3a.insert(0, "Choose the Field's Feature Class")
        self.comboBox3a.config(values = comboBoxList3a)
        self.comboBox3a.current(0)
        
        
        self.comboBox3 = Combobox(self, width=40, height=5, justify="left", state="readonly")
        comboBoxList3 = ['1', '2', '3', '4', '5', '6', '7', '8'] # This should come from the default field names list.
        self.comboBox3.config(values = comboBoxList3)
        self.comboBox3.grid(row=3, column=2)
        self.comboBox3.grid_remove()
        comboBoxList3.insert(0, 'Choose the Default Field Name')
        self.comboBox3.config(values = comboBoxList3)
        self.comboBox3.current(0)
        self.comboBox3.bind("<<ComboboxSelected>>", self.comboBox3Selection)
        
        self.comboBox4 = Combobox(self, width=40, height=5, justify="left", state="readonly")
        comboBoxList4 = ['1', '2', '3', '4', '5', '6', '7', '8'] # This should come from the selected Feature Class's Field names.
        self.comboBox4.config(values = comboBoxList4)
        self.comboBox4.grid(row=4, column=2)
        self.comboBox4.grid_remove()
        comboBoxList4.insert(0, 'Choose the Mapped Field Name')
        self.comboBox4.config(values = comboBoxList4)
        self.comboBox4.current(0)
        self.comboBox4.bind("<<ComboboxSelected>>", self.comboBox4Selection)
        
        
    def selectGDBToUse(self):
        self.testVar = str(self.comboBox0.get())
        #self.value_of_combo = self.comboBox1.get()
        #if self.testVar != "Choose the Default Feature Class":
        print self.testVar
        if self.testVar != '' and self.testVar.find('.gdb') >= 0:
            env.workspace = self.testVar
            print 'env.workspace now set to '+ env.workspace + '.'  # @UndefinedVariable
            self.gdbSelectLabel.config(text="Current GDB: " + env.workspace)  # @UndefinedVariable
            self.comboBox0.grid_remove()
            self.selectGDBButton.grid_remove()
            self.featureClassButton.grid()
            self.fieldNameButton.grid()
            # Adds values to the self.FcsList variable
            # based on the selected GDB.
            self.listFcsInGDB()
            # Populate the 2nd ComboList with those
            # values.
            comboBoxList2 = sorted(self.FcsList)
            comboBoxList2.insert(0, 'Choose the Mapped Feature Class')
            self.comboBox2.config(values = comboBoxList2)
            self.comboBox2.current(0)
            #self.comboBox0.grid_remove()
            
        else:
            print 'GDB not found.' # Create a label that complains about there not being a gdb selected.
            self.gdbSelectLabel.config(text="GDB not found. Please make sure there is a .gdb file in the same folder as this script.")
        '''
        self.comboBox1.grid()
        self.labelBox1.grid()
        self.comboBox3.grid_remove()
        self.comboBox4.grid_remove()
        self.labelBox3.grid_remove()
        self.labelBox4.grid_remove()
        app.updateFieldNameButton.grid_remove()
        '''
    
    def changeFeatureClassMapping(self):
        self.comboBox1.grid()
        self.labelBox1.grid()
        self.comboBox3a.grid_remove()
        self.labelBox3a.grid_remove()
        self.comboBox3.grid_remove()
        self.labelBox3.grid_remove()
        self.comboBox4.grid_remove()
        self.labelBox4.grid_remove()
        app.updateFieldNameButton.grid_remove()
        
    def updateFeatureClassMapping(self):
        self.comboResult1 = self.comboBox1.get()
        self.comboResult2 = self.comboBox2.get()
        self.rowFoundInCursor = 0
        if  str(self.comboResult1) != 'Choose the Default Feature Class' and str(self.comboResult2) != 'Choose the Mapped Feature Class':
            print "Updating Feature Class " + str(self.comboResult1) + " to Map to " + str(self.comboResult2)
            #Write the feature class mapping to the geodatabase.
            #------------------------------------------------
            #If exists mapping table
            if arcpyExists(env.workspace + '\FeatureClassLookup'):  # @UndefinedVariable
                print 'Table already exists.'
                print 'Looking for previous mapping.'
                newCursor = daSearchCursor(env.workspace + '\FeatureClassLookup', ['OBJECTID', 'DefaultFeatureClass', 'MappedFeatureClass', 'LastModified'])  # @UnusedVariable @UndefinedVariable
                rowList = list()
                for searchRow in newCursor:
                    rowList.append(list(searchRow))
                #if 'newCursor' in locals():
                del newCursor
                #else:
                    #pass
                for listedRow in rowList:
                    if str(self.comboResult1) == str(listedRow[1]):
                        print 'Found previous mapping from ' + str(listedRow[3]) + '.'
                        objectIDToUpdate = listedRow[0]
                        print 'Need to update the mapping for ObjectID ' + str(objectIDToUpdate) + '.'
                        self.rowFoundInCursor = 1
                    else:
                        pass
                
                if self.rowFoundInCursor == 1:
                    rowForUpdate = [objectIDToUpdate, str(self.comboResult1), str(self.comboResult2), datetime.datetime.now()]
                    # Should add a where clause on the OID to speed this up.
                    newCursor = daUpdateCursor(env.workspace + '\FeatureClassLookup', ['OBJECTID', 'DefaultFeatureClass', 'MappedFeatureClass', 'LastModified'])  # @UnusedVariable @UndefinedVariable
                    for updateableRow in newCursor:
                        if updateableRow[0] == objectIDToUpdate:
                            newCursor.updateRow(rowForUpdate)
                            print "Updated row with OID " + str(objectIDToUpdate)
                        else:
                            pass
                    
                    if 'newCursor' in locals():
                        del newCursor
                    
                else:
                    print 'Adding new mapping.'
                    newCursor = daInsertCursor(env.workspace + '\FeatureClassLookup', ['DefaultFeatureClass', 'MappedFeatureClass', 'LastModified'])  # @UnusedVariable @UndefinedVariable
                    rowToInsert = [str(self.comboResult1), str(self.comboResult2), datetime.datetime.now()]
                    insertedOID = newCursor.insertRow(rowToInsert)
                    print "Inserted row with OID " + str(insertedOID)
                    if 'newCursor' in locals():
                        del newCursor
                        
            else:
                print 'Creating table.'
                CreateTable_management(env.workspace, 'FeatureClassLookup')  # @UndefinedVariable
                AddField(env.workspace + '\FeatureClassLookup', 'DefaultFeatureClass', 'TEXT', '100')  # @UndefinedVariable
                AddField(env.workspace + '\FeatureClassLookup', 'MappedFeatureClass', 'TEXT', '100')  # @UndefinedVariable
                #AddField(env.workspace + '\FeatureClassLookup', 'IsModified', 'String', '10')  # @UndefinedVariable
                AddField(env.workspace + '\FeatureClassLookup', 'LastModified', 'DATE')  # @UndefinedVariable
                print 'Adding new mapping.'
                newCursor = daInsertCursor(env.workspace + '\FeatureClassLookup', ['DefaultFeatureClass', 'MappedFeatureClass', 'LastModified'])  # @UnusedVariable @UndefinedVariable
                rowToInsert = [str(self.comboResult1), str(self.comboResult2), datetime.datetime.now()]
                insertedObjectID = newCursor.insertRow(rowToInsert)
                print "Inserted row with ObjectID " + str(insertedObjectID)
                if 'newCursor' in locals():
                    print 'Done with newCursor. Deleting.'
                    del newCursor
            
            #check for a previous mapping for this fc
            #if previous mapping, update
            #if not previous mapping, insert.
            #if not exists mapping table
            #add mapping table
            #insert mapping.
        
    def changeFieldNameMapping(self):
        self.comboBox3a.grid()
        self.labelBox3a.grid()
        self.comboBox1.grid_remove()
        self.comboBox2.grid_remove()
        self.labelBox1.grid_remove()
        self.labelBox2.grid_remove()
        app.updateFeatureClassButton.grid_remove()
        
    def updateFieldNameMapping(self):
        self.comboResult3a = self.comboBox3a.get()
        self.comboResult3 = self.comboBox3.get()
        self.comboResult4 = self.comboBox4.get()
        self.rowFoundInCursor = 0
        if str(self.comboResult3) != 'Choose the Default Field Name' and str(self.comboResult4) != 'Choose the Mapped Field Name':
            print "Updating Field Name " + str(self.comboResult3) + " to Map to " + str(self.comboResult4)
            
            
            
            
            # If exists FC mapping table
            # load the mapped FCs + defaults.
            # If not, assume all defaults for FCs.
            # If exists FN mapping table
            # check for previous mapping.
            # if not previous mapping, insert.
            # if not exists mapping table
            # add mapping table
            # insert mapping.
            
            #-Write the feature class mapping to the geodatabase.
            #------------------------------------------------
            #-If exists field mapping table
            if arcpyExists(env.workspace + '\FieldNameLookup'):  # @UndefinedVariable
                print 'Table already exists.'
                print 'Looking for previous mapping.'
                newCursor = daSearchCursor(env.workspace + '\FieldNameLookup', ['OBJECTID', 'DefaultFieldName', 'MappedFieldName', 'LastModified'])  # @UnusedVariable @UndefinedVariable
                rowList = list()
                for searchRow in newCursor:
                    rowList.append(list(searchRow))
                #if 'newCursor' in locals():
                del newCursor
                #else:
                    #pass
                for listedRow in rowList:
                    if str(self.comboResult3) == str(listedRow[1]):
                        print 'Found previous mapping from ' + str(listedRow[3]) + '.'
                        objectIDToUpdate = listedRow[0]
                        print 'Need to update the mapping for ObjectID ' + str(objectIDToUpdate) + '.'
                        self.rowFoundInCursor = 1
                    else:
                        pass
                
                if self.rowFoundInCursor == 1:
                    rowForUpdate = [objectIDToUpdate, str(self.comboResult3), str(self.comboResult4), datetime.datetime.now()]
                    # Should add a where clause on the OID to speed this up.
                    newCursor = daUpdateCursor(env.workspace + '\FieldNameLookup', ['OBJECTID', 'DefaultFieldName', 'MappedFieldName', 'LastModified'])  # @UnusedVariable @UndefinedVariable
                    for updateableRow in newCursor:
                        if updateableRow[0] == objectIDToUpdate:
                            newCursor.updateRow(rowForUpdate)
                            print "Updated row with OID " + str(objectIDToUpdate)
                        else:
                            pass
                    
                    if 'newCursor' in locals():
                        del newCursor
                    
                else:
                    print 'Adding new mapping.'
                    newCursor = daInsertCursor(env.workspace + '\FieldNameLookup', ['DefaultFieldName', 'MappedFieldName', 'LastModified'])  # @UnusedVariable @UndefinedVariable
                    rowToInsert = [str(self.comboResult3), str(self.comboResult4), datetime.datetime.now()]
                    insertedOID = newCursor.insertRow(rowToInsert)
                    print "Inserted row with OID " + str(insertedOID)
                    if 'newCursor' in locals():
                        del newCursor
                        
            else:
                print 'Creating table.'
                CreateTable_management(env.workspace, 'FieldNameLookup')  # @UndefinedVariable
                AddField(env.workspace + '\FieldNameLookup', 'DefaultFieldName', 'TEXT', '100')  # @UndefinedVariable
                AddField(env.workspace + '\FieldNameLookup', 'MappedFieldName', 'TEXT', '100')  # @UndefinedVariable
                #AddField(env.workspace + '\FieldNameLookup', 'IsModified', 'String', '10')  # @UndefinedVariable
                AddField(env.workspace + '\FieldNameLookup', 'LastModified', 'DATE')  # @UndefinedVariable
                print 'Adding new mapping.'
                newCursor = daInsertCursor(env.workspace + '\FieldNameLookup', ['DefaultFieldName', 'MappedFieldName', 'LastModified'])  # @UnusedVariable @UndefinedVariable
                rowToInsert = [str(self.comboResult3), str(self.comboResult4), datetime.datetime.now()]
                insertedObjectID = newCursor.insertRow(rowToInsert)
                print "Inserted row with ObjectID " + str(insertedObjectID)
                if 'newCursor' in locals():
                    print 'Done with newCursor. Deleting.'
                    del newCursor
            
            #check for a previous mapping for this fc
            #if previous mapping, update
            #if not previous mapping, insert.
            #if not exists mapping table
            #add mapping table
            #insert mapping.
            
    def comboBox0Selection(self, event):
        # Highlight continue button when a GDB
        # is selected from the Combo Box.
        self.selectGDBButton.focus_set()
        
            
    
    def comboBox1Selection(self, event):
        self.testVar = str(self.comboBox1.get())
        #self.value_of_combo = self.comboBox1.get()
        if self.testVar != "Choose the Default Feature Class":
            print self.testVar
            #self.comboBox2.current(0)
            #self.comboBox2.config(values = self.FcsList)
            self.comboBox2.grid()
            self.labelBox2.grid()
    
    def comboBox2Selection(self, event):
        self.testVar = str(self.comboBox2.get())
        #self.value_of_combo = self.comboBox1.get()
        if self.testVar != "Choose the Mapped Feature Class":
            print self.testVar
            app.updateFeatureClassButton.grid()
            
    def comboBox3aSelection(self, event):
        self.testVar = str(self.comboBox3a.get())
        if self.testVar != "Choose the Field's Feature Class":
            print self.testVar
            self.comboBox3.current(0)
            self.comboBox3.grid()
            self.labelBox3.grid()
            # Need to populate the comboBox3a values with the fields
            # from the default feature classes + the mapped feature
            # classes.
            # Then, the field names list for the combobox3 can come from  ## This should be from the .txt file, modified incase of a mapping.
            # the .txt and the default list side of the mapping + default
            # feature classes and the
            # field names list for the combobox4 can come from a listFields ## This should be solely from the fields found in the current gdb.
            # ran on the selected feature class in this box.
            # This needs to be a feature class that is in the current gdb.
            # Then, use a searchcursor to get the fields in the current gdb
            # 
            
    def comboBox3Selection(self, event):
        self.testVar = str(self.comboBox3.get())
        #self.value_of_combo = self.comboBox1.get()
        if self.testVar != "Choose the Default Field Name":
            print self.testVar
            self.comboBox4.current(0)
            self.comboBox4.grid()
            self.labelBox4.grid()
            
    def comboBox4Selection(self, event):
        self.testVar = str(self.comboBox4.get())
        #self.value_of_combo = self.comboBox1.get()
        if self.testVar != "Choose the Mapped Field Name":
            print self.testVar
            app.updateFieldNameButton.grid()
            
            
app = Application()                       
app.master.title('Test application')
app.mainloop()
app.getDefaultClassesAndFields()

# Addition: After a Feature Class has a mapping assigned, change it to a different font color.
# Do the same for Field Names, give a tertiary color if the field mapping is changed from a loaded mapping.


# Initial Pseudocode follows below:
'''
During the initial setup
make sure to query the user as to
Whether or not they will be using
The defaults.
If not, display customization options.
Then allow them to close the customization options
when they are complete by pressing
a finish customization button
or similar.

Save the customization options so that they
are loaded again when the GUI is opened
next time. If possible, have them also be
the new defaults for the geoprocessing scripts
if those scripts are run from the command line
instead of the GUI.

After customization or defaults are chosen,
Give the option to run the checking tools.
Either one at a time or a full check.
If one at a time, open a frame that
displays an icon for each checking tool
and allows the user to run them in any
order.

Show a running display of the output
on a vertically scrollable canvas object.

Also adapt a progress bar for each
geoprocessing operation so that the
user can tell how long something is
taking.

Save this output so that it can be recalled
later on without having to run the tools.

-- Kristen may already be doing this. Will just
 need to pull the information from wherever she 
 placed it, if so.

Display instructions for the user to find and open
this information in Arcmap if they wish to use it
in making corrections. -- Maybe produce/modify ifexists
a map document that shows this?
'''