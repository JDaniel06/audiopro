"""
Página Admin: Gestión de Pagos y Evidencias - AudioPro
"""
import streamlit as st
from utils.api import api_get, api_post
from utils.auth import require_admin

st.set_page_config(page_title='Admin Pagos - AudioPro', page_icon='💰', layout='wide')
require_admin()

st.title('💰 Gestión de Pagos')

STATUS_LABELS = {
    'pending': '⏳ Pendiente',
    'under_review': '🔍 En Revisión',
    'approved': '✅ Aprobado',
    'rejected': '❌ Rechazado',
    'refunded': '↩️ Reembolsado',
}

# Filtros
col1, col2 = st.columns([3, 2])
with col1:
    search = st.text_input('🔍 Buscar por número de pedido o email')
with col2:
    status_filter = st.selectbox(
        'Estado',
        ['Todos', 'pending', 'under_review', 'approved', 'rejected'],
        format_func=lambda x: STATUS_LABELS.get(x, x) if x != 'Todos' else 'Todos'
    )

params = {}
if search:
    params['search'] = search
if status_filter != 'Todos':
    params['status'] = status_filter

payments_data, error = api_get('/payments/', params=params)
if error:
    st.error(error)
    st.stop()

payments = payments_data.get('results', payments_data) if isinstance(payments_data, dict) else payments_data
st.markdown(f'**{len(payments)} pago(s)**')

for payment in payments:
    label = STATUS_LABELS.get(payment['status'], payment['status'])
    with st.expander(
        f"{label} | Pedido #{payment.get('order_number', '')} | {payment.get('user_email', '')} | ${float(payment['amount']):,.2f} | {payment['method_display']}"
    ):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Método:** {payment['method_display']}")
            st.markdown(f"**Referencia:** {payment.get('reference_number', 'N/A')}")
            st.markdown(f"**Notas:** {payment.get('notes', 'N/A')}")
            if payment.get('reviewed_at'):
                st.markdown(f"**Revisado:** {payment['reviewed_at'][:10]}")
            if payment.get('rejection_reason'):
                st.error(f"Motivo rechazo: {payment['rejection_reason']}")

        with col2:
            # Evidencias
            evidences = payment.get('evidences', [])
            if evidences:
                st.markdown('**Comprobantes adjuntos:**')
                for ev in evidences:
                    file_url = ev.get('file_url', '')
                    st.markdown(f"📎 [{ev.get('file_name', 'Archivo')}]({file_url})")
                    if ev.get('description'):
                        st.caption(ev['description'])
            else:
                st.info('Sin comprobantes adjuntos.')

        # Acciones de revisión
        if payment['status'] in ['pending', 'under_review']:
            st.markdown('---')
            st.subheader('Revisar Pago')
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button('✅ Aprobar', key=f'approve_{payment["id"]}', type='primary', use_container_width=True):
                    result, err = api_post(f'/payments/{payment["id"]}/review/', {'action': 'approve'})
                    if err:
                        st.error(err)
                    else:
                        st.success('Pago aprobado.')
                        st.rerun()
            with col_b:
                reason = st.text_input('Motivo de rechazo', key=f'reason_{payment["id"]}')
                if st.button('❌ Rechazar', key=f'reject_{payment["id"]}', use_container_width=True):
                    if not reason:
                        st.error('Indica el motivo del rechazo.')
                    else:
                        result, err = api_post(f'/payments/{payment["id"]}/review/', {
                            'action': 'reject', 'rejection_reason': reason
                        })
                        if err:
                            st.error(err)
                        else:
                            st.warning('Pago rechazado.')
                            st.rerun()
