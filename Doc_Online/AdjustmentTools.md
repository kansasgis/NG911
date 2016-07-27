**Adjustment Tools**

Description: The adjustment tools will help prepare data so it passes
all data checks prior to submission into the NG911 Portal.

*Create Geocode Exceptions*: This tool creates a table in the
geodatabase called GeocodeExceptions. Based on geocoding errors that
exist in FieldValuesCheckResults, the tool adds those ADDIDs to the
GeocodeException table. In the future, any ADDIDs noted in
GeocodeExceptions will not be flagged as geocoding errors.

*Fix Domain Case:* Based on domain issues that exist in
FieldValuesCheckResults, this tool edits case issues in data. For
example, if FieldValuesCheckResults has the error “Value Primary not in
approved domain for field LOCTYPE”, any occurrences of “Primary” in
LOCTYPE will be edited to “PRIMARY”.

*Fix Duplicate ESBIDs*: For counties with three ESB layers, all ESBIDs
must be unique when comparing all three layers against one another. This
tool creates unique ESBIDs by appending “E”, “F”, or “L” to the end of
ESBIDs. Thus, if “1” is the ESBID in EMS, Fire, and Law, after running
the tool, features will have unique ESBIDs like “1E”, “1F”, & “1L”.

The adjustment tools require these Python scripts:

-   Adjustment\_CreateGeocodeExceptions.py

-   Adjustment\_FixDomainCase.py

-   Adjustment\_FixDuplicateESBIDs.py

-   NG911\_DataCheck.py

-   NG911\_DataFixes.py

Running Create Geocode Exceptions:

1.  First, either run “Validation Tools” &gt; “2 Check Address Points”
    and make sure to check “Geocode Address Points” or “Validation
    Tools” &gt; “9 Optional Check All Required”. Running these will
    record any geocoding errors in FieldValuesCheckResults.

2.  Verify that ALL geocoding errors recorded in FieldValuesCheckResults
    are indeed exceptions.

3.  Open “Adjustment Tools” &gt; “Create Geocode Exceptions” and fill in
    the parameter for the NG911 Geodatabase.

4.  Run the tool.

5.  The tool will create a table called “GeocodeException” with one
    field called ADDID. This tool copies over all ADDIDs flagged as
    geocoding errors from FieldValuesCheckResults as
    geocoding exceptions.

6.  If any of the ADDIDs copied over are genuine errors and are not
    exceptions, you can manually delete the ADDID in an edit session
    in ArcMap.

Running Fix Domain Case:

1.  First, run “Validation Tools” &gt; “9 Optional Check All Required”
    to make sure all domains of all feature classes are examined and all
    issues are recorded in FieldValuesCheckResults.

2.  Open “Adjustment Tools” &gt; “Fix Domain Case” and identify the
    parameters for the NG911 geodatabase and the folder containing
    domains files.

3.  Run the tool.

4.  Run “Validation Tools” &gt; “9 Optional Check All Required” again.
    See the difference of results in FieldValuesCheckResults.

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
