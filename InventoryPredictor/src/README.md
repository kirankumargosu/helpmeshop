# src folder contains code for Prediction.
- predictor.py - is the main class, which initiates the flow
- gconn.py - connects to the google spreadsheets and reads the data
- expenses.py - a singleton class which holds the data statically
- analyzer.py - contains most of the end points for usage/prediction
- wordcloudgen.py - generates the word cloud
- logger.py - log utils - to be enhanced.
- config.py - has the configuration details
- synthesizer.py - currently the data curation is handled by predictor.py. The curation will be moved here
- db.py - for future usage when the data input is created