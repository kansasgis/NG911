#!/usr/bin/env python
# NG911_Frontend.py -- The PySide version.
# Should make the layout more stable
# across different window sizes and allows
# for better looking icons and a more native
# appearance to the window.
# Also gives a better chance of not
# crashing ArcMap when called as a
# script tool.

# Requires PySide.
# DisUtils or similar should make for simple-ish
# distribution, but for testing/development, make sure that you
# have installed pip, then run:
# pip install -U PySide
# from the command line to install PySide.

# ***Check compatibility with the new version of NG911_DataChecks.***
# ^^ Partially complete.

# The ability to select and run the datachecks from this GUI will be
# added in layoutContainer4. -- Next step in development after
# reverse translation for the written to GDB field name mapping.
# ^^ Partially complete.

## ^^ Simplified writes/reads for these settings in preparation for
## reverse translation.

### ^^^ Recently collapsed page 2 and page 3 into page 2 alone.
### References still go to pages 1, 2, 3, 4 as layoutContainer<x>.
### Will keep them that way until the rest of the functionality
### is added, then remove old references and update to
### pages 1, 2, 3... renaming layoutContainer to applicationPage
### or similar.

## Need to remove old functions dealing with page 2/3 after done using them
## as templates for the new functions dealing with page 2.

## See about using function decorators
## to display text sent to the userMessage() function
## in the output message boxes.
## ^^ Used a monkey patch instead, but need
## to replace with a better programming practice later.

#-------------------------------------------------------------------------------
# Name:        NG911_Frontend
# Purpose:     Allows the user to define the feature
#              class and field mapping/crosswalk.
#              Allows the user to select
#              processes to run and view results.
#              Use a scrollable TextEdit box to display output.
#
# Author:      Dirk Talley, Kansas Department of Transportation
#               dtalley@ksdot.org
#
# Created:     26/09/2014
# Modified:    31/10/2014 by dirktall04
# Version:     0.43a
#-------------------------------------------------------------------------------


import sys
import platform  # @UnusedImport
import re  # @UnusedImport

import PySide  # @UnusedImport
from PySide.QtCore import QRect, Qt  # @UnusedImport
from PySide.QtGui import (QApplication, QMainWindow, QTextEdit, QPushButton,  # @UnusedImport
        QMessageBox, QIcon, QAction, QWidget, QGridLayout, QHBoxLayout,  # @UnusedImport
        QMenuBar, QMenu, QStatusBar, QComboBox, QVBoxLayout, QFormLayout,  # @UnusedImport
        QStyleFactory, QLabel, QPixmap, QImage, QPainter, QTextDocument,  # @UnusedImport
        QTextCursor, QCheckBox)

import os  # @UnusedImport
import datetime

from arcpy import (env, Exists as arcpyExists, ListWorkspaces, ListDatasets, ListFeatureClasses, CreateTable_management,
                ListTables, ListFields, GetCount_management)  # @UnusedImport
from arcpy.da import (InsertCursor as daInsertCursor, SearchCursor as daSearchCursor, # @UnresolvedImport
                       UpdateCursor as daUpdateCursor)  # @UnresolvedImport
from arcpy.management import AddField

import NG911_DataCheck

# Use NG91_DataCheck's getCurrentLayerList function instead when it is fully implemented.
# from NG911_Config import currentLayerList, nonDisplayFields
from NG911_Config import currentLayerList, nonDisplayFields, pathInformationClass

env.workspace = os.getcwd()
lineSeparator = os.linesep
guiOutputSetting = True # Boolean Toggle for changing the NG911_DataCheck.userMessage function.


# Every Qt application must have one and only one QApplication object;
# it receives the command line arguments passed to the script, as they
# can be used to customize the application's appearance and behavior
qt_app = QApplication(sys.argv)


