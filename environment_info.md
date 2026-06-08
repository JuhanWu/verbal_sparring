# Server Environment Migration & Deployment Report

This report documents the exact system package configurations, CUDA drivers, and Python dependencies required to successfully deploy the **Verbal Sparring (Toxic Referee & Player)** system on a new target server.

## 1. Runtime Platform Diagnostics

*   **Python Target Interpreter**: `3.12.13`
*   **PyTorch Binding**: `2.11.0+cu129`
*   **CUDA Platform Support**: `Enabled`
*   **CUDA Driver Version**: `12.9`

---

## 2. Dynamic Package Status

Below is the verified status of the core dependencies in the source environment:

| Package Group / Name | Version in Source Environment | Required Role in Architecture |
| :--- | :---: | :--- |
| **torch** | `2.11.0+cu129` | Deep Learning & Backprop Runtime |
| **transformers** | `5.10.2` | LLM Model Loading & Tokenization |
| **peft** | `NOT_INSTALLED` | Multi-Adapter LoRA Weight Updates |
| **trl** | `NOT_INSTALLED` | DPOTrainer & Alignment Alignment |
| **accelerate** | `NOT_INSTALLED` | HuggingFace Multi-GPU Offloading |
| **bitsandbytes** | `NOT_INSTALLED` | 4-Bit NF4 Quantized Inference & SFT |
| **datasets** | `NOT_INSTALLED` | DPO/SFT JSON Data Stream Loading |
| **fastapi** | `0.136.3` | API Server Hosting (serve_referee.py) |
| **uvicorn** | `0.49.0` | ASGI High-Performance Server Engine |
| **websockets** | `16.0` | Real-Time Game WebSockets Protocol |
| **requests** | `2.34.2` | Ollama API HTTP Request Client |
| **matplotlib** | `NOT_INSTALLED` | Metric Analytics & Chart Generating |
| **numpy** | `2.3.5` | Numerical Computation & Seed Controls |
| **Cython** | `NOT_INSTALLED` | Compilation of Performance Critical Core |
| **setuptools** | `80.10.2` | Extension Compiling Tools |
| **Pillow** | `12.2.0` | Image Preprocessing (Vision Tower input) |

---

## 3. Migration Setup Instructions (Target Server)

Follow these steps on the new server to reproduce the environment:

### Step 3.1: Initialize Conda Virtual Environment
Create a clean Python 3.10 environment:
```bash
conda create -n verbal-sparring python=3.10 -y
conda activate verbal-sparring
```

### Step 3.2: Install PyTorch with Native CUDA Bindings
Install the exact matching PyTorch build:
```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu129
```

### Step 3.3: Install Remaining Python Dependencies
Install the remaining packages via the generated lockfile:
```bash
pip install -r requirements_freeze.txt
```

### Step 3.4: Setup Cython Native Modules
Compile the native referee logic extension (referee_core):
```bash
python setup.py build_ext --inplace
```

### Step 3.5: Pull Ollama Models
Deploy Ollama on the new server and pull the correct Qwen judge:
```bash
ollama pull qwen3.6:latest
```
