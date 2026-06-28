# Análise de E-commerce Brasileiro — Olist

Análise exploratória completa de ~100 mil pedidos do marketplace Olist (2016–2018), com dashboard interativo para exploração dos resultados.

## 📊 Principais Achados

| Métrica | Resultado |
|---|---|
| Total de pedidos analisados | 96.478 |
| Receita total | R$ 13.591.644 |
| Ticket médio | R$ 154,10 |
| Nota média dos clientes | 4,09 ⭐ |
| Tempo médio de entrega | 12,1 dias |
| Pedidos entregues no prazo | **93,2%** |
| Queda na nota por atraso | de 4,29 → 2,27 (-47%) |

### 🔍 Insights de negócio
- **Sazonalidade:** forte crescimento de set/2016 a nov/2017, com pico na Black Friday (nov/2017 ~7.200 pedidos)
- **Geografia:** SP concentra ~40k pedidos — quase 4x mais que RJ e MG
- **Categoria líder:** `health_beauty` lidera em receita (R$ 1,2M), seguida de `watches_gifts`
- **Pagamento:** cartão de crédito representa 74% das transações, com mediana de 3 parcelas
- **Impacto do atraso:** pedidos atrasados têm nota média 2,27 vs 4,29 nos pontuais — queda de ~47%

## 🛠️ Tecnologias

- Python (pandas, numpy)
- Matplotlib / Seaborn
- Plotly / Streamlit
- Jupyter Notebook
- Git / GitHub

## 📁 Estrutura
olist-analise/

├── data/

│   ├── raw/           # Dados originais (não versionado)

│   └── processed/     # Dados tratados (não versionado)

├── notebooks/

│   └── 01_eda.ipynb   # Análise exploratória completa

├── src/

│   ├── data_loader.py

│   ├── data_cleaning.py

│   └── utils.py

├── dashboard/

│   └── app.py         # Dashboard Streamlit

├── requirements.txt

└── README.md

## 🚀 Como reproduzir

```bash
git clone git@github.com:VictorMeirellesG/olist-ecommerce-analysis.git
cd olist-ecommerce-analysis
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Baixe o dataset em kaggle.com/datasets/olistbr/brazilian-ecommerce
# Extraia os CSVs em data/raw/
streamlit run dashboard/app.py
```

## 📌 Status
✅ Concluído

## 👤 Autor
**Victor Meirelles** — [GitHub](https://github.com/VictorMeirellesG)