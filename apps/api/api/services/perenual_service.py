import re
import httpx
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

from ..core.config import settings

PERENUAL_BASE = "https://perenual.com/api/v2"

# Species-list's coarse `watering` category, used when species/details doesn't have a
# watering_general_benchmark to compute an exact day count from.
_WATERING_CATEGORY_DAYS = {
    "frequent": 3,
    "average": 7,
    "minimum": 14,
    "none": 30,
}

# Perenual's `q=` search is a loose substring match across its whole species table, so
# a colloquial common name with no exact hit (e.g. "Money Plant") can return a totally
# unrelated species first (Lunaria annua - "annual honesty" - is also nicknamed "money
# plant" in British English for its coin-shaped seed pods, even though the vast
# majority of gardening apps mean pothos/Epipremnum aureum). These aliases bias
# resolution toward the meaning app users overwhelmingly intend before falling back to
# generic similarity scoring.
_COMMON_NAME_ALIASES = {
    "money plant": "epipremnum aureum",
    "money tree": "pachira aquatica",
    "snake plant": "dracaena trifasciata",
    "zz plant": "zamioculcas zamiifolia",
    "chinese money plant": "pilea peperomioides",
    "jade plant": "crassula ovata",
    "spider plant": "chlorophytum comosum",
    "swiss cheese plant": "monstera deliciosa",
    "devil's ivy": "epipremnum aureum",
    "peace lily": "spathiphyllum",
    "boston fern": "nephrolepis exaltata",
}

# Below this fuzzy-match score against every candidate's own name fields, a search
# result is treated as unrelated rather than forced into being "the" match.
_MIN_MATCH_CONFIDENCE = 0.45


