# symbolic_rules.py
"""Implements symbolic evaluation constraints and game environment rules.

Acts as the symbolic system verification layer to detect exploit attempts and
enforce game constraints (e.g., repetitiveness penalties).
"""

from typing import Dict, Any, List

def calculate_symbolic_penalties(
    player_text: str,
    player_history: List[str],
    raw_damage: int
) -> int:
    """Calculates final damage by enforcing environmental penalties.

    Checks for exact duplicates or extreme brevity to prevent simple exploit loops.

    Args:
        player_text: The current round text input.
        player_history: List of previous inputs from the same player.
        raw_damage: The initial damage value parsed from neural network.

    Returns:
        The updated damage value after applying symbolic rules.
    """
    cleaned_input = player_text.strip().lower()
    
    # Rule 1: Empty input check
    if not cleaned_input:
        return 0
        
    # Rule 2: Repetition Penalty (System Memory check)
    # If same roast was used in recent rounds, degrade damage to minimum threshold.
    for past_roast in player_history[-3:]:
        if cleaned_input == past_roast.strip().lower():
            print(f"⚠️ Exploit detected: Repeat phrase '{player_text}'! Applying penalty.")
            return 1 # Minimum damage penalty
            
    # Rule 3: Extreme brevity check (e.g., spamming single words)
    if len(cleaned_input) <= 1:
        return max(1, int(raw_damage * 0.1))
        
    return raw_damage

def validate_referee_json(raw_output: Dict[str, Any]) -> bool:
    """Validates whether referee output matches expected game JSON schemas.

    Args:
        raw_output: Parsed dict from neural network output.

    Returns:
        True if schema matches, False otherwise.
    """
    if not isinstance(raw_output, dict):
        return False
    if "damage" not in raw_output or "referee_comment" not in raw_output:
        return False
    if not isinstance(raw_output["damage"], (int, float)):
        return False
    if not isinstance(raw_output["referee_comment"], str):
        return False
    return True
