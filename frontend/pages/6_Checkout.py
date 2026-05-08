"""
Página de checkout y registro de pago.
"""
import streamlit as st
from utils.api import api_get, api_post
from utils.auth import require_login

st.set_page_config(page_title="Checkout - Audio Store Pro", page_icon="💳", layout="wide")
require_login()

st.title("💳 Finalizar Pedido")

user = st.session_state.get("user", {})

# ── Paso 1: Confirmar pedido ──────────────────────────────────────────────────
st.markdown("### Paso 1: Confirmar Pedido")

cart, error = api_get("/orders/cart/")
if error or not cart.get("items"):
    st.warning("Tu carrito está vacío.")
    st.page_link("pages/3_Catalogo.py", label="← Ir al catálogo")
    st.stop()

# Mostrar resumen
with st.expander("📋 Ver resumen del carrito", expanded=True):
    for item in cart["items"]:
        p = item.get("product_detail", {})
        st.markdown(f"- **{p.get('name')}** x{item['quantity']} — ${float(item['subtotal']):,.2f}")
    st.markdown(f"**Total: ${float(cart['total']):,.2f}**")

with st.form("checkout_form"):
    st.markdown("### Datos de Envío")
    shipping_address = st.text_area(
        "Dirección de envío",
        value=user.get("address", ""),
        placeholder="Calle, Ciudad, Estado, País"
    )
    notes = st.text_area("Notas adicionales (opcional)", placeholder="Instrucciones especiales...")

    confirm = st.form_submit_button("📦 Confirmar Pedido", use_container_width=True, type="primary")

    if confirm:
        with st.spinner("Procesando pedido..."):
            result, err = api_post("/orders/orders/checkout/", {
                "shipping_address": shipping_address,
                "notes": notes
            })
        if err:
            if isinstance(err, dict):
                for k, v in err.items():
                    st.error(f"{k}: {v}")
            else:
                st.error(f"Error: {err}")
        else:
            st.session_state["current_order"] = result
            st.success(f"✅ Pedido #{result['order_number']} creado exitosamente.")
            st.rerun()

# ── Paso 2: Registrar pago ────────────────────────────────────────────────────
order = st.session_state.get("current_order")
if order:
    st.markdown("---")
    st.markdown("### Paso 2: Registrar Comprobante de Pago")
    st.info(f"Pedido **#{order['order_number']}** — Total: **${float(order['total']):,.2f}**")

    with st.form("payment_form"):
        method = st.selectbox("Método de pago", [
            ("transfer", "Transferencia Bancaria"),
            ("mobile_pay", "Pago Móvil"),
            ("cash", "Efectivo"),
            ("other", "Otro"),
        ], format_func=lambda x: x[1])

        amount = st.number_input("Monto pagado ($)", min_value=0.01, value=float(order["total"]))
        reference = st.text_input("Número de referencia / confirmación")
        voucher_file = st.file_uploader("Adjuntar comprobante (imagen o PDF)", type=["jpg", "jpeg", "png", "pdf"])

        pay_submit = st.form_submit_button("📤 Enviar Comprobante", use_container_width=True, type="primary")

        if pay_submit:
            files = None
            if voucher_file:
                files = {"voucher": (voucher_file.name, voucher_file.getvalue(), voucher_file.type)}

            payload = {
                "order": order["id"],
                "method": method[0],
                "amount": str(amount),
                "reference": reference,
            }

            with st.spinner("Enviando comprobante..."):
                result, err = api_post("/payments/", data=payload, files=files, json_data=False)

            if err:
                st.error(f"Error al registrar pago: {err}")
            else:
                st.success("✅ Comprobante enviado. El administrador revisará tu pago.")
                st.session_state.pop("current_order", None)
                st.balloons()
