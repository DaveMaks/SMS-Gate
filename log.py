from datetime import datetime


class Log:

    @staticmethod
    def Info(value: str):
        Log.SaveFile(value, "INFO")

    @staticmethod
    def Debug(value: str):
        Log.SaveFile(value, "DEBUG")

    @staticmethod
    def Warning(value: str):
        Log.SaveFile(value, "WARNING")

    @staticmethod
    def SaveFile(value: str, act: str):
        file = open('./gsmGate.log', 'a')
        file.write('%s\t%s:\t%s\r\n' % (datetime.now().strftime('%y-%m-%d %H:%M:%S'), act, value))
        #print('%s\t%s:\t%s\r\n' % (datetime.now().strftime('%y-%m-%d %H:%M:%S'), act, value))
        file.close()

