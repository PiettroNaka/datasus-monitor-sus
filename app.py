import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard DATASUS - SIH/SIA", layout="wide")

st.title("📊 Monitoramento de Produção Hospitalar e Ambulatorial (SUS)")
st.markdown("Dados extraídos do portal DATASUS TabNet para o período de 2024-2026.")

# Conexão com o banco de dados
db_path = "datasus.db"

def load_data(table_name):
    if not os.path.exists(db_path):
        st.error(f"Arquivo de banco de dados '{db_path}' não encontrado.")
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Sidebar para navegação
st.sidebar.header("Configurações")
source = st.sidebar.radio("Selecione a fonte de dados:", ["Produção Hospitalar (SIH)", "Produção Ambulatorial (SIA)"])

table_name = "sih_data" if source == "Produção Hospitalar (SIH)" else "sia_data"
df = load_data(table_name)

if df.empty:
    st.warning(f"Nenhum dado encontrado para {source}. Certifique-se de que a extração foi concluída.")
else:
    # 3.1 Lista dos dados armazenados
    st.header(f"📋 Lista de Dados - {source}")
    st.dataframe(df.head(100))

    # 3.2 Estatísticas descritivas
    st.header("📈 Estatísticas Descritivas")
    
    # Identificar colunas numéricas (incluindo as que o pandas pode ter lido como float mas são valores)
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Se 'Município gestor' ou similar foi lido como numérico (código), vamos remover das estatísticas se houver outras
    potential_id_cols = ['Município gestor', 'Municipio gestor', 'Município', 'Municipio']
    stats_cols = [c for c in num_cols if c not in potential_id_cols]
    
    if stats_cols:
        st.write(df[stats_cols].describe())
    elif num_cols:
        st.write(df[num_cols].describe())
    else:
        st.info("Nenhuma coluna numérica detectada para estatísticas descritivas.")

    # 3.3 Diversos gráficos
    st.header("📊 Visualizações")
    
    col1, col2 = st.columns(2)
    
    # Identificar coluna de município para o eixo X
    mun_col = None
    for c in potential_id_cols:
        if c in df.columns:
            mun_col = c
            break

    with col1:
        if mun_col and stats_cols:
            metric = st.selectbox(f"Selecione a métrica (Barra):", stats_cols, key="bar_metric")
            # Remover zeros para o gráfico ser mais limpo
            df_plot = df[df[metric] > 0]
            top_10 = df_plot.nlargest(10, metric)
            if not top_10.empty:
                fig1 = px.bar(top_10, x=mun_col, y=metric, title=f"Top 10 Municípios por {metric}", color=metric)
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("Sem dados significativos (maiores que zero) para exibir no gráfico de barras.")
    
    with col2:
        if stats_cols:
            hist_metric = st.selectbox(f"Selecione a métrica (Histograma):", stats_cols, key="hist_metric")
            df_hist = df[df[hist_metric] > 0]
            if not df_hist.empty:
                fig2 = px.histogram(df_hist, x=hist_metric, title=f"Distribuição de {hist_metric}", nbins=30)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Sem dados significativos para o histograma.")

# Marca d'água removida
