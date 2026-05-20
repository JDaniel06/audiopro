"""
Página Admin: Gestión de Usuarios - AudioPro
"""
import streamlit as st
from utils.api import api_get, api_post
from utils.auth import require_admin

st.set_page_config(page_title='Admin Usuarios - AudioPro', page_icon='👥', layout='wide')
require_admin()

st.title('👥 Gestión de Usuarios')

# Filtros
col1, col2, col3 = st.columns([3, 2, 2])
with col1:
    search = st.text_input('🔍 Buscar por nombre o email')
with col2:
    role_filter = st.selectbox('Rol', ['Todos', 'client', 'admin'])
with col3:
    active_filter = st.selectbox('Estado', ['Todos', 'Activos', 'Inactivos'])

params = {}
if search:
    params['search'] = search
if role_filter != 'Todos':
    params['role'] = role_filter
if active_filter == 'Activos':
    params['is_active'] = 'true'
elif active_filter == 'Inactivos':
    params['is_active'] = 'false'

users_data, error = api_get('/users/admin/', params=params)
if error:
    st.error(error)
    st.stop()

users = users_data.get('results', users_data) if isinstance(users_data, dict) else users_data
st.markdown(f'**{len(users)} usuario(s)**')

for user in users:
    active_icon = '🟢' if user['is_active'] else '🔴'
    role_icon = '🔑' if user['role'] == 'admin' else '👤'
    with st.expander(
        f"{active_icon} {role_icon} {user.get('full_name', user['email'])} | {user['email']} | {user.get('total_orders', 0)} pedidos"
    ):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Email:** {user['email']}")
            st.markdown(f"**Usuario:** {user['username']}")
            st.markdown(f"**Rol:** {user['role']}")
            st.markdown(f"**Registrado:** {user['created_at'][:10]}")
        with col2:
            st.markdown(f"**Teléfono:** {user.get('phone', 'N/A')}")
            st.markdown(f"**Ciudad:** {user.get('city', 'N/A')}")
            st.markdown(f"**País:** {user.get('country', 'N/A')}")
        with col3:
            st.markdown(f"**Pedidos:** {user.get('total_orders', 0)}")
            status_label = '🟢 Activo' if user['is_active'] else '🔴 Inactivo'
            st.markdown(f"**Estado:** {status_label}")

        st.markdown('---')
        col_a, col_b = st.columns(2)
        with col_a:
            btn_label = '🔴 Desactivar' if user['is_active'] else '🟢 Activar'
            if st.button(btn_label, key=f'toggle_{user["id"]}', use_container_width=True):
                result, err = api_post(f'/users/admin/{user["id"]}/toggle_active/', {})
                if err:
                    st.error(err)
                else:
                    st.success(result['message'])
                    st.rerun()
        with col_b:
            if st.button('📦 Ver Pedidos', key=f'orders_{user["id"]}', use_container_width=True):
                orders_data, _ = api_get('/orders/', params={'user': user['id']})
                orders = orders_data.get('results', []) if orders_data else []
                if orders:
                    for o in orders:
                        st.caption(f"#{o['order_number']} — {o['status_display']} — ${float(o['total']):,.2f}")
                else:
                    st.info('Sin pedidos.')