class PerenualService:
    """
    Deterministic plant-care lookups against Perenual's species database - used instead
    of an LLM guess wherever watering cadence / sunlight requirement needs to be
    accurate rather than merely plausible (adding a plant to the garden, and grounding
    PlantMind's chat answers). Every method fails soft (returns None) when no API key
    is configured or the lookup comes up empty, so callers can fall back to Groq.
    """

    @staticmethod
    def _name_score(query: str, candidate: Dict[str, Any]) -> float:
        """Best fuzzy-match ratio between `query` and any name Perenual has on file for
        this candidate (common name, alternate/other names, scientific name)."""
        query = query.strip().lower()
        names: List[str] = []
        common = candidate.get("common_name")
        if common:
            names.append(str(common))
        other = candidate.get("other_name")
        if isinstance(other, list):
            names.extend(str(n) for n in other)
        sci = candidate.get("scientific_name")
        if isinstance(sci, list):
            names.extend(str(n) for n in sci)
        elif sci:
            names.append(str(sci))

        if not names:
            return 0.0
        return max(
            SequenceMatcher(None, query, name.lower()).ratio()
            for name in names
        )

    @staticmethod
    async def _search_raw(client: httpx.AsyncClient, query: str) -> List[Dict[str, Any]]:
        resp = await client.get(
            f"{PERENUAL_BASE}/species-list",
            params={"key": settings.PERENUAL_API_KEY, "q": query}
        )
        if resp.status_code != 200:
            return []
        return (resp.json() or {}).get("data") or []

    @staticmethod
    def resolve_alias(plant_name: str) -> Optional[str]:
        """The known-alias table's disambiguation for a colloquial name, if any - so
        callers building a *different* query (e.g. Tavily's web search) for the same
        plant can stay consistent with which species Perenual resolved to instead of
        each source silently disambiguating an ambiguous nickname differently."""
        return _COMMON_NAME_ALIASES.get(plant_name.strip().lower())

    @staticmethod
    async def search_species(plant_name: str) -> Optional[Dict[str, Any]]:
        """
        Best-confidence species match for a (possibly colloquial/ambiguous) common
        name. Rather than trusting Perenual's first search hit outright - its `q=`
        search is a loose substring match that can surface a completely unrelated
        species for a common nickname - every candidate is scored against the query
        text and the highest-confidence one wins, with a known-alias table checked
        first for names that are ambiguous enough to regularly return the wrong plant.
        A match below the confidence floor is treated as "no reliable match" (None)
        so callers fall back to Groq/Tavily instead of asserting a wrong identity.
        """
        if not settings.PERENUAL_API_KEY:
            return None
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                alias = _COMMON_NAME_ALIASES.get(plant_name.strip().lower())
                results = await PerenualService._search_raw(client, alias or plant_name)
                if not results and alias:
                    results = await PerenualService._search_raw(client, plant_name)
                if not results:
                    return None

                if alias:
                    # The alias table already disambiguated intent - trust Perenual's
                    # top hit for that specific scientific/common name search.
                    return results[0]

                scored = [(PerenualService._name_score(plant_name, r), r) for r in results]
                best_score, best = max(scored, key=lambda pair: pair[0])
                if best_score < _MIN_MATCH_CONFIDENCE:
                    return None
                return best
        except Exception as e:
            print(f"Perenual search error: {e}")
            return None

    @staticmethod
    async def get_species_details(species_id: int) -> Optional[Dict[str, Any]]:
        if not settings.PERENUAL_API_KEY:
            return None
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{PERENUAL_BASE}/species/details/{species_id}",
                    params={"key": settings.PERENUAL_API_KEY}
                )
                if resp.status_code != 200:
                    return None
                return resp.json()
        except Exception as e:
            print(f"Perenual details error: {e}")
            return None

    @staticmethod
    def _first(value: Any) -> Optional[str]:
        """Perenual returns some text fields as a single-item list, others as a plain string."""
        if isinstance(value, list):
            return value[0] if value else None
        return value or None

    @staticmethod
    def _parse_watering_days(details: Dict[str, Any]) -> Optional[int]:
        benchmark = details.get("watering_general_benchmark") or {}
        value = benchmark.get("value")
        unit = str(benchmark.get("unit") or "days").lower()

        if value:
            nums = [int(n) for n in re.findall(r'\d+', str(value))]
            if nums:
                days = sum(nums) / len(nums)
                if "week" in unit:
                    days *= 7
                elif "month" in unit:
                    days *= 30
                return max(1, round(days))

        category = str(details.get("watering") or "").strip().lower()
        return _WATERING_CATEGORY_DAYS.get(category)

    @staticmethod
    def _normalize_sunlight(details: Dict[str, Any]) -> Optional[str]:
        raw = details.get("sunlight")
        joined = " ".join(raw).lower() if isinstance(raw, list) else str(raw or "").lower()
        if not joined:
            return None
        if "full_shade" in joined or "full shade" in joined or "deep_shade" in joined:
            return "Shade"
        if "part" in joined:
            return "Partial Sun"
        if "filtered" in joined or "bright" in joined:
            return "Bright, indirect"
        if "full_sun" in joined or "full sun" in joined:
            return "Full Sun"
        return "Bright, indirect"

    @staticmethod
    async def get_care_info(plant_name: str) -> Optional[Dict[str, Any]]:
        """Best-match, deterministic care info for a plant name, or None if unavailable."""
        match = await PerenualService.search_species(plant_name)
        if not match:
            return None
        details = await PerenualService.get_species_details(match.get("id")) or match

        origin = details.get("origin") or match.get("origin")
        indoor = details.get("indoor")

        return {
            "common_name": details.get("common_name") or match.get("common_name") or plant_name,
            "scientific_name": PerenualService._first(details.get("scientific_name") or match.get("scientific_name")),
            "watering_frequency_days": PerenualService._parse_watering_days(details),
            "sunlight": PerenualService._normalize_sunlight(details),
            "watering_text": details.get("watering"),
            "care_level": details.get("care_level"),
            "cycle": details.get("cycle"),
            "maintenance": details.get("maintenance"),
            "native_habitat": ", ".join(origin) if isinstance(origin, list) and origin else (origin or None),
            "grows_indoors": bool(indoor) if indoor is not None else None,
            "source": "perenual",
        }
