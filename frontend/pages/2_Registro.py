"""
Página de registro de nuevos clientes.
"""
import streamlit as st
from utils.api import api_post
from utils.auth import is_logged_in

st.set_page_config(page_title="Registro - Audio Store Pro", page_icon="📝")

if is_logged_in():
    st.success("Ya tienes sesión iniciada.")
    st.page_link("app.py", label="← Ir al inicio")
    st.stop()

st.title("📝 Crear Cuenta")

with st.form("register_form"):
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("Nombre *")
        email = st.text_input("Correo electrónico *")
        phone = st.text_input("Teléfono")
        password = st.text_input("Contraseña *", type="password")
    with col2:
        last_name = st.text_input("Apellido *")
        username = st.text_input("Nombre de usuario *")
        address = st.text_area("Dirección")
        password2 = st.text_input("Confirmar contraseña *", type="password")

    submitted = st.form_submit_button("Crear Cuenta", use_container_width=True)

    if submitted:
        if not all([first_name, last_name, email, username, password, password2]):
            st.error("Por favor completa todos los campos obligatorios (*).")
        elif password != password2:
            st.error("Las contraseñas no coinciden.")
        else:
            payload = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "username": username,
                "phone": phone,
                "address": address,
                "password": password,
                "password2": password2,
            }
            with st.spinner("Creando cuenta..."):
                data, error = api_post("/users/auth/register/", payload)
            if error:
                if isinstance(error, dict):
                    for field, msgs in error.items():
                        st.error(f"{field}: {msgs}")
                else:
                    st.error(f"Error: {error}")
            else:
                st.success("¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.")
                st.page_link("pages/1_Login.py", label="🔐 Ir al Login")

st.markdown("---")
st.markdown("¿Ya tienes cuenta?")
st.page_link("pages/1_Login.py", label="🔐 Iniciar Sesión")
