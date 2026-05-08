"""
Vista de pedidos del cliente.
"""
import streamlit as st
from utils.api import api_get
from utils.auth import require_login

st.set_page_config(page_title="Mis Pedidos - Audio Store Pro", page_icon="📦")
require_login()

st.title("📦 Mis Pedidos")

data, error = api_get("/orders/orders/")
if error:
    st.error(error)
    st.stop()

orders = data.get("results", data) if isinstance(data, dict) else data

if not orders:
    st.info("Aún no tienes pedidos.")
    st.page_link("pages/3_Catalogo.py", label="🎛️ Ir al catálogo")
    st.stop()

STATUS_COLORS = {
    "pending": "🟡",
    "payment_review": "🔵",
    "paid": "🟢",
    "processing": "🟢",
    "shipped": "🟢",
    "delivered": "✅",
    "cancelled": "🔴",
}

for order in orders:
    icon = STATUS_COLORS.get(order["status"], "⚪")
    with st.expander(f"{icon} Pedido #{order['order_number']} — {order['status_display']} — ${float(order['total']):,.2f}"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Fecha:** {order['created_at'][:10]}")
            st.markdown(f"**Estado:** {order['status_display']}")
            st.markdown(f"**Total:** ${float(order['total']):,.2f}")
        with col2:
            if order.get("shipping_address"):
                st.markdown(f"**Dirección:** {order['shipping_address']}")
            if order.get("notes"):
                st.markdown(f"**Notas:** {order['notes']}")

        st.markdown("**Productos:**")
        for item in order.get("items", []):
            st.markdown(f"- {item['product_name']} x{item['quantity']} — ${float(item['subtotal']):,.2f}")

        # Ver estado del pago
        payment_data, _ = api_get(f"/payments/?order={order['id']}")
        if payment_data:
            payments = payment_data.get("results", payment_data) if isinstance(payment_data, dict) else payment_data
            if payments:
                p = payments[0]
                st.markdown("---")
                st.markdown(f"**Pago:** {p.get('method_display')} — {p.get('status_display')}")
                if p.get("reference"):
                    st.markdown(f"**Referencia:** {p['reference']}")
                if p.get("admin_notes"):
                    st.info(f"Nota del admin: {p['admin_notes']}")
