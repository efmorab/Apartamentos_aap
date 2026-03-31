import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Cuentas compra y venta apartamentos", page_icon="🧱", layout="wide")

# Título
st.title("Cuentas apartamentos")

# Cargar datos
@st.cache_data
def load_data():
    file_path = "Relación de pagos.xlsx"
    df = pd.read_excel(file_path)
    # Limpieza básica
    df = df.dropna(subset=['Fecha'])  # Eliminar filas sin año
    df['Fecha'] = df['Fecha'].astype('datetime64[ns]')
    return df

if st.button("🔄 Actualizar datos"):
    st.cache_data.clear()
    st.success("Datos actualizados")
    st.rerun()

try:
    df = load_data()
except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    st.stop()

# Sidebar - Filtros
st.sidebar.header("Filtros")

# Filtro Apartamento
Apartamento =df['Apartamento'].unique().tolist()
apartamento_seleccionado =st.sidebar.multiselect("Selecciona Apartamento", Apartamento, default=Apartamento[:5])

# Filtro Estado
Estado_transferencia = df['Estado'].unique().tolist()
Estado_seleccionado = st.sidebar.multiselect("Selecciona estado del pago", Estado_transferencia, default=Estado_transferencia[:5])



# Aplicar filtros
df_filtered = df[
    (df['Apartamento'].isin(apartamento_seleccionado)) &
    (df['Estado'].isin(Estado_seleccionado))
]

if df_filtered.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

# KPIs
col1, col2, col3 = st.columns(3)

total_pagado = df_filtered['Valor'].sum()
principal_responsable = df_filtered.groupby('Responsable')['Valor'].sum().idxmax()
total_pagos = len(df_filtered)

col1.metric("Valor total pagado o recibido", f"{total_pagado:,.2f} M")
col2.metric("Principal responsable transferencia", principal_responsable)
col3.metric("Total de pagos realizados o recibidos", total_pagos)

st.markdown("---")

# Gráficos
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Total pagos por apartamento")
    responsable_pagos = df_filtered.groupby(['Responsable', 'Estado'])['Valor'].sum().reset_index()
    fig_apartamentos= px.bar(responsable_pagos, x='Responsable', y='Valor',color='Estado',
                              title="Valor por apartamento", color_discrete_map={
        'Pagado': '#04c494',
        'Pendiente': '#8000b3',
        'Recibido': '#b0b300'
    })
    st.plotly_chart(fig_apartamentos, use_container_width=True)

with col_right:
    st.subheader("Estado de los pagos")
    estado_pagos = df_filtered.groupby('Estado')['Valor'].sum().reset_index()
    fig_estado = px.pie(estado_pagos, values='Valor', names='Estado', title="Estado del pago", hole=0.4)
    st.plotly_chart(fig_estado, use_container_width=True)

st.subheader("Evolución de los pagos")
pagos_tiempo = (df_filtered.groupby(['Fecha', 'Estado','Responsable'])['Valor'].sum().reset_index())
fig_tiempos = px.line(pagos_tiempo,x='Fecha', y='Valor',color='Estado',symbol='Responsable',title="Evolución de los pagos",markers=True,color_discrete_map={
    'Pagado': 'green',
    'Pendiente': 'orange',
    'Mora': 'red'
})
pagos_tiempo = pagos_tiempo.sort_values('Fecha')
st.plotly_chart(fig_tiempos, use_container_width=True)

st.markdown("---")
st.subheader("Datos Detallados")
st.dataframe(df_filtered)
