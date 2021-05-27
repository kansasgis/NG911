readme.txt for Kansas NG911 GIS Tools

These tools assist with various tasks in preparing and validating data for the Kansas NG911 GIS project. 

These tools are intended for ArcGIS Desktop version 10.3 and higher and ArcGIS Pro.

To get started using the tools, please read "GettingStarted.docx" located in this same folder or read
the online version at https://github.com/kansasgis/NG911/blob/master/GettingStarted.md

The project consists of:
	readme.txt
	Kansas NG911 GIS Tools.tbx
	GettingStarted.docx
	GettingStarted.md
	Doc
		AdjustmentTools.docx
		ComparisonTools.docx
		ConversionTools.docx
		Downloading_TN_records_from_911NET.docx
		Downloading_TN_records_from_911NET.pdf
		EnhancementTools.docx
		Interpreting_Tool_Results.docx
		MSAGTools.docx
		SubmissionTools.docx
		ValidationTools.docx
	Doc_Online
		.md versions of the documents listed above
		Exception: The TN records document is not available online
	Domains
		AGENCYID_Domains.txt
		COUNTRY_Domains.txt
		COUNTY_Domains.txt
		CountyCodes.cpg
		CountyCodes.dbf
		CountyCodes.dbf.xml
		EXCEPTION_Domains.txt
		GATE_TYPE_Domains.txt
		HYDTYPE_Domains.txt
		KS_HWY.txt
		LOCTYPE_Domains.txt
		MUNI_Domains.txt
		NG911_FieldDefinitions.txt
		NG911_RequiredFields.txt
		ONEWAY_Domains.txt
		PARITY_Domains.txt
		PLC_Domains.txt
		POD_Domains.txt
		POSTCO_Domains.txt
		PRD_Domains.txt
		PRIVATE_Domains.txt
		RDCLASS_Domains.txt
		STATE_Domains.txt
		STATUS_Domains.txt
		STEWARD_Domains.txt
		STS_Domains.txt
		SUBMIT_Domains.txt
		SURFACE_Domains.txt
		YNU_Domains.txt
		ZIP_Domains.txt
	Scripts
		Adjustment_CreateGeocodeExceptions.py
		Adjustment_FixDomainCase.py
		Adjustment_FixDuplicateESBIDs.py
		Comparison_CompareDataLayers.py
		Conversion_AddParcels.py
		Conversion_GDB10to11.py (not utilized in a tool)
		Conversion_GDB11to20.py
		Conversion_GDBtoShapefile.py
		Conversion_ZipNG911Geodatabase.py
		CoordConvertor.py
		Enhancement_AddKSPID.py
		Enhancement_AssignID.py
		Enhancement_CalculateLabel.py
		Enhancement_CheckRoadElevationDirection.py
		Enhancement_CreatRoadAliasRecords.py
		Enhancement_FindAddressRangeOverlaps.py
		Enhancement_GeocodeAddressPoints.py
		Enhancement_RoadNameComparison.py
		Enhancement_SplitSingleESBLayer.py
		Enhancement_VerifyRoadAlias.py
		Enhancement_XYUSNGCalc.py
		Metadata_EnhanceMetadata.py (not utilized in a tool)
		MSAG_CheckTN.py
		MSAG_CreateLocators.py
		MSAG_GeocodeTNList_Prepped.py
		NG911_arcpy_shortcuts.py
		NG911_Config.py (not utilized in a tool)
		NG911_DataCheck.py
		NG911_DataFixes.py
		Submission_CheckAllAndZip.py
		ToolboxVersion.json
		Validation_CheckAddressPointsLaunch.py
		Validation_CheckyAdminBndLaunch.py
		Validation_CheckAll.py
		Validation_CheckBoundariesLaunch.py
		Validation_CheckESBLaunch.py (not utilized in a tool)
		Validation_CheckOtherLayers.py
		Validation_CheckRoadsLaunch.py
		Validation_CheckTemplateLaunch.py
		Validation_ClearOldResults.py
		Validation_UpdateDomains.py
		Validation_VerifyTopologyExceptions.py
		
The official repository for this project is on the KansasGIS GitHub account.

The tool will be available as a package download from the Kansas Data Access and Support Center (DASC) website: http://www.kansasgis.org

Support: for questions or issues, email a full description to Kristen: kristen.kgs at ku.edu

Credits: Scripts written by Sherry Massey with Dickinson County, Kristen Jordan Koenig with DASC, and Kyle Gonterwitz and Dirk Talley with Kansas Department of Transportation

Disclaimer: The Kansas NG9-1-1 GIS Toolbox is provided by the Kansas 911 Coordinating Council, Kansas GIS Policy Board’s Data Access & Support Center (DASC), 
and associated contributors "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness 
for a particular purpose are disclaimed.  In no event shall the Kansas 911 Coordinating Council, DASC, or associated contributors be liable for any direct, 
indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, 
data, or profits; or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence 
or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.





	
