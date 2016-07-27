**Conversion Tools**

Description: The conversion tools convert data from one format to
another or upgrade data template versions.

*GDB to Shapefiles*: converts all feature classes in the NG911 dataset
of a NG911 geodatabase into shapefiles and converts the road alias table
to a DBF.

*Upgrade to GDB1.1 Template:* upgrades existing v1.0 NG911 GIS Data
Model geodatabase to the NG911 GIS Data Model v1.1 template geodatabase.

*Zip NG911 Geodatabase*: zips an NG911 geodatabase to prepare it for
submission to DASC

The conversion tools require:

-   One Python script called Conversion\_GDBtoShapefile.py

-   One Python script called Conversion\_GDB10to11.py

-   One Python script called Conversion\_ZipNG911Geodatabase.py

Running GDB to Shapefile:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    Tools”, expand the toolbox, then expand the toolset called
    “Conversion Tools.”

2.  Double click the script titled “GDB to Shapefiles.”

3.  In the “Geodatabase” parameter, select the geodatabase of data to
    be exported.

4.  In the “Output Folder” parameter, select the folder where you would
    like the shapefiles to be saved.

5.  Run the tool.

Running GDB 1.0 to 1.1:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    tools”, expand the toolbox, then expand the toolset called
    “Conversion Tools.”

2.  Double click the script titled “Upgrade to GDB 1.1 Template.”

3.  In the “Existing Geodatabase” parameter, select your
    current geodatabase.

4.  In the “1.1 Template Geodatabase” parameter, select the 1.1 template
    geodatabase you have already downloaded. Be sure to check the
    projection of the geodatabase. This script will import the data
    directly into this geodatabase, so be prepared and make a copy if
    you like.

5.  Run the tool.

Running Zip NG911 Geodatabase:

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
