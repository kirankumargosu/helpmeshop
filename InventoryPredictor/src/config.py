from enum import Enum, auto


class LogLevel(Enum):
    VERBOSE = 1
    INFO = 2
    WARN = 3
    ERROR = 4
    FATAL = 5


class LogType(Enum):
    CONSOLE = auto()
    FILE = auto()


class Config:
    __instance = None
    currencyCode = '£'
    credFileName = './InventoryPredictor/config/gspread/cred.json'
    reloadSheets = '202011,202012'
    fileName = 'Expenses_@@yyyymm@@'
    dateFormat = '%d.%m.%y'
    sheetNameRegex = '^\d{6,6}$'
    fromYear = 2020
    ignoreYears = []
    ignoreMonths = []
    ignoreMonthOfYear = {}
    logLevel = LogLevel.WARN
    logType = LogType.CONSOLE
    logTimestampFormat = '%Y-%m-%d %H:%M:%S.%f%Z'
    useCache = True
    cacheDirectory = './InventoryPredictor/cache/'
    imagesDirectory = './InventoryPredictor/images/'
    predictWindowStart = 7
    predictWindowEnd = 14
    vetoPredictionList = 'Delivery Charge'

    def __init__(self):
        if Config.__instance is not None:
            raise Exception("I'm Singleton")
        else:
            Config.__instance = self

    @staticmethod
    def get_instance():
        if Config.__instance is None:
            Config.__instance = Config()
        return Config.__instance
