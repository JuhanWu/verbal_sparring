# convert_existing_dataset.py
"""Converts Chinese prompt templates in SFT datasets to English formats.

This script parses existing player_train.json and referee_train.json files
and rewrites the prompt sections into English to match the new system prompts.
"""

import json
import re
from typing import List, Dict, Any

def convert_player_dataset(file_path: str = "player_train.json") -> None:
    """Parses player dataset and rewrites user prompts into English.

    Args:
        file_path: The file path to the player dataset.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        return

    converted_data: List[Dict[str, str]] = []
    
    # Regular expression to extract opponent roast and assistant response
    pattern = re.compile(
        r"User: 對手前一輪嗆你：「(.*?)」。請寫一句極富創意且辛辣的話嗆回去，不超過25字，不要有多餘說明。\nAssistant: (.*)",
        re.DOTALL
    )
    
    for item in data:
        text = item.get("text", "")
        match = pattern.search(text)
        if match:
            opponent_roast = match.group(1)
            player_response = match.group(2)
            
            # Format to new English prompt style
            new_text = (
                f"User: Opponent roast: \"{opponent_roast}\". "
                f"Respond with a toxic comeback in Traditional Chinese under 25 characters.\n"
                f"Assistant: {player_response}"
            )
            converted_data.append({"text": new_text})
        else:
            # Fallback if pattern does not match directly (skip or copy as-is)
            converted_data.append(item)
            
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(converted_data, f, ensure_ascii=False, indent=2)
    print(f"Successfully converted {len(converted_data)} player records in {file_path}")

def convert_referee_dataset(file_path: str = "referee_train.json") -> None:
    """Parses referee dataset and rewrites user prompts into English.

    Args:
        file_path: The file path to the referee dataset.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        return

    converted_data: List[Dict[str, str]] = []
    
    # Regular expression to extract player roast and assistant response
    pattern = re.compile(
        r"User: 你是一個毒舌裁判。請評估以下攻擊，並以 JSON 格式輸出評估結果，格式為：\n"
        r"\{\"damage\": 10到50之間的整數, \"referee_comment\": \"20字內的毒舌短評\"\}\n\n"
        r"玩家攻擊：「(.*?)」\nAssistant: (.*)",
        re.DOTALL
    )
    
    for item in data:
        text = item.get("text", "")
        match = pattern.search(text)
        if match:
            player_response = match.group(1)
            referee_response = match.group(2)
            
            # Format to new English prompt style
            new_text = (
                f"User: Evaluate the following player attack:\n\"{player_response}\"\n\nReturn JSON only.\n"
                f"Assistant: {referee_response}"
            )
            converted_data.append({"text": new_text})
        else:
            # Fallback
            converted_data.append(item)
            
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(converted_data, f, ensure_ascii=False, indent=2)
    print(f"Successfully converted {len(converted_data)} referee records in {file_path}")

if __name__ == "__main__":
    convert_player_dataset()
    convert_referee_dataset()
