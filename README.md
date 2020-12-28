# Help me Shop!
```
- Authenticator Package - for OAuth Authentication
- InventorAPI Package - currently only a placeholder
- InventoryPredictor Package - for Reading data and predicting
- config folder - Maintains the configuration
- static - contains html static files
- templates - contains the base HTML file
- app.py - the main application
- Procfile - for gunicorn to pick the starter
- requirements.txt - contains the Python libraries
- runtime.txt - Python runtime.
- swagger.yml - for configuring the end points.
```
# How to configure your env:
```
1. Install Python from here - https://www.python.org/downloads/
2. Install a Python editor. PyCharm or VSCode. I used PyCharm.
  i. I used PyCharm from https://www.jetbrains.com/pycharm/
  ii. VSCode can be downloaded from https://code.visualstudio.com
3. Install the python libraries. Instructions here - https://pip.pypa.io/en/stable/reference/pip_install/
  i. pip install -r requirements.txt
4. Run app.py
```

# Items to complete
```
- Add user info on every screen.
- Move the data curation to synthesizer.py to make it customizable to others.
- Add a template of google spreadsheet.
- Programmatically connect to any google spreadsheet via the app.
- Implement roles to various access like read only/update data.
- Create interactive reports.
- Read the data for the latest available month along with the existing env variable.
- Upload the data into the database.
- Add data entry screen.
```
