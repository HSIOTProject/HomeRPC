from typing import *
from e3dc import E3DC
from wallbox import E3DCWallboxEasyConnect
import json
from jsonrpcx import WSGIServer, WSGIServerDelegate
import logging
import opel


# does not work with gunicorn
# logging.basicConfig(filename='e3dc.log', level=logging.DEBUG,
#                     format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)
logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class EnhancedE3DC(E3DC, E3DCWallboxEasyConnect):
    def __init__(self):
        with open("settings.json") as f:
            self.config = json.loads(f.read())
            e3dcConfig = self.config["e3dc"]
        KEY = e3dcConfig["key"] # Encryption key for the communication protocl
        CONFIG = {} 
        E3DC.__init__(self, E3DC.CONNECT_LOCAL, username=e3dcConfig["user"], password=e3dcConfig["pw"], ipAddress = e3dcConfig["ip"], key = KEY, configuration = CONFIG)
        E3DCWallboxEasyConnect.__init__(self)
    
    def ping(self):
        return "pong"
    
    def setWallbox(self, status: bool, wbIndex: int=0):
        #data = self.get_wallbox_data(self, wbIndex)
        data = self.get_wallbox_data(wbIndex)
        ist = data["chargingActive"]
        if status != ist:
            self.toggle_wallbox_charging(wbIndex=wbIndex)
        return {
            "previousStatus": ist,
        }
    
    def setWallboxOn(self, wbIndex: int):
        return self.setWallbox(self, True, wbIndex)

    def setWallboxOff(self, wbIndex: int):
        return self.setWallbox(self, False, wbIndex)

    def getOpelInfo(self):
        return opel.getOpelInfo(self.config["opel"]["user"], self.config["opel"]["pass"])
    

class ServiceWeb(EnhancedE3DC, WSGIServer):
    def __init__(self, delegate):
        EnhancedE3DC.__init__(self)
        WSGIServer.__init__(self, delegate=delegate)
    

class Delegate(WSGIServerDelegate):
    def HTMLHeaders(self) -> List[str]:
        return [
            ("Content-Type", "application/json"),
            ("Access-Control-Allow-Origin", "http://iot.informatik.hs-augsburg.de:3000"),
            ("Access-Control-Allow-Credentials", "true"),
            ("Access-Control-Allow-Headers", "*"),
            ]
   

def app(environment, start_response):
    wsgiServer = ServiceWeb(delegate=Delegate())
    return wsgiServer.parseRequest(environment, start_response)
