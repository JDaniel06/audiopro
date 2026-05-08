"""
Gestión de pedidos y pagos (solo administrador).
"""
import streamlit as st
from utils.api import api_get, api_post
from utils.auth import require_admin

st.set_page_config(page_title="Admin Pedidos - Audio Store Pro", page_icon="📦", layout="wide")
require_admin()

st.title("📦 Gestión de Pedidos y Pagos")

tab1, tab2 = st.tabs(["📋 Todos los Pedidos", "💳 Pagos Pendientes"])

STATUS_CHOICES = [
    "pending", "payment_review", "paid",
    "processing", "shipped", "delivered", "cancelled"
]
STATUS_LABELS = {
    "pending": "🟡 Pendiente",
    "payment_review": "🔵 Pago en Revisión",
    "paid": "🟢 Pagado",
    "processing": "🟢 En Proceso",
    "shipped": "🚚 Enviado",
    "delivered": "✅ Entregado",
    "cancelled": "🔴 Cancelado",
}

# ── Tab 1: Todos los pedidos ──────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        status_f = st.selectbox("Filtrar por estado", ["Todos"] + STATUS_CHOICES)
    with col2:
        search_f = st.text_input("Buscar por email o número de pedido")

    params = {}
    if status_f != "Todos":
        params["status"] = status_f

    data, error = api_get("/orders/orders/", params=params)
    if error:
        st.error(error)
        st.stop()

    orders = data.get("results", data) if isinstance(data, dict) else data

    if not orders:
        st.info("No hay pedidos.")
    else:
        for order in orders:
            icon = STATUS_LABELS.get(order["status"], "⚪")
            with st.expander(f"{icon} — #{order['order_number']} | {order['user_email']} | ${float(order['total']):,.2f} | {order['created_at'][:10]}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Cliente:** {order['user_name']} ({order['user_email']})")
                    st.markdown(f"**Total:** ${float(order['total']):,.2f}")
                    st.markdown(f"**Dirección:** {order.get('shipping_address', 'N/A')}")
                with col_b:
                    new_status = st.selectbox(
                        "Cambiar estado",
                        STATUS_CHOICES,
                        index=STATUS_CHOICES.index(order["status"]),
                        key=f"status_{order['id']}"
                    )
                    if st.button("💾 Actualizar Estado", key=f"upd_status_{order['id']}"):
                        result, err = api_post(f"/orders/orders/{order['id']}/update_status/", {"status": new_status})
                        if err:
                            st.error(f"Error: {err}")
                        else:
                            st.success("Estado actualizado.")
                            st.rerun()

                st.markdown("**Productos:**")
                for item in order.get("items", []):
                    st.markdown(f"- {item['product_name']} x{item['quantity']} — ${float(item['subtotal']):,.2f}")

# ── Tab 2: Pagos pendientes ───────────────────────────────────────────────────
with tab2:
    payments_data, err = api_get("/payments/pending_review/")
    if err:
        st.error(err)
        st.stop()

    payments = payments_data if isinstance(payments_data, list) else payments_data.get("results", [])

    if not payments:
        st.success("✅ No hay pagos pendientes de revisión.")
    else:
        st.warning(f"⚠️ {len(payments)} pago(s) pendiente(s) de revisión")

        for p in payments:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 2, 2])
                with col1:
                    st.markdown(f"**Pedido:** #{p['order_number']}")
                    st.markdown(f"**Cliente:** {p['user_name']} ({p['user_email']})")
                    st.markdown(f"**Método:** {p['method_display']}")
                    st.markdown(f"**Monto:** ${float(p['amount']):,.2f}")
                    if p.get("reference"):
                        st.markdown(f"**Referencia:** {p['reference']}")
                with col2:
                    if p.get("voucher_url"):
                        st.markdown("**Comprobante:**")
                        if p["voucher_url"].lower().endswith((".jpg", ".jpeg", ".png")):
                            st.image(p["voucher_url"], width=200)
                        else:
                            st.markdown(f"[📄 Ver comprobante]({p['voucher_url']})")
                    else:
                        st.caption("Sin comprobante adjunto")
                with col3:
                    admin_notes = st.text_area("Notas", key=f"notes_{p['id']}", placeholder="Motivo de rechazo, etc.")
                    col_ap, col_re = st.columns(2)
                    with col_ap:
                        if st.button("✅ Aprobar", key=f"approve_{p['id']}", type="primary"):
                            result, error = api_post(f"/payments/{p['id']}/review/", {
                                "status": "approved",
                                "admin_notes": admin_notes
                            })
                            if error:
                                st.error(f"Error: {error}")
                            else:
                                st.success("Pago aprobado.")
                                st.rerun()
                    with col_re:
                        if st.button("❌ Rechazar", key=f"reject_{p['id']}"):
                            result, error = api_post(f"/payments/{p['id']}/review/", {
                                "status": "rejected",
                                "admin_notes": admin_notes
                            })
                            if error:
                                st.error(f"Error: {error}")
                            else:
                                st.warning("Pago rechazado.")
                                st.rerun()
