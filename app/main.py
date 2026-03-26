"""Streamlit entrypoint for the Quantum-Resistant Vault application."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = Path(__file__).resolve().parent
for candidate in (str(PROJECT_ROOT), str(APP_ROOT)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

import streamlit as st
from dotenv import load_dotenv

from components.status_bar import render_status
from components.theme import apply_theme
from pages.login import render_login_page
from pages.settings import render_settings_page
from pages.vault import render_vault_page
from core import storage


def _init_state() -> None:
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "session" not in st.session_state:
        st.session_state["session"] = None
    if "status_message" not in st.session_state:
        st.session_state["status_message"] = ""
    if "status_level" not in st.session_state:
        st.session_state["status_level"] = "info"


def _logout() -> None:
    st.session_state["authenticated"] = False
    st.session_state["session"] = None
    st.session_state["status_message"] = "Logged out successfully."
    st.session_state["status_level"] = "success"
    st.rerun()


def main() -> None:
    load_dotenv()
    st.set_page_config(page_title="Quantum Vault", page_icon="🔐", layout="wide")
    apply_theme()
    _init_state()

    db_path = os.getenv("DB_PATH", "vault.db")
    storage.init_db(db_path)
    db_conn = storage.get_connection(db_path)

    # Display one-time status messages.
    if st.session_state.get("status_message"):
        render_status(st.session_state["status_message"], st.session_state.get("status_level", "info"))
        st.session_state["status_message"] = ""

    if not st.session_state["authenticated"]:
        render_login_page(db_conn)
        return

    session = st.session_state.get("session")
    if not session:
        st.session_state["authenticated"] = False
        st.rerun()

    st.sidebar.markdown("## 🔐 Quantum Vault")
    st.sidebar.caption("Post-quantum secure personal vault")
    st.sidebar.markdown("<span class='vault-chip'>ML-KEM</span><span class='vault-chip'>ML-DSA</span><span class='vault-chip'>AES-256-GCM</span>", unsafe_allow_html=True)
    st.sidebar.divider()
    page = st.sidebar.radio("Navigate", ["Vault", "Settings"], index=0)
    if st.sidebar.button("Logout", use_container_width=True):
        _logout()

    if page == "Vault":
        render_vault_page(session)
    elif page == "Settings":
        render_settings_page(session)


if __name__ == "__main__":
    main()
