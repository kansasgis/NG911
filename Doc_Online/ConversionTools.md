**Conversion Tools**

Description: The conversion tools convert data from one format to
another or upgrade data template versions.

[*Add/Update Parcel Layer*](#parcels): converts a county's parcel layer to NG911
template standards and loads data into the geodatabase

[*GDB to Shapefiles*](#gdb2shp): converts all feature classes in the NG911 dataset
of a NG911 geodatabase into shapefiles and converts the road alias table
to a DBF.

[*Upgrade to GDB1.1 Template*](#upgrade11): upgrades existing v1.0 NG911 GIS Data
Model geodatabase to the NG911 GIS Data Model v1.1 template geodatabase.

[*Zip NG911 Geodatabase*](#zip): zips an NG911 geodatabase to prepare it for
submission to DASC

<a name="parcels"></a>
Running *Add/Update Parcel Layer*:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    tools”, expand the toolbox, then expand the toolset called
    “Conversion Tools.”

2.  Double click the script titled “Add/Update Parcel Layer.”

3.	In the “Existing Parcel Layer” parameter, add in the full path to the existing 
parcel feature class.

4.	In the “PID Field” parameter, select the field in the parcel layer that contains 
the parcel ID number. It can be the 16 or 19 digit version and contain dots and 
dashes or be straight digits. 

5.	In the “County” parameter, enter the appropriate county name.

6.	In the “Target NG911 Geodatabase”, select the full path of the geodatabase where 
you’d like to import the parcels.

7.	Run the tool.


<a name="upgrade11"></a>
Running *Convert 1.1 to 2.0*:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    tools”, expand the toolbox, then expand the toolset called
    “Conversion Tools.”

2.  Double click the script titled “Convert 1.1 to 2.0.”

3.  In the “1.1 Geodatabase” parameter, select your
    current geodatabase.

4.  In the “2.0 Geodatabase Template” parameter, select the 2.0 template
    geodatabase you have already downloaded. Be sure to check the
    projection of the geodatabase. This script will import the data
    directly into this geodatabase, so be prepared and make a copy if
    you like.

5.  Run the tool.

<a name="gdb2shp"></a>
Running *GDB to Shapefile*:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    Tools”, expand the toolbox, then expand the toolset called
    “Conversion Tools.”

2.  Double click the script titled “GDB to Shapefiles.”

3.  In the “Geodatabase” parameter, select the geodatabase of data to
    be exported.

4.  In the “Output Folder” parameter, select the folder where you would
    like the shapefiles to be saved.

5.  Run the tool.

<a name="zip"></a>
Running *Zip NG911 Geodatabase*:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    tools”, expand the toolbox, then expand the toolset called
    “Conversion Tools.”

2.  Double click the script titled “Zip NG911 Geodatabase.”

3.  In the “Geodatabase” parameter, select the geodatabase to be
    zipped up.

4.  In the “Zip File Output” parameter, put in the filename including
    the zip extension of your output zip file. If the zip file already
    exists, the file will be overwritten.

5.  Run the tool.


The conversion tools require:

-	Conversion\_AddParcels.py

-   Conversion\_GDB11to20.py

-   Conversion\_GDBtoShapefile.py

-   Conversion\_ZipNG911Geodatabase.py

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
