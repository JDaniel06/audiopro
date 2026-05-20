"""
AudioPro - Aplicación principal Streamlit
Punto de entrada: página de inicio / catálogo público
"""
import streamlit as st
from utils.auth import is_authenticated, is_admin, logout, get_current_user
from utils.api import api_get

st.set_page_config(
    page_title='AudioPro - Equipos de Audio Profesional',
    page_icon='🎵',
    layout='wide',
    initial_sidebar_state='expanded',
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image('https://via.placeholder.com/200x60?text=AudioPro', use_column_width=True)
    st.markdown('---')

    if is_authenticated():
        user = get_current_user()
        st.success(f'👤 {user.get("full_name", user.get("email", ""))}')
        if is_admin():
            st.info('🔑 Administrador')
        if st.button('🚪 Cerrar Sesión', use_container_width=True):
            logout()
    else:
        st.info('Inicia sesión para comprar')

    st.markdown('---')
    st.markdown('### 🎵 AudioPro')
    st.markdown('Equipos de audio profesional de las mejores marcas.')

# ── Página principal: Catálogo ────────────────────────────────────────────────
st.title('🎵 AudioPro — Catálogo de Productos')
st.markdown('Equipos de audio profesional: micrófonos, consolas, amplificadores, monitores y más.')

# Filtros
col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
with col1:
    search = st.text_input('🔍 Buscar producto', placeholder='Nombre, marca, modelo...')
with col2:
    cats_data, _ = api_get('/products/categories/')
    categories = [{'id': '', 'name': 'Todas las categorías'}]
    if cats_data:
        categories += cats_data.get('results', cats_data) if isinstance(cats_data, dict) else cats_data
    cat_names = [c['name'] for c in categories]
    cat_sel = st.selectbox('Categoría', cat_names)
    cat_slug = next((c.get('slug', '') for c in categories if c['name'] == cat_sel), '')
with col3:
    min_price = st.number_input('Precio mínimo ($)', min_value=0, value=0)
with col4:
    max_price = st.number_input('Precio máximo ($)', min_value=0, value=0)

# Construir parámetros
params = {}
if search:
    params['search'] = search
if cat_slug:
    params['category'] = cat_slug
if min_price > 0:
    params['min_price'] = min_price
if max_price > 0:
    params['max_price'] = max_price

# Obtener productos
products_data, error = api_get('/products/', params=params)

if error:
    st.error(f'Error al cargar productos: {error}')
elif products_data:
    products = products_data.get('results', products_data) if isinstance(products_data, dict) else products_data
    total = products_data.get('count', len(products)) if isinstance(products_data, dict) else len(products)

    st.markdown(f'**{total} producto(s) encontrado(s)**')
    st.markdown('---')

    if not products:
        st.info('No se encontraron productos con los filtros seleccionados.')
    else:
        # Grid de productos: 3 columnas
        cols = st.columns(3)
        for idx, product in enumerate(products):
            with cols[idx % 3]:
                with st.container(border=True):
                    # Imagen
                    img_url = product.get('image_url')
                    if img_url:
                        st.image(img_url, use_column_width=True)
                    else:
                        st.image('https://via.placeholder.com/300x200?text=Sin+Imagen', use_column_width=True)

                    st.markdown(f"**{product['brand']} {product['name']}**")
                    st.caption(product.get('category_name', ''))
                    st.markdown(f"### ${float(product['price']):,.2f}")

                    if product.get('short_description'):
                        st.caption(product['short_description'][:100] + '...' if len(product.get('short_description', '')) > 100 else product.get('short_description', ''))

                    stock = product.get('stock', 0)
                    if stock > 0:
                        st.success(f'✅ En stock ({stock} unidades)')
                    else:
                        st.error('❌ Sin stock')

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button('Ver detalle', key=f'detail_{product["id"]}', use_container_width=True):
                            st.session_state['selected_product_id'] = product['id']
                            st.switch_page('pages/2_Detalle_Producto.py')
                    with col_b:
                        if is_authenticated() and stock > 0:
                            if st.button('🛒 Agregar', key=f'cart_{product["id"]}', use_container_width=True):
                                from utils.api import api_post
                                result, err = api_post('/orders/cart/items/', {
                                    'product_id': product['id'],
                                    'quantity': 1
                                })
                                if err:
                                    st.error(err)
                                else:
                                    st.success('Agregado al carrito')
                                    st.rerun()
                        elif not is_authenticated():
                            if st.button('🔑 Login', key=f'login_{product["id"]}', use_container_width=True):
                                st.switch_page('pages/1_Login.py')
