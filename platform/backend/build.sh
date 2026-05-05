#!/bin/bash
set -e

LIBOQS_INSTALL="$HOME/liboqs-install"

git clone --depth 1 https://github.com/open-quantum-safe/liboqs.git /tmp/liboqs
cd /tmp/liboqs
mkdir build && cd build
cmake -DBUILD_SHARED_LIBS=ON \
      -DCMAKE_INSTALL_PREFIX="$LIBOQS_INSTALL" \
      -DCMAKE_BUILD_TYPE=Release \
      ..
make -j$(nproc)
make install

# Install into the VENV that Render uses at runtime
/opt/render/project/src/.venv/bin/pip install -r /opt/render/project/src/platform/backend/requirements.txt