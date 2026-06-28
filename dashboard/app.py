import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data_loader import load_all_datasets
from src.data_cleaning import parse_order_dates, get_delivered_orders, build_items_full

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Olist Analytics",
    layout="wide",
    page_icon="🛒",
    initial_sidebar_state="expanded",
)

# ── CSS customizado ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252a3d);
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid #7c6af7;
        margin-bottom: 8px;
    }
    .metric-label { color: #9099b0; font-size: 13px; font-weight: 500; margin-bottom: 4px; }
    .metric-value { color: #ffffff; font-size: 28px; font-weight: 700; }
    .metric-delta { font-size: 12px; margin-top: 4px; }
    .section-title {
        color: #e0e4f0;
        font-size: 18px;
        font-weight: 600;
        margin: 24px 0 12px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid #2a2f45;
    }
    [data-testid="stSidebar"] { background-color: #13151f; }
</style>
""", unsafe_allow_html=True)

PURPLE = "#7c6af7"
TEAL   = "#4ecdc4"
CORAL  = "#ff6b6b"
GOLD   = "#ffd93d"

# ── Traduções ─────────────────────────────────────────────────────────────────
PAYMENT_PT = {
    "credit_card": "Cartão de Crédito",
    "boleto":      "Boleto",
    "voucher":     "Voucher",
    "debit_card":  "Cartão de Débito",
    "not_defined": "Não definido",
}

STATUS_PT = {
    "delivered":   "Entregue",
    "shipped":     "Enviado",
    "canceled":    "Cancelado",
    "unavailable": "Indisponível",
    "invoiced":    "Faturado",
    "processing":  "Processando",
    "created":     "Criado",
    "approved":    "Aprovado",
}

def fmt_category(name: str) -> str:
    if not isinstance(name, str):
        return "Não Definido"
    return name.replace("_", " ").title()

def metric_card(label, value, delta=None, delta_color="normal"):
    color = "#4ecdc4" if delta_color == "good" else "#ff6b6b" if delta_color == "bad" else "#9099b0"
    delta_html = f'<div class="metric-delta" style="color:{color}">{delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>""", unsafe_allow_html=True)

# ── Carregamento dos dados ────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    data_path = Path(__file__).resolve().parents[1] / "data" / "raw"
    datasets = load_all_datasets(data_path)
    datasets["orders"]     = parse_order_dates(datasets["orders"])
    datasets["delivered"]  = get_delivered_orders(datasets["orders"])
    datasets["items_full"] = build_items_full(
        datasets["order_items"], datasets["products"], datasets["category_translation"]
    )
    datasets["orders_customers"] = datasets["delivered"].merge(
        datasets["customers"][["customer_id", "customer_state", "customer_city"]],
        on="customer_id", how="left"
    )
    datasets["delivery_review"] = datasets["delivered"].merge(
        datasets["reviews"][["order_id", "review_score"]], on="order_id", how="inner"
    )
    return datasets

with st.spinner("Carregando dados..."):
    datasets = load_data()

delivered        = datasets["delivered"]
reviews          = datasets["reviews"]
payments         = datasets["payments"]
items_full       = datasets["items_full"]
orders_customers = datasets["orders_customers"]
delivery_review  = datasets["delivery_review"]

# Definição dinâmica da coluna de categorias (Português como prioridade)
cat_col = "product_category_name" if "product_category_name" in items_full.columns else "product_category_name_english"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 Olist Analytics")
    st.markdown("E-commerce brasileiro · 2016–2018")
    st.divider()
    pagina = st.radio("Navegação", ["📊 Visão Geral", "🚚 Entregas", "📦 Produtos", "💳 Pagamentos", "🗺️ Geografia"], label_visibility="collapsed")
    st.divider()
    st.caption("Fonte: Olist · Kaggle")
    st.caption(f"**{len(delivered):,}** pedidos analisados")

# ── VISÃO GERAL ───────────────────────────────────────────────────────────────
if pagina == "📊 Visão Geral":
    st.title("📊 Visão Geral")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: metric_card("Total de Pedidos", f"{len(delivered):,}")
    with c2: metric_card("Receita Total", f"R$ {items_full['price'].sum()/1e6:.2f}M")
    with c3: metric_card("Ticket Médio", f"R$ {payments['payment_value'].mean():.2f}")
    with c4: metric_card("Nota Média", f"{reviews['review_score'].mean():.2f} ⭐")
    with c5: metric_card("Entregues no Prazo", f"{delivered['on_time'].mean()*100:.1f}%", delta="✓ acima de 90%", delta_color="good")

    st.markdown('<div class="section-title">Crescimento Mensal de Pedidos</div>', unsafe_allow_html=True)
    orders_by_month = delivered.groupby("order_month").size().reset_index(name="Pedidos")
    fig = px.area(orders_by_month, x="order_month", y="Pedidos",
                  color_discrete_sequence=[PURPLE],
                  labels={"order_month": "Mês"})
    fig.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                      font_color="#9099b0", xaxis_title="Mês", yaxis_title="Pedidos",
                      margin=dict(l=0, r=0, t=10, b=0))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#1e2130")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Status dos Pedidos</div>', unsafe_allow_html=True)
        status = datasets["orders"]["order_status"].map(STATUS_PT).fillna("Outros").value_counts().reset_index()
        status.columns = ["Status", "Quantidade"]
        
        total_pedidos = status["Quantidade"].sum()
        status["Porcentagem"] = (status["Quantidade"] / total_pedidos) * 100
        status["Texto"] = status.apply(lambda row: f"{row['Porcentagem']:.2f}% ({row['Quantidade']:,})", axis=1)

        fig2 = px.bar(status, x="Quantidade", y="Status", orientation="h",
                      color="Quantidade", color_continuous_scale="Purp", text="Texto")
        fig2.update_traces(textposition="outside", textfont_size=11, cliponaxis=False)
        fig2.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117", font_color="#9099b0",
                          margin=dict(l=0, r=100, t=10, b=0), coloraxis_showscale=False,
                          yaxis=dict(autorange="reversed"), xaxis_title="", yaxis_title="")
        fig2.update_xaxes(showgrid=False, showticklabels=False)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Distribuição das Notas dos Clientes</div>', unsafe_allow_html=True)
        score_dist = reviews["review_score"].value_counts().sort_index().reset_index()
        score_dist.columns = ["Nota", "Quantidade"]
        score_dist["Nota"] = score_dist["Nota"].astype(str) + " ⭐"
        colors = [CORAL, CORAL, GOLD, TEAL, TEAL]
        fig3 = px.bar(score_dist, x="Nota", y="Quantidade",
                      color="Nota", color_discrete_sequence=colors,
                      text="Quantidade")
        fig3.update_traces(textposition="outside", textfont_size=12)
        fig3.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                           font_color="#9099b0", showlegend=False,
                           xaxis_title="Nota", yaxis_title="Quantidade de Avaliações",
                           margin=dict(l=0, r=0, t=30, b=0))
        fig3.update_yaxes(gridcolor="#1e2130")
        st.plotly_chart(fig3, use_container_width=True)

