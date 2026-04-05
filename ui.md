# ui_upgrade.md — Quantum Vault UI/UX Overhaul
> Cline instruction file. Do not break existing Streamlit logic — only touch CSS, layout, and visual presentation.

---

## Current State
- Streamlit app running on `localhost:8501`
- Pages: `main`, `login`, `settings`, `vault`
- Dark theme, flat black backgrounds, plain red button, no visual hierarchy
- Sidebar shows raw page names

## Goal
Sophisticated dark UI — feels like a security product (think 1Password / Bitwarden meets a terminal aesthetic). Keep all existing Python logic untouched.

---

## Step 1 — Global Theme (`~/.streamlit/config.toml`)

Create or overwrite this file:

```toml
[theme]
base = "dark"
primaryColor = "#6C63FF"
backgroundColor = "#0D0D14"
secondaryBackgroundColor = "#13131F"
textColor = "#E2E2F0"
font = "monospace"
```

---

## Step 2 — Inject Global CSS

Add this block at the top of `main.py` (and any page that needs it), called once:

```python
import streamlit as st

def inject_css():
    st.markdown("""
    <style>
    /* ── Base ── */
    html, body, [data-testid="stAppViewContainer"] {
        background: #0D0D14;
    }
    [data-testid="stSidebar"] {
        background: #0A0A12;
        border-right: 1px solid #1E1E30;
    }

    /* ── Sidebar nav links ── */
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

    /* ── Cards / containers ── */
    .vault-card {
        background: #13131F;
        border: 1px solid #1E1E30;
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 16px;
    }

    /* ── Inputs ── */
    [data-testid="stTextInput"] input,
    [data-testid="stTextInputRootElement"] input {
        background: #0D0D14 !important;
        border: 1px solid #2A2A40 !important;
        border-radius: 8px !important;
        color: #E2E2F0 !important;
        font-family: monospace !important;
        font-size: 14px !important;
        padding: 10px 14px !important;
        transition: border-color 0.15s;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #6C63FF !important;
        box-shadow: 0 0 0 3px rgba(108,99,255,0.15) !important;
    }

    /* ── Primary button ── */
    [data-testid="stButton"] > button[kind="primary"],
    [data-testid="stButton"] > button {
        background: linear-gradient(135deg, #6C63FF 0%, #4B44CC 100%) !important;
        border: none !important;
        border-radius: 8px !important;
        color: #fff !important;
        font-family: monospace !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        padding: 10px 24px !important;
        transition: opacity 0.15s, transform 0.1s !important;
        width: 100%;
    }
    [data-testid="stButton"] > button:hover {
        opacity: 0.88 !important;
        transform: translateY(-1px) !important;
    }
    [data-testid="stButton"] > button:active {
        transform: translateY(0px) !important;
    }

    /* ── Tabs ── */
    [data-testid="stTabs"] [role="tab"] {
        color: #5A5A80;
        font-family: monospace;
        font-size: 13px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding-bottom: 8px;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: #6C63FF;
        border-bottom: 2px solid #6C63FF;
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background: #0D0D14;
        border: 1px dashed #2A2A40;
        border-radius: 10px;
        padding: 20px;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #6C63FF;
    }

    /* ── Status badges ── */
    .badge-secure {
        display: inline-block;
        background: rgba(108,99,255,0.15);
        color: #6C63FF;
        border: 1px solid rgba(108,99,255,0.3);
        border-radius: 99px;
        font-size: 11px;
        font-family: monospace;
        padding: 3px 10px;
        letter-spacing: 0.05em;
    }
    .badge-warning {
        background: rgba(255,165,0,0.12);
        color: #FFA500;
        border-color: rgba(255,165,0,0.3);
    }

    /* ── Metrics row ── */
    [data-testid="metric-container"] {
        background: #13131F;
        border: 1px solid #1E1E30;
        border-radius: 10px;
        padding: 16px;
    }

    /* ── Hide Streamlit branding ── */
    #MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
```

