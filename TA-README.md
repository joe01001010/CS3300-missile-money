# TA Instructions
These instruction were created for windows as the OS to run them but it they work on Linux as well with the corresponding commands


## Pre requisites
You will one of the 4 following python versions to run this.
python 3.10, 3.11, 3.12, 3.13
You will also need pip installed to install the python packages for this program


## Steps
Locate the zip file titled "TA-run-folder.zip"
Unzip the file in a location of your choosing. This will create a directory called TA-run-folder that contains all the files for the program
Change directories into TA-run-folder that was created by unzip
(Optional but recommended) Create a virtual environment before installing the program (python -m venv venv)
Activate the virtual environment (.\venv\Scripts\Activate.ps1)
Install the libraries from the requirements.txt file (pip install -r requirements.txt)
Run the server (python .\missile_money\manage.py runserver)
This will output a line "Starting development server at http://127.0.0.1:8000/"
That is the link to the webpage you are hosting. Hold ctrl and click the link to be taken to the page.
From here you will be brought to the browser to interact with the website as a user.
Follow the user guide to explore the web application.