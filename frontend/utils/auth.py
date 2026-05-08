"""
Funciones de autenticación para Streamlit.
"""
import streamlit as st
from .api import api_post, api_get


def login(email: str, password: str) -> bool:
    """Autentica al usuario y guarda el token en session_state."""
    data, error = api_post("/users/auth/login/", {"email": email, "password": password})
    if error:
        st.error(f"Error al iniciar sesión: {error}")
        return False

    st.session_state["access_token"] = data["access"]
    st.session_state["refresh_token"] = data["refresh"]

    # Cargar perfil del usuario
    profile, _ = api_get("/users/profile/")
    if profile:
        st.session_state["user"] = profile
        st.session_state["is_admin"] = profile.get("role") == "admin" or profile.get("is_staff", False)

    return True


def logout():
    """Cierra la sesión limpiando el estado."""
    for key in ["access_token", "refresh_token", "user", "is_admin"]:
        st.session_state.pop(key, None)
    st.rerun()


def is_logged_in() -> bool:
    return bool(st.session_state.get("access_token"))


def is_admin() -> bool:
    return st.session_state.get("is_admin", False)


def require_login():
    """Redirige al login si no está autenticado."""
    if not is_logged_in():
        st.warning("Debes iniciar sesión para acceder a esta sección.")
        st.stop()


def require_admin():
    """Detiene la ejecución si no es admin."""
    require_login()
    if not is_admin():
        st.error("Acceso restringido a administradores.")
        st.stop()
