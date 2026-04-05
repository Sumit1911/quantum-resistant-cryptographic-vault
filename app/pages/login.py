"""Login and registration page for the Streamlit vault UI."""

from __future__ import annotations

import streamlit as st

from components.status_bar import render_status
from core import vault_manager


def render_login_page(db_conn) -> None:
    """Render login/register tabs and update session state on success."""
    st.markdown(
        """
        <div style="text-align:center; padding: 40px 0 32px;">
            <div style="font-size:40px; margin-bottom:8px;">🔐</div>
            <h1 style="color:#E2E2F0; font-family:monospace; font-size:26px;
                       font-weight:700; letter-spacing:0.06em; margin:0;">
                QUANTUM VAULT
            </h1>
            <p style="color:#5A5A80; font-size:13px; font-family:monospace;
                      margin-top:6px; letter-spacing:0.04em;">
                post-quantum encryption · kyber-512 · dilithium
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        st.markdown('<div class="vault-card">', unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Master Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login to Vault", use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

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
        st.markdown('<div class="vault-card">', unsafe_allow_html=True)
        with st.form("register_form", clear_on_submit=False):
            username = st.text_input("Username", key="register_username")
            password = st.text_input("Master Password", type="password", key="register_password")
            confirm_password = st.text_input(
                "Confirm Master Password", type="password", key="register_confirm_password"
            )
            submitted = st.form_submit_button("Create Account", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

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

    st.markdown(
        """
        <p style="text-align:center; color:#3A3A55; font-size:11px;
                   font-family:monospace; margin-top:16px; letter-spacing:0.04em;">
            🔒 &nbsp; end-to-end encrypted &nbsp;·&nbsp; keys never leave your device
        </p>
        """,
        unsafe_allow_html=True,
    )