# ── ENTREGAS ──────────────────────────────────────────────────────────────────
elif pagina == "🚚 Entregas":
    st.title("🚚 Análise de Entregas")

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Tempo Médio de Entrega", f"{delivered['delivery_time_days'].mean():.1f} dias")
    with c2: metric_card("Mediana de Entrega", f"{delivered['delivery_time_days'].median():.0f} dias")
    with c3: metric_card("Entregues no Prazo", f"{delivered['on_time'].mean()*100:.1f}%", delta="✓ 93.2%", delta_color="good")
    with c4:
        late_orders = delivery_review[~delivery_review['on_time']]
        avg_delay = late_orders['delivery_vs_estimate'].mean() if not late_orders.empty else 0
        metric_card("Atraso Médio (atrasados)", f"{avg_delay:.0f} dias", delta="✗ acima do estimado", delta_color="bad")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Distribuição do Tempo de Entrega</div>', unsafe_allow_html=True)
        fig = px.histogram(delivered, x="delivery_time_days", nbins=60,
                           color_discrete_sequence=[PURPLE],
                           labels={"delivery_time_days": "Dias até a Entrega", "count": "Quantidade de Pedidos"})
        fig.add_vline(x=delivered["delivery_time_days"].mean(), line_dash="dash",
                      line_color=CORAL,
                      annotation_text=f"Média: {delivered['delivery_time_days'].mean():.1f} dias",
                      annotation_font_color=CORAL)
        fig.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                          font_color="#9099b0", margin=dict(l=0, r=0, t=10, b=0),
                          xaxis_title="Dias até a Entrega", yaxis_title="Quantidade de Pedidos")
        fig.update_yaxes(gridcolor="#1e2130")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Nota Média por Pontualidade da Entrega</div>', unsafe_allow_html=True)
        avg_score = delivery_review.groupby("on_time")["review_score"].mean().reset_index()
        avg_score["Situação"] = avg_score["on_time"].map({True: "No Prazo", False: "Atrasado"})
        fig2 = px.bar(avg_score, x="Situação", y="review_score",
                      color="Situação",
                      color_discrete_map={"No Prazo": TEAL, "Atrasado": CORAL},
                      text=avg_score["review_score"].round(2),
                      labels={"review_score": "Nota Média (1–5)"})
        fig2.update_traces(textposition="outside", textfont_size=16)
        fig2.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                           font_color="#9099b0", showlegend=False,
                           yaxis_range=[0, 5.5], margin=dict(l=0, r=0, t=30, b=0),
                           xaxis_title="", yaxis_title="Nota Média (1–5)")
        fig2.update_yaxes(gridcolor="#1e2130")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Distribuição das Notas — No Prazo vs Atrasado</div>', unsafe_allow_html=True)
    on_time_scores = delivery_review[delivery_review["on_time"]]["review_score"].value_counts().sort_index()
    late_scores    = delivery_review[~delivery_review["on_time"]]["review_score"].value_counts().sort_index()
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name="No Prazo", x=[f"{i} ⭐" for i in on_time_scores.index],
                          y=on_time_scores.values, marker_color=TEAL,
                          text=on_time_scores.values, textposition="outside"))
    fig3.add_trace(go.Bar(name="Atrasado", x=[f"{i} ⭐" for i in late_scores.index],
                          y=late_scores.values, marker_color=CORAL,
                          text=late_scores.values, textposition="outside"))
    fig3.update_layout(barmode="group", paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                       font_color="#9099b0", margin=dict(l=0, r=0, t=10, b=0),
                       xaxis_title="Nota do Cliente", yaxis_title="Quantidade de Pedidos",
                       legend_title="Situação da Entrega")
    fig3.update_yaxes(gridcolor="#1e2130")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="section-title">Volume de Pedidos por Dia da Semana</div>', unsafe_allow_html=True)
    if "weekday" not in delivered.columns:
        delivered["weekday"] = delivered["order_purchase_timestamp"].dt.day_name()
    order_days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    day_pt = {"Monday":"Segunda","Tuesday":"Terça","Wednesday":"Quarta",
              "Thursday":"Quinta","Friday":"Sexta","Saturday":"Sábado","Sunday":"Domingo"}
    weekday_counts = delivered["weekday"].value_counts().reindex(order_days).reset_index()
    weekday_counts.columns = ["dia_en", "Pedidos"]
    weekday_counts["Dia da Semana"] = weekday_counts["dia_en"].map(day_pt)
    fig4 = px.bar(weekday_counts, x="Dia da Semana", y="Pedidos",
                  color_discrete_sequence=[PURPLE], text="Pedidos")
    fig4.update_traces(textposition="outside", textfont_size=12)
    fig4.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                       font_color="#9099b0", margin=dict(l=0, r=0, t=30, b=0),
                       xaxis_title="", yaxis_title="Quantidade de Pedidos")
    fig4.update_yaxes(gridcolor="#1e2130")
    st.plotly_chart(fig4, use_container_width=True)

