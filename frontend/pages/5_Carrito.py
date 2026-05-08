"""
Vista del carrito de compras.
"""
import streamlit as st
from utils.api import api_get, api_post, api_put, api_delete
from utils.auth import require_login

st.set_page_config(page_title="Carrito - Audio Store Pro", page_icon="🛒", layout="wide")
require_login()

st.title("🛒 Mi Carrito")

# ── Cargar carrito ────────────────────────────────────────────────────────────
cart, error = api_get("/orders/cart/")

if error:
    st.error(error)
    st.stop()

items = cart.get("items", [])

if not items:
    st.info("Tu carrito está vacío.")
    st.page_link("pages/3_Catalogo.py", label="🎛️ Ir al catálogo")
    st.stop()

# ── Tabla de ítems ────────────────────────────────────────────────────────────
st.markdown(f"**{len(items)} producto(s) en tu carrito**")

for item in items:
    product = item.get("product_detail", {})
    with st.container(border=True):
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

        with col1:
            st.markdown(f"**{product.get('name', 'Producto')}**")
            st.caption(f"{product.get('brand', '')} | ${float(product.get('price', 0)):,.2f} c/u")

        with col2:
            new_qty = st.number_input(
                "Cant.", min_value=1, max_value=product.get("stock", 99),
                value=item["quantity"], key=f"qty_{item['id']}"
            )

        with col3:
            if st.button("✏️ Actualizar", key=f"upd_{item['id']}"):
                result, err = api_put(f"/orders/cart/items/{item['id']}/", {"quantity": new_qty})
                if err:
                    st.error("Error al actualizar.")
                else:
                    st.rerun()

        with col4:
            st.markdown(f"**${float(item['subtotal']):,.2f}**")

        with col5:
            if st.button("🗑️", key=f"del_{item['id']}"):
                ok, err = api_delete(f"/orders/cart/items/{item['id']}/")
                if ok:
                    st.rerun()
                else:
                    st.error("Error al eliminar.")

# ── Resumen ───────────────────────────────────────────────────────────────────
st.markdown("---")
col_empty, col_total = st.columns([2, 1])

with col_total:
    with st.container(border=True):
        st.markdown("### Resumen del Pedido")
        st.markdown(f"**Subtotal:** ${float(cart.get('total', 0)):,.2f}")
        st.markdown(f"**Total:** ${float(cart.get('total', 0)):,.2f}")

        if st.button("✅ Proceder al Pago", use_container_width=True, type="primary"):
            st.session_state["checkout_ready"] = True
            st.switch_page("pages/6_Checkout.py")

with col_empty:
    if st.button("🗑️ Vaciar carrito"):
        ok, err = api_delete("/orders/cart/items/clear/")
        if ok:
            st.rerun()
