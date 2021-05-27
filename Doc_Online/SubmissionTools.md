**Submission Tools**

Description: The data submission tools perform a variety of basic
verification checks against the NG911 Data Model template to determine
if the data is ready for submission. The scripts will run all required
validation checks (1-5) and zip the data if it passes validation.

Running submission scripts.

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    Tools”, expand the toolbox, then expand the toolset called
    “Submission Tools.”

2.  In the “NG911 Geodatabase” parameter, select the geodatabase of data
    to be checked.


3.  In the “Output Zip File” parameter, enter the path name including
    “.zip” of where the data should be saved.

4.  Run the tool.

5.  The basic results of the data checks are shared in the ArcGIS
    dialog box. The detailed results of the data checks will appear in
    two tables that are added to your geodatabase: TemplateCheckResults
    & FieldValuesCheckResults. The results reported in these tables will
    accumulate until you run the script titled “6 Optional Clear
    Results Table”.

6. If the data did not pass the validation check, the data will not
    be zipped.

Support Contact:

For issues or questions, please contact Kristen Jordan Koenig with the
Kansas Data Access and Support Center. Email Kristen at
<Kristen.kgs@ku.edu> and please include in the email which script you
were running, any error messages, and a zipped copy of your geodatabase.

If you have a domain issue to report, please email Kristen Jordan-Koenig
at <kriste.kgs@ku.edu>. Please indicate what type of domain the issue
is with and the values needing corrections. If you're feeling fancy, you
can also fork the GitHub repository at
<https://github.com/kansasgis/NG911>. Make your changes and submit a
pull request.

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
