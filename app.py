import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard DATASUS - SIH/SIA", layout="wide")

st.title("📊 Monitoramento de Produção Hospitalar e Ambulatorial (SUS)")
st.markdown("Dados extraídos do portal DATASUS TabNet para o período de 2024-2026.")

# Conexão com o banco de dados
db_path = "/home/ubuntu/datasus.db"

def load_data(table_name):
    if not os.path.exists(db_path):
        return pd.DataFrame()
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

# Sidebar para navegação
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
    
    # Identificar colunas numéricas
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    if num_cols:
        st.write(df[num_cols].describe())
    else:
        st.info("Nenhuma coluna numérica detectada para estatísticas descritivas.")

    # 3.3 Diversos gráficos
    st.header("📊 Visualizações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras por Município (Top 10)
        if 'Município' in df.columns or 'Municipio' in df.columns:
            mun_col = 'Município' if 'Município' in df.columns else 'Municipio'
            if num_cols:
                metric = st.selectbox("Selecione a métrica para o gráfico:", num_cols)
                top_10 = df.nlargest(10, metric)
                fig1 = px.bar(top_10, x=mun_col, y=metric, title=f"Top 10 Municípios por {metric}")
                st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Gráfico de pizza ou distribuição
        if num_cols:
            fig2 = px.histogram(df, x=num_cols[0], title=f"Distribuição de {num_cols[0]}")
            st.plotly_chart(fig2, use_container_width=True)
            
    # Gráfico de dispersão se houver pelo menos 2 colunas numéricas
    if len(num_cols) >= 2:
        st.subheader(f"Dispersão: {num_cols[0]} vs {num_cols[1]}")
        fig3 = px.scatter(df, x=num_cols[0], y=num_cols[1], hover_name=mun_col if 'mun_col' in locals() else None)
        st.plotly_chart(fig3, use_container_width=True)

st.sidebar.info("Desenvolvido por Manus AI")
