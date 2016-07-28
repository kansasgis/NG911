Interpreting Tool Results
=========================

Results Location
----------------

After the Validation Tools run, if the tool found issues in the data,
one or two tables will be added to the geodatabase. The table called
TemplateCheckResults displays issues regarding the geodatabase in
general or schema issues. The table called FieldValuesCheckResults
displays issues with individual data pieces such as field values or
geometry.

If “9 Optional Check All Required” runs and finds no issues, a table
called DASC\_Communication will appear with the date recorded in the
attribute table.

#### Note: What the Tools Ignore

Generally speaking, all validation tools ignore records that are marked
“Not For Submission.” The tools also usually ignore Address Points that
are not marked as PRIMARY, Road Centerline segments marked as Exceptions
and Road Centerline segments that have no address ranges.

Results Information
-------------------

TemplateCheckResults has three fields that share information about
issues. Not all fields will be filled out for all issues.

-   **DateFlagged**: the date the issue was identified using the NG911
    toolbox

-   **Description**: a description of the issue

-   **Category**: general category of the issue

FieldValuesCheckResults has five fields to share information about
issues. Not all fields will be filled out for all issues.

-   **DateFlagged**: the date the issue was identified using the NG911
    toolbox

-   **Description**: a description of the issue prefixed by “Error” or
    “Notice”

-   **Layer**: the specific layer in the geodatabase where the issue was
    found

-   **Field**: if the issue was found with a specific field, this
    identifies which field

-   **FeatureID**: the unique feature ID of the issue. The matching
    unique ID field depends on the layer name.

    -   AddressPoints: ADDID

    -   AuthoritativeBoundary: ABID

    -   CountyBoundary: COUNTYID

    -   ESB (includes EMS, FIRE, LAW, PSAP): ESBID

    -   ESZ: ESZID

    -   MunicipalBoundary: MUNI\_ID

    -   RoadAlias: ALIASID

    -   RoadCenterline: SEGID

A quick way to visualize issues inside ArcMap is to create a join
between a feature class’s unique ID field and FeatureID in
FieldValuesCheckResults. From the attribute table in ArcMap, both the
feature information and the error message are visible for quick
adjustments and edits.

“Errors” Versus “Notices”
-------------------------

In FieldValuesCheckResults and TemplateCheckResults, issues prefixed
with “Error” will prevent data from being accepted and processed into
Vesta Locate. Issues prefixed with “Notice” should be addressed by the
PSAP if necessary, but these issues will not prevent the data from being
accepted and processed into Vesta Locate.

Below, errors and notices are listed separately. General messages are
reported first followed by specific messages targeting Address Points,
Road Alias and Road Centerline issues.

Under “Error Message” and “Notice Message”, any words in all caps
represent variables in the messages such as layer names, field names,
values and feature IDs.

Errors
------
<a name="TemplateCheckResults></a>
#### TemplateCheckResults

|Error Message|Meaning|Fix Tips|
|--------------------|-----------------------------------------------------------------|--------------------|
|*LAYERNAME does not have required field FIELDNAME*|Found by: 1 Check Template &gt; Check Required Fields<br><br>The tool did not find a required field for a specific layer.|In the layer specified, make sure a field exists with the specified name. Make sure the field name itself and not just the field alias is uppercase and matches the required field name exactly.|
|*LAYERNAME has 0 records for submission*|Found by: 1 Check Template &gt; Check Submission Counts<br><br>A layer has no records marked for submission. In this check, the tool queries the SUBMIT field for all records that do not equal ‘N’. All records that are blank, null, spaces or ‘Y’ are counted as being for submission.|Make sure the layer specified has features, and then make sure that all the records are not marked as ‘N’.|
|*No feature dataset name ‘NG911’ exists*|Found by: 1 Check Template &gt; Check Layer List<br><br>The NG911 Data Model requires a feature dataset named ‘NG911’ to exist.|Make sure a feature dataset exists that is named ‘NG911’.|
|*Required layer LAYERNAME is not in geodatabase*|Found by: 1 Check Template &gt; Check Layer List<br><br>A required layer is not in the geodatabase. Required layers & tables are AddressPoints, AuthoritativeBoundary, ESB layers, ESZ, RoadAlias,  and RoadCenterline|Make sure the geodatabase includes all required layers and tables. All layers must be inside the feature dataset named ‘NG911’. The Road Alias table sits outside the feature dataset.|

<a name="FVCR"></a>
#### FieldValuesCheckResults

