"""
Página de Reportes y Dashboard - AudioPro
Reporte de clientes, ventas y dashboard con gráficas
"""
import streamlit as st
import pandas as pd
from utils.api import api_get
from utils.auth import require_admin

st.set_page_config(page_title='Reportes - AudioPro', page_icon='📊', layout='wide')
require_admin()

st.title('📊 Reportes y Dashboard')

tab_dash, tab_clients, tab_sales = st.tabs(['📈 Dashboard', '👥 Clientes', '💰 Ventas'])

# ── Dashboard ─────────────────────────────────────────────────────────────────
with tab_dash:
    st.subheader('Resumen General')

    # KPIs
    user_stats, _ = api_get('/users/admin/stats/')
    order_stats, _ = api_get('/orders/stats/')
    payment_stats, _ = api_get('/payments/stats/')
    product_stats, _ = api_get('/products/stats/')

    col1, col2, col3, col4 = st.columns(4)
    if user_stats:
        col1.metric('👥 Clientes Totales', user_stats.get('total_clients', 0))
        col2.metric('🆕 Nuevos (30 días)', user_stats.get('new_last_30_days', 0))
    if order_stats:
        col3.metric('📦 Pedidos Totales', order_stats.get('total_orders', 0))
        col4.metric('💵 Ingresos Totales', f"${order_stats.get('total_revenue', 0):,.2f}")

    st.markdown('---')
    col5, col6, col7, col8 = st.columns(4)
    if order_stats:
        col5.metric('📦 Pedidos (30 días)', order_stats.get('orders_last_30_days', 0))
        col6.metric('💵 Ingresos (30 días)', f"${order_stats.get('revenue_last_30_days', 0):,.2f}")
    if payment_stats:
        col7.metric('✅ Pagos Aprobados', payment_stats.get('approved', 0))
        col8.metric('🔍 Pagos en Revisión', payment_stats.get('pending_review', 0))

    st.markdown('---')

    # Gráfica de ventas por mes
    st.subheader('📈 Ventas por Mes')
    sales_data, _ = api_get('/orders/sales_by_month/')
    if sales_data and len(sales_data) > 0:
        df_sales = pd.DataFrame(sales_data)
        if 'month' in df_sales.columns:
            df_sales['month'] = pd.to_datetime(df_sales['month']).dt.strftime('%Y-%m')
            df_sales = df_sales.rename(columns={'month': 'Mes', 'total': 'Ingresos ($)'})
            st.bar_chart(df_sales.set_index('Mes')['Ingresos ($)'])
    else:
        st.info('No hay datos de ventas por mes aún.')

    # Top productos
    st.subheader('🏆 Top 10 Productos Más Vendidos')
    top_data, _ = api_get('/orders/top_products/')
    if top_data and len(top_data) > 0:
        df_top = pd.DataFrame(top_data)
        df_top = df_top.rename(columns={
            'product__name': 'Producto',
            'product__brand': 'Marca',
            'total_sold': 'Unidades Vendidas',
            'total_revenue': 'Ingresos ($)'
        })
        cols_show = [c for c in ['Marca', 'Producto', 'Unidades Vendidas', 'Ingresos ($)'] if c in df_top.columns]
        st.dataframe(df_top[cols_show], use_container_width=True)
    else:
        st.info('No hay datos de productos vendidos aún.')

    # Estado de pedidos
    st.subheader('📊 Pedidos por Estado')
    if order_stats and order_stats.get('by_status'):
        STATUS_LABELS = {
            'pending': 'Pendiente', 'payment_pending': 'Pago Pendiente',
            'paid': 'Pagado', 'processing': 'En Proceso',
            'shipped': 'Enviado', 'delivered': 'Entregado', 'cancelled': 'Cancelado'
        }
        df_status = pd.DataFrame(order_stats['by_status'])
        if not df_status.empty:
            df_status['status'] = df_status['status'].map(STATUS_LABELS).fillna(df_status['status'])
            df_status = df_status.rename(columns={'status': 'Estado', 'count': 'Cantidad'})
            st.bar_chart(df_status.set_index('Estado')['Cantidad'])

    # Estado de productos
    if product_stats:
        st.subheader('📦 Estado del Inventario')
        col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
        col_p1.metric('Total', product_stats.get('total', 0))
        col_p2.metric('🟢 Activos', product_stats.get('active', 0))
        col_p3.metric('🔴 Inactivos', product_stats.get('inactive', 0))
        col_p4.metric('🟡 Sin Stock', product_stats.get('out_of_stock', 0))
        col_p5.metric('⚠️ Stock Bajo', product_stats.get('low_stock', 0))

