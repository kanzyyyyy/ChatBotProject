"""
emotion_oracle.py
-----------------
Oracle d'émotion utilisant NRCLex 4.1.0.

NRCLex est basé sur le lexique NRC Emotion de Mohammad & Turney.
Il détecte 8 émotions de base (Plutchik) + 2 sentiments :
    fear, anger, anticipation, trust, surprise,
    positive, negative, sadness, disgust, joy

Installation :
    pip install nrclex==4.1.0

NRCLex 4.1.0 API :
    from nrclex import NRCLex
    emotion = NRCLex(text)
    emotion.affect_frequencies   # dict {emotion: frequency (0.0-1.0)}
    emotion.top_emotions         # list of (emotion, frequency) sorted desc
    emotion.raw_emotion_scores   # dict {emotion: raw count}
"""

from nrclex import NRCLex

# Mapping NRCLex → nos labels internes utilisés dans strategies.json
# NRCLex retourne: fear, anger, anticipation, trust, surprise,
#                  positive, negative, sadness, disgust, joy
NRCLEX_TO_INTERNAL = {
    "sadness":      "sadness",
    "anger":        "anger",
    "fear":         "anxiety",   # "fear" mappé sur notre label "anxiety"
    "disgust":      "disgust",
    "joy":          "joy",
    "surprise":     "surprise",
    "anticipation": "anticipation",
    "trust":        "trust",
    "positive":     None,        # sentiments ignorés (pas des émotions)
    "negative":     None,
}

# Sentiments à exclure du résultat final
EXCLUDED = {"positive", "negative"}


def analyze(text: str) -> dict:
    """
    Analyse le texte avec NRCLex et retourne l'émotion dominante
    avec son score de confiance normalisé.

    Parameters
    ----------
    text : str
        Le message de l'utilisateur

    Returns
    -------
    dict
        {
          "emotion": str,      # label interne (ex: "sadness", "anxiety")
          "confidence": float  # score entre 0.0 et 1.0
        }
    """
    if not text or not text.strip():
        return {"emotion": "neutral", "confidence": 0.0}

    nrc = NRCLex(text)

    # affect_frequencies est un dict {emotion: fréquence normalisée}
    # Ex: {"fear": 0.4, "anger": 0.2, "positive": 0.3, ...}
    frequencies = nrc.affect_frequencies

    # Filtrer les sentiments (positive/negative) et garder les émotions pures
    emotion_scores = {
        emotion: score
        for emotion, score in frequencies.items()
        if emotion not in EXCLUDED and score > 0.0
    }

    if not emotion_scores:
        return {"emotion": "neutral", "confidence": 0.0}

    # Émotion dominante = celle avec la fréquence la plus haute
    top_nrclex_emotion = max(emotion_scores, key=emotion_scores.get)
    top_score = emotion_scores[top_nrclex_emotion]

    # Convertir vers notre label interne
    internal_emotion = NRCLEX_TO_INTERNAL.get(top_nrclex_emotion, top_nrclex_emotion)

    # Si le mapping retourne None (ex: "positive"), on prend la 2e émotion
    if internal_emotion is None:
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        for nrc_label, score in sorted_emotions:
            mapped = NRCLEX_TO_INTERNAL.get(nrc_label, nrc_label)
            if mapped is not None:
                internal_emotion = mapped
                top_score = score
                break
        else:
            return {"emotion": "neutral", "confidence": 0.0}

    # Normaliser la confiance : NRCLex donne des fréquences entre 0 et 1.
    confidence = round(min(max(top_score, 0.0), 1.0), 2)

    return {
        "emotion": internal_emotion,
        "confidence": confidence
    }


def get_all_emotions(text: str) -> dict:
    """
    Retourne toutes les émotions détectées avec leurs fréquences.
    Utile pour le debug ou pour des stratégies multi-émotions.

    Parameters
    ----------
    text : str
        Le message de l'utilisateur

    Returns
    -------
    dict
        {emotion_label: frequency} pour toutes les émotions avec score > 0,
        triées par fréquence décroissante, sentiments exclus.
    """
    if not text or not text.strip():
        return {}

    nrc = NRCLex(text)
    frequencies = nrc.affect_frequencies

    result = {
        NRCLEX_TO_INTERNAL.get(em, em): score
        for em, score in frequencies.items()
        if em not in EXCLUDED and score > 0.0
        and NRCLEX_TO_INTERNAL.get(em, em) is not None
    }

    return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))


# --- Test rapide si lancé directement ---
if __name__ == "__main__":
    tests = [
        "I failed again, I feel so sad and hopeless",
        "I'm so angry about this unfair situation!",
        "I'm really stressed and scared, I can't cope",
        "Today was a great and joyful day!",
        "I don't know what to say",
        ""
    ]
    for t in tests:
        result = analyze(t)
        all_em = get_all_emotions(t)
        print(f"Input   : '{t}'")
        print(f"Top     : {result}")
        print(f"All     : {all_em}")
        print()