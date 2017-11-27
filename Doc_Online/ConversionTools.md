**Conversion Tools**

Description: The conversion tools convert data from one format to
another or upgrade data template versions.

[*1. Convert 2.0 to 2.1*](#conversion): the first step in upgrading 
an existing v2.0 NG911 GIS Data Model geodatabase to the NG911 GIS 
Data Model v2.1 template geodatabase. This step completes the 
initial data migration between the two geodatabases.

[*2. Populate Road AUTH_X*](#conversion): the second step in the 
2.0 > 2.1 conversion process auto-populates any “Y” values in the 
AUTH_L and AUTH_R fields in the road centerline file.

[*3. Populate Road GEOMSAGX*](#conversion): the third step in the 
2.0 > 2.1 conversion process auto-populates both the “Y” and “N” 
values in the GEOMSAGL and GEOMSAGR fields in the road centerline file.

[*4. Populate Address RCLMATCH*](#conversion): the fourth step in the 
2.0 > 2.1 conversion process populates both the RCLMATCH and RCLSIDE 
fields in the address point file.

[*5. Populate RCLMATCH NO_MATCH*](#conversion): the fifth step in the 
2.0 > 2.1 conversion process populates any blank or null RCLMATCH 
features with “NO_MATCH”.

[*6. Populate Address GEOMSAG*](#conversion): the final step in the 
2.0 > 2.1 conversion process populates the GEOMSAG field of the address point file.

[*Add/Update Parcel Layer*](#parcels): converts a county's parcel layer to NG911
template standards and loads data into the geodatabase

[*GDB to Shapefiles*](#gdb2shp): converts all feature classes in the NG911 dataset
of a NG911 geodatabase into shapefiles and converts the road alias table
to a DBF.

[*Zip NG911 Geodatabase*](#zip): zips an NG911 geodatabase to prepare it for
submission to DASC

< a name="conversion"></a>
Running 2.0 to 2.1 Conversion Tools:

For full documentation, please see the official conversion documentation called 
"ConvertingGDB_2.0_to_2.1".

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

-	The complete NG911 toolbox setup and all scripts it includes.

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
