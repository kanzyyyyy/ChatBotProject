patterns = {
    "sadness": [
        "i failed", "i messed up", "i lost", "i feel sad", "i feel down",
        "i'm depressed", "i am depressed", "i feel hopeless",
        "nothing works", "nothing ever works", "i give up",
        "i feel empty", "i'm tired of everything", "i feel alone",
        "sad", "hopeless", "lonely", "taxes", "bad"
    ],
    "anger": [
        "whatever", "nobody listens", "this is so annoying",
        "i'm angry", "i am angry", "this makes me mad", "mad",
        "why does everything go wrong", "i'm pissed",
        "this is frustrating", "i hate this", "leave me alone"
    ],
    "fear": [
        "i'm nervous", "i am nervous", "i'm scared",
        "i am scared", "i'm afraid", "i am afraid",
        "i'm worried", "i am worried",
        "i feel anxious", "i'm stressed", "i am stressed", "anxious", "anxiety", "stress", "exam"
    ],
    "joy": [
        "that was amazing", "i'm happy", "i am happy",
        "i feel great", "this is awesome", "so happy",
        "i love this", "this is wonderful", "best day ever"
    ],
    "disgust": [
        "this is disgusting", "that's gross", "this is gross",
        "ew", "this is horrible", "this is awful",
        "i can't stand this", "astaghfiruallah"
    ],
    "surprise": [
        "what just happened", "wait what", "are you serious",
        "no way", "i can't believe it", "really?",
        "that's unexpected", "surprise", "i am surprised", "i'm surprised", "holy shit"
    ]
}

INTENSIFIERS = [
    "so", "very", "really", "extremely", "absolutely", "totally", "extremly",
    "completely", "deeply", "truly", "always", "never", "everything", "nothing", "nobody", "ever", "super"
]

def analyze(text: str) -> dict:
    if not text or not text.strip():
        return {"emotion": "neutral", "confidence": "low"}

    original = text
    text = text.lower()
    scores = {emotion: 0 for emotion in patterns}

    for emotion, phrases in patterns.items():
        for p in phrases:
            if all(word in text for word in p.split()):
                scores[emotion] += len(p.split()) 

    if all(score == 0 for score in scores.values()):
        return {"emotion": "neutral", "confidence": "low"}

    top_emotion = max(scores, key=scores.get)
    top_score = scores[top_emotion]

    sorted_scores = sorted(scores.values(), reverse=True)
    dominance = sorted_scores[0] - (sorted_scores[1] if len(sorted_scores) > 1 else 0)

    intensifier_count = sum(1 for w in INTENSIFIERS if w in text.split())
    top_score += intensifier_count * 2

    if "!" in original:
        top_score += 2
    if "?" in original:
        top_score += 1

    word_count = len(text.split())
    if word_count >= 8:
        top_score += 2
    elif word_count >= 5:
        top_score += 1

    if dominance == 0:
        top_score = max(0, top_score - 3)

    if top_score >= 7:
        confidence = "high"
    elif top_score >= 4:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "emotion": top_emotion,
        "confidence": confidence
    }

if __name__ == "__main__":
    tests = [
        "I failed again, I feel so sad and hopeless", #sadness high
        "Whatever. Nobody listens anyway.", #anger medium
        "I'm really nervous about tomorrow.", #fear high
        "That was amazing!", #joy high
        "This is disgusting.", #disgust medium
        "Wait, what just happened?", #surprise low
        "Nothing ever works for me.", #sadness medium
        "Why does everything go wrong?" #anger high
    ]
    for t in tests:
        result = analyze(t)
        print(f"Input   : '{t}'")
        print(f"Top     : {result}")
        print()