#!/bin/bash
set -e

# Install liboqs to a local directory (no sudo needed)
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

# Tell the system where to find the shared library
export LD_LIBRARY_PATH="$LIBOQS_INSTALL/lib:$LIBOQS_INSTALL/lib64:$LD_LIBRARY_PATH"

# Now install Python deps
cd /opt/render/project/src
pip install -r requirements.txt