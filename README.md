# Dynamic REST API Mocker

This is a REST mocker build with Python Flask to facilitate API Developement.

## Pre-requisites

### Python 3 Installed

Please visit [Python.org](https://www.python.org/downloads/windows/) to download the recent **Windows Installer (64-bit)** and get it installed on your PC, ensure the Python exeuction folder is added to your **Path** during the installation.

To verify Python is installed properly, launch "cmd" to execute:
```
python --version
```

### Use Virtual Environment

Due to the IT restrictions within SRG, it is much more convenient to use virtual environment to install required Python libraries.

In the project folder, run following commands from the **Terminal** of your GUI to create and activate a virtual environment:

```
py -m venv venv
.\venv\Scripts\activate
```

Now the terminal shall show something like: *(venv) PS C:\project_foldername\>*

### Config PIP within the Virtual Environment

Try to execute following command from the *cmd*:
```
pip install flask
```

If you get *[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed* error, create *pip.ini* file under *C:\project_foldername\venv*:
```
# pip.ini (Windows)
# pip.conf (Unix, macOS)

[global]
trusted-host = pypi.org
               files.pythonhosted.org
```

### Install Dependencies

Once Python Virtual Environment is configured properly, run following command from the *cmd*:
```
pip install -r .\requirements.txt
```

To extend this library to meet your requirements, please feel free to use or install any Python GUI, like VS Code, PyCharm or IntelliJ.


## Getting Started

### Install Packages

From the terminal of your GUI, or project folder opened in the *cmd.exe*, execute following command to install packages:

```
python -m pip install -r .\requirements.txt
```

Then the dependencies shall be installed to enable running this mocking service.

### Launch the service

From command line or Terminal of the GUI, you can type `python app.py` from the project folder to launch the service and seeing the output showing:

```
(env) PS C:\lab\flask_rest> python app.py
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 ```

Now you can access *http://localhost:5000/* to see the content of this file in HTML format.

To stop the service, just press *CTRL+C* in the command line or Terminal of the GUI.


## Mock APIs

There are some APIs created and could be loaded on the fly, and it is also possible to create new APIs with CSV/JSON data and consume them immediately.

### View All API Routes

Open the [Routes page](http://localhost:5000/routes), there are two portions:
1. The first part in gray background list all routes supported by the Flask App that cannot be changed.
2. The second part are mocking APIs that are backed by the data files in "./data" folder of this project.

***Unless defined as fixed route before launching this mock service, all mocking API shall start with "http://localhost:5000/api/".***

### Create New API

Click on the "Create New" manu on top of the home page, a form is displayed to upload data file and specify parameters needed to create a new API:
* *Choose File*: open the file browser to locate a JSON or CSV file that contains data to be used to simulate the new API. For example, choose an external file "Products.csv".
* *Key Name*: to specify the unique identifer of the items in above file. For example, if "PLU" can be used as unique identifier of all rows in above file, just enter "PLU". 
* *Route*: to set the path of the new API. For example, entering "products" would create two new APIs:
  * http://localhost:5000/api/products: to list all items of the CSV or JSON file as a JSON array, or apply optional query strings to filter them.
  * http://localhost:5000/api/products/<key>: use the unique identifier to show a single item of all items imported from the CSV/JSON file.

Following steps could be taken to mock a new API:
1. Generate a data file containing a list of mocking objects as either CSV or JSON file. For example, execute the [traAccounts.sql](./external/traAccounts.sql) to get 1000 rows of data, save it with headers as [traAccounts.csv](./external/traAccounts.csv).
2. Launch the above [Create page](http://localhost:5000/create) to:
   1. Choose the [traAccounts.csv](./external/traAccounts.csv)
   2. Enter "accounts" in the Route text input field.
   3. Enter "traAccountNo" in the "Key Name" input field, which is the first column of the CSV file.
3. Once "Submit" button is clicked, the [Routes page](http://localhost:5000/routes) would be loaded showing 2 new routes are added at the bottom of that page and the **traAccounts.csv** would be copied to the **./data** folder.


### Consume the mocked APIs

Once the mock APIs are created, you can call them immediately, just notice: ***all mocking API shall start with "http://localhost:5000/api/".***

If the [traAccounts.csv](./external/traAccounts.csv) is loaded as in previous section, following actions can be taken:
  *  **GET** "http://localhost:5000/api/accounts" would list all items in above CSV file;
  *  Filters can be applied upon the above link. For example, **GET** "http://localhost:5000/api/accounts?STATE=QLD" would list all QLD accounts, while "http://localhost:5000/api/accounts?STATE=QLD&creditLimit=5000" would list all QLD accounts whose credit limit is 5000.
  *  To get a single item, with a known traAccountNo, just append the identifier to the end of "http://localhost:5000/api/accounts/". For example: "http://localhost:5000/api/accounts/600001451" would list the account whose AccountNo is 600001451
  *  CREATE, UPDATE and DELETE operations upon the single entity:
    1. **POST** "http://localhost:5000/api/accounts/600009999" with JSON object as payload to CREATE a new entity whose AccountNo is 600009999.
    2. **PUT** "http://localhost:5000/api/accounts/600001451" with the updated JSON content as the payload to update the existing entity of 600001451.
    3. ""DELETE** "http://localhost:5000/api/accounts/600001451" to DELETE the existing entity of 600001451.

Compared with composing the URLs and payloads, it is much easier to consume the APIs with REST client.

To facilitate the API testing and development, the [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) on VS code is highly recommended to init API calls and check their responses.

The corresponding settings within VS Code settings(C:\Users&bsol;**YourUserId**\AppData\Roaming\Code\User\settings.json) is listed below:

```
{
  "rest-client.environmentVariables": {

    "$shared": {
      "autoinfo": "https://test.autoinfo.com.au/APIsandbox/Autoimdmwebservice.asmx",
      "UserId": "9014",
      "AuthCode": "sup3rch77pcc",
      "CallingIpAddress": "1.1.1.1"
    },
    "@autoInfoGateway": {
      "autoinfo": "https://test.autoinfo.com.au/APIsandbox/AutoInfoGateway.asmx"
    },
    "$local": {
      "mocker": "http://127.0.0.1:5000/api"
    },
    "$local-working": {
      "mocker": "http://127.0.0.1:5000/file/working"
    },
    "$local-fault": {
      "mocker": "http://127.0.0.1:5000/file/fault"
    }
  },
  "rest-client.fontSize": 12,
  "rest-client.logLevel": "verbose",
  "rest-client.requestNameAsResponseTabTitle": true,
  "rest-client.previewOption": "exchange"
}

```

There are multiple *.http files created under "./requests" folder. Once choosing the "$local" environment, the **mocker** would point to "http://127.0.0.1:5000/api", then all HTTP methods can be prepared and executed easily.


### Persistent Mock APIs

The APIs created after launching the mock service would not be loaded automatically once service is closed. To make the mocking APIs persistent, following steps shall be taken:
1. Put the CSV/JSON file containing list of items to "./data" folder if they are not copied yet.
2. Edit the [mappings.json](mappings.json) file by appending new arrays into the **collection_mappings** field. For each CSV/JSON file, one array shall be appended with 3 values:
   1. The first value specify the name of the data file.
   2. The second value specify the name of the keys of the items defined in the CSV/JSON file.
   3. The route to be appended after "/api/".

For example, to persistent the "http://localhost:5000/api/accounts" APIs, following array shall be appended once "traAcconts.csv" is copied to "./data" folder:
```
[ "traAccounts.csv", "traAccountNo", "accounts"]

```

### Compare JSON Payloads

The [Compare page](http://localhost:5000/compare) provides a means to compare two objects represented as two JSON strings.

Just paste the two JSON strings into the two text areas and click "Submit" button would get their differences shown in the message bar below the navigation bar. By default:
* The keys would be matched by ignoring their cases.
* Default values would be treated as eqaul. That is: NULLs, "", 0, 0.0 would be regarded as equal.


