"""
Cliente HTTP para la API de AudioPro
"""
import requests
import streamlit as st
import os

API_BASE = os.environ.get('API_BASE_URL', 'http://localhost:8000/api')


def get_headers():
    """Retorna headers con token JWT si existe."""
    headers = {'Content-Type': 'application/json'}
    token = st.session_state.get('access_token')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers


def api_get(endpoint, params=None):
    try:
        r = requests.get(f'{API_BASE}{endpoint}', headers=get_headers(), params=params, timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.HTTPError as e:
        return None, _parse_error(e.response)
    except requests.exceptions.ConnectionError:
        return None, 'No se puede conectar con el servidor.'
    except Exception as e:
        return None, str(e)


def api_post(endpoint, data=None, files=None):
    headers = get_headers()
    if files:
        headers.pop('Content-Type', None)  # multipart/form-data
    try:
        r = requests.post(
            f'{API_BASE}{endpoint}', headers=headers,
            json=data if not files else None,
            data=data if files else None,
            files=files, timeout=15
        )
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.HTTPError as e:
        return None, _parse_error(e.response)
    except requests.exceptions.ConnectionError:
        return None, 'No se puede conectar con el servidor.'
    except Exception as e:
        return None, str(e)


def api_patch(endpoint, data):
    try:
        r = requests.patch(f'{API_BASE}{endpoint}', headers=get_headers(), json=data, timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.HTTPError as e:
        return None, _parse_error(e.response)
    except Exception as e:
        return None, str(e)


def api_delete(endpoint):
    try:
        r = requests.delete(f'{API_BASE}{endpoint}', headers=get_headers(), timeout=10)
        r.raise_for_status()
        return True, None
    except requests.exceptions.HTTPError as e:
        return False, _parse_error(e.response)
    except Exception as e:
        return False, str(e)


def _parse_error(response):
    """Extrae mensaje de error de la respuesta."""
    try:
        data = response.json()
        if isinstance(data, dict):
            # Buscar mensajes de error comunes
            for key in ['detail', 'error', 'message', 'non_field_errors']:
                if key in data:
                    val = data[key]
                    return val[0] if isinstance(val, list) else val
            # Primer campo con error
            first_key = next(iter(data))
            val = data[first_key]
            msg = val[0] if isinstance(val, list) else val
            return f'{first_key}: {msg}'
        return str(data)
    except Exception:
        return f'Error {response.status_code}'
