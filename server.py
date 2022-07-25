import json
import urllib.request

from log import Log


class API:
    __url = ''

    def __init__(self, baseUrl):
        self.__url = baseUrl
        pass

    def get(self, url: str):
        pass

    def post(self, data):
        pass

    def DeleteMessages(self, id: str):
        try:
            with urllib.request.urlopen(self.__url + "/getmsg.php?id=" + id) as url:
                data = url.read().decode()
                if data == 'OK':
                    return True
                else:
                    Log.Warning("NOT OK request url: %s/getmsg.php?id=%s" % (self.__url, id))
        except urllib.error.HTTPError as e:
            Log.Warning("url: %s/getmsg.php?id=%s, %s " % (self.__url, id, e))
            return False

    def GetMessages(self):
        try:
            with urllib.request.urlopen(self.__url + "/getmsg.php") as url:
                data = json.loads(url.read().decode())
            return data
        except urllib.error.HTTPError as e:
            Log.Warning("url: %s/getmsg.php, %s" % (self.__url, e))
            return False
        except Exception as e:
            Log.Warning("url: %s/getmsg.php, %s" % (self.__url, e))
            return False

    def Connect(self):
        pass
