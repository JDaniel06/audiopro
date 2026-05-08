"""
Audio Store Pro - Aplicación principal Streamlit
"""
import streamlit as st

st.set_page_config(
    page_title="Audio Store Pro",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializar session_state
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

from utils.auth import is_logged_in, is_admin, logout

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🎵 Audio Store Pro")
    st.markdown("---")

    if is_logged_in():
        user = st.session_state.get("user", {})
        st.success(f"👤 {user.get('first_name', 'Usuario')}")
        if is_admin():
            st.caption("🔑 Administrador")
        st.markdown("---")

        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()
    else:
        st.info("Inicia sesión para continuar")

# ── Página principal ──────────────────────────────────────────────────────────
st.title("🎵 Audio Store Pro")
st.subheader("Equipos de Audio Profesional")

st.markdown("""
Bienvenido a **Audio Store Pro**, tu tienda de equipos de audio profesional.

### Navega usando el menú de la izquierda:
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("🎛️ **Catálogo**\nExplora nuestros equipos de audio profesional")

with col2:
    st.info("🛒 **Carrito**\nGestiona tus productos seleccionados")

with col3:
    st.info("📦 **Mis Pedidos**\nRevisa el estado de tus pedidos")

if not is_logged_in():
    st.markdown("---")
    st.markdown("### ¿Nuevo aquí? Regístrate o inicia sesión")
    col_a, col_b = st.columns(2)
    with col_a:
        st.page_link("pages/1_Login.py", label="🔐 Iniciar Sesión", use_container_width=True)
    with col_b:
        st.page_link("pages/2_Registro.py", label="📝 Registrarse", use_container_width=True)
