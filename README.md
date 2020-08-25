# nih-redcap-report
Python interface to report NIH demographic measures from REDCap

### Setting up the project on your own computer
#### Prerequisites
- python 3
- git (optional if you do not want to make changes to the code here in the repository)

#### Setup
- Clone repository by entering the command `git clone https://github.com/ReubenJ/nih-redcap-report.git` into your command line (or download the zip file from this repository's [main page](https://github.com/ReubenJ/nih-redcap-report) if you do not want to make changes to the code here in the repository)
- Change into the directory where the repository is cloned or downloaded `cd nih-redcap-report`
- Create a python virtual environment (optional, but recommended) `python3 -m venv .venv`, and activate it by running one of the following commands:
  - On Windows cmd.exe: `.venv/Scripts/activate.bat`
  - On Windows PowerShell: `.venv/Scripts/Activate.ps1`
  - Linux bash/zsh: `source .venv/bin/activate`
- Install python dependencies `pip3 install -r requirements.txt`
- Run the application `python3 report_app.py`


### Structure
- **report_app.py** holds the main frame of the application, including the menu bar. Run this to run the application.
- **api_key_frame.py** creates the frame/window where one can enter their api key and the api URL.
- **reqport_window.py** fills in the main frame with all of the report options and results, and handles exporting results to csv.
- **build.py** builds the application to a single executable file. Running it on Windows creates a Windows executable, on Linux creates a  Linux executable, etc..
