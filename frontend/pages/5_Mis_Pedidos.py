"""
Página de Mis Pedidos - AudioPro
"""
import streamlit as st
from utils.api import api_get
from utils.auth import require_auth

st.set_page_config(page_title='Mis Pedidos - AudioPro', page_icon='📦', layout='wide')
require_auth()

st.title('📦 Mis Pedidos')

STATUS_COLORS = {
    'pending': '🟡',
    'payment_pending': '🟠',
    'paid': '🟢',
    'processing': '🔵',
    'shipped': '🚚',
    'delivered': '✅',
    'cancelled': '🔴',
}

orders_data, error = api_get('/orders/')
if error:
    st.error(f'Error: {error}')
    st.stop()

orders = orders_data.get('results', orders_data) if isinstance(orders_data, dict) else orders_data

if not orders:
    st.info('No tienes pedidos aún.')
    if st.button('🎵 Ver Catálogo', type='primary'):
        st.switch_page('app.py')
    st.stop()

for order in orders:
    icon = STATUS_COLORS.get(order['status'], '⚪')
    with st.expander(
        f"{icon} Pedido #{order['order_number']} — {order['status_display']} — ${float(order['total']):,.2f}",
        expanded=False
    ):
        col1, col2, col3 = st.columns(3)
        col1.metric('Subtotal', f"${float(order['subtotal']):,.2f}")
        col2.metric('IVA', f"${float(order['tax']):,.2f}")
        col3.metric('Total', f"${float(order['total']):,.2f}")

        st.caption(f"Fecha: {order['created_at'][:10]}")
        if order.get('shipping_address'):
            st.caption(f"Dirección: {order['shipping_address']}")

        st.markdown('**Productos:**')
        for item in order.get('items', []):
            st.markdown(
                f"- {item['quantity']}x **{item['product_brand']} {item['product_name']}** "
                f"@ ${float(item['unit_price']):,.2f} = ${float(item['subtotal']):,.2f}"
            )

        if order['status'] == 'payment_pending':
            if st.button(f"💳 Pagar ahora", key=f"pay_{order['id']}", type='primary'):
                st.session_state['current_order_id'] = order['id']
                st.switch_page('pages/4_Pago.py')
