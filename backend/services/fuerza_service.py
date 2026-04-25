# backend/services/fuerza_service.py
from typing import Literal
import logging

logger = logging.getLogger(__name__)

STANDARDS = {
    "m": {"pull": [0,3,8,15,22], "dips": [0,5,12,20,30], "push": [0,10,25,40,60], "squat": [0,15,40,70,100]},
    "f": {"pull": [0,1,4,8,14],  "dips": [0,2,6,12,20],  "push": [0,5,15,28,45],  "squat": [0,20,50,80,110]},
}

WEAK_LABELS = {
    "pull":  "tracción (dominadas)",
    "dips":  "empuje (fondos)",
    "push":  "empuje (flexiones)",
    "squat": "piernas (sentadillas)",
}

LEVEL_THRESHOLDS = [
    (95, "elite"),
    (80, "avanzado"),
    (60, "intermedio"),
    (40, "novato"),
    (0,  "principiante"),
]

BAR_COLORS = [
    (85, "#1D9E75"),
    (65, "#378ADD"),
    (40, "#EF9F27"),
    (0,  "#E24B4A"),
]


def _score_exercise(val: int, tiers: list[int]) -> float:
    for i in range(len(tiers) - 1, -1, -1):
        if val >= tiers[i]:
            next_tier = tiers[i + 1] if i < len(tiers) - 1 else tiers[i] * 1.5
            fraction = min((val - tiers[i]) / (next_tier - tiers[i]), 1.0)
            return (i + fraction) / (len(tiers) - 1)
    return 0.0


def _get_level(score: int) -> str:
    for threshold, level in LEVEL_THRESHOLDS:
        if score >= threshold:
            return level
    return "principiante"


def _get_bar_color(pct: int) -> str:
    for threshold, color in BAR_COLORS:
        if pct >= threshold:
            return color
    return "#E24B4A"


def calculate_fuerza(
    sexo: Literal["m", "f"],
    pull: int,
    dips: int,
    push: int,
    squat: int,
) -> dict:
    s = STANDARDS[sexo]
    reps = {"pull": pull, "dips": dips, "push": push, "squat": squat}

    raw_scores = {ex: _score_exercise(val, s[ex]) for ex, val in reps.items()}

    avg   = sum(raw_scores.values()) / 4
    score = round(avg * 100)
    level = _get_level(score)

    scores_pct = {ex: round(v * 100) for ex, v in raw_scores.items()}
    weakest    = min(raw_scores, key=raw_scores.get)
    bar_colors = {ex: _get_bar_color(pct) for ex, pct in scores_pct.items()}

    logger.info(f"Fuerza calculada: sexo={sexo} score={score} level={level}")

    return {
        "score":      score,
        "level":      level,
        "scores":     scores_pct,
        "bar_colors": bar_colors,
        "weakest":    weakest,
        "weak_label": WEAK_LABELS[weakest],
        "reps":       reps,
    }