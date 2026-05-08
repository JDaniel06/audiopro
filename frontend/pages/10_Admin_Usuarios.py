"""
Gestión de usuarios (solo administrador).
"""
import streamlit as st
from utils.api import api_get, api_post
from utils.auth import require_admin

st.set_page_config(page_title="Admin Usuarios - Audio Store Pro", page_icon="👥", layout="wide")
require_admin()

st.title("👥 Gestión de Usuarios")

col1, col2 = st.columns(2)
with col1:
    search = st.text_input("Buscar por email o nombre")
with col2:
    role_filter = st.selectbox("Rol", ["Todos", "client", "admin"])

params = {}
if search:
    params["search"] = search
if role_filter != "Todos":
    params["role"] = role_filter

data, error = api_get("/users/admin/users/", params=params)
if error:
    st.error(error)
    st.stop()

users = data.get("results", data) if isinstance(data, dict) else data

st.caption(f"{len(users)} usuario(s) encontrado(s)")

for u in users:
    active_icon = "🟢" if u["is_active"] else "🔴"
    role_icon = "🔑" if u["role"] == "admin" else "👤"
    with st.expander(f"{active_icon} {role_icon} {u['first_name']} {u['last_name']} — {u['email']}"):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown(f"**Email:** {u['email']}")
            st.markdown(f"**Usuario:** {u['username']}")
            st.markdown(f"**Teléfono:** {u.get('phone', 'N/A')}")
        with col_b:
            st.markdown(f"**Rol:** {u['role']}")
            st.markdown(f"**Estado:** {'Activo' if u['is_active'] else 'Inactivo'}")
            st.markdown(f"**Pedidos:** {u.get('total_orders', 0)}")
            st.markdown(f"**Registrado:** {u['created_at'][:10]}")
        with col_c:
            if u["is_active"]:
                if st.button(f"🔴 Desactivar", key=f"deact_{u['id']}"):
                    result, err = api_post(f"/users/admin/users/{u['id']}/toggle_active/", {})
                    if err:
                        st.error(f"Error: {err}")
                    else:
                        st.warning("Usuario desactivado.")
                        st.rerun()
            else:
                if st.button(f"🟢 Activar", key=f"act_{u['id']}"):
                    result, err = api_post(f"/users/admin/users/{u['id']}/toggle_active/", {})
                    if err:
                        st.error(f"Error: {err}")
                    else:
                        st.success("Usuario activado.")
                        st.rerun()
            if u.get("address"):
                st.markdown(f"**Dirección:** {u['address']}")
