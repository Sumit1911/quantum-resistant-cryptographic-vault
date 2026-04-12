# Quantum-Resistant Cryptographic Vault

Post-quantum security project with two runnable stacks:

- `app/` legacy Streamlit vault (fully tested core flows)
- `platform/` modern FastAPI + React research platform (Arena, Attack Lab, Vault Lens)

## Quick Start

Run from project root:

```bash
make run-platform
```

This starts:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173`

## Other Common Commands

```bash
make run-streamlit   # legacy Streamlit app
make run-backend     # platform backend only
make run-frontend    # platform frontend only
make test            # quick tests
make test-all        # unit + integration + security
make setup-db        # initialize vault.db
make benchmark       # benchmark report
make keygen          # key generation utility
```

You can also use the unified runner directly:

```bash
python3 scripts/run_project.py platform
python3 scripts/run_project.py streamlit
```

## Clean Project Structure

```text
.
├── app/                # Streamlit UI
├── core/               # Auth, crypto, storage, vault orchestration
├── db/                 # Schema + migrations
├── docs/               # Architecture/API/threat model docs
├── platform/
│   ├── backend/        # FastAPI API services
│   └── frontend/       # React + Vite app
├── scripts/            # Setup, benchmark, keygen, unified runner
└── tests/              # Unit/integration/security/benchmarks
```

## Install Notes

- Python deps (legacy + tests): `pip install -r requirements.txt`
- Platform backend deps: `pip install -r platform/backend/requirements.txt`
- Platform frontend deps: `cd platform/frontend && npm install`

If `liboqs` is not available, install native `liboqs` first, then `liboqs-python`.

## Streamlit PQC Setup (Windows + macOS)

The Streamlit vault (`make run-streamlit`) uses real PQC algorithms from `liboqs`:
- KEM: Kyber-512
- Signature: Dilithium / ML-DSA

### Windows

1. Create/activate local virtual environment and install Python deps:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install "git+https://github.com/open-quantum-safe/liboqs-python.git@v0.14"
```

2. Install Visual Studio Build Tools with C++ workload/components:
- Desktop development with C++
- MSVC v143 x64/x86
- Windows SDK
- C++ CMake tools for Windows

3. Build and install native `liboqs`:
```powershell
git clone --depth 1 --branch 0.14.0 https://github.com/open-quantum-safe/liboqs.git C:\Users\Admin\_oqs-src\liboqs
cmake -S C:\Users\Admin\_oqs-src\liboqs -B C:\Users\Admin\_oqs-src\liboqs\build -DBUILD_SHARED_LIBS=ON -DOQS_BUILD_ONLY_LIB=ON -DCMAKE_WINDOWS_EXPORT_ALL_SYMBOLS=TRUE -DCMAKE_INSTALL_PREFIX=C:\Users\Admin\_oqs
cmake --build C:\Users\Admin\_oqs-src\liboqs\build --config Release --target install
setx OQS_INSTALL_PATH C:\Users\Admin\_oqs
```

4. Open a new terminal after `setx`, then run Streamlit:
```powershell
make run-streamlit
```

### macOS

1. Install build prerequisites:
```bash
xcode-select --install
brew install cmake
```

2. Create/activate local virtual environment and install Python deps:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install "git+https://github.com/open-quantum-safe/liboqs-python.git@v0.14"
```

3. Build and install native `liboqs`:
```bash
git clone --depth 1 --branch 0.14.0 https://github.com/open-quantum-safe/liboqs.git "$HOME/_oqs-src/liboqs"
cmake -S "$HOME/_oqs-src/liboqs" -B "$HOME/_oqs-src/liboqs/build" -DBUILD_SHARED_LIBS=ON -DOQS_BUILD_ONLY_LIB=ON -DCMAKE_INSTALL_PREFIX="$HOME/_oqs"
cmake --build "$HOME/_oqs-src/liboqs/build" --parallel
cmake --install "$HOME/_oqs-src/liboqs/build"
echo 'export OQS_INSTALL_PATH="$HOME/_oqs"' >> ~/.zshrc
source ~/.zshrc
```

4. Run Streamlit:
```bash
make run-streamlit
```

### Verify PQC Is Active

Run from project root:
```bash
.venv/Scripts/python.exe -c "import oqs; print(oqs.oqs_version()); print('Kyber512' in oqs.get_enabled_kem_mechanisms()); print(any(x in oqs.get_enabled_sig_mechanisms() for x in ['Dilithium3','ML-DSA-65']))"
```

On macOS/Linux use:
```bash
.venv/bin/python -c "import oqs; print(oqs.oqs_version()); print('Kyber512' in oqs.get_enabled_kem_mechanisms()); print(any(x in oqs.get_enabled_sig_mechanisms() for x in ['Dilithium3','ML-DSA-65']))"
```

Expected output includes:
- `True` for `Kyber512`
- `True` for Dilithium/ML-DSA support