class NG911_Window(QWidget):
    
    def __init__(self):
        # Initialize the object as a QWidget and
        # set its title and minimum width
        QWidget.__init__(self)
        # Set a variable to let the application know
        # if it should exit when the quit button is
        # pressed or print a warning message.
        self.okayToQuit = 1
        self.selectedGDBpath = ""
        self.combinedFeatureClassesDict = dict()
        self.dataCheckFunctList = list()
        self.selectedItemsList = list()
        
        # Object to pass to the data check functions, containing dynamic
        # paths and related variables.
        self.pathsObject = pathInformationClass()
        
        self.domainsPath = self.getDomainsLocation()
        self.defaultFieldsDict = NG911_DataCheck.getRequiredFields(self.domainsPath)
        
        self.pathsObject.domainsFolderPath = self.domainsPath
        
        self.loadedImage = QIcon()
        self.loadedImage.addFile("DataCheckIcon")
        self.setWindowIcon(self.loadedImage)
        self.setWindowTitle("NG911 Data Check Add-in 1.1")
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)
        self.createWidgets()
        self.monkeyPatchOutput()
        self.startGDBSelection()
        
        
    def listLocalGDBs(self):
        # Scans the parent folder and each contained folder
        # for GDBs.
        
        # Store the path of the current directory.
        osCwd = os.getcwd()
        # Go up one level.
        os.chdir("..")
        # Store the path of the directory which is up one level.
        upOneLevelDir = os.getcwd()
        
        # List directories in the directory which is up one level.
        upOneLevelDirList = os.listdir(upOneLevelDir)
        
        gdbList = list()
        
        # Run listWorkspaces for FileGDBs only on the upper level directory
        # Append the results to gdbList
        env.workspace = upOneLevelDir
        workspacesList = ListWorkspaces("", "FileGDB")
        if workspacesList != None:
            for gdbLocation in workspacesList:
                gdbList.append(gdbLocation)
        else:
            pass
        
        # Then, run listWorkspaces for FileGDBs only on the current directory and adjacent directories
        # Append the results to gdbList
        for dirItem in upOneLevelDirList:
            env.workspace = os.path.join(upOneLevelDir, dirItem)
            workspacesList = ListWorkspaces("", "FileGDB")
            if workspacesList != None:
                for gdbLocation in workspacesList:
                    gdbList.append(gdbLocation)
            else:
                pass
        
        # Set the directory back to the starting directory.
        os.chdir(osCwd)
        
        return gdbList
    
    
    def getDomainsLocation(self):
        # Scans the parent folder and each contained folder
        # for the Domains folder.
        
        # Store the path of the current directory.
        osCwd = os.getcwd()
        # Go up one level.
        os.chdir("..")
        # Store the path of the directory which is up one level.
        upOneLevelDir = os.getcwd()
        
        domainsFolderList = list()
        
        # Check for the domains folder in the current directory.
        for folderName in os.listdir(osCwd):
            if folderName.upper() == "Domains".upper():
                domainsFolderList.append(os.path.join(upOneLevelDir, folderName))
            else:
                pass
        
        # Check for the domains folder in the directory which is up one level.
        for folderName in os.listdir(upOneLevelDir):
            if folderName.upper() == "Domains".upper():
                domainsFolderList.append(os.path.join(upOneLevelDir, folderName))
            else:
                pass
        
        domainsLocation = ""
        
        # If the domainsFolderList is not empty, use the first entry as the location for the domains folder.
        if len(domainsFolderList) != 0: # Not the pythonic way to make this check, but I like this method better.
            domainsLocation = domainsFolderList[0]
        # If there is no domains folder found, default to using the current folder for the text files' location.
        else:
            domainsLocation = self.pathsObject.domainsFolderPath
        
        # Set the directory back to the starting directory.
        os.chdir(osCwd)
        
        return domainsLocation
    
    
    def createWidgets(self):
        # Create the QVBoxLayout that lays out the whole form
        self.layout = QVBoxLayout()
        
        # Set the VBox layout as the window's main layout
        self.setLayout(self.layout)
        
        self.outputTextBoxHeight = 125
        
        # --------------------------------------------------
        # Create Dialogue Layout 1 - GDB Selection
        # --------------------------------------------------
        
        self.dialogueLayout1Container = QWidget()
        self.layout.addWidget(self.dialogueLayout1Container)
        self.dialogueLayout1 = QVBoxLayout()
        self.dialogueLayout1Container.setLayout(self.dialogueLayout1)
        self.dialogueLayout1Container.setContentsMargins(-7,-7,-7,-7)

        # Create a label box that says 'Searching for GDBs...'
        self.gdbPromptLabel = QLabel(self)
        self.gdbPromptLabel.setText("Searching for GDBs...")
        self.dialogueLayout1.addWidget(self.gdbPromptLabel)
 
        # Create the form layout that manages the labeled controls
        self.form_layout1 = QFormLayout()
        
        # Add the form layout to the main VBox layout
        self.dialogueLayout1.addLayout(self.form_layout1)
        
        # Create the localGDBCombobox prior to adding it to the layout.
        self.localGDBCombobox = QComboBox(self)
        self.localGDBCombobox.setMinimumWidth(25)
        
        # Add the GDB Combobox to the right-hand side of the form layout
        # with a text label in the left-hand side of the same row.
        self.form_layout1.addRow("GDB Path:", self.localGDBCombobox)
        
        # Add stretch to separate the form layout from the button
        self.dialogueLayout1.addStretch(1)
        
        # The main text box that holds all of the text, which
        # gets copied to the other text boxes. This text
        # box does not get added to the display or unhidden.
        # It just serves as a place to keep the text
        # consistent between the boxes on the different
        # pages of the application.
        self.textBoxMain = QTextEdit()
        self.textBoxMain.hide()
        
        # Create a text box to serve as a message box
        # for print outputs that the application
        # should display instead of or in addition
        # to sending to the console.
        self.textBox1 = QTextEdit()
        
        self.textBox1.setReadOnly(True)
        
        self.textBox1.setMinimumHeight(50)
        self.textBox1.setMaximumHeight(self.outputTextBoxHeight)
        self.textBox1.setMinimumWidth(200)
        self.textBox1.setMaximumWidth(400)
        self.dialogueLayout1.addWidget(self.textBox1)
        self.textBox1.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth) # Set line wrapping to the widget width.
        
        #Set background color for the textbox to something other than white?
        ## Requires modifying the stylesheet. Not sure if I want to do that right now.
        
        # Create a horizontal box layout to hold the button
        self.buttonBox1 = QHBoxLayout()
        
        # Add stretch to push the button to the far right
        self.buttonBox1.addStretch(1)
        
        # Create the build button with its caption
        self.nextButton1 = QPushButton("&Next", self)
        
        # Connect the button's clicked signal to the doneWithGDBSelection function
        # Lambda used to differentiate this signal between the next button used here
        # and the back button from the third layout.
        self.nextButton1.clicked.connect(lambda: self.doneWithGDBSelection("Next"))
        
        self.buttonBox1.addWidget(self.nextButton1)
        
        self.quitButton1 = QPushButton("&Quit", self)
        
        # Add it to the button box
        self.buttonBox1.addWidget(self.quitButton1)
        
        self.quitButton1.clicked.connect(self.quitApplication)
        
        # Add the button box to the bottom of the main VBox layout
        self.dialogueLayout1.addLayout(self.buttonBox1)
        
        
        # -------------------------------------------------------
        # Create Dialogue Layout 2 - Feature Class and Field Mapping
        # -------------------------------------------------------
        self.dialogueLayout2Container = QWidget()
        self.layout.addWidget(self.dialogueLayout2Container)
        self.dialogueLayout2Container.setContentsMargins(-7,-7,-7,-7)
        self.dialogueLayout2 = QVBoxLayout()
        self.dialogueLayout2Container.setLayout(self.dialogueLayout2)
        
        # Create a label box that says gives instructions
        # on how to update the feature class
        # and field name mapping.
        self.featureClassMappingLabel = QLabel(self)
        self.featureClassMappingLabel.setWordWrap(True)
        self.featureClassMappingLabelText = ("1) Select the Default Feature Class and Field Name from the first and second drop-down boxes." + \
                                              lineSeparator + \
                                              "2) Select the Target Feature Class and Field Name from the third and fourth drop-down boxes." + \
                                              lineSeparator + \
                                              "3) Click the \"Update Mapping\" button." + \
                                              lineSeparator + \
                                              "4) Repeat from step #1 or #2 as necessary, then click the \"Next\" button.")
        self.featureClassMappingLabel.setText(self.featureClassMappingLabelText)
        self.dialogueLayout2.addWidget(self.featureClassMappingLabel)
        
        # Create the form layout that manages the labeled controls
        self.form_layout2 = QFormLayout()
        
        # Add the form layout to the main VBox layout
        self.dialogueLayout2.addLayout(self.form_layout2)
        
        # Create and fill the combobox to choose the default Feature Class
        self.defaultFeatureClassComboBox2 = QComboBox(self)
        self.defaultFeatureClassComboBox2.setMinimumWidth(25)
        self.form_layout2.addRow("Default Feature Class:", self.defaultFeatureClassComboBox2)
        # Add the signal connection to call a function that populates defaultFieldNameComboBox2.
        self.defaultFeatureClassComboBox2.activated.connect(self.populateDefaultFieldNameComboBox2)
        
        self.defaultFieldNameComboBox2 = QComboBox(self)
        self.defaultFieldNameComboBox2.setMinimumWidth(25)
        self.form_layout2.addRow("Default Field Name:", self.defaultFieldNameComboBox2)
        
        self.targetFeatureClassComboBox2 = QComboBox(self)
        self.targetFeatureClassComboBox2.setMinimumWidth(25)
        self.form_layout2.addRow("Target Feature Class:", self.targetFeatureClassComboBox2)
        # Add the signal connection to call a function that populates targetFieldNameComboBox2.
        self.targetFeatureClassComboBox2.activated.connect(self.populateTargetFieldNameComboBox2)
        
        self.targetFieldNameComboBox2 = QComboBox(self)
        self.targetFieldNameComboBox2.setMinimumWidth(25)
        self.form_layout2.addRow("Target Field Name:", self.targetFieldNameComboBox2)
        
        
        self.updateFeatureClassMappingButton2 = QPushButton("Update Mapping", self)
        self.updateFeatureClassMappingButton2.clicked.connect(self.updateFeatureClassAndFieldNameMapping)
        self.form_layout2.addRow("", self.updateFeatureClassMappingButton2)
        self.updateFeatureClassMappingButton2.setMaximumWidth(100)
        
        # Add stretch to separate the form layout from the output message box.
        self.dialogueLayout2.addStretch(1)
        
        self.textBox2 = QTextEdit()
        
        self.textBox2.setReadOnly(True)
        self.textBox2.setMinimumHeight(50)
        self.textBox2.setMaximumHeight(self.outputTextBoxHeight)
        self.textBox2.setMinimumWidth(200)
        self.textBox2.setMaximumWidth(400)
        self.dialogueLayout2.addWidget(self.textBox2)
        self.textBox2.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth) # Set line wrapping to the widget width.
        
        
        # Create a horizontal box layout to hold the buttons
        self.buttonBox2 = QHBoxLayout()
        # Add stretch to push the buttons to the far right
        self.buttonBox2.addStretch(1)

        self.backButton2 = QPushButton("&Back", self)
        self.backButton2.clicked.connect(self.startGDBSelection)
        self.buttonBox2.addWidget(self.backButton2)
        
        self.nextButton2 = QPushButton("&Next", self)
        self.nextButton2.clicked.connect(self.doneFeatureAndFieldMapping)
        self.buttonBox2.addWidget(self.nextButton2)
        
        self.quitButton2 = QPushButton("&Quit", self)
        self.buttonBox2.addWidget(self.quitButton2)
        self.quitButton2.clicked.connect(self.quitApplication)
        
        # Add the button box to the bottom of the main VBox layout
        self.dialogueLayout2.addLayout(self.buttonBox2)
        
        # -------------------------------------------------------
        # Create Dialogue Layout 4 - Data Checks
        # -------------------------------------------------------
        self.dialogueLayout4Container = QWidget()
        self.layout.addWidget(self.dialogueLayout4Container)
        self.dialogueLayout4Container.setContentsMargins(-7,-7,-7,-7)
        self.dialogueLayout4 = QVBoxLayout()
        self.dialogueLayout4Container.setLayout(self.dialogueLayout4)
        
        # Create a label box that says gives instructions
        # on how to update the feature class mapping.
        self.dataChecksLabel = QLabel(self)
        self.dataChecksLabel.setWordWrap(True)
        self.dataChecksLabelText = ("1) Mark the check boxes for the Data Checks that you would like to run." + \
                                          lineSeparator + \
                                          "2) Click the \"Check Data\" button to run the Data Checks." + \
                                          lineSeparator + \
                                          "3) View output messages in the text box below.")
        
        self.dataChecksLabel.setText(self.dataChecksLabelText)
        self.dialogueLayout4.addWidget(self.dataChecksLabel)
        
        self.leftRightContainerQVBox4 = QHBoxLayout()
        self.dialogueLayout4.addLayout(self.leftRightContainerQVBox4)
        
        self.leftSideQVBox4 = QVBoxLayout()
        self.leftRightContainerQVBox4.addLayout(self.leftSideQVBox4)
        
        self.rightSideQVBox4 = QVBoxLayout()
        self.leftRightContainerQVBox4.addLayout(self.rightSideQVBox4)
        
        self.selectorList = list()
        
        self.checkLayerListSelector = QCheckBox()
        self.checkLayerListSelector.setText("Check Layer List")
        self.checkLayerListSelector.setProperty("associatedFunction", NG911_DataCheck.checkLayerList)
        
        self.leftSideQVBox4.addWidget(self.checkLayerListSelector)
        self.selectorList.append(self.checkLayerListSelector)
        
        
        self.checkRequiredFieldsSelector = QCheckBox()
        self.checkRequiredFieldsSelector.setText("Check Required Fields")
        self.checkRequiredFieldsSelector.setProperty("associatedFunction", NG911_DataCheck.checkRequiredFields)
        
        self.leftSideQVBox4.addWidget(self.checkRequiredFieldsSelector)
        self.selectorList.append(self.checkRequiredFieldsSelector)
        
        
        self.checkRequiredFieldValuesSelector = QCheckBox()
        self.checkRequiredFieldValuesSelector.setText("Check Required Field Values")
        self.checkRequiredFieldValuesSelector.setProperty("associatedFunction", NG911_DataCheck.checkRequiredFieldValues)
        
        self.leftSideQVBox4.addWidget(self.checkRequiredFieldValuesSelector)
        self.selectorList.append(self.checkRequiredFieldValuesSelector)
        
        
        self.checkValuesAgainstDomainSelector = QCheckBox()
        self.checkValuesAgainstDomainSelector.setText("Check Values Against Domain")
        self.checkValuesAgainstDomainSelector.setProperty("associatedFunction", NG911_DataCheck.checkValuesAgainstDomain)
        
        self.rightSideQVBox4.addWidget(self.checkValuesAgainstDomainSelector)
        self.selectorList.append(self.checkValuesAgainstDomainSelector)
        
        
        self.checkFeatureLocationsSelector = QCheckBox()
        self.checkFeatureLocationsSelector.setText("Check Feature Locations")
        self.checkFeatureLocationsSelector.setProperty("associatedFunction", NG911_DataCheck.checkRequiredFieldValues)
        
        self.rightSideQVBox4.addWidget(self.checkFeatureLocationsSelector)
        self.selectorList.append(self.checkFeatureLocationsSelector)
        
        
        self.geocodeAddressPointsSelector = QCheckBox()
        self.geocodeAddressPointsSelector.setText("Geocode Address Points")
        self.geocodeAddressPointsSelector.setProperty("associatedFunction", NG911_DataCheck.geocodeAddressPoints)
        
        self.rightSideQVBox4.addWidget(self.geocodeAddressPointsSelector)
        self.selectorList.append(self.geocodeAddressPointsSelector)
        
        self.dataCheckFunctList.append(NG911_DataCheck.checkLayerList)
        
        #for selectorItem in self.selectorList:
            #if selectorItem.property("associatedFunction") not in self.dataCheckFunctList:
                #self.dataCheckFunctList.append(selectorItem.property("associatedFunction"))
            #else:
                #pass
            
        self.runSelectedDataChecksButton4 = QPushButton("Run Selected Data Checks", self)
        
        
        # Connect the button's clicked signal to the runSelectedDataChecks function
        self.runSelectedDataChecksButton4.clicked.connect(self.runSelectedDataChecks)
        
        # Add it to the layout
        self.dialogueLayout4.addWidget(self.runSelectedDataChecksButton4)
        
        #for selectorListItem in self.selectorList:
            #functToRun = self.dataCheckDecorator("selectorListItem.NG911_DataCheck." + str(functToRun.property("associatedFunction")))
            #print functToRun
        
        
        # Loop through all the buttons and call .isChecked() on them.
        # If .isChecked() == True
        # checkedItemsList.append(buttonName)
        
        # Make non-exclusive checkboxes so that more than one can be selected
        # at a given time.
        # See http://srinikom.github.io/pyside-docs/PySide/QtGui/QCheckBox.html
        
        
        # Make a button to run the selected functions
        # Make a button to run all the functions
        # Make a button that returns a help message for
        # the selected functions.
        
        # Add each checkbox to a list, then call
        # for checkBoxListItem in checkBoxList:
        #    if QAbstractButton.isChecked() == True:
        #        checkedItemsList.append(checkBoxListItem)
        
        # for funct in functList:
        #     if funct in checkedItems:
        #        funct(configObject)
        #                    # Might be difficult to add the appropriate variables.
        #                    # Try adding them to a config object or similar
        #                    # that the scripts can access to make things easier.
        #                    # Then, pass them all the same config object.
        
        # Needs to have several labels with checkboxes.
        # Make another list that holds checkboxes that are checked at the
        # time that the user clicks the "Run Selected Checks" button. (selectedFunctList)
        
        # If the user clicks the "Run All Checks" button instead,
        # then just run all the checks in their proper sequence.
        
        # Store the list of all functions that can be run as a
        # list.
        
        # You can then use
        # for funct in functList:
        #     funct()
        # To run them all in order.
        # and
        # for funct in functList:
        #     if funct in selectedFunctList:
        #        funct()
        # To run just the selected ones
        # in the order that they appear in functList.
        
        # Can use function decorators to give the functions new variables,
        # unless they redefine those values themselves.
        
        # If certain checks should always be run after another check,
        # handle that by force-checking a box if the postcedent box is checked
        # or by just running them together any time that either the first or
        # second one is checked.
        
        
        # Add stretch to separate the form layout from the button
        self.dialogueLayout4.addStretch(1)
        
        # Create a text box to serve as a message box
        # for print outputs that the application
        # should display instead of or in addition
        # to sending to the console.
        self.textBox4 = QTextEdit()
        
        self.textBox4.setReadOnly(True)
        
        self.textBox4.setMinimumHeight(50)
        self.textBox4.setMaximumHeight(self.outputTextBoxHeight)
        self.textBox4.setMinimumWidth(200)
        self.textBox4.setMaximumWidth(400)
        self.dialogueLayout4.addWidget(self.textBox4)
        self.textBox4.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth) # Set line wrapping to the widget width.
        
        # Create a horizontal box layout to hold the button
        self.buttonBox4 = QHBoxLayout()
        
        # Add stretch to push the button to the far right
        self.buttonBox4.addStretch(1)
        
        # Create the next button with its caption
        self.backButton4 = QPushButton("&Back", self)
        
        # Connect the button's clicked signal to the doneFeatureAndFieldMapping function
        self.backButton4.clicked.connect(lambda: self.doneWithGDBSelection("Back"))
        
        # Add it to the button box
        self.buttonBox4.addWidget(self.backButton4)
        
        # Create the next button with its caption
        self.finishButton4 = QPushButton("&Finish", self)
        
        # Connect the button's clicked signal to the doneFeatureAndFieldMapping function
        self.finishButton4.clicked.connect(self.doneWithDataChecks)
        
        # Add it to the button box
        self.buttonBox4.addWidget(self.finishButton4)
        
        # Disable it for the time being
        self.finishButton4.setEnabled(False)
        
        # Create the quit button with its caption
        self.quitButton4 = QPushButton("&Quit", self)
        
        # Add it to the button box
        self.buttonBox4.addWidget(self.quitButton4)
        
        # Connect the button's clicked signal to the quitApplication function
        self.quitButton4.clicked.connect(self.quitApplication)
        
        # Add the button box to the bottom of the main VBox layout
        self.dialogueLayout4.addLayout(self.buttonBox4)
        
        # ----------------------------------------------------------------------
        # Init function continues by calling the Start GDB Selection function
        # ----------------------------------------------------------------------
    
    
    def updateTextBoxes(self, textToAdd):
        if self.textBoxMain.toPlainText() == "":
            self.textBoxMain.setPlainText(str(textToAdd))
        else:
            self.textBoxMain.setPlainText(self.textBoxMain.toPlainText() + lineSeparator + str(textToAdd))
        
        self.textBox1.setPlainText(self.textBoxMain.toPlainText())
        self.textCursor1 = self.textBox1.textCursor()
        self.textCursor1.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        self.textBox1.setTextCursor(self.textCursor1)
        
        self.textBox2.setPlainText(self.textBoxMain.toPlainText())
        self.textCursor2 = self.textBox2.textCursor()
        self.textCursor2.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        self.textBox2.setTextCursor(self.textCursor2)
        
        self.textBox4.setPlainText(self.textBoxMain.toPlainText())
        self.textCursor4 = self.textBox4.textCursor()
        self.textCursor4.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        self.textBox4.setTextCursor(self.textCursor4)
    
    
    def newMessaging(self, textToDisplay):
        self.updateTextBoxes(textToDisplay)
        print str(textToDisplay)
    
    
    def monkeyPatchOutput(self):
        # Replaces the userMessage function from
        # NG911_DataCheck with a different function.
        
        # The new function prevents the output from
        # printin twice on the console
        #(once from print statement, once from AddMessage)
        # and also shows it in the outputMessageBoxes.
        
        # This is known as "Monkey patching" a function
        # and is generally not recommended, but I'm
        # not 100% sure how else to get the DataChecks
        # to write output to the outputMessageBoxes
        # without inlining them or risking
        # a circular import by passing them the
        # NG911_Window object and its functions.
        
        # ^^ Calling them through subprocesses and piping
        # their output from proc.communicate()[0] per
        # http://stackoverflow.com/questions/4537259/python-how-to-pipe-the-output-using-popen
        # is probably the correct solution, but I'll leave that
        # upgrade for another time. Just trying
        # to get everything displaying/functioning right now.
        if guiOutputSetting == True:
            NG911_DataCheck.userMessage = self.newMessaging
            print "Modified userMessage."
        else:
            pass
        
    
    def startGDBSelection(self):
        
        #NG911_DataCheck.decoratorTest("Test Message-4") ## Success!
        
        #for selectorListItem in self.selectorList:
            #NG911_DataCheck.userMessage(selectorListItem.property("associatedFunction"))
        
        
        # -------------------------------------------------------
        # Hide Dialogue Layout 2 - Feature Mapping
        # -------------------------------------------------------
        
        self.dialogueLayout2Container.hide()
        #self.dialogueLayout3Container.hide()
        self.dialogueLayout4Container.hide()
        
        
        # -------------------------------------------------------
        # Show Dialogue Layout 1  - GDB Selection
        # -------------------------------------------------------
        
        self.dialogueLayout1Container.show()
        
        self.gdbPromptLabel.setText("Searching for GDBs...")
        
        
        # Then run listLocalGDBs(self)s
        self.gdbList1 = self.listLocalGDBs()
        # Sort the paths alphabetically
        self.gdbList1 = sorted(self.gdbList1)
        
        # Create and fill the ComboBox to choose the GDB
        
        self.localGDBCombobox.clear()
        self.localGDBCombobox.addItems(self.gdbList1)
        self.localGDBCombobox.setCurrentIndex(0)
        self.localGDBCombobox.adjustSize()
        self.localGDBCombobox.hasFocus()
        # Change the label box to prompt for geodatabase selection
        self.gdbPromptLabel.setText("Please select the GeoDatabase to check, then click the \"Next\" button.")
        
        
    def doneWithGDBSelection(self, fromButton):
        self.selectedGDBpath = self.localGDBCombobox.currentText()
        self.pathsObject.gdbPath = self.selectedGDBpath
        if self.localGDBCombobox.currentIndex() != -1 and self.selectedGDBpath.find(".gdb") >= 0:
            if fromButton == "Next":
                print self.selectedGDBpath + " selected."
                self.updateTextBoxes(self.selectedGDBpath + " selected.")
            else:
                pass
            
            # --------------------------------------------------
            # Hide Dialogue Layout 1 - GDB Selection
            # --------------------------------------------------
            
            # Instead of hiding/showing layouts, hide/show widget that contains the layout.
            self.dialogueLayout1Container.hide()
            self.dialogueLayout4Container.hide()
            
            # --------------------------------------------------
            # Show Dialogue Layout 2 - Feature Mapping
            # --------------------------------------------------
            
            self.dialogueLayout2Container.show()
            
            
            # Populate the default Feature Class ComboBox with the feature classes
            # that exist in the default model.
            self.defaultFeatureClassComboBox2.clear()
            self.defaultFeatureClassComboBox2.addItems(currentLayerList)
            self.defaultFeatureClassTextPrompt2 = "Select the Default Feature Class"
            self.defaultFeatureClassComboBox2.insertItem(0, self.defaultFeatureClassTextPrompt2)
            self.defaultFeatureClassComboBox2.setCurrentIndex(0)
            self.defaultFeatureClassComboBox2.adjustSize()
            self.defaultFeatureClassComboBox2.hide()
            self.defaultFeatureClassComboBox2.show()
            
            self.defaultFeatureClassComboBox2.hasFocus()
            
            # Default Fieldname combo box populated in a different function,
            # but needs to be cleared here also.
            self.defaultFieldNameComboBox2.clear()
            self.defaultFieldNamePretextPrompt2 = "First select a Default Feature Class"
            self.defaultFieldNameComboBox2.insertItem(0, self.defaultFieldNamePretextPrompt2)
            self.defaultFieldNameComboBox2.hide()
            self.defaultFieldNameComboBox2.show()
            
            # Populate the target Feature Class ComboBox with the feature classes
            # available in the selected gdb.
            self.featureClassesInSelectedGDB = self.listFeatureClassesInGDB(self.selectedGDBpath)
            
            self.targetFeatureClassComboBox2.clear()
            self.targetFeatureClassComboBox2.addItems(self.featureClassesInSelectedGDB)
            self.targetFeatureClassTextPrompt2 = "Select the Target Feature Class"
            self.targetFeatureClassComboBox2.insertItem(0, self.targetFeatureClassTextPrompt2)
            self.targetFeatureClassComboBox2.setCurrentIndex(0)
            self.targetFeatureClassComboBox2.setMinimumWidth(25)
            self.targetFeatureClassComboBox2.adjustSize()
            self.targetFeatureClassComboBox2.hide()
            self.targetFeatureClassComboBox2.show()
            
            # Target Field Name Combo Box populated in a different function,
            # but needs to be cleared here also.
            self.targetFieldNameComboBox2.clear()
            self.targetFieldNamePretextPrompt2 = "First select a Target Feature Class"
            self.targetFieldNameComboBox2.insertItem(0, self.targetFieldNamePretextPrompt2)
            self.targetFieldNameComboBox2.hide()
            self.targetFieldNameComboBox2.show()
            
            # Perform a function to show the feature class/field mapping buttons.
            # Done with feature class and field mapping button. -- Takes you to the data checks dialogue.
            # Start feature class mapping.
            # In Feature Class mapping dialogue:
            # add "Done mapping feature classes" button
            # Return to 
        else:
            print "No GDB selected."
            self.updateTextBoxes("No GDB selected.")
    
    
    def populateDefaultFieldNameComboBox2(self):
        self.currentDefaultFeatureClassResult2 = self.defaultFeatureClassComboBox2.currentText()
        if self.currentDefaultFeatureClassResult2 == self.defaultFeatureClassTextPrompt2:
            self.defaultFieldNameComboBox2.clear()
            self.defaultFieldNameComboBox2.insertItem(0, self.defaultFieldNamePretextPrompt2)
            self.defaultFieldNameComboBox2.setCurrentIndex(0)
            self.defaultFieldNameComboBox2.adjustSize()
        else:
            self.defaultFieldsList =  self.getDefaultFieldNames(self.currentDefaultFeatureClassResult2)
            
            self.defaultFieldNameComboBox2.clear()
            # Populate from default fields for the selected default feature class.
            self.defaultFieldNameComboBox2.addItems(self.defaultFieldsList)
            self.defaultFieldNameTextPrompt2 = "Select the Default Field Name"
            self.defaultFieldNameComboBox2.insertItem(0, self.defaultFieldNameTextPrompt2)
            self.defaultFieldNameComboBox2.setCurrentIndex(0)
            self.defaultFieldNameComboBox2.adjustSize()
            
        # Have to do an additional hide/show here to get the width right.
        self.defaultFieldNameComboBox2.hide()
        self.defaultFieldNameComboBox2.show()
    
    
    def populateTargetFieldNameComboBox2(self):
        self.currentTargetFeatureClassResult2 = self.targetFeatureClassComboBox2.currentText()
        if self.currentTargetFeatureClassResult2 == self.targetFeatureClassTextPrompt2:
            self.targetFieldNameComboBox2.clear()
            self.targetFieldNameComboBox2.insertItem(0, self.targetFieldNamePretextPrompt2)
            self.targetFieldNameComboBox2.setCurrentIndex(0)
            self.targetFieldNameComboBox2.adjustSize()
        else:
            self.currentTargetFieldsList2 = self.getTargetFieldNames(self.currentTargetFeatureClassResult2)
            
            self.targetFieldNameComboBox2.clear()
            # Populate from the existing fields in the selected target feature class.
            self.targetFieldNameComboBox2.addItems(self.currentTargetFieldsList2)
            self.targetFieldNameTextPrompt2 = "Select the Target Field Name"
            self.targetFieldNameComboBox2.insertItem(0, self.targetFieldNameTextPrompt2)
            self.targetFieldNameComboBox2.setCurrentIndex(0)
            self.targetFieldNameComboBox2.adjustSize()
            
        # Have to do an additional hide/show here to get the width right.
        self.targetFieldNameComboBox2.hide()
        self.targetFieldNameComboBox2.show()
    
    def doneFeatureAndFieldMapping(self):
        print "This feature is not yet fully implemented."
        # --------------------------------------------------
        # Hide Dialogue Layout 2 - Feature Class and Field Name Mapping
        # --------------------------------------------------
        # Instead of hiding/showing layouts, hide/show widget that contains the layout.
        self.dialogueLayout1Container.hide()
        self.dialogueLayout2Container.hide()
        
        
        # --------------------------------------------------
        # Show Dialogue Layout 4 - Data Checks
        # --------------------------------------------------
        self.dialogueLayout4Container.show()
        
        NG911_DataCheck.userMessage(self.pathsObject.gdbPath)
        
        #NG911_DataCheck.checkLayerList(self.pathsObject)
        
        #########################################################
        #
        # Need to give the option to select a default
        # feature class and select all for field mapping
        # along with the mapped feature class and all
        # for the field mapping...
        # This will be equivalent to telling
        # the program that all of the field names
        # are the same and only the feature class names
        # are changed.
        # Use ObjectID, DFC, DFN, MFC, MFN, DateTime for fields.
        # Then, load the entire table at once
        # and evaluate based on entries for
        # DFC\All and DFC\DFN instead of
        # trying to parse together and write out
        # then reparse together separate DFC\MFC and
        # DFN\MFN tables.
        # 
        # 
        # Also need to give the option to clear
        # all of the mappings for a default feature class.
        # Then, explain how ALL and CLEAR
        # work as fields and set up the logic to deal with
        # them.
        # 
        # 
        # First, it would make sense to get the data checks
        # in here though, so that you can share your progress
        # better and get some feedback.
        #########################################################
        
        #### Current Work Area ####
    
    
    def updateFeatureClassAndFieldNameMapping(self):
        self.defaultFeatureClassComboResult2 = self.defaultFeatureClassComboBox2.currentText()
        self.defaultFieldNameComboResult2 = self.defaultFieldNameComboBox2.currentText()
        self.targetFeatureClassComboResult2 = self.targetFeatureClassComboBox2.currentText()
        self.targetFieldNameComboResult2 = self.targetFieldNameComboBox2.currentText()
        
        featureAndFieldTableColumns = ["OBJECTID", "DefaultFeatureClass", "DefaultFieldName", "TargetFeatureClass", \
                                       "TargetFieldName", "LastModified"]
        featureAndFieldTablePath = os.path.join(env.workspace, "FeatureAndFieldLookup")  # @UndefinedVariable
        
        self.rowFoundInCursor = 0
        ##############################################################################
        # Add pretext prompt checks for defaultfieldname and targetfieldname.
        ##############################################################################
        if (self.defaultFeatureClassComboResult2 != self.defaultFeatureClassTextPrompt2 and \
            self.defaultFeatureClassComboResult2 != "" and \
            
            self.defaultFieldNameComboResult2 != self.defaultFieldNamePretextPrompt2 and \
            self.defaultFieldNameComboResult2 != self.defaultFieldNameTextPrompt2 and \
            self.defaultFieldNameComboResult2 != "" and \
            
            self.targetFeatureClassComboResult2 != self.targetFeatureClassTextPrompt2 and \
            self.targetFeatureClassComboResult2!= "" and \
            
            self.targetFieldNameComboResult2 != self.targetFieldNamePretextPrompt2 and \
            self.targetFieldNameComboResult2 != self.targetFieldNameTextPrompt2 and \
            self.targetFieldNameComboResult2 != ""):
            
            print "Updating Feature Class & Field Name: " + os.path.join(self.defaultFeatureClassComboResult2, self.defaultFieldNameComboResult2)
            print "to Map to: " + os.path.join(self.targetFeatureClassComboResult2, self.targetFieldNameComboResult2)
            self.updateTextBoxes("Updating Feature Class & Field Name: " + os.path.join(self.defaultFeatureClassComboResult2, self.defaultFieldNameComboResult2))
            self.updateTextBoxes("to Map to: " + os.path.join(self.targetFeatureClassComboResult2, self.targetFieldNameComboResult2))
            
            # Write the mapping to the geodatabase.
            #------------------------------------------------
            if arcpyExists(featureAndFieldTablePath):
                print "Found Table"
                featureAndFieldList = self.getFeatureAndFieldRows(featureAndFieldTablePath, featureAndFieldTableColumns)
                for featureAndFieldEntry in featureAndFieldList:
                    if (self.defaultFeatureClassComboResult2 == featureAndFieldEntry[1] and self.defaultFieldNameComboResult2 == featureAndFieldEntry[2]):
                        objectIDToUpdate = featureAndFieldEntry[0]
                        self.rowFoundInCursor = 1
                    else:
                        pass # Not found, will cause the next if/else to go to the else and insert rather than update.
                    
                if (self.rowFoundInCursor == 1): #row already exists with a matching defaultFeatureClassComboResult and defaultFieldNameComboResult
                    rowForUpdate = [objectIDToUpdate, str(self.defaultFeatureClassComboResult2), str(self.defaultFieldNameComboResult2),
                                    str(self.targetFeatureClassComboResult2), str(self.targetFieldNameComboResult2),
                                     datetime.datetime.now()]
                    
                    # Update the Row with the matching FeatureClassComboResult and FieldNameComboResult
                    # Should add a where clause on the OID to speed this up.
                    newCursor = daUpdateCursor(featureAndFieldTablePath, featureAndFieldTableColumns)  # @UnusedVariable @UndefinedVariable
                    for updateableRow in newCursor:
                        if updateableRow[0] == objectIDToUpdate:
                            newCursor.updateRow(rowForUpdate)
                            print "Updated row with ObjectID " + str(objectIDToUpdate)
                            self.updateTextBoxes("Updated row with ObjectID " + str(objectIDToUpdate))
                        else:
                            pass
                else:
                    # add a new row with FeatureClassComboResult and FieldNameComboResult
                    # [1:] gets the 2nd item through the end of the list. ObjectID is not included as it will be auto-added by the insert cursor.
                    newCursor = daInsertCursor(featureAndFieldTablePath, featureAndFieldTableColumns[1:])
                    rowToInsert = [str(self.defaultFeatureClassComboResult2), str(self.defaultFieldNameComboResult2), \
                                    str(self.targetFeatureClassComboResult2), str(self.targetFieldNameComboResult2), datetime.datetime.now()]
                    insertedObjectID = newCursor.insertRow(rowToInsert)
                    print "Inserted row with ObjectID " + str(insertedObjectID)
                    self.updateTextBoxes("Inserted row with ObjectID " + str(insertedObjectID))
                    if "newCursor" in locals():
                        del newCursor
                    else:
                        pass
                
            else:
                CreateTable_management(env.workspace, "FeatureAndFieldLookup")  # @UndefinedVariable
                AddField(featureAndFieldTablePath, "DefaultFeatureClass", "TEXT", "100")
                AddField(featureAndFieldTablePath, "DefaultFieldName", "TEXT", "100")
                AddField(featureAndFieldTablePath, "TargetFeatureClass", "TEXT", "100")
                AddField(featureAndFieldTablePath, "TargetFieldName", "TEXT", "100")
                AddField(featureAndFieldTablePath, "LastModified", "DATE")
                
                # add a new row with FeatureClassComboResult and FieldNameComboResult
                # [1:] gets the 2nd item through the end of the list. ObjectID is not included as it will be auto-added by the insert cursor.
                newCursor = daInsertCursor(featureAndFieldTablePath, featureAndFieldTableColumns[1:])
                rowToInsert = [str(self.defaultFeatureClassComboResult2), str(self.defaultFieldNameComboResult2), \
                                str(self.targetFeatureClassComboResult2), str(self.targetFieldNameComboResult2), datetime.datetime.now()]
                insertedObjectID = newCursor.insertRow(rowToInsert)
                print "Inserted row with ObjectID " + str(insertedObjectID)
                self.updateTextBoxes("Inserted row with ObjectID " + str(insertedObjectID))
                
                if "newCursor" in locals():
                    del newCursor
                else:
                    pass
        else:
            # Default Feature Class Combo Box Warnings:
            if self.defaultFeatureClassComboResult2 == self.defaultFeatureClassTextPrompt2:
                print "Please select a Default Feature Class."
                self.updateTextBoxes("Please select a Default Feature Class.")
            elif self.defaultFeatureClassComboResult2 == "":
                print "No Default Feature Class selected."
                self.updateTextBoxes("No Default Feature Class selected.")
                
            # Default Field Name Combo Box Warnings:
            elif str(self.defaultFieldNameComboResult2).upper() == str(self.defaultFieldNamePretextPrompt2).upper():
                print "Please select a Default Feature Class."
                self.updateTextBoxes("Please select a Default Feature Class.")
            elif str(self.defaultFieldNameComboResult2).upper() == str(self.defaultFieldNameTextPrompt2).upper():
                print "Please select a Default Field Name to map."
                self.updateTextBoxes("Please select a Default Field Name to map.")
            elif str(self.defaultFieldNameComboResult2) == "":
                print "No Default Field Name selected."
                self.updateTextBoxes("No Default Field Name selected.")
                
            # Target Feature Class Combo Box Warnings:
            elif self.targetFeatureClassComboResult2 == self.targetFeatureClassTextPrompt2:
                print "Please select a Target Feature Class."
                self.updateTextBoxes("Please select a Target Feature Class.")
            elif self.targetFeatureClassComboResult2 == "":
                print "No Target Feature Class selected."
                self.updateTextBoxes("No Target Feature Class selected.")
                
            # Target Field Name Combo Box Warnings:
            elif str(self.targetFieldNameComboResult2).upper() == str(self.targetFieldNamePretextPrompt2).upper():
                print "Please select a Target Field Name to map."
                self.updateTextBoxes("Please select a Target Field Name to map.")
            elif str(self.targetFieldNameComboResult2).upper() == str(self.targetFieldNameTextPrompt2).upper():
                print "Please select a Target Field Name to map."
                self.updateTextBoxes("Please select a Target Field Name to map.")
            elif str(self.targetFieldNameComboResult2) == "":
                print "No Target Field Name selected."
                self.updateTextBoxes("No Target Field Name selected.")
                
            else:
                pass
    
    
    def runSelectedDataChecks(self):
        self.selectedItemsList = list()
        for possiblySelectedItem in self.selectorList:
            if possiblySelectedItem.isChecked() == True:
                self.selectedItemsList.append(possiblySelectedItem.property("associatedFunction"))
                
        for dataCheckFunct in self.dataCheckFunctList:
            if dataCheckFunct in self.selectedItemsList:
                dataCheckFunct(self.pathsObject)
            else:
                pass
    
    
    def listFeatureClassesInGDB(self, inWorkspaceLocation):
        """ Will not work properly if inWorkspaceLocation is not properly defined. """
        env.workspace = inWorkspaceLocation
        featureClassesList = list()
        for foundFeatureDataset in ListDatasets("",""):
            for foundFeatureClass in ListFeatureClasses("","",foundFeatureDataset):
                FeatureClassesHold1 = str(foundFeatureDataset)
                FeatureClassesHold2 = str(foundFeatureClass)
                FeatureClassesJoin1 = os.path.join(FeatureClassesHold1, FeatureClassesHold2)
                featureClassesList.append(FeatureClassesJoin1)
        for foundFeatureClass in ListFeatureClasses("",""): # Doesn't seem to be working. Troubleshoot. Should show road alias table.
            featureClassesList.append(str(foundFeatureClass))
        for foundTable in ListTables("", ""): # Added ListTables to actually list tables, see if it fixes.
            featureClassesList.append(str(foundTable))
            
        itemsToRemove = list()
        itemsToRemove.append(str("FeatureClassLookup").upper())
        itemsToRemove.append(str("FieldNameLookup").upper())
        itemsToRemove.append(str("FeatureAndFieldLookup").upper())
        
        # List comprehension to build a list that is a copy of featureClasses list, without the
        # entries in the itemsToRemove list. Changes the strings to uppercase for comparison, 
        # but does not change them in the output list.
        cleanedFeatureClassesList = [feature for feature in featureClassesList if str(feature).upper() not in itemsToRemove]
        cleanedFeatureClassesList = sorted(cleanedFeatureClassesList)
        return cleanedFeatureClassesList
    
    
    def getCombinedFeatureClasses(self):
        # Read the feature class mapping table into a dictionary.
        self.combinedFeatureClassesDict = dict()
        # Use list() to make a copy of the currentLayerList variable.
        ### WARNING: ###
        # Using combinedFeatureClassesList = currentLayerList modifies curretLayerList every time combinedFeatureClassesList is changed.
        # Without calling list() again, the second assignment just adds a name that points to the same list.
        combinedFeatureClassesList = list(currentLayerList)
        
        if arcpyExists(str(os.path.join(str(self.selectedGDBpath), "FeatureClassLookup"))):  # @UndefinedVariable
            newCursor = daSearchCursor(str(os.path.join(str(self.selectedGDBpath), "FeatureClassLookup")), ["DefaultFeatureClass", "MappedFeatureClass"])
            for searchRow in newCursor:
                self.combinedFeatureClassesDict[searchRow[0]] = searchRow[1]
            
            for i, defaultItem in enumerate(combinedFeatureClassesList):
                if defaultItem in self.combinedFeatureClassesDict:
                    combinedFeatureClassesList[i] = self.combinedFeatureClassesDict[defaultItem]
                else:
                    pass
        else:
            pass
        
        combinedFeatureClassesList = sorted(combinedFeatureClassesList)
        return combinedFeatureClassesList
    
    
    def fieldNamesFilter(self, textToFilterOn):
        #print "0: " + textToFilterOn.split(os.path.sep)[0]
        #print "0\\1: " + str(os.path.join(textToFilterOn.split(os.path.sep)[0], textToFilterOn.split(os.path.sep)[1]))
        if str(os.path.join(textToFilterOn.split(os.path.sep)[0], textToFilterOn.split(os.path.sep)[1])).upper() == str(self.currentFeatureText).upper():
            return True
        elif str(textToFilterOn.split(os.path.sep)[0]).upper() == str(self.currentFeatureText).upper():
            return True
        else:
            return False
    
    
    def fieldNamesFilterNonDisplay(self, textToFilterOn):
        
        textToFilterOnList = textToFilterOn.split(os.path.sep)[-1:]
        textToFilterOnStr = textToFilterOnList[0]
        for nonDisplayField in nonDisplayFields:
            if textToFilterOnStr.upper() == nonDisplayField.upper():
                return False
            else:
                pass
            
        return True
    
    
    def getDefaultFieldNames(self, defaultFeatureClassResult):
        defaultFieldNamesList = list()
        for keyName in self.defaultFieldsDict:
            if str(keyName).upper() == str(os.path.split(defaultFeatureClassResult)[-1]).upper():
                defaultFieldNamesList = self.defaultFieldsDict[keyName]
                
                defaultFieldNamesList = filter(self.fieldNamesFilterNonDisplay, defaultFieldNamesList)
                defaultFieldNamesList = sorted(defaultFieldNamesList)
            else:
                pass
            
        return defaultFieldNamesList
    
    
    def getTargetFieldNames(self, targetFeatureClassResult):
        targetFieldNamesList = list()
        
        if arcpyExists(os.path.join(self.selectedGDBpath, targetFeatureClassResult)):
            targetFieldList = ListFields(os.path.join(self.selectedGDBpath, targetFeatureClassResult))
            for targetField in targetFieldList:
                targetFieldNamesList.append(targetField.name)
                
            targetFieldNamesList = filter(self.fieldNamesFilterNonDisplay, targetFieldNamesList)
            targetFieldNamesList = sorted(targetFieldNamesList)
        else:
            pass
        
        return targetFieldNamesList
        
    
    
    def getFeatureAndFieldRows(self, passedTableName, passedTableFields):
        newCursor = daSearchCursor(passedTableName, passedTableFields)
        rowList = list()
        for searchRow in newCursor:
            rowList.append(list(searchRow))
        if "newCursor" in locals():
            del newCursor
        else:
            pass
        return rowList
    
    
    def getMappedFeatureClasses(self):
        newCursor = daSearchCursor(env.workspace + "\FeatureClassLookup", ["OBJECTID", "DefaultFeatureClass", "MappedFeatureClass", "LastModified"])  # @UnusedVariable @UndefinedVariable
        rowList = list()
        for searchRow in newCursor:
            rowList.append(list(searchRow))
        if "newCursor" in locals():
            del newCursor
        else:
            pass
        return rowList
    
    def updateFieldNameMapping(self): 
            
        
        if str(self.selectDefaultFieldNameResult3).upper() == str(self.selectDefaultFieldNameTextPreprompt3).upper():
            print "Please select a Feature Class to map first."
            self.updateTextBoxes("Please select a Feature Class to map first.")
        elif str(self.selectTargetFieldNameResult3).upper() == str(self.selectTargetFieldNameTextPreprompt3).upper():
            print "Please select a Feature Class to map first."
            self.updateTextBoxes("Please select a Feature Class to map first.")
        elif str(self.selectDefaultFieldNameResult3).upper() == str(self.selectDefaultFieldNameTextPrompt3).upper():
            print "Please select a Default Field Name to map."
            self.updateTextBoxes("Please select a Default Field Name to map.")
        elif str(self.selectTargetFieldNameResult3).upper() == str(self.selectTargetFieldNameTextPrompt3).upper():
            print "Please select a Target Field Name to map."
            self.updateTextBoxes("Please select a Target Field Name to map.")
        else:
            pass


    def getFieldNameMapping(self):
        print "This feature is not yet fully implemented."
        return "!Error!"
        # Test updateFieldNameMapping, then
        # Add a way to get the data back out
        # and combine with the default
        # feature classes and field names
        # to get a full listing
        # that can be used for the data
        # checks that need it.
    
    def doneFieldNameMapping(self):
        print "This feature is not yet fully implemented."
        # --------------------------------------------------
        # Hide Dialogue Layout 2 - Feature Class and Field Name Mapping
        # --------------------------------------------------
        # Instead of hiding/showing layouts, hide/show widget that contains the layout.
        self.dialogueLayout1Container.hide()
        self.dialogueLayout2Container.hide()
        
        
        # --------------------------------------------------
        # Show Dialogue Layout 4 - Data Checks
        # --------------------------------------------------
        self.dialogueLayout4Container.show()
        
        
    def doneWithDataChecks(self):
        print "All done!"
        self.quitApplication()
        pass


    def quitApplication(self):
        if self.okayToQuit == 1:
            qt_app.quit()
        else:
            print "Please wait for the current operation to complete before closing."
            pass


    def run(self):
        # Show the form
        self.show()
        # Set the qt_app's style.
        qt_app.setStyle(QStyleFactory.create("WindowsXP"))
        # Run the qt application
        qt_app.exec_()


def formatCurrentLayerList(inputLayerList):
    if len(inputLayerList) <= 0:
        inputLayerList = ["RoadAlias", "AddressPoints", "RoadCenterline", "AuthoritativeBoundary", "CountyBoundary", "ESZ", "PSAP", "MunicipalBoundary", "EMS", "FIRE", "LAW"]
    else:
        pass
    
    for i, listItem in enumerate(inputLayerList):
        if listItem == "RoadAlias":
            pass
        else:
            inputLayerList[i] = str(os.path.join("NG911", listItem))
            
    outputLayerList = sorted(inputLayerList)
    return outputLayerList


# Also, try to center the update mapping buttons in the right-hand column of the layouts.
# Unused decorator function example below:
'''def userMessageAndTextBoxes(self, functionName):
        def addedMessaging(textInput):
            functionName(textInput)
            self.updateTextBoxes(textInput)
        return addedMessaging'''

currentLayerList = formatCurrentLayerList(currentLayerList)
#Creates an instance of the NG911_Window class and runs it.
app = NG911_Window()
app.run()
