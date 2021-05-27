**Validation Tools**

Description: The data validation tools perform a variety of basic
verification checks against the NG911 Data Model template to determine
if the data is ready for submission. The scripts are organized to
validate data by specific layers or groups of layers, and multiple,
optional tests are included for each set. Any issues found with the data
will be reported in tables added to the geodatabase. The scripts can be
run multiple times as necessary so users can correct basic issues prior
to submitting their NG911 updates. Currently, these data validation
tools do not provide complete quality assurance (QA) of the data. The
included data validation tools check for the following errors:

-   Checks if required layers exist

-   Checks if required fields are present

-   Checks if required fields have values for all records

-   Checks if MSAGCO fields have leading or trailing spaces

-   Checks number of records for submission

-   Checks for invalid geometry

-   Checks field values against template domains where appropriate

-   Checks if all features are inside authoritative boundary

-   Checks if road features have any geometry cutbacks

-   Checks road address range directionality

-   Checks road alias and centerline correspondence

-   Checks road alias highway names

-   Checks if road segments have duplicate address ranges on dual carriageways

-   Checks if road segments are addressed outside of the PSAP (typically across a county boundary)

-   Checks for address range overlaps in road centerline

-   Checks road centerline parity against the address range

-   Finds duplicate features in road centerlines and addresses

-   Finds duplicate unique IDs

-   Makes sure address point ESN & MUNI are correctly attributed

-   Verifies topology exceptions (optional)

Running *Validation scripts*:

1.  Navigate to the toolset called “Validation Tools.” Use the tools 
    in the numerical order presented with the following guidelines.

2.  In the “Geodatabase” parameter, select the geodatabase of data to
    be checked.

3.  Check which data checks you want to run. When running each tool for
    the first time, we recommend choosing all options.

4.  Run the tool.

5.  Alternatively, to run all checks, open and run “9 Optional Check
    All Required”.

6.  The basic results of the data checks are shared in the ArcGIS
    dialog box. The detailed results of the data checks will appear in
    two tables that are added to your geodatabase: TemplateCheckResults
    & FieldValuesCheckResults. The results reported in these tables will
    accumulate until you run the script titled “6 Optional Clear
    Results Table”.

7.  Based on the results of the data check, you can edit your data
    as necessary. Documentation for [Interpreting Tool Results](https://github.com/kansasgis/NG911/blob/master/Doc_Online/Interpreting_Tool_Results.md).

8. After data is edited, the necessary data checks can be rerun.

9. The script called “7 Optional Update Domains” will sync your domains
    with the master copy on GitHub. This tool requires internet access
    to <https://raw.githubusercontent.com/kansasgis>

10. The script called “8 Optional Verify Topology Exceptions” will
    double check that all road centerline topology error are recorded as
    exceptions in the data and the topology.
	
The validation tools require:

-	The complete NG911 toolbox setup and all scripts it includes.

Support Contact:

For issues or questions, please contact Kristen Jordan Koenig with the
Kansas Data Access and Support Center. Email Kristen at
<Kristen.kgs@ku.edu> and please include in the email which script you
were running, any error messages, and a zipped copy of your geodatabase.

If you have a domain issue to report, please email Kristen Jordan-Koenig
at <kristen.kgs@ku.edu>. Please indicate what type of domain the issue
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
