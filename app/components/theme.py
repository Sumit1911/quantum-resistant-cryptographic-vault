"""Theme helpers for consistent, polished Streamlit UI styling."""

from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    """Inject custom CSS theme for app polish and readability."""
    st.markdown(
        """
        <style>
            .stApp {
                background: radial-gradient(circle at 15% 20%, #141E30 0%, #0f172a 35%, #020617 100%);
                color: #E2E8F0;
            }
            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 2rem;
                max-width: 1150px;
            }
            .vault-hero {
                background: linear-gradient(120deg, rgba(59,130,246,0.2), rgba(14,165,233,0.18));
                border: 1px solid rgba(148, 163, 184, 0.25);
                border-radius: 14px;
                padding: 1rem 1.2rem;
                margin-bottom: 1rem;
            }
            .vault-chip {
                display: inline-block;
                padding: 0.2rem 0.55rem;
                border-radius: 999px;
                border: 1px solid rgba(148, 163, 184, 0.25);
                margin-right: 0.35rem;
                font-size: 0.78rem;
                color: #cbd5e1;
            }
            .stTabs [data-baseweb="tab-list"] button {
                border-radius: 10px 10px 0 0;
            }
            .stSidebar {
                border-right: 1px solid rgba(148, 163, 184, 0.2);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
