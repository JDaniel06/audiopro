"""
Página de Login y Registro - AudioPro
"""
import streamlit as st
from utils.auth import login, is_authenticated
from utils.api import api_post

st.set_page_config(page_title='Login - AudioPro', page_icon='🔑', layout='centered')

if is_authenticated():
    st.success('Ya tienes sesión iniciada.')
    if st.button('Ir al catálogo'):
        st.switch_page('app.py')
    st.stop()

st.title('🔑 Acceso a AudioPro')

tab_login, tab_register = st.tabs(['Iniciar Sesión', 'Registrarse'])

# ── Login ─────────────────────────────────────────────────────────────────────
with tab_login:
    st.subheader('Iniciar Sesión')
    with st.form('login_form'):
        email = st.text_input('Correo electrónico', placeholder='tu@email.com')
        password = st.text_input('Contraseña', type='password')
        submitted = st.form_submit_button('Ingresar', use_container_width=True, type='primary')

    if submitted:
        if not email or not password:
            st.error('Completa todos los campos.')
        else:
            with st.spinner('Verificando credenciales...'):
                if login(email, password):
                    st.success('¡Bienvenido!')
                    st.switch_page('app.py')

# ── Registro ──────────────────────────────────────────────────────────────────
with tab_register:
    st.subheader('Crear Cuenta')
    with st.form('register_form'):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input('Nombre *')
            email_r = st.text_input('Correo electrónico *', placeholder='tu@email.com')
            phone = st.text_input('Teléfono')
            city = st.text_input('Ciudad')
        with col2:
            last_name = st.text_input('Apellido *')
            username = st.text_input('Usuario *', placeholder='sin espacios')
            country = st.text_input('País', value='Venezuela')
            address = st.text_area('Dirección', height=68)

        password_r = st.text_input('Contraseña *', type='password', key='reg_pass')
        password2 = st.text_input('Confirmar contraseña *', type='password', key='reg_pass2')
        submitted_r = st.form_submit_button('Crear Cuenta', use_container_width=True, type='primary')

    if submitted_r:
        required = [first_name, last_name, email_r, username, password_r, password2]
        if not all(required):
            st.error('Completa todos los campos obligatorios (*).')
        elif password_r != password2:
            st.error('Las contraseñas no coinciden.')
        elif len(password_r) < 8:
            st.error('La contraseña debe tener al menos 8 caracteres.')
        else:
            with st.spinner('Creando cuenta...'):
                data, error = api_post('/users/register/', {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email_r,
                    'username': username,
                    'phone': phone,
                    'address': address,
                    'city': city,
                    'country': country,
                    'password': password_r,
                    'password2': password2,
                })
            if error:
                st.error(f'Error al registrarse: {error}')
            else:
                st.success('¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.')
                # Auto-login
                if login(email_r, password_r):
                    st.switch_page('app.py')
