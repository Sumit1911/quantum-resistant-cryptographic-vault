"""Vault page for listing, uploading, downloading, and deleting files."""

from __future__ import annotations

import streamlit as st

from components.file_card import render_file_card
from components.status_bar import render_metric_row, render_status
from core import vault_manager
from core.vault_manager import IntegrityError


def render_vault_page(session: dict) -> None:
    """Render vault management interface."""
    st.markdown(
        """
        <div class="vault-hero">
            <h3 style="margin:0;">📁 Your Vault</h3>
            <p style="margin:0.35rem 0 0 0;color:#cbd5e1;">
                Upload files, retrieve encrypted content, and manage secure artifacts.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("#### 🚀 Upload new item")
        with st.form("upload_form", clear_on_submit=True):
            uploaded = st.file_uploader("Select file", type=None)
            submit_upload = st.form_submit_button("Encrypt & Store", use_container_width=True, type="primary")

    if submit_upload:
        if uploaded is None:
            render_status("Please choose a file to upload.", "warning")
        else:
            try:
                item_id = vault_manager.store_file(
                    session,
                    uploaded.name,
                    uploaded.getvalue(),
                    uploaded.type or "application/octet-stream",
                )
            except Exception:
                render_status("Failed to store file.", "error")
            else:
                render_status(f"Stored file successfully (item #{item_id}).", "success")

    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:20px;">
            <span style="font-family:monospace; font-size:13px; color:#5A5A80;
                         letter-spacing:0.08em; text-transform:uppercase;">Vault contents</span>
            <div style="flex:1; height:1px; background:#1E1E30;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    items = vault_manager.list_files(session)
    total_size = sum((item.original_size or 0) for item in items)
    render_metric_row(len(items), total_size)

    if not items:
        st.info("No items in vault yet.")
        return

    for item in items:
        download_clicked, delete_clicked = render_file_card(item)

        if download_clicked:
            try:
                plaintext = vault_manager.retrieve_file(session, item.id)
            except IntegrityError:
                render_status("Tampered file detected. Download blocked.", "error")
            except Exception:
                render_status("Failed to retrieve file.", "error")
            else:
                if plaintext is None:
                    render_status("File not found.", "warning")
                else:
                    st.download_button(
                        label=f"Click to download {item.item_name}",
                        data=plaintext,
                        file_name=item.item_name,
                        mime=item.mime_type or "application/octet-stream",
                        key=f"download_button_{item.id}",
                        use_container_width=True,
                    )

        if delete_clicked:
            st.session_state["confirm_delete_id"] = item.id

        if st.session_state.get("confirm_delete_id") == item.id:
            st.warning(f"Confirm deletion for: {item.item_name}")
            c1, c2 = st.columns(2)
            with c1:
                confirm = st.button(
                    "✅ Confirm delete",
                    key=f"confirm_delete_{item.id}",
                    use_container_width=True,
                )
            with c2:
                cancel = st.button(
                    "Cancel",
                    key=f"cancel_delete_{item.id}",
                    use_container_width=True,
                )

            if confirm:
                deleted = vault_manager.delete_file(session, item.id)
                st.session_state.pop("confirm_delete_id", None)
                if deleted:
                    render_status(f"Deleted {item.item_name}.", "success")
                    st.rerun()
                else:
                    render_status("Delete failed or item no longer exists.", "warning")
            elif cancel:
                st.session_state.pop("confirm_delete_id", None)
                st.rerun()
