# generate_dpo_dataset.py
"""Dataset generation script for DPO preference alignment training.

This script loads the SFT-tuned player model, generates K=3 candidate comebacks
for prompts from the SFT dataset, and scores them using the local Ollama
qwen3.6:latest model to establish preference pairs (chosen vs rejected).
"""

import argparse
import json
import os
import random
import time
from typing import Any, Dict, List, Tuple

import requests
import torch
# Workaround for float8 attribute crash on older PyTorch versions
if not hasattr(torch, "float8_e8m0fnu"):
    setattr(torch, "float8_e8m0fnu", torch.float32)

from peft import PeftModel
from transformers import AutoProcessor, AutoModelForImageTextToText, BitsAndBytesConfig

# Configuration parameters
OLLAMA_URL: str = "http://localhost:11434/api/chat"
OLLAMA_MODEL: str = "qwen3.6:latest"
REPRODUCIBILITY_SEED: int = 42


def set_reproducibility_seeds(seed: int = 42) -> None:
    """Locks random seeds to guarantee reproducible candidate generation.

    Args:
        seed: The integer seed value.
    """
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True


def extract_json_payload(text: str) -> Dict[str, Any] | None:
    """Safely extracts JSON dict from LLM markdown response.

    Args:
        text: Raw output string from the language model.

    Returns:
        A dictionary containing parsed metrics, or None if parsing fails.
    """
    cleaned = text.strip()
    for candidate in (cleaned, cleaned.replace("```json", "").replace("```", "").strip()):
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
    return None


def extract_json_list_payload(text: str) -> List[Dict[str, Any]] | None:
    """Safely extracts JSON list from LLM markdown response.

    Args:
        text: Raw output string from the language model.

    Returns:
        A list of dictionaries, or None if parsing fails.
    """
    cleaned = text.strip()
    for candidate in (cleaned, cleaned.replace("```json", "").replace("```", "").strip()):
        try:
            obj = json.loads(candidate)
            if isinstance(obj, list):
                return obj
        except json.JSONDecodeError:
            pass
    return None


