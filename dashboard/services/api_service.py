import requests
from config.api_config import API_URL


def get_trajets():
    response = requests.get(f"{API_URL}/trajets")
    return response.json()


def get_gares():
    response = requests.get(f"{API_URL}/gares")
    return response.json()


def get_lignes():
    response = requests.get(f"{API_URL}/lignes")
    return response.json()


def get_trajets_count():
    response = requests.get(f"{API_URL}/stats/trajets/count")
    return response.json()


def get_gares_count():
    response = requests.get(f"{API_URL}/stats/gares/count")
    return response.json()


def get_lignes_count():
    response = requests.get(f"{API_URL}/stats/lignes/count")
    return response.json()


def get_pays_count():
    response = requests.get(f"{API_URL}/stats/pays/count")
    return response.json()


def get_emissions():
    response = requests.get(f"{API_URL}/stats/emissions")
    return response.json()


def get_operateurs():
    response = requests.get(f"{API_URL}/stats/operateurs")
    if response.status_code != 200:
        return []
    try:
        return response.json()
    except Exception:
        return []


def get_trajets_map():
    response = requests.get(f"{API_URL}/stats/trajets/map")
    if response.status_code != 200:
        return []
    return response.json()


def get_trajets_type():
    try:
        response = requests.get(f"{API_URL}/stats/trajets/type", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {"JOUR": 0, "NUIT": 0}
import requests
from config.api_config import API_URL


def get_trajets():
    response = requests.get(f"{API_URL}/trajets")
    return response.json()


def get_gares():
    response = requests.get(f"{API_URL}/gares")
    return response.json()


def get_lignes():
    response = requests.get(f"{API_URL}/lignes")
    return response.json()


def get_trajets_count():
    response = requests.get(f"{API_URL}/stats/trajets/count")
    return response.json()


def get_gares_count():
    response = requests.get(f"{API_URL}/stats/gares/count")
    return response.json()


def get_lignes_count():
    response = requests.get(f"{API_URL}/stats/lignes/count")
    return response.json()

def get_emissions():
    response = requests.get(f"{API_URL}/stats/emissions")
    return response.json()

def get_operateurs():

    response = requests.get(f"{API_URL}/stats/operateurs")

    if response.status_code != 200:
        return []

    try:
        return response.json()
    except:
        return []
    
    
def get_trajets_map():
    response = requests.get(f"{API_URL}/stats/trajets/map")
    if response.status_code != 200:
        return []
    return response.json()


def get_trajets_type():
    try:
        response = requests.get(f"{API_URL}/stats/trajets/type", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {"JOUR": 0, "NUIT": 0}