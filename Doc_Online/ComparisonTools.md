**Comparison Tools**

Description: The comparison tools evaluate attribute and spatial changes
between two different data resources. These tools are intended to be run
against same-PSAP data as it changes through time to flag edited,
updated and deleted records.

[*Compare NG911 Data*](#data): compares two NG911 feature classes of similar
kinds (ex. Address points edited recently against address points from
three months ago). This check will flag all attribute edits, spatial
edits, new records and deleted records between the two feature classes
compared.

[*Compare NG911 Geodatabases*](#geodatabases): compares two NG911 geodatabases (ex.
Geodatabase edited recently against geodatabase from a year ago). This
check will flag all attribute edits, spatial edits, new records and
deleted records between all common layers and tables in the two
geodatabases.

The comparison tools require:

-   One Python script called Comparison\_CompareDataLayers.py

<a name="data"></a>
Running *Compare NG911 Data*:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    tools”, expand the toolbox, then expand the toolset called
    “Comparison Tools.”

2.  Double click the script titled “Compare NG911 Data.”

3.  In the parameter for “One NG911 Feature Class”, enter in the full
    path to an NG911 feature class you wish to compare with another.

4.  In the parameter for “The other NG911 Feature Class,” enter in the
    full path to an NG911 feature class of a similar kind. For example,
    you will want to compare a road centerline feature class with
    another road centerline feature class. You will not be able to
    compare a road centerline feature class with any other kind.

5.  In the parameter for “Table for comparison results,” enter the full
    path to where the results table should be saved. This can reside
    inside an NG911 geodatabase or not, it does not matter.

6.  Click OK and wait for the tool to process.

7.  The results table will show descriptions of edits as well as the
    unique ID of the features edited. The unique ID shown is NOT the
    object ID, but instead of the unique ID outlined in the Kansas NG911
    Data Model.

<a name="geodatabases"></a>
Running Compare NG911 Geodatabases:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    tools”, expand the toolbox, then expand the toolset called
    “Comparison Tools.”

2.  Double click the script titled “Compare NG911 Geodatabases.”

3.  In the parameter for “One NG911 Geodatabase”, enter in the full path
    to an NG911 geodatabase you wish to compare with another.

4.  In the parameter for “The other NG911 Geodatabase,” enter in the
    full path to an NG911 geodatabase completed by the same PSAP.

5.  In the parameter for “Table for comparison results,” enter the full
    path to where the results table should be saved. This can reside
    inside an NG911 geodatabase or not, it does not matter.

6.  Click OK and wait for the tool to process.

7.  The results table will show descriptions of edits as well as the
    unique ID of the features edited. The unique ID shown is NOT the
    object ID, but instead of the unique ID outlined in the Kansas NG911
    Data Model.

Support Contact:

For issues or questions, please contact Kristen Jordan Koenig with the
Kansas Data Access and Support Center. Email Kristen at
Kristen@kgs.ku.edu and please include in the email which script you were
running, any error messages, and a zipped copy of your geodatabase
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
