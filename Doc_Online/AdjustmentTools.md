**Adjustment Tools**

Description: The adjustment tools will help prepare data so it passes
all data checks prior to submission into the NG911 Portal.

[*Fix Attributes*](#fixAttributes): Based on attribute issues that exist 
in FieldValuesCheckResults, this tool edits character issues in data. 
It fixes spelled out NULL and various special characters that cause 
issues with geospatial call routing.

[*Fix Domain Case*](#domainCase): Based on domain issues that exist in
FieldValuesCheckResults, this tool edits case issues in data. For
example, if FieldValuesCheckResults has the error “Value Primary not in
approved domain for field LOCTYPE”, any occurrences of “Primary” in
LOCTYPE will be edited to “PRIMARY”.

[*Fix Duplicate ESBIDs*](#duplicateESBID): For counties with three ESB layers, all ESBIDs/NGESBIDs
must be unique when comparing all three layers against one another. This
tool creates unique ESBIDs/NGESBIDs by appending “E”, “F”, or “L” to the end of
ESBIDs/NGESBIDs. Thus, if “1” is the ESBID/NGESBID in EMS, Fire, and Law, after running
the tool, features will have unique ESBIDs/NGESBIDs like “1E”, “1F”, & “1L”.

[*Fix KSPID*](#fixSpaces): If a county’s KSPID includes dashes or dots, this tool with automatically 
remove those characters so the KSPID is the required 19 digits.

[*Fix MSAGCO Spaces*](#fixSpaces): This tool will remove any leading or trailing spaces in MSAGCO, MSAGCO_L, and 
MSAGCO_R fields in the Address Point and Road Centerline feature classes.

[*Fix Submit*](#fixSpaces): This tool auto-fills all blank or null SUBMIT fields in all required feature classes as “Y”.

<a name="fixAttributes"></a>
Running *Fix Attributes*:
1.	First, run “Validation Tools” > “9 Optional Check All Required” to 
    make sure all address field components of address points and road 
    centerlines are examined and all issues are recorded in FieldValuesCheckResults.
2.	Open “Adjustment Tools” > “Fix Attributes” and identify the parameters for the 
    NG911 geodatabase and the folder containing domains files.
3.	Run the tool.
4.	Run “Validation Tools” > “9 Optional Check All Required” again. See the difference 
    of results in FieldValuesCheckResults.

<a name="domainCase"></a>
Running *Fix Domain Case*:

1.  First, run “Validation Tools” &gt; “9 Optional Check All Required”
    to make sure all domains of all feature classes are examined and all
    issues are recorded in FieldValuesCheckResults.

2.  Open “Adjustment Tools” &gt; “Fix Domain Case” and identify the
    parameters for the NG911 geodatabase and the folder containing
    domains files.

3.  Run the tool.

4.  Run “Validation Tools” &gt; “9 Optional Check All Required” again.
    See the difference of results in FieldValuesCheckResults.

<a name="duplicateESBID"></a>
Running *Fix Duplicate ESB IDs*:

1.	Open “Adjustment Tools” > “Fix Duplicate ESB IDs” and identify all the pertinent ESB layers according to the parameters.

2.	Run the tool.

3.	Run “Validation Tools” > “9 Optional Check All Required” again. See the difference of results in FieldValuesCheckResults.

< a name="fixSpaces"></a>
Running *Fix KSPID, Fix MSAGCO Spaces, & Fix Submit*:

1.	Open “Adjustment Tools” and the tool you want to run and identify your NG911 geodatabase.

2.	Run the tool.

3.	Run “Validation Tools” > “9 Optional Check All Required” again. See the difference of results in FieldValuesCheckResults.

The adjustment tools require:

-   The complete NG911 toolbox setup and all scripts it includes.

Support Contact:

For issues or questions, please contact Kristen Jordan Koenig with the
Kansas Data Access and Support Center. Email Kristen at
<Kristen@kgs.ku.edu> and please include in the email which script you
were running, any error messages, and a zipped copy of your geodatabase
(change the file extension from zip to piz so it gets through the email
server).

Disclaimer: The Kansas NG9-1-1 GIS Toolbox is provided by the Kansas 911
Coordinating Council, Kansas GIS Policy Board’s Data Access & Support
Center (DASC), and associated contributors "as is" and any express or
implied warranties, including, but not limited to, the implied
warranties of merchantability and fitness for a particular purpose are
disclaimed. In no event shall the Kansas 911 Coordinating Council, DASC,
or associated contributors be liable for any direct, indirect,
incidental, special, exemplary, or consequential damages (including, but
not limited to, procurement of substitute goods or services; loss of
use, data, or profits; or business interruption) however caused and on
any theory of liability, whether in contract, strict liability, or tort
(including negligence or otherwise) arising in any way out of the use of
this software, even if advised of the possibility of such damage.
