"""
Página Admin: Gestión de Pedidos - AudioPro
"""
import streamlit as st
from utils.api import api_get, api_post
from utils.auth import require_admin

st.set_page_config(page_title='Admin Pedidos - AudioPro', page_icon='📋', layout='wide')
require_admin()

st.title('📋 Gestión de Pedidos')

STATUS_OPTIONS = [
    'pending', 'payment_pending', 'paid',
    'processing', 'shipped', 'delivered', 'cancelled'
]
STATUS_LABELS = {
    'pending': '🟡 Pendiente',
    'payment_pending': '🟠 Pago Pendiente',
    'paid': '🟢 Pagado',
    'processing': '🔵 En Proceso',
    'shipped': '🚚 Enviado',
    'delivered': '✅ Entregado',
    'cancelled': '🔴 Cancelado',
}

# Filtros
col1, col2 = st.columns([3, 2])
with col1:
    search = st.text_input('🔍 Buscar por número de pedido')
with col2:
    status_filter = st.selectbox('Filtrar por estado', ['Todos'] + STATUS_OPTIONS,
                                  format_func=lambda x: STATUS_LABELS.get(x, x) if x != 'Todos' else 'Todos')

params = {}
if search:
    params['search'] = search
if status_filter != 'Todos':
    params['status'] = status_filter

orders_data, error = api_get('/orders/', params=params)
if error:
    st.error(error)
    st.stop()

orders = orders_data.get('results', orders_data) if isinstance(orders_data, dict) else orders_data
st.markdown(f'**{len(orders)} pedido(s)**')

for order in orders:
    label = STATUS_LABELS.get(order['status'], order['status'])
    with st.expander(
        f"{label} | #{order['order_number']} | {order.get('user_name', order.get('user_email', ''))} | ${float(order['total']):,.2f} | {order['created_at'][:10]}"
    ):
        col1, col2, col3 = st.columns(3)
        col1.metric('Subtotal', f"${float(order['subtotal']):,.2f}")
        col2.metric('IVA', f"${float(order['tax']):,.2f}")
        col3.metric('Total', f"${float(order['total']):,.2f}")

        st.caption(f"Cliente: {order.get('user_email', '')} | Dirección: {order.get('shipping_address', 'N/A')}")

        st.markdown('**Productos:**')
        for item in order.get('items', []):
            st.markdown(
                f"- {item['quantity']}x {item['product_brand']} {item['product_name']} "
                f"@ ${float(item['unit_price']):,.2f}"
            )

        st.markdown('---')
        st.subheader('Actualizar Estado')
        col_status, col_notes, col_btn = st.columns([2, 3, 1])
        with col_status:
            new_status = st.selectbox(
                'Nuevo estado',
                STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(order['status']) if order['status'] in STATUS_OPTIONS else 0,
                key=f'status_{order["id"]}',
                format_func=lambda x: STATUS_LABELS.get(x, x)
            )
        with col_notes:
            notes = st.text_input('Notas', key=f'notes_{order["id"]}')
        with col_btn:
            st.markdown('<br>', unsafe_allow_html=True)
            if st.button('💾 Guardar', key=f'save_{order["id"]}', type='primary'):
                result, err = api_post(f'/orders/{order["id"]}/update_status/', {
                    'status': new_status, 'notes': notes
                })
                if err:
                    st.error(err)
                else:
                    st.success('Estado actualizado.')
                    st.rerun()