# ── PRODUTOS ──────────────────────────────────────────────────────────────────
elif pagina == "📦 Produtos":
    st.title("📦 Análise de Produtos")

    receita_total = items_full["price"].sum()
    top_cat_id = items_full.groupby(cat_col)["price"].sum().idxmax()
    top_cat = fmt_category(top_cat_id)
    
    c1, c2, c3 = st.columns(3)
    with c1: metric_card("Receita Total", f"R$ {receita_total/1e6:.2f}M")
    with c2: metric_card("Categoria Líder", top_cat)
    with c3: metric_card("Total de Categorias", str(items_full[cat_col].nunique()))

    top_n = st.slider("Número de categorias exibidas", 5, 30, 15)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Receita Total por Categoria (R$)</div>', unsafe_allow_html=True)
        revenue = items_full.groupby(cat_col)["price"].sum().sort_values(ascending=True).tail(top_n).reset_index()
        revenue.columns = ["Categoria", "Receita"]
        revenue["Categoria"] = revenue["Categoria"].apply(fmt_category)
        fig = px.bar(revenue, x="Receita", y="Categoria", orientation="h",
                     color="Receita", color_continuous_scale="Purp",
                     text=revenue["Receita"].apply(lambda x: f"R$ {x/1e3:.0f}k"))
        fig.update_traces(textposition="outside", textfont_size=11)
        fig.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                          font_color="#9099b0", margin=dict(l=0, r=0, t=10, b=0),
                          coloraxis_showscale=False, xaxis_title="Receita Total (R$)", yaxis_title="")
        fig.update_xaxes(gridcolor="#1e2130")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Volume de Itens Vendidos por Categoria</div>', unsafe_allow_html=True)
        volume = items_full.groupby(cat_col)["order_item_id"].count().sort_values(ascending=True).tail(top_n).reset_index()
        volume.columns = ["Categoria", "Itens Vendidos"]
        volume["Categoria"] = volume["Categoria"].apply(fmt_category)
        fig2 = px.bar(volume, x="Itens Vendidos", y="Categoria", orientation="h",
                      color="Itens Vendidos", color_continuous_scale="Teal",
                      text="Itens Vendidos")
        fig2.update_traces(textposition="outside", textfont_size=11)
        fig2.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                           font_color="#9099b0", margin=dict(l=0, r=0, t=10, b=0),
                           coloraxis_showscale=False, xaxis_title="Itens Vendidos", yaxis_title="")
        fig2.update_xaxes(gridcolor="#1e2130")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Ticket Médio por Categoria — Top 15 (R$)</div>', unsafe_allow_html=True)
    ticket = items_full.groupby(cat_col)["price"].mean().sort_values(ascending=False).head(15).reset_index()
    ticket.columns = ["Categoria", "Ticket Médio"]
    ticket["Categoria"] = ticket["Categoria"].apply(fmt_category)
    fig3 = px.bar(ticket, x="Categoria", y="Ticket Médio",
                  color="Ticket Médio", color_continuous_scale="Purp",
                  text=ticket["Ticket Médio"].apply(lambda x: f"R$ {x:.0f}"))
    fig3.update_traces(textposition="outside", textfont_size=12)
    fig3.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                       font_color="#9099b0", margin=dict(l=0, r=0, t=40, b=0),
                       coloraxis_showscale=False, xaxis_tickangle=-30,
                       xaxis_title="", yaxis_title="Preço Médio (R$)")
    fig3.update_yaxes(gridcolor="#1e2130")
    st.plotly_chart(fig3, use_container_width=True)

