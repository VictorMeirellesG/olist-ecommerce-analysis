# Análise de E-commerce Brasileiro — Olist

Análise exploratória de dados de pedidos, clientes, vendedores e avaliações da Olist Store, um marketplace brasileiro, com o objetivo de extrair insights de negócio sobre vendas, logística e satisfação do cliente.

## 🎯 Objetivo

Este projeto tem como objetivo:
- Praticar e demonstrar habilidades de análise de dados (limpeza, EDA, visualização)
- Responder perguntas de negócio reais a partir de dados transacionais
- Construir um dashboard interativo para exploração dos resultados

## 📊 Sobre os dados

Dataset público disponibilizado pela [Olist](https://olist.com) no Kaggle, contendo informações de ~100 mil pedidos realizados entre 2016 e 2018 em diversos marketplaces brasileiros.

Fonte: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

> Os dados não estão incluídos neste repositório. Para reproduzir a análise, baixe o dataset do Kaggle e extraia os arquivos CSV em `data/raw/`.

## ❓ Perguntas que este projeto busca responder

- [ ] Quais categorias de produtos geram mais receita?
- [ ] Como o tempo de entrega impacta a satisfação do cliente (reviews)?
- [ ] Existe sazonalidade nas vendas ao longo do ano?
- [ ] Quais estados concentram mais clientes e vendedores?
- [ ] Qual a relação entre forma de pagamento e valor do pedido?

## 🛠️ Tecnologias utilizadas

- Python (pandas, numpy)
- Matplotlib / Seaborn / Plotly
- Jupyter Notebook
- Streamlit (dashboard)

## 📁 Estrutura do projeto

```
olist-analise/
├── data/
│   ├── raw/          # Dados originais (não versionado)
│   └── processed/    # Dados tratados (não versionado)
├── notebooks/         # Notebooks de exploração e análise
├── src/                # Scripts reutilizáveis (limpeza, utils)
├── reports/
│   └── figures/        # Gráficos exportados
├── dashboard/          # Aplicação Streamlit
├── requirements.txt
└── README.md
```

## 🚀 Como reproduzir

```bash
# Clonar o repositório
git clone git@github.com:VictorMeirellesG/olist-ecommerce-analysis.git
cd olist-ecommerce-analysis

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Baixar o dataset do Kaggle e extrair em data/raw/
```

## 📌 Status do projeto

🚧 Em desenvolvimento

## 👤 Autor

**Victor Meirelles**
[GitHub](https://github.com/VictorMeirellesG)