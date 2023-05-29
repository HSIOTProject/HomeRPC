from .api import *
from .psaconfig import PSAConfiguration

def fetch_soc_modified(config: PSAConfiguration) -> Tuple[float, float, str]:
    try:
        session = create_session(
            config.user_id, config.password, config.client_id, config.client_secret, config.manufacturer)

        vehicle = fetch_vehicle(config.vin, session)
        log.info("Fetching details for VIN: %s with vehicle_id: %s", vehicle['vin'], vehicle['id'])
        energy = fetch_energy(vehicle['id'], session)
    except Exception:
        raise Exception("Error requesting PSA data for vehicle")
    log.info("psa.fetch_soc: soc=%s%%, range=%s, timestamp=%s",
             energy['level'], energy['autonomy'], energy['updatedAt'])
    return energy


def getOpelInfo(psaUser: str, psaPassword: str, vin: str=None):
    config = PSAConfiguration(
        user_id = psaUser,
        password = psaPassword,
        manufacturer = "Opel",
        calculate_soc = False,
        vin=vin
    )
    return fetch_soc_modified(config)

