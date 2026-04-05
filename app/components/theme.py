"""Theme helpers for consistent, polished Streamlit UI styling."""

from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    """Inject custom CSS theme for app polish and readability."""
    st.markdown(
        """
        <style>
            html, body, [data-testid="stAppViewContainer"] {
                background: #0D0D14;
                color: #E2E2F0;
            }
            .block-container {
                max-width: 1150px;
                padding-top: 1.25rem;
                padding-bottom: 2rem;
            }
            [data-testid="stSidebar"] {
                background: #0A0A12;
                border-right: 1px solid #1E1E30;
            }
            [data-testid="stSidebarNav"] a {
                color: #7070A0 !important;
                font-size: 13px;
                letter-spacing: 0.04em;
                padding: 6px 12px;
                border-radius: 6px;
                transition: all 0.15s;
            }
            [data-testid="stSidebarNav"] a:hover,
            [data-testid="stSidebarNav"] a[aria-selected="true"] {
                color: #E2E2F0 !important;
                background: #1A1A2E;
            }
            .vault-card {
                background: #13131F;
                border: 1px solid #1E1E30;
                border-radius: 12px;
                padding: 20px 22px;
                margin-bottom: 16px;
            }
            .vault-hero {
                background: #13131F;
                border: 1px solid #1E1E30;
                border-radius: 12px;
                padding: 16px 20px;
                margin-bottom: 16px;
            }
            .vault-chip {
                display: inline-block;
                background: rgba(108,99,255,0.15);
                color: #6C63FF;
                border: 1px solid rgba(108,99,255,0.3);
                border-radius: 999px;
                font-size: 11px;
                font-family: monospace;
                padding: 3px 10px;
                letter-spacing: 0.05em;
                margin-right: 0.35rem;
            }
            [data-testid="stTextInput"] input,
            [data-testid="stTextInputRootElement"] input {
                background: #0D0D14 !important;
                border: 1px solid #2A2A40 !important;
                border-radius: 8px !important;
                color: #E2E2F0 !important;
                font-family: monospace !important;
                font-size: 14px !important;
            }
            [data-testid="stTextInput"] input:focus {
                border-color: #6C63FF !important;
                box-shadow: 0 0 0 3px rgba(108,99,255,0.15) !important;
            }
            [data-testid="stButton"] > button {
                background: linear-gradient(135deg, #6C63FF 0%, #4B44CC 100%) !important;
                border: none !important;
                border-radius: 8px !important;
                color: #fff !important;
                font-family: monospace !important;
                font-size: 14px !important;
                font-weight: 600 !important;
                letter-spacing: 0.05em !important;
                transition: opacity 0.15s, transform 0.1s !important;
            }
            [data-testid="stButton"] > button:hover {
                opacity: 0.88 !important;
                transform: translateY(-1px) !important;
            }
            [data-testid="stTabs"] [role="tab"] {
                color: #5A5A80;
                font-family: monospace;
                font-size: 13px;
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }
            [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
                color: #6C63FF;
                border-bottom: 2px solid #6C63FF;
            }
            [data-testid="stFileUploader"] {
                background: #0D0D14;
                border: 1px dashed #2A2A40;
                border-radius: 10px;
                padding: 14px;
            }
            [data-testid="metric-container"] {
                background: #13131F;
                border: 1px solid #1E1E30;
                border-radius: 10px;
                padding: 12px;
            }
            #MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
