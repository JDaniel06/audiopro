"""
Cliente HTTP para comunicarse con el backend Django REST Framework.
"""
import requests
import streamlit as st

BASE_URL = "http://localhost:8000/api"


def get_headers():
    """Retorna headers con token JWT si existe en sesión."""
    token = st.session_state.get("access_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def api_get(endpoint, params=None):
    try:
        r = requests.get(f"{BASE_URL}{endpoint}", headers=get_headers(), params=params, timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "No se puede conectar al servidor. ¿Está corriendo el backend?"
    except requests.exceptions.HTTPError as e:
        return None, f"Error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)


def api_post(endpoint, data=None, files=None, json_data=True):
    try:
        headers = get_headers()
        if json_data and not files:
            r = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers, timeout=10)
        else:
            r = requests.post(f"{BASE_URL}{endpoint}", data=data, files=files, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.HTTPError as e:
        try:
            return None, e.response.json()
        except Exception:
            return None, e.response.text
    except requests.exceptions.ConnectionError:
        return None, "No se puede conectar al servidor."
    except Exception as e:
        return None, str(e)


def api_put(endpoint, data=None):
    try:
        r = requests.put(f"{BASE_URL}{endpoint}", json=data, headers=get_headers(), timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.HTTPError as e:
        try:
            return None, e.response.json()
        except Exception:
            return None, e.response.text
    except Exception as e:
        return None, str(e)


def api_patch(endpoint, data=None):
    try:
        r = requests.patch(f"{BASE_URL}{endpoint}", json=data, headers=get_headers(), timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.HTTPError as e:
        try:
            return None, e.response.json()
        except Exception:
            return None, e.response.text
    except Exception as e:
        return None, str(e)


def api_delete(endpoint):
    try:
        r = requests.delete(f"{BASE_URL}{endpoint}", headers=get_headers(), timeout=10)
        r.raise_for_status()
        return True, None
    except requests.exceptions.HTTPError as e:
        return False, e.response.text
    except Exception as e:
        return False, str(e)