Call `inject_css()` at the top of every page file.

---

## Step 3 — Login Page (`pages/login.py`)

Replace the plain header with this branded block:

```python
st.markdown("""
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
""", unsafe_allow_html=True)
```

Wrap the login form in a card:

```python
st.markdown('<div class="vault-card">', unsafe_allow_html=True)
# ... existing login tab content (username input, password input, button) ...
st.markdown('</div>', unsafe_allow_html=True)
```

Add a trust line below the card:

```python
st.markdown("""
<p style="text-align:center; color:#3A3A55; font-size:11px;
           font-family:monospace; margin-top:16px; letter-spacing:0.04em;">
    🔒 &nbsp; end-to-end encrypted &nbsp;·&nbsp; keys never leave your device
</p>
""", unsafe_allow_html=True)
```

---

## Step 4 — Sidebar

Replace raw page names with a styled logo + nav at the top of `main.py`:

```python
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px 0 24px; border-bottom: 1px solid #1E1E30; margin-bottom:16px;">
        <span style="font-family:monospace; font-size:15px; font-weight:700;
                     color:#6C63FF; letter-spacing:0.1em;">⬡ QVAULT</span>
        <span style="display:block; font-size:10px; color:#3A3A55;
                     font-family:monospace; margin-top:2px; letter-spacing:0.06em;">
            v1.0 · PQC ENABLED
        </span>
    </div>
    """, unsafe_allow_html=True)
```

---

## Step 5 — Vault Page (`pages/vault.py`)

Each stored file card should use this pattern:

```python
def render_file_card(item_name, item_type, size_kb, created_at):
    st.markdown(f"""
    <div class="vault-card" style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <span style="font-family:monospace; font-size:14px; color:#E2E2F0;">
                {'📄' if item_type == 'file' else '🔑'} &nbsp; {item_name}
            </span>
            <br>
            <span style="font-family:monospace; font-size:11px; color:#5A5A80;">
                {size_kb} KB &nbsp;·&nbsp; {created_at} &nbsp;·&nbsp;
            </span>
            <span class="badge-secure">KYBER-512</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
```

Add a section header above the file list:

```python
st.markdown("""
<div style="display:flex; align-items:center; gap:10px; margin-bottom:20px;">
    <span style="font-family:monospace; font-size:13px; color:#5A5A80;
                 letter-spacing:0.08em; text-transform:uppercase;">Vault contents</span>
    <div style="flex:1; height:1px; background:#1E1E30;"></div>
</div>
""", unsafe_allow_html=True)
```

---

## Step 6 — Settings Page (`pages/settings.py`)

Wrap each setting group in a card and show key fingerprints in a monospace code style:

```python
st.markdown('<div class="vault-card">', unsafe_allow_html=True)
st.markdown("**Kyber-512 Public Key Fingerprint**")
st.code(kyber_fingerprint_hex, language=None)  # already monospace, styled by theme
st.markdown('</div>', unsafe_allow_html=True)
```

---

## What NOT to change
- Do not modify any function in `core/` (auth, crypto, storage, vault_manager)
- Do not change `st.session_state` keys or login/logout logic
- Do not change page file names or routing
- Do not add new Python dependencies — all changes are pure CSS + `st.markdown()`

---

## Checklist for Cline

- [ ] Create `~/.streamlit/config.toml` with theme block from Step 1
- [ ] Add `inject_css()` function to `main.py` and call it on load
- [ ] Import and call `inject_css()` at top of `login.py`, `vault.py`, `settings.py`
- [ ] Replace login header with branded block (Step 3)
- [ ] Wrap login form in `.vault-card` div (Step 3)
- [ ] Add sidebar logo block (Step 4)
- [ ] Apply file card template to vault item list (Step 5)
- [ ] Add vault section header (Step 5)
- [ ] Wrap settings groups in cards (Step 6)
- [ ] Verify app still runs: `streamlit run app/main.py`
- [ ] Verify login still works end-to-end after changes