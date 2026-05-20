"""
Página Admin: Gestión de Productos - AudioPro
"""
import streamlit as st
from utils.api import api_get, api_post, api_patch, api_delete
from utils.auth import require_admin

st.set_page_config(page_title='Admin Productos - AudioPro', page_icon='📦', layout='wide')
require_admin()

st.title('📦 Gestión de Productos')

tab_list, tab_new, tab_cats = st.tabs(['📋 Listado', '➕ Nuevo Producto', '🗂️ Categorías'])

# ── Listado de productos ──────────────────────────────────────────────────────
with tab_list:
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input('🔍 Buscar', placeholder='Nombre, marca...')
    with col2:
        status_filter = st.selectbox('Estado', ['Todos', 'active', 'inactive', 'out_of_stock'])

    params = {}
    if search:
        params['search'] = search
    if status_filter != 'Todos':
        params['status'] = status_filter

    products_data, error = api_get('/products/', params=params)
    if error:
        st.error(error)
    else:
        products = products_data.get('results', products_data) if isinstance(products_data, dict) else products_data

        STATUS_BADGE = {'active': '🟢', 'inactive': '🔴', 'out_of_stock': '🟡'}

        for p in products:
            badge = STATUS_BADGE.get(p['status'], '⚪')
            with st.expander(f"{badge} {p['brand']} {p['name']} — ${float(p['price']):,.2f} | Stock: {p['stock']}"):
                col_a, col_b, col_c, col_d = st.columns(4)

                with col_a:
                    if st.button('✏️ Editar', key=f'edit_{p["id"]}'):
                        st.session_state['edit_product_id'] = p['id']
                        st.rerun()

                with col_b:
                    label = '🔴 Desactivar' if p['status'] == 'active' else '🟢 Activar'
                    if st.button(label, key=f'toggle_{p["id"]}'):
                        result, err = api_post(f'/products/{p["id"]}/toggle_status/', {})
                        if err:
                            st.error(err)
                        else:
                            st.success(f'Estado actualizado: {result["status"]}')
                            st.rerun()

                with col_c:
                    new_stock = st.number_input('Nuevo stock', min_value=0, value=p['stock'], key=f'stock_{p["id"]}')
                    if st.button('💾 Actualizar Stock', key=f'upd_stock_{p["id"]}'):
                        result, err = api_post(f'/products/{p["id"]}/update_stock/', {
                            'quantity': new_stock, 'operation': 'set'
                        })
                        if err:
                            st.error(err)
                        else:
                            st.success(f'Stock actualizado: {result["stock"]}')
                            st.rerun()

                with col_d:
                    if st.button('🗑️ Eliminar', key=f'del_{p["id"]}'):
                        ok, err = api_delete(f'/products/{p["id"]}/')
                        if err:
                            st.error(err)
                        else:
                            st.success('Producto eliminado.')
                            st.rerun()

# ── Nuevo / Editar Producto ───────────────────────────────────────────────────
with tab_new:
    edit_id = st.session_state.get('edit_product_id')
    edit_data = {}
    if edit_id:
        edit_data, _ = api_get(f'/products/{edit_id}/')
        st.info(f'Editando: {edit_data.get("brand", "")} {edit_data.get("name", "")}')
        if st.button('➕ Crear nuevo en su lugar'):
            st.session_state.pop('edit_product_id', None)
            st.rerun()

    cats_data, _ = api_get('/products/categories/')
    cats = cats_data.get('results', cats_data) if isinstance(cats_data, dict) else (cats_data or [])
    cat_map = {c['name']: c['id'] for c in cats}

    with st.form('product_form'):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input('Nombre del producto *', value=edit_data.get('name', ''))
            brand = st.text_input('Marca *', value=edit_data.get('brand', ''))
            model_number = st.text_input('Número de modelo', value=edit_data.get('model_number', ''))
            price = st.number_input('Precio (USD) *', min_value=0.01, value=float(edit_data.get('price', 0.01)), format='%.2f')
            stock = st.number_input('Stock inicial *', min_value=0, value=edit_data.get('stock', 0))
        with col2:
            cat_names = list(cat_map.keys())
            current_cat = edit_data.get('category', {})
            current_cat_name = current_cat.get('name', '') if isinstance(current_cat, dict) else ''
            default_idx = cat_names.index(current_cat_name) if current_cat_name in cat_names else 0
            cat_sel = st.selectbox('Categoría *', cat_names, index=default_idx) if cat_names else st.text_input('Categoría ID')
            slug = st.text_input('Slug (URL) *', value=edit_data.get('slug', ''), placeholder='ej: shure-sm7b')
            status_sel = st.selectbox(
                'Estado',
                ['active', 'inactive'],
                index=0 if edit_data.get('status', 'active') == 'active' else 1
            )
            short_desc = st.text_input('Descripción corta', value=edit_data.get('short_description', ''))

        description = st.text_area('Descripción completa *', value=edit_data.get('description', ''), height=120)
        image = st.file_uploader('Imagen del producto (JPG/PNG)', type=['jpg', 'jpeg', 'png', 'webp'])

        submitted = st.form_submit_button(
            '💾 Guardar Producto' if edit_id else '➕ Crear Producto',
            use_container_width=True, type='primary'
        )

    if submitted:
        if not all([name, brand, slug, description]) or not cat_names:
            st.error('Completa todos los campos obligatorios.')
        else:
            payload = {
                'name': name, 'brand': brand, 'model_number': model_number,
                'slug': slug, 'price': price, 'stock': stock,
                'status': status_sel, 'short_description': short_desc,
                'description': description,
                'category_id': cat_map.get(cat_sel, 1),
            }
            if edit_id:
                result, err = api_patch(f'/products/{edit_id}/', payload)
                msg = 'Producto actualizado.'
            else:
                result, err = api_post('/products/', payload)
                msg = 'Producto creado.'

            if err:
                st.error(f'Error: {err}')
            else:
                st.success(msg)
                st.session_state.pop('edit_product_id', None)
                st.rerun()

# ── Categorías ────────────────────────────────────────────────────────────────
with tab_cats:
    cats_data, _ = api_get('/products/categories/')
    cats = cats_data.get('results', cats_data) if isinstance(cats_data, dict) else (cats_data or [])

    for cat in cats:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{cat['name']}** — {cat.get('product_count', 0)} productos")
        with col2:
            if st.button('🗑️', key=f'del_cat_{cat["id"]}'):
                ok, err = api_delete(f'/products/categories/{cat["id"]}/')
                if err:
                    st.error(err)
                else:
                    st.rerun()

    st.markdown('---')
    st.subheader('Nueva Categoría')
    with st.form('cat_form'):
        cat_name = st.text_input('Nombre de la categoría')
        cat_slug = st.text_input('Slug', placeholder='ej: microfonos')
        cat_desc = st.text_area('Descripción', height=80)
        if st.form_submit_button('➕ Crear Categoría', type='primary'):
            result, err = api_post('/products/categories/', {
                'name': cat_name, 'slug': cat_slug, 'description': cat_desc
            })
            if err:
                st.error(err)
            else:
                st.success('Categoría creada.')
                st.rerun()
