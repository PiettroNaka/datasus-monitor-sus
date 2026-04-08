import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard DATASUS - SIH/SIA", layout="wide")

st.title("📊 Monitoramento de Produção Hospitalar e Ambulatorial (SUS)")
st.markdown("Dados extraídos do portal DATASUS TabNet para o período de 2024-2026.")

# Conexão com o banco de dados - Usar caminho relativo para funcionar no Streamlit Cloud
# O banco de dados datasus.db deve estar na mesma pasta do app.py
db_path = "datasus.db"

def load_data(table_name):
    if not os.path.exists(db_path):
        # Tenta procurar em subdiretórios se necessário, mas o padrão é na raiz
        st.error(f"Arquivo de banco de dados '{db_path}' não encontrado no diretório: {os.getcwd()}")
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(db_path)
        # Verificar se as tabelas existem
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        
        if table_name not in tables:
            st.warning(f"Tabela '{table_name}' não encontrada no banco de dados. Tabelas disponíveis: {tables}")
            conn.close()
            return pd.DataFrame()
            
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Sidebar para navegação
st.sidebar.header("Configurações")
source = st.sidebar.radio("Selecione a fonte de dados:", ["Produção Hospitalar (SIH)", "Produção Ambulatorial (SIA)"])

# Mapeamento correto das tabelas conforme o script de carga (load_data.py)
# No load_data.py original, as tabelas foram criadas como 'sih_data' e 'sia_data'
table_name = "sih_data" if source == "Produção Hospitalar (SIH)" else "sia_data"
df = load_data(table_name)

if df.empty:
    st.warning(f"Nenhum dado encontrado para {source}. Certifique-se de que a extração foi concluída e o banco de dados foi carregado.")
else:
    # 3.1 Lista dos dados armazenados
    st.header(f"📋 Lista de Dados - {source}")
    st.dataframe(df.head(100))

    # 3.2 Estatísticas descritivas
    st.header("📈 Estatísticas Descritivas")
    
    # Identificar colunas numéricas
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    if num_cols:
        st.write(df[num_cols].describe())
    else:
        st.info("Nenhuma coluna numérica detectada para estatísticas descritivas.")

    # 3.3 Diversos gráficos
    st.header("📊 Visualizações")
    
    col1, col2 = st.columns(2)
    
    # Identificar coluna de município
    mun_col = None
    for c in ['Município', 'Municipio', 'municipio', 'município']:
        if c in df.columns:
            mun_col = c
            break

    with col1:
        # Gráfico de barras por Município (Top 10)
        if mun_col:
            if num_cols:
                metric = st.selectbox(f"Selecione a métrica para o gráfico (Barra - {source}):", num_cols, key="bar_metric")
                top_10 = df.nlargest(10, metric)
                fig1 = px.bar(top_10, x=mun_col, y=metric, title=f"Top 10 Municípios por {metric}", color=metric, color_continuous_scale='Viridis')
                st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Gráfico de histograma ou distribuição
        if num_cols:
            hist_metric = st.selectbox(f"Selecione a métrica para o histograma ({source}):", num_cols, key="hist_metric")
            fig2 = px.histogram(df, x=hist_metric, title=f"Distribuição de {hist_metric}", nbins=30, color_discrete_sequence=['#38B2AC'])
            st.plotly_chart(fig2, use_container_width=True)
            
    # Gráfico de dispersão se houver pelo menos 2 colunas numéricas
    if len(num_cols) >= 2:
        st.subheader(f"Análise de Dispersão: {num_cols[0]} vs {num_cols[1]}")
        fig3 = px.scatter(df, x=num_cols[0], y=num_cols[1], 
                         hover_name=mun_col if mun_col else None,
                         title=f"Relação entre {num_cols[0]} e {num_cols[1]}",
                         trendline="ols" if len(df) > 2 else None)
        st.plotly_chart(fig3, use_container_width=True)

# Marca d'água removida conforme solicitado