###### General
|Error Message|Meaning|Fix Tips|
|--------------------|-----------------------------------------------------------------|--------------------|
|*FEATUREID has duplicate field information*|Found by: 2 Check Address Points &gt; Check Address Point Frequency and 3 Check Roads &gt; Check Road Frequency<br><br>This check only runs on address points and road centerlines. For address points, only PRIMARY addresses are checked where the HNO is not 0; for road centerlines, only roads with at least one valid address range is checked (L or R).<br><br>For Address Points, the following fields are checked for duplication:<br>MUNI;HNO;HNS;PRD;STP;RD;STS;POD;POM;<br>ZIP;BLD;FLR;UNIT;ROOM;SEAT;LOC;LOCTYPE;MSAGCO<br><br>For Road Centerlines, the following fields are checked for duplication: <br>STATE\_L;STATE\_R;COUNTY\_L;COUNTY\_R;MUNI\_L; MUNI\_R;L\_F\_ADD;<br>L\_T\_ADD;R\_F\_ADD;R\_T\_ADD; PARITY\_L;PARITY\_R;POSTCO\_L;POSTCO\_R;<br>ZIP\_L; ZIP\_R;ESN\_L;ESN\_R;MSAGCO\_L;MSAGCO\_R;PRD; STP;RD;STS;POD;POM;SPDLIMIT;ONEWAY;RDCLASS;LABEL;<br>ELEV\_F;ELEV\_T;ESN\_C;SURFACE;STATUS; TRAVEL; LRSKEY|Take a look at the ADDIDs or SEGIDs with duplicate information and either make necessary edits to differentiate records or delete duplicate records.|              
|*FEATUREID is a duplicate ID*|Found by: 2 Check Address Points/3 Check Roads/ 4 Check Emergency Services Boundaries/5 Check Administrative Boundaries &gt; Check Unique IDs<br><br>A unique ID value is duplicated inside a feature class. See above under “Results Information” for unique ID field names for each layer type.|Make sure every unique ID is actually unique inside each feature class. For separate ESBs (EMS, FIRE & LAW), the IDs must be unique across all layers. If ESB IDs are duplicated, run Adjustment Tools &gt; Fix Duplicate ESB IDs for a quick fix.|
|*Feature not inside authoritative boundary*|Found by: 3 Check Roads/ 4 Check Emergency Services Boundaries/5 Check Administrative Boundaries &gt; Check Feature Locations<br><br>Some part of this feature’s geometry falls outside of the authoritative boundary. This is only an error for features NOT in AddressPoints.|Take a look at the identified features in comparison to the Authoritative Boundary. Either the features need to be moved inside the Authoritative Boundary or the Authoritative Boundary should be expanded to include the features.|
|*FIELDNAME is null for FeatureID FEATUREID*|Found by: 1 Check Template &gt; Check Required Field Values<br><br>A required field contains a null value. To narrow down the issue, look at the Layer, Field and FeatureID columns of FieldValuesCheckResults for the exact location of the null value.|Look at the specified field value for the identified feature and edit the value. If the field has a domain, make sure the new value is approved for the domain.|
|*Invalid geometry*|Found by: 1 Check Template &gt; Find Invalid Geometry<br><br>This check makes sure all features have an appropriate number of coordinate pairs stored for their feature class’s geometry. The check makes sure a record did not get added to the attribute table without corresponding geometry. Points must have at least 1 coordinate pair, lines must have at least 2 coordinate pairs and polygons must have at least 3 coordinate pairs.|Try running a “zoom to” on the identified feature. If necessary, use the “Replace Geometry” tool to create a valid feature or delete the record from the attribute table.|
|*Value ATTRIBUTEVALUE not in approved domain for field FIELDNAME*|Found by: 2 Check Address Points/3 Check Roads/ 4 Check Emergency Services Boundaries/5 Check Administrative Boundaries &gt; Check Values Against Domains<br><br>A field with a domain contains a value that is not in the approved domain. In many cases, this situation is caused by field case (mixed case versus upper case).|Look at the specified field value for the identified feature and edit the value to one approved for the domain.<br><br>If the issue is a case issue, run Adjustment Tools &gt; Fix Domain Case for a quick and easy fix.|

###### Address Points
|Error Message|Meaning|Fix Tips|
|--------------------|-----------------------------------------------------------------|--------------------|
|*FEATUREID did not geocode against centerline*|Found by: 2 Check Address Points &gt; Geocode Address Points<br><br>An address point was flagged as “Unmatched” during the geocoding process. If any geocoding issues are found, the tool leaves GeocodeTable (the input addresses) and gc\_test (the geocoding results) in the geodatabase instead of removing them for cleanup. To examine exactly what was geocoded, look at the SingleLineInput field of the GeocodeTable. The information for SingleLineInput is derived from the AddressPoints layer by concatenating the LABEL and ZIP fields. In gc\_test, the results of the geocoding process are coded in the Status field (M = Match, T = Tie, U = Unmatched).|Fixes for geocoding issues might either be in the AddressPoints layer or the RoadCenterline layer. Examine the LABEL and ZIP fields of the AddressPoints layer in comparison to the appropriate data in the Road Centerline layer to see if things match up correctly.<br><br>If you need to create geocoding exceptions, run Adjustment Tools &gt; Create Geocode Exceptions. Tool tip: leave only the geocoding issues you want to turn into geocoding exceptions in FieldValuesCheckResults prior to running the Geocode Exception tool.|
|*Error: FEATUREID geocoded against more than one centerline segment. Possible address range overlap*|Found by: 2 Check Address Points &gt; Geocode Address Points<br><br>A primary address point was flagged as a “Tie” during the geocoding process. In most cases, the road centerline file contains overlapping address ranges. Secondary address points that “Tie” are not counted as errors and will show up as notices.|Follow the “Fix Tips” for unmatched geocoding, but see if any address ranges overlap.|

