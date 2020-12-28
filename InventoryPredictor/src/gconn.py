from InventoryPredictor.src.config import Config, LogLevel
import gspread
import pandas as pd
import numpy as np
import re
import os
from datetime import datetime as dt
from InventoryPredictor.src.logger import Logger

from pathlib import Path


class GoogleSheetAdaptor:
    # Spreadsheet - The entire file
    # Worksheet - The tab

    __client = None
    __googleSpreadsheetFileName = None
    __spreadSheet = None
    __cnf = None
    __logger = None
    __latestSheet = None

    def __init__(self, credFileName, googleSpreadsheetFileName):
        self.__cfg = Config.get_instance()
        self.__logger = Logger.get_instance()
        cred_json = os.environ.get('GOOGLE_CREDENTIALS')

        if cred_json is not None:
            with open(self.__cfg.credFileName, 'w') as f:
                f.write(cred_json)

        self.__client = gspread.service_account(filename=credFileName)

        if os.path.isfile(self.__cfg.credFileName) and cred_json is not None:
            os.remove(self.__cfg.credFileName)

        self.__googleSpreadsheetFileName = googleSpreadsheetFileName
        self.__spreadsheet = self.__client.open(self.__googleSpreadsheetFileName)

    def set_google_spreadsheet_filename(self, googleSpreadSheetFileName):
        self.__googleSpreadsheetFileName = googleSpreadSheetFileName

    def get_worksheets(self):
        return self.__spreadsheet.worksheets()

    def get_spreadsheet_data(self):
        # get all the worksheets
        # for each worksheet, get data
        appendedData = []
        worksheets = self.get_worksheets()

        worksheetMap = {worksheets[i]: worksheets[i].title for i in range(0, len(worksheets))}
        expensesWorksheets = {key: value for (key, value) in worksheetMap.items() if re.match(self.__cfg.sheetNameRegex,
                                                                                              value)}
        self.__latestSheet = max(expensesWorksheets.values())

        for expenseWorksheet in expensesWorksheets:
            monthlyData = self.get_worksheet_data(expenseWorksheet)
            appendedData.append(monthlyData)
        result = pd.concat(appendedData)
        # result = result.sort_values(by=['iDate'])
        # result['RowIndex'] = np.arange(len(result))
        return result

    def get_worksheet_data(self, worksheet):
        # We are passing a worksheet object
        if self.use_data_from_cache(worksheet):
            return self.get_data_from_cache(worksheet)
        else:
            return self.get_data_from_worksheet(worksheet)

    def get_data_from_worksheet(self, worksheet):
        self.__logger.log(LogLevel.INFO,
                          'Started Reading {}.{} from Google Spreadsheet'.format(self.__googleSpreadsheetFileName,
                                                                                 worksheet.title))
        sheetData = pd.DataFrame(worksheet.get_all_values())
        namedColumns = sheetData.iloc[1][1:6]
        sheetData.drop(index=[0, 1], inplace=True)
        result = sheetData[list(range(1, len(namedColumns) + 1))]
        result.columns = namedColumns
        result['Date'] = result.apply(lambda row: np.NaN if row['Date'] == "" else row['Date'], axis=1)
        result['Amount'] = result.apply(lambda row: row['Amount'].replace(self.__cfg.currencyCode, '').replace(',', ''),
                                        axis=1).astype(np.float)
        result.fillna(method='ffill', inplace=True)
        result['Date'] = result.apply(lambda row: dt.strftime(pd.to_datetime(row['Date'], format=self.__cfg.dateFormat),
                                                              '%Y%m%d'), axis=1)

        result['iDate'] = result.apply(lambda row: int(row['Date']), axis=1)
        result['Month'] = result.apply(lambda row: row['Date'][4:6], axis=1)
        self.__logger.log(LogLevel.INFO,
                          'Completed Reading {}.{} from Google Spreadsheet'.format(self.__googleSpreadsheetFileName,
                                                                                   worksheet.title))
        self.update_cache(result, worksheet.title)
        return result

    def update_cache(self, newData, cacheFileName):
        self.__logger.log(LogLevel.INFO,
                          'Started Caching Data {}.{}'.format(self.__googleSpreadsheetFileName, cacheFileName))
        newData.to_csv(self.__cfg.cacheDirectory + cacheFileName + '.csv', index=False)
        self.__logger.log(LogLevel.INFO,
                          'Completed Caching Data {}.{}'.format(self.__googleSpreadsheetFileName, cacheFileName))

    def get_data_from_cache(self, worksheet):
        self.__logger.log(LogLevel.INFO,
                          'Started Reading {}.{} from Cache'.format(self.__googleSpreadsheetFileName, worksheet.title))
        result = pd.read_csv(self.__cfg.cacheDirectory + worksheet.title + '.csv')
        self.__logger.log(LogLevel.INFO,
                          'Completed Reading {}.{} from Cache'.format(self.__googleSpreadsheetFileName,
                                                                      worksheet.title))
        return result

    def use_data_from_cache(self, worksheet):
        # use cache | cache file    | return
        # 0         | 0             | False
        # 0         | 1             | False
        # 1         | 0             | False
        # 1         | 1             | True

        # reload    | cache file    | return
        # 0         | 0             | False
        # 0         | 1             | True
        # 1         | 0             | False
        # 1         | 1             | False

        reloadSheets = self.__latestSheet if os.environ.get('RELOAD_SHEETS') is None \
                                          else os.environ.get('RELOAD_SHEETS')
        isSheetToBeReloaded = [x.strip() for x in reloadSheets.lstrip(',').rstrip(',').split(',')]

        # print('{} is in list {}'.format(worksheet.title, worksheet.title not in isSheetToBeReloaded))
        if (worksheet.title not in isSheetToBeReloaded) and self.is_data_cached(worksheet):
            return True
        return False

    def is_data_cached(self, worksheet):
        cachedFile = Path(self.__cfg.cacheDirectory + worksheet.title + '.csv')
        if cachedFile.is_file():
            return True
        return False
