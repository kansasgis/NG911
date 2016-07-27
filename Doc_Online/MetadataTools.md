**Enhance Metadata** (v1.0 ONLY)

Description: This tool fills in required metadata components regarding
layer definitions, field definitions, domains, and domain definitions.
In later editions of the NG911 Geodatabase Template, these definitions
are already filled in, so this tool is unnecessary.

The metadata enhancement tool requires:

-   One Python script called “Metadata\_EnhanceMetadata.py”

-   One folder called “Domains” that contains text files of resource
    information

Running “Enhance Metadata”:

1.  Open ArcCatalog and navigate to the toolbox called “Kansas NG911 GIS
    Tools”, expand the toolbox, then expand the toolset called “Metadata
    Tools.”

2.  Double click on “Enhance Metadata” to open the tool.

3.  In the “Geodatabase” parameter, select the geodatabase that needs
    metadata updated.

4.  In the “Domain Folder” parameter, select the “Domains” folder.

5.  In the “Emergency Services Boundary Layers” parameter, select ALL
    layers that represent emergency services (ESB, Law, Fire, etc.).

6.  Run the tool.

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