# ── PAGAMENTOS ────────────────────────────────────────────────────────────────
elif pagina == "💳 Pagamentos":
    st.title("💳 Análise de Pagamentos")

    credit = payments[payments["payment_type"] == "credit_card"]
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Forma Mais Usada", "Cartão de Crédito")
    with c2: metric_card("% no Cartão de Crédito", f"{(payments['payment_type']=='credit_card').mean()*100:.1f}%")
    with c3: metric_card("Mediana de Parcelas", f"{credit['payment_installments'].median():.0f}x" if not credit.empty else "0x")
    with c4: metric_card("Ticket Médio no Cartão", f"R$ {credit['payment_value'].mean():.2f}" if not credit.empty else "R$ 0,00")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Participação por Forma de Pagamento</div>', unsafe_allow_html=True)
        counts = payments["payment_type"].map(PAYMENT_PT).fillna("Outros").value_counts().reset_index()
        counts.columns = ["Forma de Pagamento", "Quantidade"]
        fig = px.pie(counts, names="Forma de Pagamento", values="Quantidade",
                     color_discrete_sequence=[PURPLE, TEAL, CORAL, GOLD, "#b0b8d0"],
                     hole=0.4)
        fig.update_traces(textinfo="percent+label", textfont_size=13)
        fig.update_layout(paper_bgcolor="#0f1117", font_color="#9099b0",
                          showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Ticket Médio por Forma de Pagamento (R$)</div>', unsafe_allow_html=True)
        avg_val = payments.copy()
        avg_val["payment_type"] = avg_val["payment_type"].map(PAYMENT_PT).fillna("Outros")
        avg_val = avg_val.groupby("payment_type")["payment_value"].mean().sort_values(ascending=False).reset_index()
        avg_val.columns = ["Forma de Pagamento", "Ticket Médio"]
        fig2 = px.bar(avg_val, x="Forma de Pagamento", y="Ticket Médio",
                      color="Forma de Pagamento",
                      color_discrete_sequence=[PURPLE, TEAL, CORAL, GOLD, "#b0b8d0"],
                      text=avg_val["Ticket Médio"].apply(lambda x: f"R$ {x:.0f}"))
        fig2.update_traces(textposition="outside", textfont_size=13)
        fig2.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                           font_color="#9099b0", showlegend=False,
                           xaxis_title="", yaxis_title="Valor Médio (R$)",
                           margin=dict(l=0, r=0, t=30, b=0))
        fig2.update_yaxes(gridcolor="#1e2130")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Distribuição de Parcelas — Cartão de Crédito</div>', unsafe_allow_html=True)
    if not credit.empty:
        installments = credit["payment_installments"].value_counts().sort_index().reset_index()
        installments.columns = ["Parcelas", "Quantidade"]
        installments = installments[installments["Parcelas"] <= 12]
        installments["label"] = installments["Parcelas"].astype(int).astype(str) + "x"
        fig3 = px.bar(installments, x="label", y="Quantidade",
                      color_discrete_sequence=[PURPLE], text="Quantidade")
        fig3.update_traces(textposition="outside", textfont_size=12)
        fig3.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                           font_color="#9099b0", margin=dict(l=0, r=0, t=30, b=0),
                           xaxis_title="Número de Parcelas", yaxis_title="Quantidade de Pedidos")
        fig3.update_yaxes(gridcolor="#1e2130")
        st.plotly_chart(fig3, use_container_width=True)

