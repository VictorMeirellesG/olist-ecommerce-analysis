import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_loader import load_all_datasets
from src.data_cleaning import parse_order_dates, get_delivered_orders, build_items_full

st.set_page_config(page_title="Olist Dashboard", layout="wide", page_icon="🛒")

@st.cache_data
def load_data():
    data_path = Path(__file__).resolve().parents[1] / "data" / "raw"
    datasets = load_all_datasets(data_path)
    datasets["orders"] = parse_order_dates(datasets["orders"])
    datasets["delivered"] = get_delivered_orders(datasets["orders"])
    datasets["items_full"] = build_items_full(
        datasets["order_items"], datasets["products"], datasets["category_translation"]
    )
    return datasets

datasets = load_data()
delivered = datasets["delivered"]
reviews   = datasets["reviews"]
payments  = datasets["payments"]
items_full = datasets["items_full"]

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("🛒 Olist Analytics")
st.sidebar.markdown("Análise exploratória do e-commerce brasileiro (2016–2018)")
pagina = st.sidebar.radio("Navegação", ["Visão Geral", "Entregas", "Produtos", "Pagamentos"])

# ── Visão Geral ───────────────────────────────────────────────────────────────
if pagina == "Visão Geral":
    st.title("📊 Visão Geral")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Pedidos", f"{len(delivered):,}")
    col2.metric("Receita Total", f"R$ {items_full['price'].sum():,.0f}")
    col3.metric("Ticket Médio", f"R$ {payments['payment_value'].mean():.2f}")
    col4.metric("Nota Média", f"{reviews['review_score'].mean():.2f} ⭐")

    st.subheader("Pedidos por Mês")
    orders_by_month = delivered.groupby("order_month").size().reset_index(name="pedidos")
    fig = px.line(orders_by_month, x="order_month", y="pedidos", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# ── Entregas ──────────────────────────────────────────────────────────────────
elif pagina == "Entregas":
    st.title("🚚 Análise de Entregas")

    col1, col2, col3 = st.columns(3)
    col1.metric("Tempo médio de entrega", f"{delivered['delivery_time_days'].mean():.1f} dias")
    col2.metric("Entregues no prazo", f"{delivered['on_time'].mean()*100:.1f}%")
    col3.metric("Mediana de entrega", f"{delivered['delivery_time_days'].median():.0f} dias")

    st.subheader("Distribuição do Tempo de Entrega")
    fig = px.histogram(delivered, x="delivery_time_days", nbins=50,
                       labels={"delivery_time_days": "Dias até a entrega"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Nota Média por Pontualidade")
    delivery_review = delivered.merge(reviews[["order_id", "review_score"]], on="order_id")
    avg_score = delivery_review.groupby("on_time")["review_score"].mean().reset_index()
    avg_score["on_time"] = avg_score["on_time"].map({True: "No prazo", False: "Atrasado"})
    fig = px.bar(avg_score, x="on_time", y="review_score", color="on_time",
                 labels={"review_score": "Nota Média", "on_time": ""},
                 color_discrete_map={"No prazo": "#2ecc71", "Atrasado": "#e74c3c"})
    st.plotly_chart(fig, use_container_width=True)

# ── Produtos ──────────────────────────────────────────────────────────────────
elif pagina == "Produtos":
    st.title("📦 Análise de Produtos")

    top_n = st.slider("Número de categorias", 5, 20, 15)
    revenue = (
        items_full.groupby("product_category_name_english")["price"]
        .sum().sort_values(ascending=False).head(top_n).reset_index()
    )
    revenue.columns = ["Categoria", "Receita"]
    fig = px.bar(revenue, x="Receita", y="Categoria", orientation="h",
                 color="Receita", color_continuous_scale="viridis")
    st.plotly_chart(fig, use_container_width=True)

# ── Pagamentos ────────────────────────────────────────────────────────────────
elif pagina == "Pagamentos":
    st.title("💳 Análise de Pagamentos")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Transações por Forma de Pagamento")
        counts = payments["payment_type"].value_counts().reset_index()
        counts.columns = ["Forma", "Quantidade"]
        fig = px.bar(counts, x="Forma", y="Quantidade", color="Forma")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Ticket Médio por Forma de Pagamento")
        avg_val = payments.groupby("payment_type")["payment_value"].mean().reset_index()
        avg_val.columns = ["Forma", "Ticket Médio"]
        fig = px.bar(avg_val, x="Forma", y="Ticket Médio", color="Forma")
        st.plotly_chart(fig, use_container_width=True)