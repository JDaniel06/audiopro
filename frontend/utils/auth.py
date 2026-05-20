"""
Utilidades de autenticación para Streamlit
"""
import streamlit as st
from .api import api_post


def login(email: str, password: str) -> bool:
    """Autentica al usuario y guarda el token en session_state."""
    data, error = api_post('/auth/login/', {'email': email, 'password': password})
    if error:
        st.error(f'Error al iniciar sesión: {error}')
        return False
    st.session_state['access_token'] = data['access']
    st.session_state['refresh_token'] = data['refresh']
    # Obtener perfil
    from .api import api_get
    profile, _ = api_get('/users/profile/')
    if profile:
        st.session_state['user'] = profile
    return True


def logout():
    """Cierra la sesión del usuario."""
    for key in ['access_token', 'refresh_token', 'user']:
        st.session_state.pop(key, None)
    st.rerun()


def is_authenticated() -> bool:
    return bool(st.session_state.get('access_token'))


def is_admin() -> bool:
    user = st.session_state.get('user', {})
    return user.get('role') == 'admin' or user.get('is_staff', False)


def require_auth():
    """Redirige al login si no está autenticado."""
    if not is_authenticated():
        st.warning('Debes iniciar sesión para acceder a esta página.')
        st.stop()


def require_admin():
    """Detiene la ejecución si no es admin."""
    require_auth()
    if not is_admin():
        st.error('Acceso restringido a administradores.')
        st.stop()


def get_current_user() -> dict:
    return st.session_state.get('user', {})