# ── GEOGRAFIA ─────────────────────────────────────────────────────────────────
elif pagina == "🗺️ Geografia":
    st.title("🗺️ Análise Geográfica")

    top_state = orders_customers["customer_state"].value_counts().idxmax() if not orders_customers.empty else "N/A"
    total_sp = (orders_customers['customer_state']=='SP').sum()
    pct_sp = (orders_customers['customer_state']=='SP').mean() * 100
    
    c1, c2, c3 = st.columns(3)
    with c1: metric_card("Estado com Mais Pedidos", top_state)
    with c2: metric_card("Pedidos em SP", f"{total_sp:,}")
    with c3: metric_card("Concentração em SP", f"{pct_sp:.1f}%", delta="⚠ alta concentração regional", delta_color="bad")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Top 10 Estados por Número de Pedidos</div>', unsafe_allow_html=True)
        state_orders = orders_customers["customer_state"].value_counts().head(10).reset_index()
        state_orders.columns = ["Estado", "Pedidos"]
        fig = px.bar(state_orders, x="Pedidos", y="Estado", orientation="h",
                     color="Pedidos", color_continuous_scale="Purp",
                     text="Pedidos")
        fig.update_traces(textposition="outside", textfont_size=12)
        fig.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                          font_color="#9099b0", margin=dict(l=0, r=0, t=10, b=0),
                          coloraxis_showscale=False,
                          xaxis_title="Quantidade de Pedidos", yaxis_title="Estado")
        fig.update_xaxes(gridcolor="#1e2130")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Top 10 Cidades por Número de Pedidos</div>', unsafe_allow_html=True)
        city_orders = orders_customers["customer_city"].str.title().value_counts().head(10).reset_index()
        city_orders.columns = ["Cidade", "Pedidos"]
        fig2 = px.bar(city_orders, x="Pedidos", y="Cidade", orientation="h",
                      color="Pedidos", color_continuous_scale="Teal",
                      text="Pedidos")
        fig2.update_traces(textposition="outside", textfont_size=12)
        fig2.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                           font_color="#9099b0", margin=dict(l=0, r=0, t=10, b=0),
                           coloraxis_showscale=False,
                           xaxis_title="Quantidade de Pedidos", yaxis_title="Cidade")
        fig2.update_xaxes(gridcolor="#1e2130")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Satisfação do Cliente por Estado (Nota Média)</div>', unsafe_allow_html=True)
    state_score = orders_customers.merge(
        reviews[["order_id", "review_score"]], on="order_id", how="inner"
    ).groupby("customer_state")["review_score"].mean().sort_values(ascending=False).reset_index()
    state_score.columns = ["Estado", "Nota Média"]
    fig3 = px.bar(state_score, x="Estado", y="Nota Média",
                  color="Nota Média", color_continuous_scale="RdYlGn",
                  text=state_score["Nota Média"].round(2))
    fig3.update_traces(textposition="outside", textfont_size=11)
    fig3.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                       font_color="#9099b0", margin=dict(l=0, r=0, t=40, b=0),
                       yaxis_range=[0, 5.3],
                       xaxis_title="Estado", yaxis_title="Nota Média (1–5)")
    fig3.update_yaxes(gridcolor="#1e2130")
    st.plotly_chart(fig3, use_container_width=True)