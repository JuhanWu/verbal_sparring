#!/bin/bash
# setup_env.sh
# Automates the creation of a Conda environment and installs GPU-accelerated dependencies.
# Uses pip for large package installation to mitigate Conda incomplete download issues.

# Enforce script safety
set -euo pipefail

ENV_NAME="verbal-sparring"
PYTHON_VERSION="3.10"

echo "🍀 Creating Conda environment: ${ENV_NAME} with Python ${PYTHON_VERSION}..."
# Create the environment with only base python and pip
conda create -y -n "${ENV_NAME}" python="${PYTHON_VERSION}" pip

echo "🔄 Activating Conda environment..."
eval "$(conda shell.bash hook)"
conda activate "${ENV_NAME}"

echo "🔥 Installing PyTorch (CUDA 12.1) via pip with extended timeout..."
# Using pip with --default-timeout to prevent connection drops on large files
pip install --no-cache-dir --default-timeout=1000 \
  torch==2.1.2 \
  torchvision==0.16.2 \
  --index-url https://download.pytorch.org/whl/cu121

echo "📦 Installing HuggingFace and PEFT libraries for model training..."
pip install --no-cache-dir --default-timeout=1000 \
  transformers==4.38.2 \
  peft==0.9.0 \
  trl==0.8.1 \
  accelerate==0.27.2 \
  bitsandbytes==0.42.0 \
  datasets==2.18.0 \
  Pillow==10.2.0

echo "🎮 Installing Game Server dependencies..."
pip install --no-cache-dir \
  fastapi==0.110.0 \
  uvicorn==0.28.0 \
  websockets==12.0 \
  requests==2.31.0 \
  Cython==3.0.8

echo "✅ Environment setup complete! Run 'conda activate ${ENV_NAME}' to start."
