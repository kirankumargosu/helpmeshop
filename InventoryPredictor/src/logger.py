from InventoryPredictor.src.config import Config, LogType
import datetime as dt


class Logger:
    __instance = None
    __cnf = None

    def __init__(self):
        if Logger.__instance is not None:
            raise Exception("I'm Singleton")
        else:
            Logger.__instance = self
            self.__cfg = Config.get_instance()

    @staticmethod
    def get_instance():
        if Logger.__instance is None:
            Logger.__instance = Logger()
        return Logger.__instance

    def log(self, logLevel, logMessage):
        if logLevel.value >= self.__cfg.logLevel.value:
            self.__send_logs__(logLevel, logMessage)

    def __send_logs__(self, logLevel, logMessage):
        curatedMessage = dt.datetime.utcnow().strftime(self.__cfg.logTimestampFormat) + " : " + \
                         logLevel.name + " | " + logMessage
        if self.__cfg.logType == LogType.CONSOLE:
            print(curatedMessage)
