"""Login and registration page for the Streamlit vault UI."""

from __future__ import annotations

import streamlit as st

from components.status_bar import render_status
from core import vault_manager


def render_login_page(db_conn) -> None:
    """Render login/register tabs and update session state on success."""
    st.markdown(
        """
        <div class="vault-hero">
            <h2 style="margin:0;">🔐 Quantum-Resistant Vault</h2>
            <p style="margin:0.4rem 0 0 0;color:#cbd5e1;">
                Store sensitive files with post-quantum cryptography built for harvest-now-decrypt-later defense.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Master Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login to Vault", use_container_width=True, type="primary")

        if submitted:
            session = vault_manager.login(username.strip(), password, db_conn)
            if session is None:
                render_status("Invalid credentials. Please try again.", "error")
            else:
                st.session_state["authenticated"] = True
                st.session_state["session"] = session
                st.session_state["status_message"] = "Logged in successfully."
                st.session_state["status_level"] = "success"
                st.rerun()

    with register_tab:
        with st.form("register_form", clear_on_submit=False):
            username = st.text_input("Username", key="register_username")
            password = st.text_input("Master Password", type="password", key="register_password")
            confirm_password = st.text_input(
                "Confirm Master Password", type="password", key="register_confirm_password"
            )
            submitted = st.form_submit_button("Create Account", use_container_width=True)

        if submitted:
            if not username.strip() or not password:
                render_status("Username and password are required.", "warning")
            elif password != confirm_password:
                render_status("Passwords do not match.", "warning")
            else:
                try:
                    vault_manager.register(username.strip(), password, db_conn)
                except Exception:
                    render_status("Unable to register. Username may already exist.", "error")
                else:
                    render_status("Registration successful. Please login.", "success")
