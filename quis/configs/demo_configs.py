"""
Demo configuration for QUIS Streamlit app.

Configure paths for datasets, insight cards, and insights summaries.
"""

import os


def get_project_root() -> str:
    """Get the project root directory."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_demo_datasets() -> tuple:
    """
    Return curated demo datasets with their file paths.
    
    Returns:
        tuple of dicts with keys: label, insights_path, cards_path, csv_path
    """
    root = get_project_root()
    
    curated_history = (
        {
            "label": "Steel metal company (v2)",
            "insights_path": os.path.join(root, "quis_results", "quis_20241201_000000_transactions_v2", "insights_summary_v2.json"),
            "cards_path": os.path.join(root, "quis_results", "quis_20241201_000000_transactions_v2", "insight_cards_v2.json"),
            "csv_path": os.path.join(root, "data", "transactions_cleaned.csv"),
        },
        {
            "label": "Adidas (v4)",
            "insights_path": os.path.join(root, "quis_results", "quis_20241201_000000_Adidas_cleaned_v4", "insights_summary_adidas_v4.json"),
            "cards_path": os.path.join(root, "quis_results", "quis_20241201_000000_Adidas_cleaned_v4", "insight_cards_adidas_v4.json"),
            "csv_path": os.path.join(root, "data", "Adidas_cleaned.csv"),
        },
    )
    
    results = []
    for item in curated_history:
        if not os.path.isfile(item["insights_path"]):
            continue
        results.append({
            "label": item["label"],
            "insights_path": item["insights_path"],
            "cards_path": item["cards_path"] if os.path.isfile(item["cards_path"]) else None,
            "csv_path": item["csv_path"] if os.path.isfile(item["csv_path"]) else None,
        })
    
    return tuple(results)


def get_assets_dir() -> str:
    """Get the assets directory for the demo app."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo", "assets")
