"""
strategy_engine.py
------------------
Moteur de dialogue : charge les stratégies depuis strategies.json,
sélectionne la bonne action selon l'émotion, la confiance et la réaction utilisateur.
"""

import json
import os

STRATEGIES_FILE = os.path.join(os.path.dirname(__file__), "strategies.json")

ACTION_RESPONSES = {
    "acknowledge": (
        "I hear you. It sounds like things have been really tough. "
        "Thank you for sharing that with me."
    ),
    "ask_clarification": (
        "Could you tell me a bit more about what's been going on? "
        "I want to make sure I understand."
    ),
    "offer_support": (
        "I'm here for you. You don't have to face this alone — "
        "we can work through this together."
    ),
    "slow_down": (
        "No rush at all. Take your time. "
        "I'm not going anywhere, and there's no pressure here."
    ),
    "de_escalate": (
        "I understand this feels overwhelming right now. "
        "Let's take a breath together and look at this step by step."
    ),
    "encourage": (
        "You've already shown a lot of strength just by talking about this. "
        "Keep going — things can get better."
    ),
    "suggest_pause": (
        "It might help to take a short break and come back to this. "
        "Sometimes stepping away gives us a fresh perspective."
    ),
    "continue": (
        "I'm listening. Please continue — "
        "what else would you like to share?"
    )
}

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _load_strategies() -> list:
    if not os.path.exists(STRATEGIES_FILE):
        raise FileNotFoundError(f"[engine] {STRATEGIES_FILE} not found.")
    with open(STRATEGIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("strategies", [])


def _confidence_level(score: float) -> str:
    if score >= 0.75:
        return "high"
    elif score >= 0.45:
        return "medium"
    else:
        return "low"


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

_strategies = _load_strategies()


def get_strategy(emotion: str, confidence_score: str) -> dict:
    """
    Retourne la stratégie pour une émotion + score de confiance.

    Parameters
    ----------
    emotion : str
        L'émotion détectée (ex: "anger", "sadness")
    confidence_score : float
        Score de confiance entre 0 et 1

    Returns
    -------
    dict
        La stratégie complète
    """
    key = f"{emotion}_{(confidence_score)}"
    strategy = next((s for s in _strategies if s["name"] == key), None)
    if strategy is None:
        raise ValueError(f"[engine] No strategy found for '{key}' in strategies.json")
    return strategy


def get_action(emotion: str, confidence_score: float, turn: int, reaction: str = None) -> str:
    """
    Retourne l'action appropriée selon l'émotion, la confiance, le tour et la réaction.

    Parameters
    ----------
    emotion : str
        L'émotion détectée
    confidence_score : float
        Score de confiance entre 0 et 1
    turn : int
        Numéro du tour (1, 2 ou 3)
    reaction : str or None
        Réaction de l'utilisateur : "opens_up", "stays_negative", "rejects_help"

    Returns
    -------
    str
        Le label de l'action (ex: "acknowledge")
    """
    strategy = get_strategy(emotion, confidence_score)
    turn_data = next((t for t in strategy["turns"] if t["turn"] == turn), None)

    if turn_data is None:
        return "continue"

    if "default" in turn_data:
        return turn_data["default"]

    reaction = reaction or "stays_negative"
    match = next((b for b in turn_data["branches"] if b["signal"] == reaction), None)
    return match["action"] if match else "acknowledge"


def get_response_text(action: str) -> str:
    """Retourne le texte de réponse pour une action donnée."""
    return ACTION_RESPONSES.get(action, ACTION_RESPONSES["acknowledge"])


def get_strategy_info(emotion: str, confidence_score: float) -> str:
    """Retourne un résumé lisible de la stratégie active."""
    strategy = get_strategy(emotion, confidence_score)
    return (
        f"Strategy: {strategy.get('name', '?')} | "
        f"Goal: {strategy.get('goal', '?')}"
    )


# ------------------------------------------------------------------
# Test rapide
# ------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Test: sadness, low")
    print(get_strategy_info("sadness", "high"))
    print(f"Turn 1:                  {get_action('sadness', "high", 1)}")
    print(f"Turn 2 (opens_up):       {get_action('sadness', "high", 2, 'opens_up')}")
    print(f"Turn 3 (rejects_help):   {get_action('sadness', "high", 3, 'rejects_help')}")

    print("\n=== Test: anger, confidence medium ===")
    print(get_strategy_info("anger", "medium"))
    print(f"Turn 1:                  {get_action('anger', "medium", 1)}")
    print(f"Turn 2 (stays_negative): {get_action('anger', "medium", 2, 'stays_negative')}")

    print("\n=== Test: response text ===")
    print(get_response_text(get_action("anxiety", "low", 1)))