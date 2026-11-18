import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import glob
import os

st.set_page_config(page_title="Dashboard Financiero y Comercial - Yura S.A.", layout="wide", initial_sidebar_state="expanded")

st.sidebar.header("📂 1. Cargar Base de Datos")
archivo_subido = st.sidebar.file_uploader("Sube tu Excel o CSV aquí:", type=["xlsx", "csv"])

# Quitamos el caché para que actualice en tiempo real cada vez que subas un archivo
def load_data(file):
    if file is not None:
        st.sidebar.success(f"✅ Leyendo archivo subido: {file.name}")
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file, sheet_name=0)
    else:
        archivos = glob.glob("*Yura*.xlsx") + glob.glob("*Yura*.csv") + glob.glob("*yura*.xlsx") + glob.glob("*yura*.csv")
        if archivos:
            archivo_reciente = max(archivos, key=os.path.getctime)
            st.sidebar.info(f"📁 Archivo automático: {archivo_reciente}")
            df = pd.read_csv(archivo_reciente) if archivo_reciente.endswith('.csv') else pd.read_excel(archivo_reciente, sheet_name=0)
        else:
            st.warning("⚠️ Sube tu archivo Excel/CSV usando el botón 'Upload' de la izquierda.")
            st.stop()
            
    df.columns = df.columns.str.strip().str.lower()
    return df
df = load_data(archivo_subido)
if 'anio' not in df.columns or 'ventas_zona' not in df.columns:
    st.error("⚠️ El archivo cargado es el antiguo. Sube tu nuevo archivo Excel o CSV usando el botón 'Browse files' de la izquierda.")
    st.stop()

st.sidebar.header("🕹️ 2. Filtros de Control")

años_disp = sorted(df['anio'].unique())
year_filter = st.sidebar.multiselect("📅 Selecciona el Año:", options=años_disp, default=años_disp)

zonas_disp = df['region_principal'].unique()
zone_filter = st.sidebar.multiselect("📍 Selecciona la Región:", options=zonas_disp, default=zonas_disp)

df_filtered = df[(df['anio'].isin(year_filter)) & (df['region_principal'].isin(zone_filter))]
df_finanzas = df[df['anio'].isin(year_filter)].drop_duplicates(subset=['anio']).sort_values('anio')

st.title("📊 Dashboard Estratégico: Comercial y Financiero — YURA S.A.")
st.markdown("**RUC:** 20312372895 | **Moneda:** Miles de Soles (S/. '000) | **Periodo:** 2020 - 2025")
st.write("---")

st.subheader("🛒 Resumen Comercial (Según Regiones y Años Filtrados)")

ventas_tot = df_filtered['ventas_zona'].sum()
compras_tot = df_filtered['compras_zona'].sum()
costo_tot = df_filtered['costo_ventas_zona'].sum()
margen_comercial = ventas_tot - costo_tot

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ventas Totales (Miles S/.)", f"S/. {ventas_tot:,.2f}")
c2.metric("Compras Totales (Miles S/.)", f"S/. {compras_tot:,.2f}")
c3.metric("Costo de Ventas (Miles S/.)", f"S/. {costo_tot:,.2f}")
c4.metric("Margen Bruto Comercial", f"S/. {margen_comercial:,.2f}")

graf1, graf2 = st.columns(2)

with graf1:
    st.markdown("**📈 Evolución de Ventas vs Compras por Año**")
    df_evol = df_filtered.groupby('anio')[['ventas_zona', 'compras_zona', 'costo_ventas_zona']].sum().reset_index()
    fig_evol = go.Figure()
    fig_evol.add_trace(go.Bar(x=df_evol['anio'], y=df_evol['ventas_zona'], name='Ventas', marker_color='#1f77b4'))
    fig_evol.add_trace(go.Bar(x=df_evol['anio'], y=df_evol['compras_zona'], name='Compras', marker_color='#ff7f0e'))
    fig_evol.add_trace(go.Scatter(x=df_evol['anio'], y=df_evol['costo_ventas_zona'], name='Costo de Ventas', line=dict(color='#d62728', width=3)))
    fig_evol.update_layout(barmode='group', xaxis=dict(tickmode='linear'), margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_evol, use_container_width=True)

with graf2:
    st.markdown("**🏢 Participación de Ventas por Región Principal**")
    df_reg = df_filtered.groupby('region_principal')['ventas_zona'].sum().reset_index()
    fig_pie = px.pie(df_reg, values='ventas_zona', names='region_principal', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
    fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_pie, use_container_width=True)

st.write("---")

st.subheader("🏦 Indicadores Financieros y Ratios Corporativos (Promedio del Periodo)")

if not df_finanzas.empty:
    liq_prom = df_finanzas['ratio_1_liquidez_corriente'].mean()
    roe_prom = df_finanzas['ratio_2_roe_rentabilidad_patrimonio'].mean() * 100
    end_prom = df_finanzas['ratio_3_endeudamiento_patrimonial'].mean()
    margen_neto_prom = df_finanzas['indicador_margen_neto'].mean() * 100

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Ratio Liquidez Corriente", f"{liq_prom:.2f}x")
    r2.metric("ROE (Rentabilidad Patrimonio)", f"{roe_prom:.2f}%")
    r3.metric("Endeudamiento Patrimonial", f"{end_prom:.2f}x")
    r4.metric("Margen Neto Anual", f"{margen_neto_prom:.2f}%")

    graf3, graf4 = st.columns(2)

    with graf3:
        st.markdown("**💰 Estado de Resultados: Ventas Netas vs Utilidad Neta Anual**")
        fig_er = go.Figure()
        fig_er.add_trace(go.Scatter(x=df_finanzas['anio'], y=df_finanzas['er_ventas_netas_anual'], name='Ventas Netas Anuales', mode='lines+markers', line=dict(color='#2ca02c', width=3)))
        fig_er.add_trace(go.Scatter(x=df_finanzas['anio'], y=df_finanzas['er_utilidad_neta_anual'], name='Utilidad Neta Anual', mode='lines+markers', line=dict(color='#9467bd', width=3)))
        fig_er.update_layout(xaxis=dict(tickmode='linear'), margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_er, use_container_width=True)

    with graf4:
        st.markdown("**⚖️ Estructura Financiera: Activo, Pasivo y Patrimonio**")
        fig_esf = go.Figure()
        fig_esf.add_trace(go.Bar(x=df_finanzas['anio'], y=df_finanzas['esf_activo_total'], name='Activo Total', marker_color='#17becf'))
        fig_esf.add_trace(go.Bar(x=df_finanzas['anio'], y=df_finanzas['esf_pasivo_total'], name='Pasivo Total', marker_color='#e377c2'))
        fig_esf.add_trace(go.Bar(x=df_finanzas['anio'], y=df_finanzas['esf_patrimonio_neto'], name='Patrimonio Neto', marker_color='#bcbd22'))
        fig_esf.update_layout(barmode='group', xaxis=dict(tickmode='linear'), margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_esf, use_container_width=True)

st.write("---")

st.subheader("📋 Base de Datos Filtrada (En Miles de Soles)")
st.dataframe(df_filtered, height=280, use_container_width=True)
