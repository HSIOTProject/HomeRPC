# Source: https://github.com/fsantini/python-e3dc/pull/59/files Unmerged PR
import struct
from e3dc._e3dc import *
import logging

class E3DCWallboxEasyConnect:
    def get_wallbox_data(self, wbIndex=0, keepAlive=False):
        """Polls the wallbox status via rscp protocol locally.

        Args:
            wbIndex (Optional[int]): Index of the wallbox to poll data for
            keepAlive (Optional[bool]): True to keep connection alive

        Returns:
            dict: Dictionary containing the wallbox status structured as follows::

                {
                    "appSoftware": <version of the app>,
                    "chargingActive": <true if charging is currently active, otherwise false>,
                    "chargingCanceled": <true if charging was manually canceled, otherwise false>,
                    "consumptionNet": <power currently consumed by the wallbox, provided by the grid in watts>,
                    "consumptionSun": <power currently consumed by the wallbox, provided by the solar panels in watts>,
                    "energyAll": <total consumed energy this month in watthours>,
                    "energyNet": <consumed net energy this month in watthours>,
                    "energySun": <consumed solar energy this month in watthours>,
                    "index": <index of the requested wallbox>,
                    "keyState": <state of the key switch at the wallbox>,
                    "maxChargeCurrent": <configured maximum charge current in A>,
                    "phases": <number of phases used for charging>,
                    "schukoOn": <true if the connected schuko of the wallbox is on, otherwise false>,
                    "soc": <state of charge>,
                    "sunModeOn": <true if sun-only-mode is active, false if mixed mode is active>
                }
        """
        req = self.sendRequest(
            (
                "WB_REQ_DATA",
                "Container",
                [
                    ("WB_INDEX", "UChar8", wbIndex),
                    ("WB_REQ_EXTERN_DATA_ALG", "None", None),
                    ("WB_REQ_EXTERN_DATA_SUN", "None", None),
                    ("WB_REQ_EXTERN_DATA_NET", "None", None),
                    ("WB_REQ_APP_SOFTWARE", "None", None),
                    ("WB_REQ_KEY_STATE", "None", None),
                ],
            ),
            keepAlive=keepAlive,
        )
        logging.debug("Get Wallbox data, Req response: %s", req)

        outObj = {
            "index": rscpFindTagIndex(req, "WB_INDEX"),
            "appSoftware": rscpFindTagIndex(req, "WB_APP_SOFTWARE"),
        }

        extern_data_alg = rscpFindTag(req, "WB_EXTERN_DATA_ALG")
        if extern_data_alg is not None:
            extern_data = rscpFindTagIndex(extern_data_alg, "WB_EXTERN_DATA")
            status_byte = extern_data[2]
            outObj["sunModeOn"] = (status_byte & 128) != 0
            outObj["chargingCanceled"] = (status_byte & 64) != 0
            outObj["chargingActive"] = (status_byte & 32) != 0
            outObj["plugLocked"] = (status_byte & 16) != 0
            outObj["plugged"] = (status_byte & 8) != 0
            outObj["soc"] = extern_data[0]
            outObj["phases"] = extern_data[1]
            outObj["maxChargeCurrent"] = extern_data[3]
            outObj["schukoOn"] = extern_data[5] != 0

        extern_data_sun = rscpFindTag(req, "WB_EXTERN_DATA_SUN")
        if extern_data_sun is not None:
            extern_data = rscpFindTagIndex(extern_data_sun, "WB_EXTERN_DATA")
            outObj["consumptionSun"] = struct.unpack("h", extern_data[0:2])[0]
            outObj["energySun"] = struct.unpack("i", extern_data[2:6])[0]

        extern_data_net = rscpFindTag(req, "WB_EXTERN_DATA_NET")
        if extern_data_net is not None:
            extern_data = rscpFindTagIndex(extern_data_net, "WB_EXTERN_DATA")
            outObj["consumptionNet"] = struct.unpack("h", extern_data[0:2])[0]
            outObj["energyNet"] = struct.unpack("i", extern_data[2:6])[0]

        if "energySun" in outObj and "energyNet" in outObj:
            outObj["energyAll"] = outObj["energyNet"] + outObj["energySun"]

        key_state = rscpFindTag(req, "WB_KEY_STATE")
        if key_state is not None:
            outObj["keyState"] = rscpFindTagIndex(key_state, "WB_KEY_STATE")

        outObj = {k: v for k, v in sorted(outObj.items())}
        return outObj

    def set_wallbox_sunmode(self, enable: bool, wbIndex=0, keepAlive=False):
        """Sets the sun mode of the wallbox via rscp protocol locally.

        Args:
            enable (bool): True to enable sun mode, otherwise false,
            wbIndex (Optional[int]): index of the requested wallbox,
            keepAlive (Optional[bool]): True to keep connection alive
        """
        return self.__wallbox_set_extern(0, 1 if enable else 2, wbIndex, keepAlive)

    def set_wallbox_schuko(self, on: bool, wbIndex=0, keepAlive=False):
        """Sets the Schuko of the wallbox via rscp protocol locally.

        Args:
            on (bool): True to activate the Schuko, otherwise false
            wbIndex (Optional[int]): index of the requested wallbox,
            keepAlive (Optional[bool]): True to keep connection alive
        """
        return self.__wallbox_set_extern(5, 1 if on else 0, wbIndex, keepAlive)

    def set_wallbox_max_charge_current(
        self, max_charge_current: int, wbIndex=0, keepAlive=False
    ):
        """Sets the maximum charge current of the wallbox via rscp protocol locally.

        Args:
            max_charge_current (int): maximum allowed charge current in A
            wbIndex (Optional[int]): index of the requested wallbox,
            keepAlive (Optional[bool]): True to keep connection alive
        """
        barry = bytearray([0, 0, max_charge_current, 0, 0, 0])
        return self.sendRequest(
            (
                "WB_REQ_DATA",
                "Container",
                [
                    ("WB_INDEX", "UChar8", wbIndex),
                    (
                        "WB_REQ_SET_PARAM_1",
                        "Container",
                        [
                            ("WB_EXTERN_DATA", "ByteArray", barry),
                            ("WB_EXTERN_DATA_LEN", "UChar8", 6),
                        ],
                    ),
                ],
            ),
            keepAlive=keepAlive,
        )

    def set_wallbox_phases(self, phases: int, wbIndex=0, keepAlive=False):
        """Sets the number of phases used for charging on the wallbox via rscp protocol locally.

        Args:
            phases (int): number of phases used, valid values are 1 or 3
            wbIndex (Optional[int]): index of the requested wallbox,
            keepAlive (Optional[bool]): True to keep connection alive
        """
        if phases not in [1, 3]:
            raise Exception("Invalid phase given, valid values are 1 or 3")
        return self.__wallbox_set_extern(3, phases, wbIndex, keepAlive)

    def toggle_wallbox_charging(self, wbIndex=0, keepAlive=False):
        """Toggles charging of the wallbox via rscp protocol locally.

        Args:
            wbIndex (Optional[int]): index of the requested wallbox,
            keepAlive (Optional[bool]): True to keep connection alive
        """
        return self.__wallbox_set_extern(4, 1, wbIndex, keepAlive)

    def __wallbox_set_extern(self, index: int, value: int, wbIndex, keepAlive=False):
        barry = bytearray([0, 0, 0, 0, 0, 0])
        barry[index] = value
        self.sendRequest(
            (
                "WB_REQ_DATA",
                "Container",
                [
                    ("WB_INDEX", "UChar8", wbIndex),
                    (
                        "WB_REQ_SET_EXTERN",
                        "Container",
                        [
                            ("WB_EXTERN_DATA", "ByteArray", barry),
                            ("WB_EXTERN_DATA_LEN", "UChar8", 6),
                        ],
                    ),
                ],
            ),
            keepAlive=keepAlive,
        )

