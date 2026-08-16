import re
from typing import Any, Dict, List, Optional

_TOXIC_HIT_KEYWORDS = ["toxic", "poison"]
_SAFE_HIT_KEYWORDS = ["non-toxic", "non toxic", "pet safe", "pet-safe", "safe for cats", "safe for dogs"]
_ISSUE_KEYWORDS = [
    "root rot", "yellow leaves", "yellowing leaves", "brown tips", "brown spots",
    "spider mites", "mealybugs", "aphids", "scale insects", "fungus gnats",
    "overwatering", "underwatering", "leaf drop", "wilting", "powdery mildew",
]
_PROPAGATION_KEYWORDS = [
    "stem cutting", "leaf cutting", "division", "offset", "offsets", "pups",
    "seed", "air layering", "water propagation", "runners",
]
_HABITAT_KEYWORDS = [
    "native to", "originates from", "originated in", "indigenous to",
    "found in the wild", "naturally grows in", "hails from",
]

_CARE_LEVEL_FERTILIZE_DAYS = {"easy": 30, "moderate": 21, "difficult": 14}


def _split_sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


def _extract_sentences(text: str, keywords: List[str], limit: int) -> List[str]:
    hits: List[str] = []
    seen = set()
    for sentence in _split_sentences(text):
        low = sentence.lower()
        if any(k in low for k in keywords):
            if sentence not in seen:
                seen.add(sentence)
                hits.append(sentence)
        if len(hits) >= limit:
            break
    return hits


def _detect_pet_toxicity(text: str) -> tuple[str, List[str]]:
    hits = _extract_sentences(text, _TOXIC_HIT_KEYWORDS + _SAFE_HIT_KEYWORDS, 3)
    low_hits = " ".join(hits).lower()
    if any(k in low_hits for k in _SAFE_HIT_KEYWORDS):
        return "safe", hits
    if any(k in low_hits for k in _TOXIC_HIT_KEYWORDS):
        return "toxic", hits
    return "unknown", hits


def _perenual_identity_confirmed(plant_name: str, perenual: Dict[str, Any], combined_text: str) -> bool:
    """
    Cross-check Perenual's matched species against what the live web results are
    actually talking about. If neither its common name nor scientific name shows up
    anywhere in the Tavily text - but the plant the user actually searched for does -
    Perenual most likely matched the wrong species (e.g. a colloquial name it
    resolved to an unrelated plant that happens to share the query text). In that
    case its care facts describe the wrong plant and must not be surfaced as this
    plant's info.
    """
    low_text = combined_text.lower()
    if not low_text:
        return True  # nothing to cross-check against - don't discard Perenual's answer

    common = (perenual.get("common_name") or "").lower()
    scientific = (perenual.get("scientific_name") or "").lower()
    identity_mentioned = (common and common in low_text) or (scientific and scientific in low_text)
    if identity_mentioned:
        return True

    query_mentioned = plant_name.strip().lower() in low_text
    return not query_mentioned


def _extract_habitat(text: str, perenual_habitat: Optional[str]) -> str:
    if perenual_habitat:
        return perenual_habitat
    hits = _extract_sentences(text, _HABITAT_KEYWORDS, 2)
    return " ".join(hits) or "Not documented in available sources."


def curate_plant_info(
    plant_name: str,
    perenual: Optional[Dict[str, Any]],
    tavily_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Deterministic, rule-based curation of a plant's care profile: Perenual supplies
    whatever structured facts it has (watering cadence, sunlight, care level), Tavily's
    live search results are combined into one text blob and mined for the rest via
    keyword/sentence matching - no LLM call is involved anywhere in this function,
    per the Explore page's requirement to be internet-first and deterministically
    curated rather than Groq-generated.
    """
    perenual = perenual or {}
    combined_text = " ".join(
        f"{r.get('title', '')}. {r.get('content', '')}" for r in tavily_results
    )

    if perenual and not _perenual_identity_confirmed(plant_name, perenual, combined_text):
        # Don't let a mismatched species' facts masquerade as this plant's - fall back
        # to whatever the live search results actually say instead.
        perenual = {}

    care_level = (perenual.get("care_level") or "moderate").lower()
    watering_days = perenual.get("watering_frequency_days")
    sunlight = perenual.get("sunlight")
    fertilize_days = _CARE_LEVEL_FERTILIZE_DAYS.get(care_level, 21)

    pets_toxicity, toxicity_hits = _detect_pet_toxicity(combined_text)
    issues = _extract_sentences(combined_text, _ISSUE_KEYWORDS, 4)
    propagation = sorted({kw for kw in _PROPAGATION_KEYWORDS if kw in combined_text.lower()})
    facts = [r.get("title", "").strip() for r in tavily_results[:3] if r.get("title")]
    sources = [r.get("url") for r in tavily_results if r.get("url")][:5]

    return {
        "common_name": perenual.get("common_name") or plant_name,
        "scientific_name": perenual.get("scientific_name") or "",
        "care_level": care_level if care_level in ("easy", "moderate", "difficult") else "moderate",
        "watering": {
            "frequency": f"Every {watering_days} days" if watering_days else "See sources below",
            "amount": "",
            "tips": perenual.get("watering_text") or "",
        },
        "sunlight": {
            "requirement": sunlight or "See sources below",
            "details": "",
        },
        "fertilizing": {
            "frequency": f"Every {fertilize_days} days during the growing season",
            "type": "Balanced, water-soluble fertilizer",
        },
        "toxicity": {
            "pets": pets_toxicity,
            "humans": "unknown",
            "details": " ".join(toxicity_hits) or "No toxicity information found in search results.",
        },
        "environment": {
            "native_habitat": _extract_habitat(combined_text, perenual.get("native_habitat")),
            "grows_indoors": perenual.get("grows_indoors"),
        },
        "common_issues": issues,
        "propagation": propagation,
        "interesting_facts": facts,
        "sources": sources,
    }