def query_ollama_for_score(
    prompt_history: List[Dict[str, str]],
    candidate: str
) -> Tuple[int, str]:
    """Queries local Ollama qwen3.6:latest to score a toxic response.

    Args:
        prompt_history: List of chat messages leading to the comeback.
        candidate: The generated player comeback candidate.

    Returns:
        A tuple of (score_int, evaluation_reason).
    """
    # Build conversational history representation for the judge
    history_str = ""
    for msg in prompt_history:
        role_label = "攻擊方" if msg["role"] == "user" else "防守方"
        history_str += f"{role_label}: {msg['content']}\n"

    opponent_roast = prompt_history[-1]["content"] if prompt_history else ""

    judge_prompt = (
        "你是一位無情、機智且挑剔的「華語毒舌評審」。現在有以下對話背景：\n"
        f"{history_str}\n"
        f"對手最新攻擊為：\"{opponent_roast}\"\n\n"
        f"防守方做出以下反擊：\n"
        f"\"\"\"\n{candidate}\n\"\"\"\n\n"
        "請根據以下標準進行評分（分數範圍為 1 到 50 分，50分最完美）：\n"
        "1. **毒舌與挑釁程度 (Toxic & Provocative)**: 嗆聲是否夠辣？有沒有打中痛點？是否具有攻擊性與冒犯性？\n"
        "2. **機智與幽默感 (Wit & Humor)**: 是否具有諷刺、幽默或機智的雙關？是否流暢？\n"
        "3. **字數與格式遵循 (Length & Formatting)**: 是否在 25 字以內？是否為繁體中文？\n\n"
        "請直接輸出以下 JSON 格式，不要包含任何額外引言或文字說明：\n"
        "{\n"
        "  \"reason\": \"評分簡短理由\",\n"
        "  \"score\": 評分數字\n"
        "}"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": judge_prompt}],
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        if response.status_code == 200:
            result = response.json()
            content = result.get("message", {}).get("content", "")
            parsed = extract_json_payload(content)
            if parsed and "score" in parsed:
                return int(parsed["score"]), parsed.get("reason", "")
    except Exception as e:
        print(f"      [Ollama Error]: Failed to query judge: {e}")
    
    return 10, "Fallback score due to API parsing error"


def query_ollama_for_scores_batch(
    prompt_history: List[Dict[str, str]],
    candidates: List[str]
) -> List[Tuple[str, int]]:
    """Queries local Ollama qwen3.6:latest to score multiple candidate responses in one batch.

    Args:
        prompt_history: List of chat messages leading to the comeback.
        candidates: List of generated player comeback candidates.

    Returns:
        List of tuples containing (candidate_text, score_int).
    """
    # Build conversational history representation for the judge
    history_str = ""
    for msg in prompt_history:
        role_label = "攻擊方" if msg["role"] == "user" else "防守方"
        history_str += f"{role_label}: {msg['content']}\n"

    opponent_roast = prompt_history[-1]["content"] if prompt_history else ""

    candidates_str = ""
    for idx, cand in enumerate(candidates):
        candidates_str += f"候選 {idx + 1}：\n\"\"\"\n{cand}\n\"\"\"\n\n"

    judge_prompt = (
        "你是一位無情、機智且挑剔的「華語毒舌評審」。現在有以下對話背景：\n"
        f"{history_str}\n"
        f"對手最新攻擊為：\"{opponent_roast}\"\n\n"
        "這裡有幾個防守方候選人做出的反擊：\n"
        f"{candidates_str}"
        "請分別根據以下標準為每個候選反擊進行評分（分數範圍為 1 到 50 分，50分最完美）：\n"
        "1. **毒舌與挑釁程度 (Toxic & Provocative)**: 嗆聲是否夠辣？有沒有打中痛點？是否具有攻擊性與冒犯性？\n"
        "2. **機智與幽默感 (Wit & Humor)**: 是否具有諷刺、幽默或機智的雙關？是否流暢？\n"
        "3. **字數與格式遵循 (Length & Formatting)**: 是否在 25 字以內？是否為繁體中文？\n\n"
        "請嚴格輸出以下 JSON list 格式，不要包含任何額外說明或引言：\n"
        "[\n"
        "  {\n"
        "    \"candidate_index\": 1,\n"
        "    \"reason\": \"評分簡短理由\",\n"
        "    \"score\": 評分數字\n"
        "  },\n"
        "  ...\n"
        "]"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": judge_prompt}],
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        if response.status_code == 200:
            result = response.json()
            content = result.get("message", {}).get("content", "")
            parsed = extract_json_list_payload(content)
            if parsed and isinstance(parsed, list):
                # Map parsed score list back to candidates
                scores_map = {}
                for item in parsed:
                    idx_val = item.get("candidate_index")
                    score_val = item.get("score")
                    if idx_val is not None and score_val is not None:
                        scores_map[int(idx_val) - 1] = int(score_val)
                
                # Reconstruct output scores
                out_scores = []
                for idx, cand in enumerate(candidates):
                    score = scores_map.get(idx, 10)  # default fallback score
                    out_scores.append((cand, score))
                return out_scores
    except Exception as e:
        print(f"      [Ollama Batch Error]: Failed to query judge: {e}")

    # Fallback to single queries if batch query fails
    print("      ⚠️ Batch query failed or parsed incorrectly. Falling back to single queries...")
    out_scores = []
    for cand in candidates:
        score, _ = query_ollama_for_score(prompt_history, cand)
        out_scores.append((cand, score))
    return out_scores


def generate_candidates(
    model: PeftModel,
    processor: Any,
    prompt_history: List[Dict[str, str]],
    num_candidates: int = 3
) -> List[str]:
    """Generates K candidate responses in parallel from the SFT model.

    Args:
        model: Loaded PeftModel instance.
        processor: Processor/Tokenizer to format dialogue inputs.
        prompt_history: Contextual messages preceding the target response.
        num_candidates: Number of responses to generate.

    Returns:
        List of generated candidate strings.
    """
    if hasattr(processor, "tokenizer") and hasattr(processor.tokenizer, "apply_chat_template"):
        prompt = processor.tokenizer.apply_chat_template(prompt_history, tokenize=False, add_generation_prompt=True)
    else:
        prompt = processor.apply_chat_template(prompt_history, tokenize=False, add_generation_prompt=True)

    inputs = processor(text=prompt, return_tensors="pt").to(model.device)
    
    # Efficient parallel batch generation
    batched_inputs = {}
    for k, v in inputs.items():
        if isinstance(v, torch.Tensor):
            batched_inputs[k] = v.repeat(num_candidates, *([1] * (v.ndim - 1)))
        else:
            batched_inputs[k] = v

    with torch.no_grad():
        generated_ids = model.generate(
            **batched_inputs,
            max_new_tokens=40,
            do_sample=True,
            temperature=0.85,
            top_p=0.9
        )
    
    candidates = []
    for i in range(num_candidates):
        in_ids = batched_inputs["input_ids"][i]
        out_ids = generated_ids[i]
        trimmed_out_ids = out_ids[len(in_ids):]
        
        # Use processor/tokenizer to decode
        if hasattr(processor, "tokenizer"):
            candidate_text = processor.tokenizer.decode(trimmed_out_ids, skip_special_tokens=True).strip()
        else:
            candidate_text = processor.decode(trimmed_out_ids, skip_special_tokens=True).strip()
        candidates.append(candidate_text)

    return candidates


def main() -> None:
    """Parses arguments, loads model components, and constructs the DPO dataset."""
    parser = argparse.ArgumentParser(description="Generate DPO training pairs for the Player model.")
    parser.add_argument("--sft_dataset", type=str, default="data/player/player_train.json", help="SFT input dataset path.")
    parser.add_argument("--output_dataset", type=str, default="data/player/player_dpo.json", help="Path to save DPO dataset.")
    parser.add_argument("--num_samples", type=int, default=500, help="Number of prompt samples to process.")
    parser.add_argument("--num_candidates", type=int, default=3, help="Number of responses to evaluate per prompt.")
    args = parser.parse_args()

    set_reproducibility_seeds(REPRODUCIBILITY_SEED)

    print(f"🚀 Initializing SFT base model and loading adapter...")
    model_id = "google/gemma-4-E4B-it"
    adapter_path = "./player_lora_output/player_agent/player_agent"

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForImageTextToText.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto"
    )
    processor = AutoProcessor.from_pretrained(model_id)

    model = PeftModel.from_pretrained(model, adapter_path, adapter_name="player_agent")
    model.eval()

    print(f"📦 Model loaded on device {model.device}.")
    print(f"📂 Loading source SFT dataset from: {args.sft_dataset}")

    with open(args.sft_dataset, "r", encoding="utf-8") as f:
        sft_data = json.load(f)

    # Filter messages that are text-only
    valid_dialogues = []
    for item in sft_data:
        if "messages" not in item or len(item["messages"]) < 2:
            continue
        is_text_only = all(isinstance(msg.get("content"), str) for msg in item["messages"])
        if is_text_only:
            valid_dialogues.append(item)

    print(f"Found {len(valid_dialogues)} valid dialogues. Sampling up to {args.num_samples} prompts.")
    sampled_dialogues = random.sample(valid_dialogues, min(args.num_samples, len(valid_dialogues)))

    # Check for existing DPO dataset to resume progress
    existing_prompts = set()
    dpo_dataset: List[Dict[str, Any]] = []
    if os.path.exists(args.output_dataset):
        try:
            with open(args.output_dataset, "r", encoding="utf-8") as f:
                dpo_dataset = json.load(f)
            print(f"📂 Found existing DPO dataset at {args.output_dataset} containing {len(dpo_dataset)} pairs. Resuming...")
            for item in dpo_dataset:
                prompt_key = json.dumps(item["prompt"], ensure_ascii=False)
                existing_prompts.add(prompt_key)
        except Exception as e:
            print(f"⚠️ Error loading existing dataset: {e}. Starting fresh.")
            dpo_dataset = []

    print(f"🔥 Generating preferences using Ollama model: {OLLAMA_MODEL}...")
    
    # Process dialogues
    for idx, item in enumerate(sampled_dialogues):
        print(f"\n👉 [Dialogue {idx + 1}/{len(sampled_dialogues)}] Processing user-assistant turns...")
        messages = item["messages"]
        # Extract individual user-assistant turn pairs to generate prompts
        # For multiple turns, we can use history up to user turn
        for turn_idx in range(1, len(messages), 2):
            # The prompt is the context up to the user message
            prompt_history = messages[:turn_idx + 1]
            opponent_roast = prompt_history[-1]["content"] if prompt_history else ""
            
            # Resume skip check
            prompt_key = json.dumps(prompt_history, ensure_ascii=False)
            if prompt_key in existing_prompts:
                print(f"   ⏭️ Skipping (already generated): \"{opponent_roast[:40]}...\"")
                continue
                
            print(f"   Context: User: \"{opponent_roast[:40]}...\"")
            
            # Generate K candidates using SFT model
            print("   Generating candidate responses using SFT model...")
            candidates = generate_candidates(
                model=model,
                processor=processor,
                prompt_history=prompt_history,
                num_candidates=args.num_candidates
            )
            
            # Remove duplicate generations
            candidates = list(set(candidates))
            print(f"   Unique candidates generated: {len(candidates)}")
            if len(candidates) < 2:
                print("   ⚠️ Skipping turn: Less than 2 unique candidates generated.")
                continue

            # Query the judge for candidates in batch
            print("   Querying local Ollama Qwen judge for scoring in batch...")
            scores = query_ollama_for_scores_batch(prompt_history, candidates)
            
            # Print scores
            print("   Scores received:")
            for cand, score in scores:
                print(f"     - \"{cand}\": {score} pts")
            
            # Sort by score in descending order
            scores.sort(key=lambda x: x[1], reverse=True)
            
            # Skip if highest and lowest score are identical (no clear preference)
            if scores[0][1] == scores[-1][1]:
                print(f"   ⚠️ Skipping turn: Highest and lowest scores are equal ({scores[0][1]} pts).")
                continue
                
            chosen_candidate = scores[0][0]
            rejected_candidate = scores[-1][0]
            
            # Format according to TRL chat template preference schema
            dpo_item = {
                "prompt": prompt_history,
                "chosen": [{"role": "assistant", "content": chosen_candidate}],
                "rejected": [{"role": "assistant", "content": rejected_candidate}]
            }
            dpo_dataset.append(dpo_item)
            # Incremental auto-save to prevent data loss on interrupts
            try:
                with open(args.output_dataset, "w", encoding="utf-8") as f:
                    json.dump(dpo_dataset, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"   ⚠️ Error auto-saving dataset: {e}")
            print(f"   ✅ Added DPO pair. Chosen: \"{chosen_candidate}\" | Rejected: \"{rejected_candidate}\"")
            
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(sampled_dialogues) - 1:
            print(f"📢 Progress: {idx + 1}/{len(sampled_dialogues)} dialogues processed. Total DPO dataset size: {len(dpo_dataset)}")

    # Ensure target directory exists and save
    os.makedirs(os.path.dirname(args.output_dataset), exist_ok=True)
    with open(args.output_dataset, "w", encoding="utf-8") as f:
        json.dump(dpo_dataset, f, ensure_ascii=False, indent=2)

    print(f"🎉 Successfully completed dataset generation. Total aligned pairs: {len(dpo_dataset)}")
    print(f"💾 Saved DPO dataset file to: {args.output_dataset}")


if __name__ == "__main__":
    main()
