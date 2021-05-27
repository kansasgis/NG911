**MSAG Tools**

Description: These tools assist with verifying a PSAP’s TN list and MSAG information against the NG911 data.

*Worthwhile Information*: These tools will create a folder for all locators and geocoding output in the same folder as your NG911 geodatabase. The name of the folder will be your NG911 geodatabase name with “_TN” appended to the end. So, if your geodatabase name is “KSCO_NG911.gdb”, the folder will be named “KSCO_NG911_TN”. All geocoding working files and outputs for MSAG analysis will be inside a geodatabase in this folder.

[*Check AT&T TN List*](#TNList): This tool is for PSAPs who have AT&T as their provider. The tool geocodes a list of telephone number addresses against the MSAG information in the NG911 Address Points and Road Centerlines. This tool requires a TN (telephone number) list. Directions for obtaining the TN list are found in the Downloading_TN_records_from_911Net document. Please see detailed tool instructions below for information on the geocoding results.

[*Check Other TN List*](#GeocodePrepped): This tool is intended for PSAPs who do not have AT&T as their provider. This tool geocodes full addresses housed in a spreadsheet against MSAG information in an NG911 geodatabase. 

[*MSAG NG911 Comparison*](#https://github.com/kansasgis/NG911/tree/master/Doc_Online/MSAG_NG911_comparison.pdf): see link for full tool documentation

<a name="TNList"></a>
Running *Check AT&T TN List*:
This tool requires a telephone number list to be extracted as a spreadsheet from AT&T. Directions for obtaining the TN list are found in the Downloading_TN_records_from_911Net document.

  1.	Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS Tools” > “MSAG Tools” > “Check AT&T TN List”.
  
  2.	In the “TN Spreadsheet” input box, select the TN Spreadsheet provided by the telephone company.
  
  3.	In the “NG911 Geodatabase” box, select the appropriate NG911 geodatabase.
  
  4.	Run the tool.
  
  5.	The results will be contained in a folder that sits next to your NG911 geodatabase. The name of the folder will be your NG911 geodatabase name with “_TN” appended to the end. If your geodatabase name is “KSCO_NG911.gdb”, the folder will be named “KSCO_NG911_TN”. Inside this folder will be a geodatabase called “TN_Working.gdb”. In this geodatabase, you will find two tables and a feature class with the day’s date appended to the end.
  
  6.	Your TN list spreadsheet is copied in the geodatabase as TN_List_YYYYMMDD with one column added called NGTNID for a unique ID. If you had columns for NPA, NXX and PHONELINE, the unique ID is a concatenation of these columns to form the phone number. If the ID is the phone number, this ID is persistent throughout all of your MSAG reviewing and editing. If the ID is not a phone number, then the ID has been randomly generated and is persistent for this single geocoding session.
  
  7.	All results from the geocoding operation will be found in TN_List_YYYYMMDD. This table can be brought into ArcMap and viewed as a normal point file. The geocoding status for each record can be found in the “MATCH” column. M = Matched, T = Tied, U = Unmatched.
  
<a name="GeocodePrepped"></a>  
Running *Check Other TN List*:

1.	Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS Tools” > “MSAG Tools” > “Check Other TN List”.

2.	In the “NG911 Geodatabase” box, select the appropriate NG911 geodatabase.

3.	In “Excel Spreadsheet”, select your TN extract spreadsheet.

4.	For the various fields outlined in the tool, fill in all fields that are in your spreadsheet. The more fields you can fill in, the more accurate the results will be. Several fields are required like House Number, Road Name, and Community.

5.	Run the tool.

6.	The results will be contained in a folder that sits next to your NG911 geodatabase. The name of the folder will be your NG911 geodatabase name with “_TN” appended to the end. If your geodatabase name is “KSCO_NG911.gdb”, the folder will be named “KSCO_NG911_TN”. Inside this folder will be a geodatabase called “TN_Working.gdb”. In this geodatabase, you will find two tables and a feature class with the day’s date appended to the end.

7.	Your TN list spreadsheet is copied in the geodatabase as TN_List_YYYYMMDD with one column added called NGTNID for a unique ID. If you defined a Phone Number field when running the tool, the phone number is the unique ID. If the ID is the phone number, this ID is persistent throughout all of your MSAG reviewing and editing. If the ID is not a phone number, then the ID has been randomly generated and is persistent for this single geocoding session.

8.	All results from the geocoding operation will be found in TN_List_YYYYMMDD. This table can be brought into ArcMap. The geocoding status for each record can be found in the “MATCH” column. M = Matched, T = Tied, U = Unmatched.

Support Contact:

For issues or questions, please contact Kristen Jordan Koenig with the Kansas Data Access and Support Center. Email Kristen at Kristen.kgs@ku.edu and please include in the email which script you were running, any error messages, and a zipped copy of your geodatabase.

Disclaimer: The Kansas NG9-1-1 GIS Toolbox is provided by the Kansas 911 Coordinating Council, Kansas GIS Policy Board’s Data Access & Support Center (DASC), and associated contributors "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.  In no event shall the Kansas 911 Coordinating Council, DASC, or associated contributors be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
