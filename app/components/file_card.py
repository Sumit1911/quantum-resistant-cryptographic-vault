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

    size_kb = round((data.get("original_size") or 0) / 1024, 2)
    icon = "📄" if (data.get("item_type") or "file") == "file" else "🔑"

    st.markdown(
        f"""
        <div class="vault-card" style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span style="font-family:monospace; font-size:14px; color:#E2E2F0;">
                    {icon} &nbsp; {data.get('item_name') or 'Unnamed'}
                </span>
                <br>
                <span style="font-family:monospace; font-size:11px; color:#5A5A80;">
                    {size_kb} KB &nbsp;·&nbsp; {data.get('mime_type') or 'application/octet-stream'} &nbsp;·&nbsp;
                </span>
                <span class="vault-chip">KYBER-512</span>
            </div>
            <div><span class="vault-chip">#{data.get('id')}</span></div>
        </div>
        """,
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
