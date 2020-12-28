# https://www.analyticsvidhya.com/blog/2020/07/read-and-update-google-spreadsheets-with-python/
# https://gspread.readthedocs.io/en/latest/oauth2.html
# https://gspread.readthedocs.io/en/latest/user-guide.html


import numpy as np
import warnings
from datetime import datetime as dt, timedelta as td
from InventoryPredictor.src.config import Config, LogLevel
from InventoryPredictor.src.gconn import GoogleSheetAdaptor
from InventoryPredictor.src.expenses import Expenses
from sklearn.linear_model import LinearRegression
from InventoryPredictor.src.logger import Logger
from Authenticator.src.decorator import login_required, is_valid_user
from flask import redirect
import os

htmlTemplate = '<!DOCTYPE html>' \
               '<html lang="en">' \
               '    <head>' \
               '        <title>Help me Shop!</title>' \
               '        <meta charset="UTF-8">     ' \
               '        <meta http-equiv="X-UA-Compatible" content="IE=Edge">' \
               '        <meta name="description" content="">' \
               '        <meta name="keywords" content="">' \
               '        <meta name="team" content="">' \
               '        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"> ' \
               '        <style>' \
               '            img {' \
               '                display: block;' \
               '                margin-left: auto;' \
               '                margin-right: auto;' \
               '                }' \
               '            body {' \
               '                background-color: #404040;' \
               '                font-family: "Helvetica Neue";Helvetica;Arial;sans - serif' \
               '                }' \
               '        </style>' \
               '    </head>' \
               '    <body>' \
               '    <br>' \
               '    <h4 align="center"; style="color:#cccccc"> @@Header@@ </h4>' \
               '</html>'

warnings.filterwarnings("ignore")


# def fit_model(amount, usageIndex):
#     model = LinearRegression().fit(amount, usageIndex)
#     return model.intercept_, model.coef_

def fit_model(data):
    # print(type(data))
    description = data['Description'].unique()
    # print(description)
    # data.dropna(inplace=True)
    # print(data)
    trainData = data[data['UsageIndex'] != -999]
    testData = data[data['UsageIndex'] == -999]
    XTrain = trainData['Amount'].values.reshape((-1, 1))
    yTrain = trainData['UsageIndex'].values
    XTest = testData['Amount'].values.reshape((-1, 1))

    if len(XTrain) > 0 and len(yTrain) > 0:
        model = LinearRegression().fit(XTrain, yTrain)
        prediction = model.predict(XTest)
        # print(prediction[0])
        # print('Description = {} : Intercept = {} and Coef = {}, prediction = {} for XTest = {}'.format(
        #     description[0], model.intercept_, model.coef_[0], prediction[0], XTest))
        return model.intercept_, model.coef_[0], prediction[0]


@login_required
@is_valid_user
def read_data():
    predictor = Predictor.get_instance()
    predictor.read_data()
    expenses = Expenses.get_instance()
    expenses.wordCloud = None
    # return htmlTemplate.replace('@@Header@@', 'Successfully read the data')
    return redirect('/wc/')


