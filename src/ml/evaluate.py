"""
evaluate.py
Compute evaluation metrics and generate SHAP explanations.
"""
import numpy as np
import pandas as pd
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_shap_values(model, X: pd.DataFrame, max_display: int = 20):
    """
    Compute SHAP values using TreeExplainer (fast for LightGBM).
    Returns explainer and shap_values array.
    """
    logger.info("Computing SHAP values ...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    # For binary classification, LightGBM returns list [neg_class, pos_class]
    if isinstance(shap_values, list):
        shap_values = shap_values[1]
    logger.info("SHAP values computed.")
    return explainer, shap_values


def shap_summary_figure(model, X: pd.DataFrame, max_display: int = 20):
    """Return a matplotlib figure of the SHAP summary (beeswarm) plot."""
    explainer, shap_values = get_shap_values(model, X)
    fig, ax = plt.subplots(figsize=(10, 6))
    shap.summary_plot(
        shap_values, X,
        max_display=max_display,
        show=False,
        plot_size=None
    )
    fig = plt.gcf()
    plt.tight_layout()
    return fig


def shap_waterfall_figure(model, X_row: pd.DataFrame):
    """Return a matplotlib figure for a single-row SHAP waterfall plot."""
    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X_row)
    # For binary: pick positive class
    if hasattr(shap_values, "values") and len(shap_values.values.shape) == 3:
        sv = shap.Explanation(
            values=shap_values.values[0, :, 1],
            base_values=shap_values.base_values[0, 1],
            data=shap_values.data[0],
            feature_names=X_row.columns.tolist()
        )
    else:
        sv = shap_values[0]

    fig, ax = plt.subplots(figsize=(10, 6))
    shap.waterfall_plot(sv, max_display=15, show=False)
    fig = plt.gcf()
    plt.tight_layout()
    return fig


def top_shap_features(model, X: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return top N features by mean absolute SHAP value."""
    _, shap_values = get_shap_values(model, X)
    importance = np.abs(shap_values).mean(axis=0)
    feat_df = pd.DataFrame({
        "feature": X.columns,
        "mean_abs_shap": importance
    }).sort_values("mean_abs_shap", ascending=False).head(n)
    return feat_df