###### Road Alias
|Error Message|Meaning|Fix Tips|
|--------------------|-----------------------------------------------------------------|--------------------|
|*Issue with road alias record.*|   Found by: 3 Check Roads &gt; Check Road Alias<br><br>The validation script encountered a problem reading information from the road alias table. Most likely the ALIASID or A\_RD field is null.|Take a look at the road alias table to make sure key values are not null.|

Notices:
--------

###### Address Points
|Notice Message|Meaning|Fix Tips (if applicable)|
|--------------------|-----------------------------------------------------------------|--------------------|
|*Address point MUNI/ESN does not match MUNI/ESN in MunicipalBoundary/ESZ layer*|Found by: 2 Check Address Points &gt; Check ESN MUNI Attributes<br><br>An address point ESN or MUNI attribute does not match the MUNI or ESN information gathered from the address point’s exact geographic location.|Take a look at the identified address points in comparison to the ESZ and/or Municipal Boundary layers. Make sure for the address point’s location that the ESN attribute matches the “ESN” attribute of the intersecting ESZ boundary. Also make sure the address point’s MUNI attribute matches the MUNI attribute of the intersecting Municipal Boundary. If the address point sits outside a municipal boundary, set MUNI to UNINCORPORATED.|
|*Notice: FEATUREID geocoded against more than one centerline segment. Possible address range overlap*|Found by: 2 Check Address Points &gt; Geocode Address Points<br><br>A secondary address point was flagged as a “Tie” during the geocoding process. In most cases, the road centerline file contains overlapping address ranges.|Follow the “Fix Tips” for unmatched geocoding, but see if any address ranges overlap.|
|*Notice: Feature not inside authoritative boundary*|Found by: 2 Check Address Points &gt; Check Feature Locations<br><br>An address point falls outside of the authoritative boundary.<br><br>This notification will not prohibit data from being accepted and processed, so if an address point is truly outside the authoritative boundary, please do not edit the data.|Examine the location of the identified address point in comparison to the authoritative boundary. If necessary, move the address point inside the authoritative boundary or move the authoritative boundary to include the address point.|

###### Road Alias
|Notice Message|Meaning|Fix Tips (if applicable)|
|--------------------|-----------------------------------------------------------------|--------------------|
|*ROADNAME is not in the approved highway name list*|Found by: 3 Check Roads &gt; Check Road Alias<br><br>A highway value in A\_RD in the road alias table is not an approved highway name.|All approved highway names can be found in the KS\_HWY.txt file in the Domains folder. Compare the value of A\_RD for the identified feature with the approved highway name in the text file, and edit the value to match.|
|*Road alias entry does not have a corresponding road centerline segment*|Found by: 3 Check Roads &gt; Check Road Alias<br><br>A record in the road alias table does not have a matching record in the road centerline table.|Make sure the SEGID value in the road alias table matches the SEGID of the appropriate road centerline segment. If an appropriate road centerline segment does not exist, remove the road alias record.|

###### Road Centerlines
|Notice Message|Meaning|Fix Tips (if applicable)|
|--------------------|-----------------------------------------------------------------|--------------------|
|*Road centerline highway segment does not have a corresponding road alias record*|Found by: 3 Check Roads &gt; Check Road Alias<br><br>A road centerline segment with HIGHWAY, HWY or INTERSTATE in the road name does not have a match in the road alias table. The road segment’s SEGID value is matched to the road alias SEGID field.|Highway records should have a corresponding record in the road alias table. If a record doesn’t exist in the road alias table, create one and add all necessary information according to the [NG911 Data Model](http://www.kansasgis.org/initiatives/NG911/KSNG911GISDataModel/v1.1/Kansas_NG911_GIS_Data_Model_v1_1.pdf). If a road alias record exists, make sure the SEGID value matches the SEGID of the correct road centerline segment.|
|*Segment’s address range is from high to low instead of low to high*|Found by: 3 Check Roads &gt; Check Directionality<br><br>For the records indicated, either L\_T\_ADD is smaller than L\_F\_ADD or R\_T\_ADD is smaller than R\_F\_ADD. When a “to” portion of an address range is smaller than the “from” portion, geocoders have a harder time placing addresses correctly.|Look at the road segments identified to see if the road direction can be switched without negatively impacting the data.|
|*This segment might contain a geometry cutback*|Found by: 3 Check Roads &gt; Check for cutbacks<br><br>A segment’s geometry follows an unpredictable pattern like a Z inside the feature or a tail on one end. In some cases of tight angles, a cutback is flagged by the geometry check but the geometry is actually ok.|Inside an edit session, take a look at the individual vertices of the indicated road segments. If Z’s or tails exist, remove them.|

### Support Contact:

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
