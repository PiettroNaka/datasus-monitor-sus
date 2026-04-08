# Monitoramento de Produção Hospitalar e Ambulatorial (DATASUS)

Este projeto automatiza a extração de dados do portal DATASUS TabNet, armazena as informações em um banco de dados SQLite e disponibiliza um dashboard interativo via Streamlit para análise de indicadores de saúde.

## 📁 Estrutura do Projeto

- `get_data.py`: Robô de extração desenvolvido com **Playwright**.
- `load_data.py`: Script para limpeza de dados e carga no banco SQLite.
- `app.py`: Aplicação **Streamlit** para visualização e estatísticas.
- `datasus.db`: Banco de dados SQLite com os dados extraídos.
- `relatorio_tecnico.pdf`: Relatório técnico detalhado em LaTeX (20+ páginas).
- `presentation/`: Diretório contendo a apresentação de slides em HTML.

## 🚀 Como Executar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Executar o Robô (Opcional - Dados já inclusos)
```bash
python get_data.py
python load_data.py
```

### 3. Iniciar o Dashboard
```bash
streamlit run app.py
```

## 📊 Metodologia
O projeto utiliza o Playwright para navegar no portal TabNet, superando desafios de frames e scripts legados. Os dados são extraídos para o período de Jan/2024 a Jan/2026, focando em quantidade e valor aprovado por município.

---
Desenvolvido por **Manus AI**
