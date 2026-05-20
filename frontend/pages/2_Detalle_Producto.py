"""
Página de Detalle de Producto - AudioPro
"""
import streamlit as st
from utils.api import api_get, api_post
from utils.auth import is_authenticated

st.set_page_config(page_title='Detalle de Producto - AudioPro', page_icon='🎵', layout='wide')

product_id = st.session_state.get('selected_product_id')

if not product_id:
    st.warning('No se seleccionó ningún producto.')
    if st.button('← Volver al catálogo'):
        st.switch_page('app.py')
    st.stop()

product, error = api_get(f'/products/{product_id}/')

if error:
    st.error(f'Error al cargar el producto: {error}')
    st.stop()

# ── Breadcrumb ────────────────────────────────────────────────────────────────
col_back, _ = st.columns([1, 5])
with col_back:
    if st.button('← Catálogo'):
        st.switch_page('app.py')

st.markdown('---')

# ── Detalle ───────────────────────────────────────────────────────────────────
col_img, col_info = st.columns([2, 3])

with col_img:
    img_url = product.get('image_url')
    if img_url:
        st.image(img_url, use_column_width=True)
    else:
        st.image('https://via.placeholder.com/500x400?text=Sin+Imagen', use_column_width=True)

with col_info:
    cat = product.get('category', {})
    st.caption(f"📂 {cat.get('name', '') if isinstance(cat, dict) else cat}")
    st.title(f"{product['brand']} {product['name']}")

    if product.get('model_number'):
        st.caption(f"Modelo: {product['model_number']}")

    st.markdown(f"## ${float(product['price']):,.2f}")

    stock = product.get('stock', 0)
    status_val = product.get('status')
    if status_val == 'active' and stock > 0:
        st.success(f'✅ En stock — {stock} unidades disponibles')
    elif status_val == 'out_of_stock':
        st.error('❌ Sin stock')
    else:
        st.warning('⚠️ No disponible')

    st.markdown('---')
    st.markdown(product.get('description', ''))

    # Especificaciones técnicas
    specs = product.get('specifications', {})
    if specs:
        st.markdown('### 📋 Especificaciones Técnicas')
        for key, val in specs.items():
            st.markdown(f'- **{key}:** {val}')

    st.markdown('---')

    # Agregar al carrito
    if is_authenticated() and stock > 0:
        col_qty, col_btn = st.columns([1, 2])
        with col_qty:
            qty = st.number_input('Cantidad', min_value=1, max_value=stock, value=1)
        with col_btn:
            st.markdown('<br>', unsafe_allow_html=True)
            if st.button('🛒 Agregar al Carrito', use_container_width=True, type='primary'):
                result, err = api_post('/orders/cart/items/', {
                    'product_id': product_id,
                    'quantity': qty
                })
                if err:
                    st.error(f'Error: {err}')
                else:
                    st.success(f'✅ {qty} unidad(es) agregada(s) al carrito.')
    elif not is_authenticated():
        st.info('Inicia sesión para agregar al carrito.')
        if st.button('🔑 Iniciar Sesión', type='primary'):
            st.switch_page('pages/1_Login.py')
