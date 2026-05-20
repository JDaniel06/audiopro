"""
Página de Carrito de Compras - AudioPro
"""
import streamlit as st
from utils.api import api_get, api_post, api_patch, api_delete
from utils.auth import require_auth, get_current_user

st.set_page_config(page_title='Carrito - AudioPro', page_icon='🛒', layout='wide')
require_auth()

st.title('🛒 Mi Carrito de Compras')

cart, error = api_get('/orders/cart/')

if error:
    st.error(f'Error al cargar el carrito: {error}')
    st.stop()

items = cart.get('items', [])

if not items:
    st.info('Tu carrito está vacío.')
    if st.button('🎵 Ver Catálogo', type='primary'):
        st.switch_page('app.py')
    st.stop()

# ── Tabla de ítems ────────────────────────────────────────────────────────────
st.markdown(f"**{len(items)} producto(s) en tu carrito**")

for item in items:
    product = item.get('product', {})
    with st.container(border=True):
        col_img, col_info, col_qty, col_sub, col_del = st.columns([1, 4, 2, 2, 1])

        with col_img:
            img = product.get('image_url')
            if img:
                st.image(img, width=80)
            else:
                st.image('https://via.placeholder.com/80x80?text=AP', width=80)

        with col_info:
            st.markdown(f"**{product.get('brand', '')} {product.get('name', '')}**")
            st.caption(product.get('category_name', ''))
            st.markdown(f"Precio unitario: **${float(product.get('price', 0)):,.2f}**")

        with col_qty:
            new_qty = st.number_input(
                'Cantidad',
                min_value=1,
                max_value=product.get('stock', 99),
                value=item['quantity'],
                key=f"qty_{item['id']}"
            )
            if new_qty != item['quantity']:
                result, err = api_patch(f'/orders/cart/items/{item["id"]}/', {'quantity': new_qty})
                if err:
                    st.error(err)
                else:
                    st.rerun()

        with col_sub:
            st.markdown(f"**Subtotal**")
            st.markdown(f"### ${float(item.get('subtotal', 0)):,.2f}")

        with col_del:
            st.markdown('<br><br>', unsafe_allow_html=True)
            if st.button('🗑️', key=f"del_{item['id']}", help='Eliminar'):
                ok, err = api_delete(f'/orders/cart/items/{item["id"]}/')
                if err:
                    st.error(err)
                else:
                    st.rerun()

st.markdown('---')

# ── Resumen ───────────────────────────────────────────────────────────────────
col_clear, _, col_total = st.columns([2, 3, 2])

with col_clear:
    if st.button('🗑️ Vaciar Carrito', use_container_width=True):
        ok, err = api_post('/orders/cart/items/clear/', {})
        if err:
            st.error(err)
        else:
            st.rerun()

with col_total:
    total = cart.get('total', 0)
    st.markdown(f"### Total: **${float(total):,.2f}**")
    st.caption('(+ IVA 16% al confirmar)')

st.markdown('---')

# ── Checkout ──────────────────────────────────────────────────────────────────
st.subheader('Confirmar Pedido')
user = get_current_user()

with st.form('checkout_form'):
    shipping_address = st.text_area(
        'Dirección de envío',
        value=user.get('address', ''),
        placeholder='Calle, Ciudad, Estado, País'
    )
    notes = st.text_area('Notas adicionales (opcional)', placeholder='Instrucciones especiales...')
    submitted = st.form_submit_button('✅ Confirmar Pedido', use_container_width=True, type='primary')

if submitted:
    with st.spinner('Procesando pedido...'):
        order, err = api_post('/orders/checkout/', {
            'shipping_address': shipping_address,
            'notes': notes
        })
    if err:
        st.error(f'Error al confirmar pedido: {err}')
    else:
        st.success(f'✅ Pedido #{order["order_number"]} creado exitosamente.')
        st.session_state['current_order_id'] = order['id']
        st.info('Ahora puedes proceder al pago.')
        if st.button('💳 Ir a Pagar', type='primary'):
            st.switch_page('pages/4_Pago.py')
