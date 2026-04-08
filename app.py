import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

st.set_page_config(page_title="Monitor SUS - DATASUS", layout="wide")

st.title("📊 Monitoramento de Produção Hospitalar e Ambulatorial (SUS)")
st.markdown("Dashboard desenvolvido para análise de dados extraídos do portal DATASUS TabNet.")

# Conexão com o banco de dados
db_path = "/home/ubuntu/datasus.db"

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
    st.warning(f"Nenhum dado encontrado para {source}. Certifique-se de que a extração e carga foram concluídas.")
else:
    # 3.1 Lista dos dados armazenados
    st.header(f"📋 Lista de Dados - {source}")
    st.write(f"Total de registros: {len(df)}")
    st.dataframe(df.head(100))

    # 3.2 Estatísticas descritivas
    st.header("📈 Estatísticas Descritivas")
    
    # Identificar colunas numéricas
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Filtrar colunas de código (geralmente começam com Município ou são IDs)
    stats_cols = [c for c in num_cols if 'Município' not in c and 'Municipio' not in c]
    
    if stats_cols:
        st.write(df[stats_cols].describe())
    else:
        st.info("Nenhuma coluna numérica detectada para estatísticas descritivas.")

    # 3.3 Diversos gráficos
    st.header("📊 Visualizações")
    
    col1, col2 = st.columns(2)
    
    # Identificar coluna de município
    mun_col = next((c for c in df.columns if 'Município' in c or 'Municipio' in c), None)

    with col1:
        if mun_col and stats_cols:
            metric = st.selectbox(f"Selecione a métrica (Barra):", stats_cols, key="bar_metric")
            # Remover zeros e o Total se existir
            df_plot = df[df[metric] > 0]
            if mun_col in df_plot.columns:
                df_plot = df_plot[~df_plot[mun_col].str.contains('Total', case=False, na=False)]
            
            top_10 = df_plot.nlargest(10, metric)
            if not top_10.empty:
                fig1 = px.bar(top_10, x=mun_col, y=metric, title=f"Top 10 Municípios por {metric}", color=metric, color_continuous_scale='Viridis')
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("Sem dados significativos para exibir.")
    
    with col2:
        if stats_cols:
            hist_metric = st.selectbox(f"Selecione a métrica (Histograma):", stats_cols, key="hist_metric")
            df_hist = df[df[hist_metric] > 0]
            if not df_hist.empty:
                fig2 = px.histogram(df_hist, x=hist_metric, title=f"Distribuição de {hist_metric}", nbins=30, color_discrete_sequence=['indianred'])
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Sem dados significativos para o histograma.")

    # Gráfico de Pizza para os Subgrupos
    st.header("🍕 Distribuição por Subgrupo")
    if stats_cols:
        # No TabNet, os subgrupos são as colunas (exceto Município e Total)
        # Vamos somar os valores de cada subgrupo
        subgroup_cols = [c for c in df.columns if c not in [mun_col, 'Total'] and c in stats_cols]
        if subgroup_cols:
            sums = df[subgroup_cols].sum().reset_index()
            sums.columns = ['Subgrupo', 'Valor Total']
            fig3 = px.pie(sums, values='Valor Total', names='Subgrupo', title="Participação por Subgrupo de Procedimento")
            st.plotly_chart(fig3, use_container_width=True)
