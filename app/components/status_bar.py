"""Reusable status banner component for Streamlit pages."""

from __future__ import annotations

import streamlit as st


def render_status(message: str, level: str = "info") -> None:
    """Render a status message with consistent styling.

    Args:
        message: Text to display.
        level: One of "info", "success", "warning", "error".
    """
    if not message:
        return

    if level == "success":
        st.success(message)
    elif level == "warning":
        st.warning(message)
    elif level == "error":
        st.error(message)
    else:
        st.info(message)


def render_metric_row(total_items: int, total_size: int) -> None:
    """Render quick vault metrics."""
    col1, col2 = st.columns(2)
    col1.metric("Stored items", total_items)
    col2.metric("Total size (bytes)", total_size)
