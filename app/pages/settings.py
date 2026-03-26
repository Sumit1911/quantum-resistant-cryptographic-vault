"""Settings page with key fingerprints and password rotation."""

from __future__ import annotations

import hashlib

import streamlit as st

from components.status_bar import render_status
from core import vault_manager


def _fingerprint(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def render_settings_page(session: dict) -> None:
    """Render key fingerprints and change-master-password controls."""
    st.markdown(
        """
        <div class="vault-hero">
            <h3 style="margin:0;">⚙️ Security Settings</h3>
            <p style="margin:0.35rem 0 0 0;color:#cbd5e1;">
                Review key fingerprints and rotate your master password securely.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.subheader("Public Key Fingerprints")
        st.caption("Use these fingerprints for external verification/audits.")
        st.code(f"Kyber public key SHA-256: {_fingerprint(session['kyber_pk'])}")
        st.code(f"Dilithium public key SHA-256: {_fingerprint(session['dilithium_pk'])}")

    with st.container(border=True):
        st.subheader("Change Master Password")
        st.caption("This re-wraps private keys with a key derived from your new password.")
        with st.form("change_password_form", clear_on_submit=True):
            old_password = st.text_input("Current Master Password", type="password")
            new_password = st.text_input("New Master Password", type="password")
            confirm_new_password = st.text_input("Confirm New Master Password", type="password")
            submitted = st.form_submit_button("Update Password", use_container_width=True, type="primary")

    if submitted:
        if not old_password or not new_password:
            render_status("Current and new password are required.", "warning")
        elif new_password != confirm_new_password:
            render_status("New password confirmation does not match.", "warning")
        else:
            ok = vault_manager.change_master_password(session, old_password, new_password)
            if ok:
                render_status("Master password updated successfully.", "success")
            else:
                render_status("Failed to update password. Check current password.", "error")