class Predictor:
    log = Logger.get_instance()
    log.log(LogLevel.VERBOSE, 'Started.')
    expenses = Expenses.get_instance()
    log.log(LogLevel.VERBOSE, 'Config Instance fetched.')
    __instance = None

    def __init__(self):
        if Predictor.__instance is not None:
            raise Exception("I'm Singleton")
        else:
            Predictor.__instance = self
            self.cfg = Config.get_instance()
            self.expenses = Expenses.get_instance()

    @staticmethod
    def get_instance():
        if Predictor.__instance is None:
            Predictor.__instance = Predictor()
        return Predictor.__instance

    def read_data(self):
        gsa = GoogleSheetAdaptor(self.cfg.credFileName, 'Expenses_2020')
        curatedData = gsa.get_spreadsheet_data()
        # print(len(curatedData))
        # Sort the data by Dates, so that we can run through the usage.
        curatedData = curatedData.sort_values(by=['iDate'])

        # RowIndex = A sequence running through the dataset
        curatedData['RowIndex'] = np.arange(len(curatedData))

        # StitchIndex = Connecting links to the next usage.
        curatedData['StitchIndex'] = curatedData.apply(
            lambda row: curatedData[(curatedData['RowIndex'] <= row['RowIndex']) &
                                    (curatedData['Description'] == row['Description'])]
            ['Description'].count(),
            axis=1)

        minDate = str(min(curatedData['iDate'])) if os.environ.get('PREDICT_FROM') is None \
            else os.environ.get('PREDICT_FROM')

        # DateIndex = A sequence for Dates.
        # 0 = minDate, for example 01-Jan-2020,
        # 1 = minDate + 1, for example 02-Jan-2020, even if purchase is not made.
        curatedData['DateIndex'] = curatedData.apply(
            lambda row: (dt.strptime(str(row['Date']), '%Y%m%d') -
                         dt.strptime(minDate, '%Y%m%d')).days, axis=1)

        # UsageIndex = Distance between current purchase and the next purchase, in days
        curatedData['UsageIndex'] = curatedData.apply(
            lambda row:
            -999 if len(
                curatedData[(curatedData['Description'] == row['Description']) &
                            (curatedData['StitchIndex'] == row['StitchIndex'] + 1)]['DateIndex'].values - row[
                    'DateIndex']) == 0
            else (curatedData[(curatedData['Description'] == row['Description']) &
                              (curatedData['StitchIndex'] == row['StitchIndex'] + 1)]['DateIndex'].values - row[
                      'DateIndex'])[0],
            axis=1)

        descriptionList = curatedData['Description'].unique()

        # Split the data based on the descriptions.
        descriptionGroupMap = {description: curatedData[curatedData['Description'] == description]
                               for description in descriptionList}

        # for each of these descriptionGroups, fetch y-Intercept and Slope using LinearRegression
        modelValues = {description: fit_model(descriptionGroupMap[description])
                       for description in descriptionGroupMap}
        # print('Printing Model values ****')
        # print(modelValues['Rent'])

        # merge the y-Intercept and slope into the dataframe.
        # curatedData['Intercept'] = curatedData.apply(lambda row:
        #                                              None if (modelValues[row['Description']] is None
        #                                                       # or
        #                                                       # row['UsageIndex'] == -999
        #                                                      )
        #                                              else modelValues[row['Description']][0], axis=1)
        # curatedData['Slope'] = curatedData.apply(lambda row:
        #                                          None if (modelValues[row['Description']] is None
        #                                                   # or
        #                                                   # row['UsageIndex'] == -999
        #                                                   )
        #                                          else modelValues[row['Description']][1], axis=1)

        # curatedData['PredictedUsageIndex'] = curatedData.apply(lambda row:
        #                                                        None if (modelValues[row['Description']] is None
        #                                                                 # or
        #                                                                 # row['UsageIndex'] == -999
        #                                                                 )
        #                                                        else modelValues[row['Description']][2], axis=1)

        curatedData['DueDate'] = curatedData.apply(lambda row:
                                                   None if (modelValues[row['Description']] is None
                                                            # or
                                                            # row['UsageIndex'] == -999
                                                            )
                                                   else (dt.strptime(str(row['iDate']), "%Y%m%d") +
                                                         td(days=modelValues[row['Description']][2])).strftime(
                                                       '%Y%m%d'),
                                                   axis=1)

        # print(len(curatedData))]
        # test = curatedData[curatedData['Where'] == 'Coop']
        # test.to_csv(self.cfg.cacheDirectory + 'test.csv')
        curatedData.to_csv(self.cfg.cacheDirectory + 'curatedData.csv')
        # predictCandidates = curatedData[curatedData['UsageIndex'] == -999]
        # print(predictCandidates)
        self.expenses.data = curatedData
        # a = (curatedData[['Amount', 'UsageIndex']] for curatedData['Description'])
        # print(curatedData.groupby('Description')[['Amount', 'UsageIndex']])
        # self.run_prediction_shop('Matha', 20200101)
        self.run_prediction_shop('Matha', 20200701)
        # self.run_prediction_shop('Matha')

    def run_prediction_shop(self, shopName, fromDate=None):
        if self.expenses.data is None:
            self.read_data()
        if fromDate is not None:
            subset = self.expenses.data[(self.expenses.data['Where'] == shopName)
                                        & (self.expenses.data['iDate'] >= fromDate)
                                        & (self.expenses.data['Description'] == 'Rice - Ponni Boiled')
                                        ]
        else:
            subset = self.expenses.data[(self.expenses.data['Where'] == shopName)
                                        & (self.expenses.data['Description'] == 'Rice - Ponni Boiled')
                                        ]

        subset.sort_values(by=['DateIndex'], inplace=True)
