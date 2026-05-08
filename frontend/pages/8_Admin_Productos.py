"""
Gestión de productos (solo administrador).
"""
import streamlit as st
from utils.api import api_get, api_post, api_put, api_patch, api_delete
from utils.auth import require_admin

st.set_page_config(page_title="Admin Productos - Audio Store Pro", page_icon="🎛️", layout="wide")
require_admin()

st.title("🎛️ Gestión de Productos")

tab1, tab2 = st.tabs(["📋 Listado", "➕ Nuevo Producto"])

# ── Tab 1: Listado ────────────────────────────────────────────────────────────
with tab1:
    col_search, col_filter = st.columns([2, 1])
    with col_search:
        search = st.text_input("Buscar", placeholder="Nombre, marca...")
    with col_filter:
        status_filter = st.selectbox("Estado", ["Todos", "active", "inactive", "out_of_stock"])

    params = {}
    if search:
        params["search"] = search
    if status_filter != "Todos":
        params["status"] = status_filter

    data, error = api_get("/products/", params=params)
    if error:
        st.error(error)
        st.stop()

    products = data.get("results", data) if isinstance(data, dict) else data

    for p in products:
        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 2])
            with c1:
                st.markdown(f"**{p['name']}** — {p['brand']}")
                st.caption(f"Categoría: {p.get('category_name', 'N/A')}")
            with c2:
                st.markdown(f"${float(p['price']):,.2f}")
            with c3:
                st.markdown(f"Stock: **{p['stock']}**")
            with c4:
                status_icon = {"active": "🟢", "inactive": "🔴", "out_of_stock": "🟡"}.get(p["status"], "⚪")
                st.markdown(f"{status_icon} {p['status']}")
            with c5:
                btn1, btn2, btn3 = st.columns(3)
                with btn1:
                    if st.button("✏️", key=f"edit_{p['id']}", help="Editar"):
                        st.session_state["edit_product_id"] = p["id"]
                        st.rerun()
                with btn2:
                    toggle_label = "🔴" if p["status"] == "active" else "🟢"
                    if st.button(toggle_label, key=f"tog_{p['id']}", help="Activar/Desactivar"):
                        api_post(f"/products/{p['id']}/toggle_status/", {})
                        st.rerun()
                with btn3:
                    qty = st.number_input("", min_value=1, value=1, key=f"stk_{p['id']}", label_visibility="collapsed")
                    if st.button("📦+", key=f"addstk_{p['id']}", help="Agregar stock"):
                        api_post(f"/products/{p['id']}/add_stock/", {"quantity": qty})
                        st.success(f"Stock actualizado para {p['name']}")
                        st.rerun()

# ── Tab 2: Nuevo Producto ─────────────────────────────────────────────────────
with tab2:
    edit_id = st.session_state.get("edit_product_id")
    edit_data = {}
    if edit_id:
        edit_data, _ = api_get(f"/products/{edit_id}/")
        st.info(f"Editando: **{edit_data.get('name', '')}**")
        if st.button("✖ Cancelar edición"):
            st.session_state.pop("edit_product_id", None)
            st.rerun()

    cats, _ = api_get("/products/categories/")
    cat_list = cats.get("results", cats) if isinstance(cats, dict) else (cats or [])
    cat_map = {c["name"]: c["id"] for c in cat_list}

    with st.form("product_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nombre *", value=edit_data.get("name", ""))
            brand = st.text_input("Marca *", value=edit_data.get("brand", ""))
            model_number = st.text_input("Modelo", value=edit_data.get("model_number", ""))
            price = st.number_input("Precio ($) *", min_value=0.01, value=float(edit_data.get("price", 0.01)))
            stock = st.number_input("Stock inicial", min_value=0, value=int(edit_data.get("stock", 0)))
        with col2:
            slug = st.text_input("Slug *", value=edit_data.get("slug", ""), help="URL amigable, ej: mixer-yamaha-mg10")
            cat_names = list(cat_map.keys())
            current_cat = edit_data.get("category", {})
            current_cat_name = current_cat.get("name", "") if isinstance(current_cat, dict) else ""
            default_idx = cat_names.index(current_cat_name) if current_cat_name in cat_names else 0
            selected_cat = st.selectbox("Categoría *", cat_names, index=default_idx) if cat_names else st.text_input("Categoría ID")
            status_opt = st.selectbox("Estado", ["active", "inactive"], index=0 if edit_data.get("status", "active") == "active" else 1)
            featured = st.checkbox("Producto destacado", value=edit_data.get("featured", False))

        description = st.text_area("Descripción *", value=edit_data.get("description", ""))
        image_file = st.file_uploader("Imagen del producto", type=["jpg", "jpeg", "png"])

        submitted = st.form_submit_button("💾 Guardar Producto", use_container_width=True, type="primary")

        if submitted:
            if not all([name, brand, slug, description]):
                st.error("Completa los campos obligatorios (*).")
            else:
                payload = {
                    "name": name, "slug": slug, "brand": brand,
                    "model_number": model_number, "description": description,
                    "price": str(price), "stock": stock,
                    "status": status_opt, "featured": featured,
                    "category_id": cat_map.get(selected_cat, 1) if cat_names else 1,
                }
                files = None
                if image_file:
                    files = {"image": (image_file.name, image_file.getvalue(), image_file.type)}

                with st.spinner("Guardando..."):
                    if edit_id:
                        result, err = api_put(f"/products/{edit_id}/", payload)
                    else:
                        result, err = api_post("/products/", data=payload, files=files, json_data=(files is None))

                if err:
                    st.error(f"Error: {err}")
                else:
                    st.success("✅ Producto guardado correctamente.")
                    st.session_state.pop("edit_product_id", None)
                    st.rerun()
