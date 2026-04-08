import pandas as pd
import sqlite3
import os
import io

def clean_and_load(csv_path, table_name, db_path):
    print(f"Limpando {csv_path}...")
    
    # Ler o arquivo pulando as linhas iniciais e finais que são metadados do TabNet
    with open(csv_path, 'r', encoding='iso-8859-1') as f:
        lines = f.readlines()
    
    # Encontrar o início e fim dos dados reais
    start_idx = 0
    for i, line in enumerate(lines):
        if 'Município' in line or 'Municipio' in line:
            start_idx = i
            break
            
    end_idx = len(lines)
    for i, line in enumerate(lines[start_idx:], start_idx):
        if 'Total' in line or 'Fonte:' in line:
            end_idx = i
            break
            
    data_lines = lines[start_idx:end_idx]
    csv_content = "".join(data_lines)
    
    # Carregar no pandas
    df = pd.read_csv(io.StringIO(csv_content), sep=';', encoding='iso-8859-1', thousands='.', decimal=',')
    
    # Limpeza básica: remover colunas vazias ou 'Total'
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Conectar ao SQLite
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print(f"Dados carregados na tabela {table_name}")

if __name__ == "__main__":
    db_path = "/home/ubuntu/datasus.db"
    if os.path.exists("/home/ubuntu/data_sih.csv"):
        clean_and_load("/home/ubuntu/data_sih.csv", "sih_data", db_path)
    if os.path.exists("/home/ubuntu/data_sia.csv"):
        clean_and_load("/home/ubuntu/data_sia.csv", "sia_data", db_path)