# ── Reporte de Clientes ───────────────────────────────────────────────────────
with tab_clients:
    st.subheader('👥 Reporte de Clientes')

    col1, col2 = st.columns([3, 1])
    with col1:
        search_c = st.text_input('🔍 Buscar cliente', key='search_clients')
    with col2:
        active_c = st.selectbox('Estado', ['Todos', 'Activos', 'Inactivos'], key='active_clients')

    params_c = {'role': 'client'}
    if search_c:
        params_c['search'] = search_c
    if active_c == 'Activos':
        params_c['is_active'] = 'true'
    elif active_c == 'Inactivos':
        params_c['is_active'] = 'false'

    clients_data, err = api_get('/users/admin/clients/', params=params_c)
    if err:
        st.error(err)
    elif clients_data:
        clients = clients_data.get('results', clients_data) if isinstance(clients_data, dict) else clients_data
        if clients:
            df = pd.DataFrame([{
                'Nombre': c.get('full_name', ''),
                'Email': c['email'],
                'Ciudad': c.get('city', ''),
                'País': c.get('country', ''),
                'Pedidos': c.get('total_orders', 0),
                'Estado': '✅ Activo' if c['is_active'] else '❌ Inactivo',
                'Registrado': c['created_at'][:10],
            } for c in clients])

            st.markdown(f'**{len(df)} cliente(s)**')
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Exportar CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                '📥 Descargar CSV',
                data=csv,
                file_name='reporte_clientes.csv',
                mime='text/csv',
                use_container_width=True
            )
        else:
            st.info('No se encontraron clientes.')

# ── Reporte de Ventas ─────────────────────────────────────────────────────────
with tab_sales:
    st.subheader('💰 Reporte de Ventas')

    col1, col2 = st.columns([2, 2])
    with col1:
        status_s = st.selectbox(
            'Estado del pedido',
            ['Todos', 'paid', 'delivered', 'processing', 'shipped'],
            key='status_sales'
        )
    with col2:
        search_s = st.text_input('🔍 Buscar por número de pedido', key='search_sales')

    params_s = {}
    if status_s != 'Todos':
        params_s['status'] = status_s
    if search_s:
        params_s['search'] = search_s

    orders_data, err = api_get('/orders/', params=params_s)
    if err:
        st.error(err)
    elif orders_data:
        orders = orders_data.get('results', orders_data) if isinstance(orders_data, dict) else orders_data
        if orders:
            df_orders = pd.DataFrame([{
                '# Pedido': o['order_number'],
                'Cliente': o.get('user_name', o.get('user_email', '')),
                'Email': o.get('user_email', ''),
                'Estado': o['status_display'],
                'Subtotal ($)': float(o['subtotal']),
                'IVA ($)': float(o['tax']),
                'Total ($)': float(o['total']),
                'Fecha': o['created_at'][:10],
            } for o in orders])

            # Métricas resumen
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric('Total Pedidos', len(df_orders))
            col_m2.metric('Ingresos Totales', f"${df_orders['Total ($)'].sum():,.2f}")
            col_m3.metric('Ticket Promedio', f"${df_orders['Total ($)'].mean():,.2f}")

            st.dataframe(df_orders, use_container_width=True, hide_index=True)

            # Exportar CSV
            csv = df_orders.to_csv(index=False).encode('utf-8')
            st.download_button(
                '📥 Descargar CSV',
                data=csv,
                file_name='reporte_ventas.csv',
                mime='text/csv',
                use_container_width=True
            )
        else:
            st.info('No se encontraron pedidos con los filtros seleccionados.')
