"""UI card component for rendering vault file metadata and actions."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass

import streamlit as st


def _to_dict(item) -> dict:
    if is_dataclass(item):
        return asdict(item)
    if isinstance(item, dict):
        return item
    return {
        "id": getattr(item, "id", None),
        "item_name": getattr(item, "item_name", "Unnamed"),
        "item_type": getattr(item, "item_type", "file"),
        "mime_type": getattr(item, "mime_type", "application/octet-stream"),
        "original_size": getattr(item, "original_size", None),
    }


def render_file_card(item: dict) -> tuple[bool, bool]:
    """Render a file card and return (download_clicked, delete_clicked)."""
    data = _to_dict(item)

    with st.container(border=True):
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f"**📄 {data.get('item_name') or 'Unnamed'}**")
            st.caption(
                f"{data.get('mime_type') or 'application/octet-stream'} · "
                f"{data.get('original_size') or 0} bytes"
            )
        with c2:
            st.markdown(
                f"<span class='vault-chip'>#{data.get('id')}</span>",
                unsafe_allow_html=True,
            )

        col1, col2 = st.columns([1, 1])
        with col1:
            download_clicked = st.button(
                "⬇ Download",
                key=f"download_{data.get('id')}",
                use_container_width=True,
                type="primary",
            )
        with col2:
            delete_clicked = st.button(
                "🗑 Delete",
                key=f"delete_{data.get('id')}",
                use_container_width=True,
                type="secondary",
            )

    return download_clicked, delete_clicked
