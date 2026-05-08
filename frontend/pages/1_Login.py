"""
Página de inicio de sesión.
"""
import streamlit as st
from utils.auth import login, is_logged_in

st.set_page_config(page_title="Iniciar Sesión - Audio Store Pro", page_icon="🔐")

if is_logged_in():
    st.success("Ya tienes sesión iniciada.")
    st.page_link("app.py", label="← Ir al inicio")
    st.stop()

st.title("🔐 Iniciar Sesión")

with st.form("login_form"):
    email = st.text_input("Correo electrónico", placeholder="tu@email.com")
    password = st.text_input("Contraseña", type="password")
    submitted = st.form_submit_button("Ingresar", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Por favor completa todos los campos.")
        else:
            with st.spinner("Autenticando..."):
                if login(email, password):
                    st.success("¡Sesión iniciada correctamente!")
                    st.rerun()

st.markdown("---")
st.markdown("¿No tienes cuenta?")
st.page_link("pages/2_Registro.py", label="📝 Regístrate aquí")
