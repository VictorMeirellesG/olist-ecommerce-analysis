import pandas as pd
from pathlib import Path


def load_all_datasets(data_path: str | Path = "../data/raw") -> dict:
    """Carrega todos os CSVs do dataset Olist e retorna um dicionário de DataFrames."""
    data_path = Path(data_path)

    files = {
        "customers": "olist_customers_dataset.csv",
        "orders": "olist_orders_dataset.csv",
        "order_items": "olist_order_items_dataset.csv",
        "payments": "olist_order_payments_dataset.csv",
        "reviews": "olist_order_reviews_dataset.csv",
        "products": "olist_products_dataset.csv",
        "sellers": "olist_sellers_dataset.csv",
        "geolocation": "olist_geolocation_dataset.csv",
        "category_translation": "product_category_name_translation.csv",
    }

    datasets = {}
    for name, filename in files.items():
        datasets[name] = pd.read_csv(data_path / filename)
        print(f"✓ {name}: {datasets[name].shape}")

    return datasets