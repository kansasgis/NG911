**Enhancement Tools**

Description: These tools automate various tasks involved with data
creation and perform various checks to enhance the quality of the data.

[*Add KSPID*](#KSPID): If your PSAP/county has GIS parcels, this tool will
automatically determine, calculate and import the KSPID into the address
points. The tool can use 16 or 19 digit PIDs, and the 19 digit version
will be added to the address points.

[*Assign Unique Identifier*](#UniqueID): creates a unique ID for all null features in
a feature class.

[*Calculate Label*](#CalcLabel): calculates the label field of either an address point
file or the road centerline file. For address points, the fields used
for the calculation are: HNO, HNS, PRD, STP, RD, STS, POD, POM, BLD,
FLR, UNIT, ROOM and SEAT. For road centerlines, the fields used for the
calculation are: PRD, STP, RD, STS, POD and POM.

[*Check Road Elevation Direction*](#elevDir): makes sure the ELEV\_F and ELEV\_T
attributes correctly depict the elevation rise and fall of road
segments.

[*Check TN List*](#TNlist): geocodes a list of telephone number addresses against
the MSAG information in the NG911 Address Points and Road Centerlines.
This tool requires a TN (telephone number) list. Directions for
obtaining the TN list are found in the
Downloading\_TN\_records\_from\_911Net document.

[*Create Road Alias Records*](#createRoadAlias): creates new road alias records based on
road segments matching a user-provided road name.

[*Find Address Range Overlaps*](#overlaps): finds areas where address ranges
overlaps. Overlapping address ranges can negatively affect geocoding
accuracy.

[*Geocode Address Points*](#geocode): geocodes the address points against the road
centerline data. This test respects exceptions created in the
GeocodeExceptions table.

[*US National Grid Calculator*](#USNG): generates US National Grid coordinates.
If the Lat and Long fields are filled out, the USNG coordinates will be
based on those fields. If the fields are not populated, the tool will
calculate Lat/Long values, populated the Lat/Long fields and calculated
USNG coordinates.

[*Verify Road Alias*](#roadalias): checks the road alias name against an approved
highway name list.

<a name="KSPID"></a>
Running *Add KSPID*:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    Tools”, expand the toolbox, then expand the toolset called
    “Enhancement Tools.”

2.  Double click on the desired tool to open.

3.  In the “County” parameter, enter the name of the county where the
    PSAP is.

4.  In the “Address Point Layer” parameter, enter the full path to the
    NG911 Address Point layer that needs KSPIDs added.

5.  In the “Parcel Layer” parameter, enter the full path to the GIS
    parcel layer for the county.

6.  In the “Parcel ID Column” parameter, enter the field name where the
    county parcel ID is stored. This can be either the 16 or 19 digit
    version of the parcel number. The 19 digit version will be stored in
    the address point file.

7.  Run the tool.

8.  Please note that this tool runs a spatial join between the address
    points and parcels, so address points that do not sit inside a
    parcel will not be updated with a KSPID.

<a name="UniqueID"></a>
Running *Assign Unique Identifier* and *Assign Unique Identifier Road
Alias Table*:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    Tools”, expand the toolbox, then expand the toolset called
    “Enhancement Tools.”

2.  Double click on the desired tool to open.

3.  In the “Feature Class” or “Alias Table” input box, select the layer
    or table to have its unique ID’s updated.

4.  In the “Unique ID Field” parameter, select the field that contains
    unique ID’s.

5.  Run the tool.

<a name="CalcLabel"></a>
Running *Calculate Label*:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    Tools”, expand the toolbox, then expand the toolset called
    “Enhancement Tools.”

2.  Double click on the desired tool to open.

3.  In the “Feature Class to Receive Label” input box, select the layer
    (Address Points or Road Centerline, any other layer will
    not process) that you want to create labels for.

4.  If you only want to update labels where records are blank, check
    the box.

5.  Run the tool.

<a name="elevDir"></a>
Running *Check Road Elevation Direction*:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    Tools”, expand the toolbox, then expand the toolset called
    “Enhancement Tools.”

2.  Double click on the desired tool to open.

3.  In the “NG911 Geodatabase” input box, put in the full path of the
    NG911 geodatabase.

4.  Run the tool.

5.  Results will be reported in the “FieldValuesCheckResults” table.

<a name="TNlist"></a>
Running *Check TN List*:

This tool requires a telephone number list to be extracted as a
spreadsheet. Directions for obtaining the TN list are found in the
Downloading\_TN\_records\_from\_911Net document.

Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
Tools”, expand the toolbox, then expand the toolset called “Enhancement
Tools.”

1.  Double click on “Check TN List” to open.

2.  In the “TN Spreadsheet” input box, select the TN Spreadsheet
    provided by the telephone company.

3.  In the “NG911 Geodatabase” box, select the appropriate
    NG911 geodatabase.

4.  Run the tool.

<a name="createRoadAlias"></a>
Running *Create Road Alias Records*:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    Tools”, expand the toolbox, then expand the toolset called
    “Enhancement Tools.”

2.  Double click on “Create Road Alias Records” to open.

3.  In the “NG911 Geodatabase” box, select the appropriate
    NG911 geodatabase.

4.  In the “Road Name” box, enter the value of the RD column (the
    road name) for the road centerline segment you wish to add
    records for. Example: the road segments you need alias records for
    have a road centerline RD field value of IOWA. Enter IOWA here.

5.  In the “Road Type” box, enter the road type. This will narrow down
    road segments that receive road alias records. Example: if 6TH ST
    and 6TH AVE both exist and you only want 6TH AVE to receive alias
    records, choose AVE here.

6.  In the “Alias Road Name” box, enter the alias name you want created.
    Example: if IOWA segments need the alias name of US59, enter
    US59 here.

7.  In the “Alias Road Type (optional)” box, enter the street suffix for
    the new alias road name. Pick from the list. If your option is not
    available, enter nothing and edit the records after the tool runs.

8.  In the “Alias Road Label (optional)” box, enter the optional label
    for the new alias road records. Example: if you want the alias name
    of US59 to show up at US-59 on the label field, enter US-59 here.

9.  Run the tool.

10. Double-check the newly created records in ArcMap. This tool will
    create a road alias record for every road segment that matches the
    value of “Road Name”, so records may be created outside your
    intended range or for incorrect road types.

<a name="overlaps"></a>
Running *Find Address Range Overlaps*:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    Tools”, expand the toolbox, then expand the toolset called
    “Enhancement Tools.”

2.  Double click on “Find Address Range Overlaps” to open.

3.  In the “NG911 Geodatabase” box, select the appropriate
    NG911 geodatabase.

4.  Run the tool.

5.  If overlapping address ranges exist, they will be exported to a
    feature class in the NG911 geodatabase
    called “AddressRange\_Overlap”.

<a name="geocode"></a>
Running *Geocode Address Points*:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    Tools”, expand the toolbox, then expand the tool set called
    “Enhancement Tools.”

2.  Double click on “Geocode Address Points” to open.

3.  In the “NG911 Geodatabase” box, select the appropriate
    NG911 geodatabase.

4.  Run the tool.

5.  If geocoding errors exist, they will be recorded
    in FielValuesCheckResults.

6.  Geocoding exceptions can be added using the “Create Geocoding
    Exceptions” tool in the Adjustment Tools toolset.

<a name="USNG"></a>
Running *US National Grid Calculator*:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    Tools”, expand the toolbox, then expand the toolset called
    “Enhancement Tools.”

2.  Double click on “US National Grid Calculator” to open.

3.  In the “Address Points Layer” input box, select the address point
    layer that needs US National Grid Coordinates updated.

4.  Check the box next to “Update only blank USNG (optional)” if you
    want to only update records with blank values in the USNG column.

5.  Run the tool.

<a name="roadalias"></a>
Running *Verify Road Alias*:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    Tools”, expand the toolbox, then expand the toolset called
    “Enhancement Tools.”

2.  Double click on “Verify Road Alias” to open.

3.  In the “NG911 Geodatabase” box, select the appropriate
    NG911 geodatabase.

4.  In the “Domains Folder” box, select the appropriate NG911
    domain folder.

5.  Run the tool.

6.  Results will be in the “FieldValuesCheckResults” table.


The enhancement tools require:

-   Python scripts:

    -   Enhancement\_AddKSPID.py

    -   Enhancement\_AssignID.py

    -   Enhancement\_CalculateLabel.py

    -   Enhancement\_CheckRoadElevationDirection.py

    -   Enhancement\_CheckTN.py

    -   Enhancement\_CreateRoadAliasRecords.py

    -   Enhancement\_FindAddressRangeOverlaps.py

    -   Enhancement\_GeocodeAddressPoints.py

    -   Enhancement\_XYUSNGCal.py

    -   Enhancement\_VerifyRoadAlias.py

    -   CoordConvertor.py

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
