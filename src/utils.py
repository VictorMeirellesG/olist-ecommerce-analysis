import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def plot_delivery_distribution(delivered: pd.DataFrame) -> None:
    """Histograma da distribuição do tempo de entrega."""
    plt.figure(figsize=(10, 5))
    sns.histplot(delivered["delivery_time_days"], bins=50, kde=True)
    mean_days = delivered["delivery_time_days"].mean()
    plt.axvline(mean_days, color="red", linestyle="--", label=f"Média: {mean_days:.1f} dias")
    plt.title("Distribuição do Tempo de Entrega (dias)")
    plt.xlabel("Dias até a entrega")
    plt.ylabel("Quantidade de pedidos")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_revenue_by_category(items_full: pd.DataFrame, top_n: int = 15) -> None:
    """Barplot de receita total pelas top N categorias."""
    revenue = (
        items_full.groupby("product_category_name_english")["price"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
    )
    plt.figure(figsize=(10, 7))
    sns.barplot(x=revenue.values, y=revenue.index, hue=revenue.index,
                palette="viridis", legend=False)
    plt.title(f"Top {top_n} Categorias por Receita Total")
    plt.xlabel("Receita Total (R$)")
    plt.ylabel("Categoria")
    plt.tight_layout()
    plt.show()


def plot_punctuality_vs_score(delivery_review: pd.DataFrame) -> None:
    """Barplot de nota média por pontualidade de entrega."""
    avg_score = delivery_review.groupby("on_time")["review_score"].mean()
    plt.figure(figsize=(7, 5))
    sns.barplot(
        x=avg_score.index.map({True: "No prazo", False: "Atrasado"}),
        y=avg_score.values,
    )
    plt.title("Nota Média de Avaliação por Pontualidade da Entrega")
    plt.ylabel("Nota Média (1-5)")
    plt.ylim(0, 5)
    plt.tight_layout()
    plt.show()