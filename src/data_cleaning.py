import pandas as pd


DATE_COLS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]


def parse_order_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Converte as colunas de datas do DataFrame orders para datetime."""
    orders = orders.copy()
    for col in DATE_COLS:
        orders[col] = pd.to_datetime(orders[col])
    return orders


def get_delivered_orders(orders: pd.DataFrame) -> pd.DataFrame:
    """Filtra apenas pedidos entregues e calcula métricas de entrega."""
    delivered = orders[orders["order_status"] == "delivered"].copy()
    
    delivered["delivery_time_days"] = (
        delivered["order_delivered_customer_date"] - delivered["order_purchase_timestamp"]
    ).dt.days

    delivered["delivery_vs_estimated"] = (
        delivered["order_delivered_customer_date"] - delivered["order_estimated_delivery_date"]
    ).dt.days

    delivered["on_time"] = delivered["delivery_vs_estimated"] <= 0
    delivered["order_month"] = (
        delivered["order_purchase_timestamp"].dt.to_period("M").astype(str)
    )

    return delivered


def build_items_full(
        order_items: pd.DataFrame,
        products: pd.DataFrame,
        category_translation: pd.DataFrame
) -> pd.DataFrame:
    """Junta order_items com produtos e tradução de categorias."""
    items_full = order_items.merge(products, on="product_id", how="left")
    items_full = items_full.merge(
        category_translation, on="product_category_name", how="left"
    )
    return items_full