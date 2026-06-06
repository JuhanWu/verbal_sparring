#!/bin/bash
# serve_adversarial.sh
# Starts the vLLM server serving google/gemma-4-E4B-it with the referee adapter.

# Enforce script error trapping
set -euo pipefail

MODEL_PATH="google/gemma-4-E4B-it"
ADAPTER_PATH="./referee_lora_output/referee_agent"
PORT=8001

echo "🚀 Launching vLLM Engine on Port ${PORT}..."
echo "Model: ${MODEL_PATH}"
echo "Adapter Path: ${ADAPTER_PATH}"

# Launch vLLM with LoRA enabled and the referee adapter loaded
vllm serve "${MODEL_PATH}" \
  --port "${PORT}" \
  --served-model-name gemma4-referee \
  --gpu-memory-utilization 0.85 \
  --max-model-len 2048 \
  --enable-lora \
  --lora-modules "referee_roast=${ADAPTER_PATH}" \
  --enforce-eager
