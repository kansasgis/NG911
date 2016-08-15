**MSAG Tools**

Description: These tools assist with verifying a PSAP’s TN list and MSAG information against the NG911 data.

*Worthwhile Information*: These tools will create a folder for all locators and geocoding output in the same folder as your NG911 geodatabase. The name of the folder will be your NG911 geodatabase name with “_TN” appended to the end. So, if your geodatabase name is “KSCO_NG911.gdb”, the folder will be named “KSCO_NG911_TN”. All geocoding working files and outputs for MSAG analysis will be inside a geodatabase in this folder.

[*Check TN List*](#TNList): geocodes a list of telephone number addresses against the MSAG information in the NG911 Address Points and Road Centerlines. This tool requires a TN (telephone number) list. Directions for obtaining the TN list are found in the Downloading_TN_records_from_911Net document. Please see detailed tool instructions below for information on the geocoding results.

[*Create MSAG Locator*](#MSAGLoc): creates a composite locator from an address point locator and a road centerline locator using MSAGCO data. This tool is intended for users who want to manually geocode TN or MSAG data against the NG911 data.

[*Geocode Prepped TN List*](#GeocodePrepped): geocodes full addresses housed in a spreadsheet against MSAG information in an NG911 geodatabase. To run this tool, the user must have a spreadsheet that has a field pre-concatenated, full addresses with a city appended to the end. Appropriate address format examples include:

-	1000 3RD ST, GREAT BEND, KS

- 1000 3RD ST, GREAT BEND

<a href="TNList"></a>
Running *Check TN List*:
This tool requires a telephone number list to be extracted as a spreadsheet. Directions for obtaining the TN list are found in the Downloading_TN_records_from_911Net document.

  1.	Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS Tools” > “MSAG Tools” > “Check TN List”.
  
  2.	In the “TN Spreadsheet” input box, select the TN Spreadsheet provided by the telephone company.
  
  3.	In the “NG911 Geodatabase” box, select the appropriate NG911 geodatabase.
  
  4.	Run the tool.
  
  5.	The results will be contained in a folder that sits next to your NG911 geodatabase. The name of the folder will be your NG911 geodatabase name with “_TN” appended to the end. If your geodatabase name is “KSCO_NG911.gdb”, the folder will be named “KSCO_NG911_TN”. Inside this folder will be a geodatabase called “TN_Working.gdb”. In this geodatabase, you will find two tables and a feature class with the day’s date appended to the end.
  
  6.	Your TN list spreadsheet is copied in the geodatabase as TN_List_YYYYMMDD with one column added called NGTNID for a unique ID. If you had columns for NPA, NXX and PHONELINE, the unique ID is a concatenation of these columns to form the phone number. If the ID is the phone number, this ID is persistent throughout all of your MSAG reviewing and editing. If the ID is not a phone number, then the ID has been randomly generated and is persistent for this single geocoding session.
  
  7.	All results from the geocoding operation will be found in TN_GC_Output_YYYYMMDD. This feature class can be brought into ArcMap and viewed as a normal point file. The geocoding status for each record can be found in the “Status” column. M = Matched, T = Tied, U = Unmatched.
  
  8.	TN_Geocode_Results_YYYYMMDD contains a full report of all tied and unmatched records. These are referenced by NGTNID. Please see notes under #6 for details regarding the unique ID.
  
  9.	To review TN_Geocode_Results_YYYYMMDD against the TN_List_YYYYMMDD, bring both tables into ArcMap and create a join from TN_List_YYYYMMDD to TN_Geocode_Results_YYYYMMDD based on the NGTNID.

<a href="MSAGLoc"></a>  
Running *Create MSAG Locator*:

  1.	Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS Tools” > “MSAG Tools” > “Create MSAG Locator”.
  
  2.	In the “NG911 Geodatabase” box, select the appropriate NG911 geodatabase.
  
  3.	Run the tool.
  
  4.	This tool will create three locators in a folder that sits next to your NG911 geodatabase. The name of the folder will be your NG911 geodatabase name with “_TN” appended to the end. If your geodatabase name is “KSCO_NG911.gdb”, the folder will be named “KSCO_NG911_TN”.
  
  5.	The locators will be called: AddressLocator, Composite Loc, and RoadLocator.
  
  6.	For comprehensive geocoding, please use the CompositeLoc since it is a combination of the AddressLocator and RoadLocator.
  
<a href="GeocodePrepped"></a>  
Running *Geocode Prepped TN List*:

1.	Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS Tools” > “MSAG Tools” > “Geocode Prepped TN List”.

2.	In the “NG911 Geodatabase” box, select the appropriate NG911 geodatabase.

3.	In “Excel Spreadsheet”, select your TN extract spreadsheet.

4.	In “Full Address Field”, select the proper full address field from the dropdown. This field needs to have pre-concatenated, full addresses with a city appended to the end. Appropriate address format examples include:

  a.	1000 3RD ST, GREAT BEND, KS
  
  b.	1000 3RD ST, GREAT BEND

5.	Run the tool.

6.	The results will be contained in a folder that sits next to your NG911 geodatabase. The name of the folder will be your NG911 geodatabase name with “_TN” appended to the end. If your geodatabase name is “KSCO_NG911.gdb”, the folder will be named “KSCO_NG911_TN”. Inside this folder will be a geodatabase called “TN_Working.gdb”. In this geodatabase, you will find two tables and a feature class with the day’s date appended to the end.

7.	Your TN list spreadsheet is copied in the geodatabase as TN_List_YYYYMMDD with one column added called NGTNID for a unique ID. If you had columns for NPA, NXX and PHONELINE, the unique ID is a concatenation of these columns to form the phone number. If the ID is the phone number, this ID is persistent throughout all of your MSAG reviewing and editing. If the ID is not a phone number, then the ID has been randomly generated and is persistent for this single geocoding session.

8.	All results from the geocoding operation will be found in TN_GC_Output_YYYYMMDD. This feature class can be brought into ArcMap and viewed as a normal point file. The geocoding status for each record can be found in the “Status” column. M = Matched, T = Tied, U = Unmatched.

9.	TN_Geocode_Results_YYYYMMDD contains a full report of all tied and unmatched records. These are referenced by NGTNID. Please see notes under #8 for details regarding the unique ID.

10.	To review TN_Geocode_Results_YYYYMMDD against the TN_List_YYYYMMDD, bring both tables into ArcMap and create a join from TN_List_YYYYMMDD to TN_Geocode_Results_YYYYMMDD based on the NGTNID.

Support Contact:

For issues or questions, please contact Kristen Jordan Koenig with the Kansas Data Access and Support Center. Email Kristen at Kristen@kgs.ku.edu and please include in the email which script you were running, any error messages, and a zipped copy of your geodatabase (change the file extension from zip to piz so it gets through the email server).

Disclaimer: The Kansas NG9-1-1 GIS Toolbox is provided by the Kansas 911 Coordinating Council, Kansas GIS Policy Board’s Data Access & Support Center (DASC), and associated contributors "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.  In no event shall the Kansas 911 Coordinating Council, DASC, or associated contributors be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
