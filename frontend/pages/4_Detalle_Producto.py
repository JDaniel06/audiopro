"""
Vista de detalle de un producto.
"""
import streamlit as st
from utils.api import api_get, api_post
from utils.auth import is_logged_in

st.set_page_config(page_title="Detalle de Producto - Audio Store Pro", page_icon="🎵", layout="wide")

product_id = st.session_state.get("selected_product_id")

if not product_id:
    st.warning("No se seleccionó ningún producto.")
    st.page_link("pages/3_Catalogo.py", label="← Volver al catálogo")
    st.stop()

data, error = api_get(f"/products/{product_id}/")

if error:
    st.error(error)
    st.page_link("pages/3_Catalogo.py", label="← Volver al catálogo")
    st.stop()

product = data

# ── Breadcrumb ────────────────────────────────────────────────────────────────
st.page_link("pages/3_Catalogo.py", label="← Volver al catálogo")
st.markdown("---")

# ── Detalle ───────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 2])

with col1:
    if product.get("image_url"):
        st.image(product["image_url"], use_container_width=True)
    else:
        st.markdown("## 🎵")
        st.caption("Sin imagen disponible")

with col2:
    category = product.get("category", {})
    st.caption(f"Categoría: **{category.get('name', 'N/A') if isinstance(category, dict) else category}**")
    st.title(product["name"])
    st.subheader(f"{product['brand']} - {product.get('model_number', '')}")

    st.markdown(f"## ${float(product['price']):,.2f}")

    stock = product.get("stock", 0)
    if stock > 0:
        st.success(f"✅ Disponible — {stock} unidades en stock")
    else:
        st.error("❌ Producto sin stock")

    st.markdown("---")
    st.markdown("### Descripción")
    st.write(product.get("description", "Sin descripción disponible."))

    # Agregar al carrito
    if is_logged_in() and stock > 0:
        st.markdown("---")
        quantity = st.number_input("Cantidad", min_value=1, max_value=stock, value=1)
        if st.button("🛒 Agregar al Carrito", use_container_width=True, type="primary"):
            result, err = api_post("/orders/cart/items/", {
                "product_id": product["id"],
                "quantity": quantity
            })
            if err:
                st.error(f"Error: {err}")
            else:
                st.success(f"✅ {quantity}x {product['name']} agregado al carrito.")
    elif not is_logged_in():
        st.info("Inicia sesión para agregar al carrito.")
        st.page_link("pages/1_Login.py", label="🔐 Iniciar Sesión")

# ── Especificaciones técnicas ─────────────────────────────────────────────────
specs = product.get("specifications", {})
if specs:
    st.markdown("---")
    st.markdown("### Especificaciones Técnicas")
    spec_cols = st.columns(2)
    items = list(specs.items())
    half = len(items) // 2
    with spec_cols[0]:
        for k, v in items[:half]:
            st.markdown(f"**{k}:** {v}")
    with spec_cols[1]:
        for k, v in items[half:]:
            st.markdown(f"**{k}:** {v}")
