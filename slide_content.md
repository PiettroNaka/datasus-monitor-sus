# Apresentação: Monitoramento DATASUS SIH/SIA

## 1. Título
- **Projeto:** Monitoramento de Produção Hospitalar e Ambulatorial (SUS)
- **Ferramentas:** Python, Playwright, SQLite, Streamlit, LaTeX
- **Autor:** Manus AI
- **Data:** Abril de 2026

## 2. Objetivos
- Automatizar a extração de dados do portal DATASUS TabNet.
- Armazenar dados de forma estruturada para consultas rápidas.
- Proporcionar visualizações interativas para tomada de decisão.
- Analisar a produção hospitalar (SIH) e ambulatorial (SIA) entre 2024 e 2026.

## 3. O Portal DATASUS
- Fonte oficial de dados de saúde pública no Brasil.
- Utilização do sistema TabNet para consultas customizadas.
- Desafio: Interface complexa e necessidade de automação para grandes volumes de dados.

## 4. Robô de Extração
- Desenvolvido em Python com Playwright.
- Navegação automatizada, seleção de filtros e download de arquivos CSV.
- Tratamento de erros e retentativas para garantir a integridade da coleta.

## 5. Estrutura de Dados
- Dados detalhados de AIH (SIH) e Produção Ambulatorial (SIA).
- Filtros aplicados: Município (Linha), Subgrupo (Coluna), Quantidade e Valor (Conteúdo).
- Período: 25 meses (Jan/2024 a Jan/2026).

## 6. Banco de Dados
- Utilização de SQLite pela sua leveza e portabilidade.
- Tabelas: `sih_data` e `sia_data`.
- Processo de limpeza (ETL) para remover metadados e formatar tipos numéricos.

## 7. Aplicação Streamlit
- Interface web intuitiva.
- Sidebar para seleção da fonte de dados (SIH ou SIA).
- Visualização de tabelas, estatísticas descritivas e gráficos dinâmicos.

## 8. Resultados: Produção Hospitalar (SIH)
- Análise de internações por município.
- Identificação dos subgrupos de procedimentos mais frequentes.
- Comparação de custos entre diferentes regiões.

## 9. Resultados: Produção Ambulatorial (SIA)
- Monitoramento de atendimentos ambulatoriais.
- Distribuição geográfica da produção.
- Volume de recursos aprovados por subgrupo.

## 10. Estatísticas e Gráficos
- Top 10 municípios por volume de produção.
- Histogramas de distribuição de valores.
- Gráficos de pizza mostrando a participação de cada subgrupo.

## 11. Relatório Técnico
- Documento de 29 páginas em LaTeX.
- Detalhamento da metodologia e códigos utilizados.
- Discussão dos resultados e conclusões técnicas.

## 12. Conclusões
- A automação reduz o tempo de coleta de dados de horas para minutos.
- A centralização em banco de dados facilita análises históricas.
- Dashboards interativos democratizam o acesso à informação para gestores.

## 13. Próximos Passos
- Integração com dados de mortalidade (SIM) e nascidos vivos (SINASC).
- Implementação de modelos preditivos para demanda hospitalar.
- Expansão da abrangência temporal.

## 14. Perguntas?
- Obrigado pela atenção!
- Contato: manus@manus.im
- Repositório: github.com/PiettroNaka/datasus-monitor-sus

## 15. Encerramento
- Fim da apresentação.
