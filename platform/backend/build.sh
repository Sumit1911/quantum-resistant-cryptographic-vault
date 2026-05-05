#!/bin/bash
set -e

# Install liboqs C library from source
apt-get install -y cmake gcc g++ libssl-dev || true

git clone --depth 1 https://github.com/open-quantum-safe/liboqs.git /tmp/liboqs
cd /tmp/liboqs
cmake -DBUILD_SHARED_LIBS=ON -DCMAKE_INSTALL_PREFIX=/usr/local .
make -j$(nproc)
make install
ldconfig

# Now install Python deps
pip install -r requirements.txt