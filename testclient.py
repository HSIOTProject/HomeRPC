import jsonrpcx

e3dc = {"autarky":95.35,
         "consumption":
            {"battery":3156,
             "house":3683,
             "wallbox":0},
        "production":{
            "solar":4122,
            "add":2647,
            "grid":70},
            "selfConsumption":96.66,
            "stateOfCharge":83,
            "time":"2023-05-03T09:01:41.000584+00:00"
        }

wallboxLinks = {"appSoftware":0,"chargingActive":False,"chargingCanceled":False,"consumptionNet":0,"consumptionSun":0,"energyAll":0,"energyNet":0,"energySun":0,"index":0,"keyState":1,"maxChargeCurrent":10,"phases":3,"plugLocked":False,"plugged":False,"schukoOn":False,"soc":0,"sunModeOn":True}


wallboxRechts = {"appSoftware":0,"chargingActive":False,"chargingCanceled":False,"consumptionNet":0,"consumptionSun":0,"energyAll":0,"energyNet":0,"energySun":0,"index":1,"keyState":1,"maxChargeCurrent":16,"phases":3,"plugLocked":False,"plugged":False,"schukoOn":False,"soc":0,"sunModeOn":True}

data = {
    "e3dc": e3dc,
    "wallboxLinks": wallboxLinks,
    "wallboxRechts": wallboxRechts,
    "wärmepumpe": {
        "status": True
    }
}

print(jsonrpcx.call("http://localhost:8000", "steuerung", [data]))

