"""
Catálogo de productos de audio profesional.
"""
import streamlit as st
from utils.api import api_get, api_post
from utils.auth import is_logged_in

st.set_page_config(page_title="Catálogo - Audio Store Pro", page_icon="🎛️", layout="wide")

st.title("🎛️ Catálogo de Productos")

# ── Filtros ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Filtros")

    categories, _ = api_get("/products/categories/")
    cat_options = {"Todas": None}
    if categories and "results" in categories:
        for c in categories["results"]:
            cat_options[c["name"]] = c["id"]
    elif categories and isinstance(categories, list):
        for c in categories:
            cat_options[c["name"]] = c["id"]

    selected_cat = st.selectbox("Categoría", list(cat_options.keys()))
    search_term = st.text_input("Buscar producto", placeholder="Nombre, marca...")
    min_price = st.number_input("Precio mínimo ($)", min_value=0.0, value=0.0, step=10.0)
    max_price = st.number_input("Precio máximo ($)", min_value=0.0, value=0.0, step=10.0,
                                 help="0 = sin límite")
    sort_by = st.selectbox("Ordenar por", ["Más recientes", "Precio: menor a mayor", "Precio: mayor a menor", "Nombre"])

    sort_map = {
        "Más recientes": "-created_at",
        "Precio: menor a mayor": "price",
        "Precio: mayor a menor": "-price",
        "Nombre": "name",
    }

# ── Construir parámetros ──────────────────────────────────────────────────────
params = {"ordering": sort_map[sort_by]}
if cat_options[selected_cat]:
    params["category"] = cat_options[selected_cat]
if search_term:
    params["search"] = search_term
if min_price > 0:
    params["min_price"] = min_price
if max_price > 0:
    params["max_price"] = max_price

# ── Cargar productos ──────────────────────────────────────────────────────────
data, error = api_get("/products/", params=params)

if error:
    st.error(error)
    st.stop()

products = data.get("results", data) if isinstance(data, dict) else data

if not products:
    st.info("No se encontraron productos con los filtros seleccionados.")
    st.stop()

st.caption(f"Mostrando {len(products)} producto(s)")

# ── Grid de productos ─────────────────────────────────────────────────────────
cols = st.columns(3)
for i, product in enumerate(products):
    with cols[i % 3]:
        with st.container(border=True):
            # Imagen placeholder si no hay imagen
            if product.get("image_url"):
                st.image(product["image_url"], use_container_width=True)
            else:
                st.markdown("🎵")

            st.subheader(product["name"])
            st.caption(f"**{product['brand']}** | {product.get('category_name', '')}")
            st.markdown(f"### ${float(product['price']):,.2f}")

            stock = product.get("stock", 0)
            if stock > 0:
                st.success(f"✅ En stock ({stock} unidades)")
            else:
                st.error("❌ Sin stock")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Ver detalle", key=f"detail_{product['id']}", use_container_width=True):
                    st.session_state["selected_product_id"] = product["id"]
                    st.switch_page("pages/4_Detalle_Producto.py")

            with col_b:
                if is_logged_in() and stock > 0:
                    if st.button("🛒 Agregar", key=f"add_{product['id']}", use_container_width=True):
                        result, err = api_post("/orders/cart/items/", {
                            "product_id": product["id"],
                            "quantity": 1
                        })
                        if err:
                            st.error("Error al agregar al carrito.")
                        else:
                            st.success("¡Agregado al carrito!")
                elif not is_logged_in():
                    st.caption("Inicia sesión para comprar")
