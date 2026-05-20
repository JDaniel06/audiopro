"""
Página de Pago - AudioPro
Soporta: Stripe (tarjeta) y comprobante manual
"""
import streamlit as st
from utils.api import api_get, api_post
from utils.auth import require_auth

st.set_page_config(page_title='Pago - AudioPro', page_icon='💳', layout='centered')
require_auth()

st.title('💳 Pago de Pedido')

# Obtener pedidos pendientes de pago
orders_data, error = api_get('/orders/', params={'status': 'payment_pending'})
if error:
    st.error(f'Error: {error}')
    st.stop()

orders = orders_data.get('results', orders_data) if isinstance(orders_data, dict) else orders_data
pending_orders = [o for o in orders if o['status'] == 'payment_pending']

if not pending_orders:
    st.info('No tienes pedidos pendientes de pago.')
    col1, col2 = st.columns(2)
    with col1:
        if st.button('🎵 Ver Catálogo'):
            st.switch_page('app.py')
    with col2:
        if st.button('📦 Mis Pedidos'):
            st.switch_page('pages/5_Mis_Pedidos.py')
    st.stop()

# Seleccionar pedido
order_options = {f"#{o['order_number']} — ${float(o['total']):,.2f}": o for o in pending_orders}
selected_label = st.selectbox('Selecciona el pedido a pagar', list(order_options.keys()))
order = order_options[selected_label]

st.markdown('---')
st.subheader(f"Pedido #{order['order_number']}")

# Resumen del pedido
col1, col2, col3 = st.columns(3)
col1.metric('Subtotal', f"${float(order['subtotal']):,.2f}")
col2.metric('IVA (16%)', f"${float(order['tax']):,.2f}")
col3.metric('Total', f"${float(order['total']):,.2f}")

st.markdown('---')

# ── Método de pago ────────────────────────────────────────────────────────────
st.subheader('Método de Pago')
method = st.radio(
    'Selecciona cómo deseas pagar:',
    ['💳 Tarjeta de Crédito/Débito (Stripe)', '🏦 Transferencia Bancaria', '📎 Adjuntar Comprobante'],
    horizontal=True
)

# ── Stripe ────────────────────────────────────────────────────────────────────
if method == '💳 Tarjeta de Crédito/Débito (Stripe)':
    st.info('Serás redirigido a la pasarela segura de Stripe para completar el pago.')
    if st.button('Pagar con Stripe', type='primary', use_container_width=True):
        with st.spinner('Generando enlace de pago...'):
            result, err = api_post('/payments/stripe_checkout/', {'order_id': order['id']})
        if err:
            st.error(f'Error: {err}')
        else:
            checkout_url = result.get('checkout_url')
            if checkout_url:
                st.markdown(f'### [👉 Haz clic aquí para pagar con Stripe]({checkout_url})')
                st.info('Abre el enlace en tu navegador para completar el pago.')
            else:
                st.error('No se pudo generar el enlace de pago.')

# ── Transferencia ─────────────────────────────────────────────────────────────
elif method == '🏦 Transferencia Bancaria':
    st.markdown("""
    **Datos bancarios para transferencia:**
    - **Banco:** Banco Nacional de Venezuela
    - **Cuenta:** 0102-1234-56-0000012345
    - **Titular:** AudioPro C.A.
    - **RIF:** J-12345678-9
    - **Monto:** ${:.2f}
    """.format(float(order['total'])))

    with st.form('transfer_form'):
        reference = st.text_input('Número de referencia de la transferencia *')
        notes = st.text_area('Notas adicionales')
        submitted = st.form_submit_button('Registrar Pago', type='primary', use_container_width=True)

    if submitted:
        if not reference:
            st.error('Ingresa el número de referencia.')
        else:
            with st.spinner('Registrando pago...'):
                result, err = api_post('/payments/create_manual/', {
                    'order_id': order['id'],
                    'method': 'transfer',
                    'reference_number': reference,
                    'notes': notes,
                })
            if err:
                st.error(f'Error: {err}')
            else:
                st.success('✅ Pago registrado. El administrador verificará tu transferencia.')
                st.session_state['current_payment_id'] = result['id']

# ── Comprobante ───────────────────────────────────────────────────────────────
elif method == '📎 Adjuntar Comprobante':
    st.info('Adjunta la imagen o PDF de tu comprobante de pago.')

    # Primero crear el pago si no existe
    payment_data, _ = api_get(f'/payments/?order={order["id"]}')
    existing_payments = payment_data.get('results', []) if payment_data else []
    payment_id = existing_payments[0]['id'] if existing_payments else None

    if not payment_id:
        with st.form('create_payment_form'):
            ref = st.text_input('Referencia de pago (opcional)')
            notes_p = st.text_area('Descripción del pago')
            method_p = st.selectbox('Tipo de pago', ['transfer', 'cash', 'other'])
            if st.form_submit_button('Crear registro de pago'):
                result, err = api_post('/payments/create_manual/', {
                    'order_id': order['id'],
                    'method': method_p,
                    'reference_number': ref,
                    'notes': notes_p,
                })
                if err:
                    st.error(err)
                else:
                    payment_id = result['id']
                    st.success('Registro creado. Ahora adjunta el comprobante.')
                    st.rerun()

    if payment_id:
        uploaded_file = st.file_uploader(
            'Selecciona el comprobante (JPG, PNG, PDF — máx. 5MB)',
            type=['jpg', 'jpeg', 'png', 'webp', 'pdf']
        )
        description = st.text_input('Descripción del comprobante (opcional)')

        if uploaded_file and st.button('📤 Subir Comprobante', type='primary', use_container_width=True):
            with st.spinner('Subiendo archivo...'):
                result, err = api_post(
                    f'/payments/{payment_id}/upload_evidence/',
                    data={'description': description},
                    files={'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                )
            if err:
                st.error(f'Error al subir: {err}')
            else:
                st.success('✅ Comprobante adjuntado exitosamente. El administrador lo revisará.')
