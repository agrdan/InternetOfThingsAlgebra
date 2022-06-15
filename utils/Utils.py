from datetime import datetime as dt



class Utils:

    @staticmethod
    def createDateFromString(dateString):
        return dt.fromisoformat(dateString)

