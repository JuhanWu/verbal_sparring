# dump_environment.py
"""Environment diagnostics and migration export tool.

This script inspects the active virtual environment's dependencies (including
PyTorch CUDA bindings, HF HuggingFace libraries, API hosting frameworks) and formats
both a strict lockfile (requirements_freeze.txt) and a comprehensive deployment
walkthrough (environment_info.md) for 100% reproducible server migration.
"""

import os
import sys
from typing import Dict, List


def get_package_version(package_name: str) -> str:
    """Attempts to dynamically import and retrieve a package version.

    Args:
        package_name: The name of the Python package to inspect.

    Returns:
        Version string or "NOT_INSTALLED".
    """
    try:
        # Special alias mappings for import paths vs package names
        import_name = package_name
        if package_name == "pillow":
            import_name = "PIL"
        
        module = __import__(import_name)
        
        if hasattr(module, "__version__"):
            return str(module.__version__)
        elif hasattr(module, "version"):
            # Try nested attribute (some modules use module.version.__version__)
            version_attr = getattr(module, "version")
            if isinstance(version_attr, str):
                return version_attr
            elif hasattr(version_attr, "__version__"):
                return str(version_attr.__version__)
        
        return "INSTALLED_NO_VERSION"
    except ImportError:
        return "NOT_INSTALLED"


def main() -> None:
    """Probes CUDA configurations, maps package versions, and writes target migration artifacts."""
    print("🔍 Probing active virtual environment and GPU runtime...")
    
    # 1. Probing GPU/PyTorch/CUDA configurations
    cuda_available: bool = False
    cuda_version: str = "N/A"
    pytorch_version: str = "N/A"
    
    try:
        import torch
        pytorch_version = str(torch.__version__)
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            cuda_version = str(torch.version.cuda)
    except ImportError:
        print("❌ Critical: PyTorch is not installed in the active environment.")

    # 2. Package categories to track for migration
    core_packages: List[str] = [
        "torch",
        "transformers",
        "peft",
        "trl",
        "accelerate",
        "bitsandbytes",
        "datasets",
        "fastapi",
        "uvicorn",
        "websockets",
        "requests",
        "matplotlib",
        "numpy",
        "Cython",
        "setuptools",
        "pillow"
    ]
    
    versions_map: Dict[str, str] = {}
    for pkg in core_packages:
        versions_map[pkg] = get_package_version(pkg)

    # 3. Generate strict requirements_freeze.txt (only listing successfully installed dependencies)
    freeze_lines: List[str] = ["# Auto-generated lockfile for Server Migration\n"]
    for pkg, ver in versions_map.items():
        if ver not in ("NOT_INSTALLED", "INSTALLED_NO_VERSION"):
            # Map clean package names back to PIP format
            pip_name = pkg
            if pkg == "pillow":
                pip_name = "Pillow"
            freeze_lines.append(f"{pip_name}=={ver}\n")
            
    freeze_path = "requirements_freeze.txt"
    with open(freeze_path, "w", encoding="utf-8") as f:
        f.writelines(freeze_lines)
    print(f"✅ Generated strict requirements file: {freeze_path}")

    # 4. Generate deployment walkthrough (environment_info.md)
    # PyTorch install command recommendation based on CUDA binding found
    pytorch_install_cmd = "pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu124"
    if cuda_version != "N/A":
        cu_suffix = cuda_version.replace(".", "")
        pytorch_install_cmd = f"pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu{cu_suffix}"

    info_content = f"""# Server Environment Migration & Deployment Report

This report documents the exact system package configurations, CUDA drivers, and Python dependencies required to successfully deploy the **Verbal Sparring (Toxic Referee & Player)** system on a new target server.

## 1. Runtime Platform Diagnostics

*   **Python Target Interpreter**: `{sys.version.split()[0]}`
*   **PyTorch Binding**: `{pytorch_version}`
*   **CUDA Platform Support**: `{"Enabled" if cuda_available else "Disabled"}`
*   **CUDA Driver Version**: `{cuda_version}`

---

## 2. Dynamic Package Status

Below is the verified status of the core dependencies in the source environment:

| Package Group / Name | Version in Source Environment | Required Role in Architecture |
| :--- | :---: | :--- |
| **torch** | `{versions_map["torch"]}` | Deep Learning & Backprop Runtime |
| **transformers** | `{versions_map["transformers"]}` | LLM Model Loading & Tokenization |
| **peft** | `{versions_map["peft"]}` | Multi-Adapter LoRA Weight Updates |
| **trl** | `{versions_map["trl"]}` | DPOTrainer & Alignment Alignment |
| **accelerate** | `{versions_map["accelerate"]}` | HuggingFace Multi-GPU Offloading |
| **bitsandbytes** | `{versions_map["bitsandbytes"]}` | 4-Bit NF4 Quantized Inference & SFT |
| **datasets** | `{versions_map["datasets"]}` | DPO/SFT JSON Data Stream Loading |
| **fastapi** | `{versions_map["fastapi"]}` | API Server Hosting (serve_referee.py) |
| **uvicorn** | `{versions_map["uvicorn"]}` | ASGI High-Performance Server Engine |
| **websockets** | `{versions_map["websockets"]}` | Real-Time Game WebSockets Protocol |
| **requests** | `{versions_map["requests"]}` | Ollama API HTTP Request Client |
| **matplotlib** | `{versions_map["matplotlib"]}` | Metric Analytics & Chart Generating |
| **numpy** | `{versions_map["numpy"]}` | Numerical Computation & Seed Controls |
| **Cython** | `{versions_map["Cython"]}` | Compilation of Performance Critical Core |
| **setuptools** | `{versions_map["setuptools"]}` | Extension Compiling Tools |
| **Pillow** | `{versions_map["pillow"]}` | Image Preprocessing (Vision Tower input) |

---

## 3. Migration Setup Instructions (Target Server)

Follow these steps on the new server to reproduce the environment:

### Step 3.1: Initialize Conda Virtual Environment
Create a clean Python {sys.version_mutated if hasattr(sys, 'version_mutated') else '3.10'} environment:
```bash
conda create -n verbal-sparring python=3.10 -y
conda activate verbal-sparring
```

### Step 3.2: Install PyTorch with Native CUDA Bindings
Install the exact matching PyTorch build:
```bash
{pytorch_install_cmd}
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
ollama pull {os.environ.get("OLLAMA_MODEL", "qwen3.6:latest")}
```
"""

    info_path = "environment_info.md"
    with open(info_path, "w", encoding="utf-8") as f:
        f.write(info_content)
    print(f"✅ Generated migration guidelines: {info_path}")
    print("\n🚀 Migration preparation complete! Copy requirements_freeze.txt and environment_info.md to your target server.")


if __name__ == "__main__":
    main()
