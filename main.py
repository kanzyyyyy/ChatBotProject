"""
main.py
-------
Conversation loop : analyse l'émotion, sélectionne la stratégie,
et génère la réponse appropriée tour par tour.
"""

from oracle import analyze
from chatbot import get_strategy, get_action, get_response_text, get_strategy_info

MAX_TURNS = 3

SIGNALS = {
    "opens_up": [
        "yes", "yeah", "actually", "i think", "i feel", "because",
        "it started", "the thing is", "honestly", "i guess", "you're right",
        "i want to talk", "i need to", "let me explain", "so basically" , "better"
    ],
    "rejects_help": [
        "no", "stop", "leave me alone", "i don't want", "don't",
        "not now", "forget it", "whatever", "i'm fine", "it's fine",
        "doesn't matter", "never mind", "drop it", "ugh"
    ]
}

def detect_reaction(text: str) -> str:
    """
    Détecte la réaction de l'utilisateur au tour précédent.
    Retourne "opens_up", "rejects_help", ou "stays_negative".
    """
    text_lower = text.lower()
    for signal, phrases in SIGNALS.items():
        if any(phrase in text_lower for phrase in phrases):
            return signal
    return "stays_negative"


def run_conversation():
    print("=" * 50)
    print("  Emotional Support Assistant")
    print("  Type 'quit' to exit at any time.")
    print("=" * 50)

    while True:
        # ── Reset per conversation ─────────────────────────────
        turn = 1
        emotion = None
        confidence = None
        strategy = None

        # ── Turn 1 : get opening message + detect emotion ──────
        print()
        user_input = input("You: ").strip()

        if user_input.lower() in ("quit", "exit"):
            print("\nAssistant: Take care. I'm here whenever you need.")
            break

        if not user_input:
            continue

        result = analyze(user_input)
        emotion = result["emotion"]
        confidence = result["confidence"]

        if emotion == "neutral":
            print("\nAssistant: I'm here with you. Would you like to tell me more about how you're feeling?\n")
            continue

        strategy = get_strategy(emotion, confidence)
        print(f"\n  [strategy: {strategy['name']} | goal: {strategy['goal']}]")

        action = get_action(emotion, confidence, turn=1)
        print(f"  [turn 1 → action: {action}]")
        print(f"\nAssistant: {get_response_text(action)}\n")

        # ── Turns 2 and 3 : reaction-driven ───────────────────
        for turn in range(2, MAX_TURNS + 1):
            user_input = input("You: ").strip()

            if user_input.lower() in ("quit", "exit"):
                print("\nAssistant: Take care. I'm here whenever you need.")
                return

            reaction = detect_reaction(user_input)
            action = get_action(emotion, confidence, turn=turn, reaction=reaction)

            print(f"  [turn {turn} | reaction: {reaction} → action: {action}]")
            print(f"\nAssistant: {get_response_text(action)}\n")

        # ── After turn 3 : open-ended continuation ─────────────
        print("Assistant: I'm still here. How are you feeling now?\n")
        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ("quit", "exit"):
                print("\nAssistant: Take care. I'm here whenever you need.")
                return

            if not user_input:
                continue

            # Re-analyze in case emotion shifted
            result = analyze(user_input)
            new_emotion = result["emotion"]
            new_confidence = result["confidence"]

            if new_emotion != "neutral" and new_emotion != emotion:
                # Emotion shifted — start a fresh strategy from turn 1
                emotion = new_emotion
                confidence = new_confidence
                strategy = get_strategy(emotion, confidence)
                action = get_action(emotion, confidence, turn=1)
                print(f"\n  [emotion shift → strategy: {strategy['name']}]")
                print(f"  [turn 1 → action: {action}]")
                print(f"\nAssistant: {get_response_text(action)}\n")
                break  # re-enter the main loop for turns 2 and 3
            else:
                reaction = detect_reaction(user_input)
                action = get_action(emotion, confidence, turn=MAX_TURNS, reaction=reaction)
                print(f"  [extended | reaction: {reaction} → action: {action}]")
                print(f"\nAssistant: {get_response_text(action)}\n")


if __name__ == "__main__":
    run_conversation()