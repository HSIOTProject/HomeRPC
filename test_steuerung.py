import steuerung


def test_steuerung_wp_fullBattery():
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
    assert steuerung.sterung(data)["wärmepumpe"] == steuerung.SteuerStatus.EIN.value


def test_steuerung_wp_SurplusConsumption_MiddleBattery():
    e3dc = {"autarky":95.35,
         "consumption":
            {"battery":3156,
             "house":3683,
             "wallbox":0},
        "production":{
            "solar":4122,
            "add":2647,
            "grid":-4000}, # <-
            "selfConsumption":96.66,
            "stateOfCharge":50, # <-
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
    assert steuerung.sterung(data)["wärmepumpe"] == steuerung.SteuerStatus.EIN.value


def test_steuerung_wp_HugeNetConsumption():
    e3dc = {"autarky":95.35,
         "consumption":
            {"battery":3156,
             "house":3683,
             "wallbox":0},
        "production":{
            "solar":4122,
            "add":2647,
            "grid":4000}, 
            "selfConsumption":96.66,
            "stateOfCharge":50, # <-
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
    assert steuerung.sterung(data)["wärmepumpe"] == steuerung.SteuerStatus.AUS.value


def test_steuerung_WallboxLinks():
    e3dc = {"autarky":95.35,
         "consumption":
            {"battery":3156,
             "house":3683,
             "wallbox":0},
        "production":{
            "solar":4122,
            "add":2647,
            "grid":-4000},  # überproduktion
            "selfConsumption":96.66,
            "stateOfCharge":50,
            "time":"2023-05-03T09:01:41.000584+00:00"
        }

    wallboxLinks = {"appSoftware":0,"chargingActive":False,"chargingCanceled":False,"consumptionNet":0,"consumptionSun":0,"energyAll":0,"energyNet":0,"energySun":0,"index":0,"keyState":1,"maxChargeCurrent":10,"phases":3,"plugLocked":False,"plugged":True,"schukoOn":False,"soc":0,"sunModeOn":True}

    wallboxRechts = {"appSoftware":0,"chargingActive":False,"chargingCanceled":False,"consumptionNet":0,"consumptionSun":0,"energyAll":0,"energyNet":0,"energySun":0,"index":1,"keyState":1,"maxChargeCurrent":16,"phases":3,"plugLocked":False,"plugged":False,"schukoOn":False,"soc":0,"sunModeOn":True}

    data = {
        "e3dc": e3dc,
        "wallboxLinks": wallboxLinks,
        "wallboxRechts": wallboxRechts,
        "wärmepumpe": {
            "status": True
        }
    }
    assert steuerung.sterung(data)["wallboxLinks"] == steuerung.SteuerStatus.EIN.value


def test_steuerung_WallboxLinksHouseBatteryLow():
    e3dc = {"autarky":95.35,
         "consumption":
            {"battery":3156,
             "house":3683,
             "wallbox":0},
        "production":{
            "solar":4122,
            "add":2647,
            "grid":-4000},  # überproduktion
            "selfConsumption":96.66,
            "stateOfCharge":10, # <- Battery low
            "time":"2023-05-03T09:01:41.000584+00:00"
        }

    wallboxLinks = {"appSoftware":0,"chargingActive":False,"chargingCanceled":False,"consumptionNet":0,"consumptionSun":0,"energyAll":0,"energyNet":0,"energySun":0,"index":0,"keyState":1,"maxChargeCurrent":10,"phases":3,"plugLocked":False,"plugged":True,"schukoOn":False,"soc":0,"sunModeOn":True}

    wallboxRechts = {"appSoftware":0,"chargingActive":False,"chargingCanceled":False,"consumptionNet":0,"consumptionSun":0,"energyAll":0,"energyNet":0,"energySun":0,"index":1,"keyState":1,"maxChargeCurrent":16,"phases":3,"plugLocked":False,"plugged":False,"schukoOn":False,"soc":0,"sunModeOn":True}

    data = {
        "e3dc": e3dc,
        "wallboxLinks": wallboxLinks,
        "wallboxRechts": wallboxRechts,
        "wärmepumpe": {
            "status": True
        }
    }
    assert steuerung.sterung(data)["wallboxLinks"] == steuerung.SteuerStatus.AUS.value



def test_steuerung_WallboxLinksHouseBatteryLow():
    e3dc = {"autarky":95.35,
         "consumption":
            {"battery":3156,
             "house":3683,
             "wallbox":0},
        "production":{
            "solar":4122,
            "add":2647,
            "grid":4000},  # <- Netzbezug
            "selfConsumption":96.66,
            "stateOfCharge":80, # <- Genug Batterie
            "time":"2023-05-03T09:01:41.000584+00:00"
        }

    wallboxLinks = {"appSoftware":0,"chargingActive":False,"chargingCanceled":False,"consumptionNet":0,"consumptionSun":0,"energyAll":0,"energyNet":0,"energySun":0,"index":0,"keyState":1,"maxChargeCurrent":10,"phases":3,"plugLocked":False,"plugged":True,"schukoOn":False,"soc":0,"sunModeOn":True}

    wallboxRechts = {"appSoftware":0,"chargingActive":False,"chargingCanceled":False,"consumptionNet":0,"consumptionSun":0,"energyAll":0,"energyNet":0,"energySun":0,"index":1,"keyState":1,"maxChargeCurrent":16,"phases":3,"plugLocked":False,"plugged":False,"schukoOn":False,"soc":0,"sunModeOn":True}

    data = {
        "e3dc": e3dc,
        "wallboxLinks": wallboxLinks,
        "wallboxRechts": wallboxRechts,
        "wärmepumpe": {
            "status": True
        }
    }
    assert steuerung.sterung(data)["wallboxLinks"] == steuerung.SteuerStatus.AUS.value


def test_steuerung_AllesAn():
    e3dc = {"autarky":95.35,
         "consumption":
            {"battery":3156,
             "house":3683,
             "wallbox":0},
        "production":{
            "solar":4122,
            "add":2647,
            "grid":-12000},  # <- Überschuss
            "selfConsumption":96.66,
            "stateOfCharge":80, # <- Genug Batterie
            "time":"2023-05-03T09:01:41.000584+00:00"
        }

    wallboxLinks = {"appSoftware":0,"chargingActive":False,"chargingCanceled":False,"consumptionNet":0,"consumptionSun":0,"energyAll":0,"energyNet":0,"energySun":0,"index":0,"keyState":1,"maxChargeCurrent":10,"phases":3,"plugLocked":False,"plugged":True,"schukoOn":False,"soc":0,"sunModeOn":True}

    wallboxRechts = {"appSoftware":0,"chargingActive":False,"chargingCanceled":False,"consumptionNet":0,"consumptionSun":0,"energyAll":0,"energyNet":0,"energySun":0,"index":1,"keyState":1,"maxChargeCurrent":16,"phases":3,"plugLocked": True,"plugged":True,"schukoOn":False,"soc":0,"sunModeOn":True}

    data = {
        "e3dc": e3dc,
        "wallboxLinks": wallboxLinks,
        "wallboxRechts": wallboxRechts,
        "wärmepumpe": {
            "status": True
        }
    }
    assert steuerung.sterung(data)["wärmepumpe"] == steuerung.SteuerStatus.EIN.value
    assert steuerung.sterung(data)["wallboxLinks"] == steuerung.SteuerStatus.EIN.value
    assert steuerung.sterung(data)["wallboxRechts"] == steuerung.SteuerStatus.EIN.value


def test_steuerung_AllesNichtAllesAn():
    e3dc = {"autarky":95.35,
         "consumption":
            {"battery":3156,
             "house":3683,
             "wallbox":0},
        "production":{
            "solar":4122,
            "add":2647,
            "grid":-8000},  # <- Überschuss
            "selfConsumption":96.66,
            "stateOfCharge":20, # <- Genug Batterie
            "time":"2023-05-03T09:01:41.000584+00:00"
        }

    wallboxLinks = {"appSoftware":0,"chargingActive":False,"chargingCanceled":False,"consumptionNet":0,"consumptionSun":0,"energyAll":0,"energyNet":0,"energySun":0,"index":0,"keyState":1,"maxChargeCurrent":10,"phases":3,"plugLocked":False,"plugged":True,"schukoOn":False,"soc":0,"sunModeOn":True}

    wallboxRechts = {"appSoftware":0,"chargingActive":False,"chargingCanceled":False,"consumptionNet":0,"consumptionSun":0,"energyAll":0,"energyNet":0,"energySun":0,"index":1,"keyState":1,"maxChargeCurrent":16,"phases":3,"plugLocked": True,"plugged":True,"schukoOn":False,"soc":0,"sunModeOn":True}

    data = {
        "e3dc": e3dc,
        "wallboxLinks": wallboxLinks,
        "wallboxRechts": wallboxRechts,
        "wärmepumpe": {
            "status": True
        }
    }
    assert steuerung.sterung(data)["wärmepumpe"] == steuerung.SteuerStatus.EIN.value
    assert steuerung.sterung(data)["wallboxLinks"] == steuerung.SteuerStatus.AUS.value
    assert steuerung.sterung(data)["wallboxRechts"] == steuerung.SteuerStatus.AUS.value
