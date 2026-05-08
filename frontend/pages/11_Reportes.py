"""
Reportes y Dashboard de ventas (solo administrador).
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.api import api_get
from utils.auth import require_admin

st.set_page_config(page_title="Reportes - Audio Store Pro", page_icon="📊", layout="wide")
require_admin()

st.title("📊 Reportes y Dashboard")

tab1, tab2, tab3 = st.tabs(["📈 Dashboard de Ventas", "👥 Reporte de Clientes", "🧾 Reporte de Ventas"])

# ── Tab 1: Dashboard ──────────────────────────────────────────────────────────
with tab1:
    st.subheader("Dashboard de Ventas")

    sales_data, err = api_get("/orders/orders/sales_report/")
    if err:
        st.error(err)
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Ingresos Totales", f"${float(sales_data.get('total_revenue', 0)):,.2f}")
        with col2:
            st.metric("📦 Total Pedidos", sales_data.get("total_orders", 0))
        with col3:
            total_orders = sales_data.get("total_orders", 1) or 1
            avg = float(sales_data.get("total_revenue", 0)) / total_orders
            st.metric("📊 Ticket Promedio", f"${avg:,.2f}")

        monthly = sales_data.get("monthly_sales", [])
        if monthly:
            df_monthly = pd.DataFrame(monthly)
            df_monthly["month"] = pd.to_datetime(df_monthly["month"])
            df_monthly["month_str"] = df_monthly["month"].dt.strftime("%b %Y")

            col_a, col_b = st.columns(2)
            with col_a:
                fig1 = px.bar(
                    df_monthly, x="month_str", y="total_sales",
                    title="Ventas Mensuales ($)",
                    labels={"month_str": "Mes", "total_sales": "Ventas ($)"},
                    color_discrete_sequence=["#1f77b4"]
                )
                st.plotly_chart(fig1, use_container_width=True)

            with col_b:
                fig2 = px.line(
                    df_monthly, x="month_str", y="order_count",
                    title="Número de Pedidos por Mes",
                    labels={"month_str": "Mes", "order_count": "Pedidos"},
                    markers=True
                )
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Aún no hay datos de ventas suficientes para mostrar gráficas.")

    # Productos más vendidos
    st.markdown("---")
    st.subheader("Productos más vendidos")
    orders_data, _ = api_get("/orders/orders/")
    if orders_data:
        all_orders = orders_data.get("results", orders_data) if isinstance(orders_data, dict) else orders_data
        product_sales = {}
        for order in all_orders:
            for item in order.get("items", []):
                name = item.get("product_name", "Desconocido")
                product_sales[name] = product_sales.get(name, 0) + item.get("quantity", 0)

        if product_sales:
            df_prod = pd.DataFrame(
                list(product_sales.items()), columns=["Producto", "Unidades Vendidas"]
            ).sort_values("Unidades Vendidas", ascending=False).head(10)

            fig3 = px.bar(
                df_prod, x="Unidades Vendidas", y="Producto",
                orientation="h", title="Top 10 Productos más Vendidos",
                color_discrete_sequence=["#2ca02c"]
            )
            st.plotly_chart(fig3, use_container_width=True)

# ── Tab 2: Reporte de Clientes ────────────────────────────────────────────────
with tab2:
    st.subheader("Reporte de Clientes")

    clients_data, err = api_get("/users/admin/users/clients_report/")
    if err:
        st.error(err)
    else:
        clients = clients_data if isinstance(clients_data, list) else clients_data.get("results", [])

        if clients:
            df_clients = pd.DataFrame([{
                "Nombre": f"{c['first_name']} {c['last_name']}",
                "Email": c["email"],
                "Teléfono": c.get("phone", ""),
                "Dirección": c.get("address", ""),
                "Estado": "Activo" if c["is_active"] else "Inactivo",
                "Pedidos": c.get("total_orders", 0),
                "Registrado": c["created_at"][:10],
            } for c in clients])

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Clientes", len(df_clients))
            with col2:
                activos = df_clients[df_clients["Estado"] == "Activo"].shape[0]
                st.metric("Clientes Activos", activos)

            st.dataframe(df_clients, use_container_width=True)

            # Exportar CSV
            csv = df_clients.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Descargar CSV",
                data=csv,
                file_name="reporte_clientes.csv",
                mime="text/csv"
            )
        else:
            st.info("No hay clientes registrados.")

# ── Tab 3: Reporte de Ventas ──────────────────────────────────────────────────
with tab3:
    st.subheader("Reporte de Ventas")

    orders_data, err = api_get("/orders/orders/")
    if err:
        st.error(err)
    else:
        all_orders = orders_data.get("results", orders_data) if isinstance(orders_data, dict) else orders_data

        if all_orders:
            rows = []
            for order in all_orders:
                for item in order.get("items", []):
                    rows.append({
                        "Pedido": order["order_number"],
                        "Fecha": order["created_at"][:10],
                        "Cliente": order["user_email"],
                        "Producto": item.get("product_name", ""),
                        "Marca": item.get("product_brand", ""),
                        "Cantidad": item.get("quantity", 0),
                        "Precio Unitario": float(item.get("unit_price", 0)),
                        "Subtotal": float(item.get("subtotal", 0)),
                        "Estado Pedido": order["status_display"],
                    })

            if rows:
                df_sales = pd.DataFrame(rows)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Pedidos", len(all_orders))
                with col2:
                    st.metric("Total Ítems Vendidos", df_sales["Cantidad"].sum())
                with col3:
                    st.metric("Ingresos Totales", f"${df_sales['Subtotal'].sum():,.2f}")

                st.dataframe(df_sales, use_container_width=True)

                csv = df_sales.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Descargar CSV",
                    data=csv,
                    file_name="reporte_ventas.csv",
                    mime="text/csv"
                )
        else:
            st.info("No hay ventas registradas.")
