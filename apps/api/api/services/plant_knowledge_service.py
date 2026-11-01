"""
Authoritative plant facts that don't need an LLM to read: GBIF for species identity
(accepted name + family) and the ASPCA for pet toxicity. Both are free; GBIF needs no
key at all. plant_mcp_server.py exposes the same functions as MCP tools.
"""
import re
from typing import Any, Dict, List, Optional

import httpx

from .tavily_service import TavilyService

GBIF_MATCH_URL = "https://api.gbif.org/v1/species/match"
GBIF_SPECIES_URL = "https://api.gbif.org/v1/species"

_ASPCA_TOXICITY_RE = re.compile(r"(Non-)?Toxicity:\s*([^\n]*?)(?:\s{2,}|Toxic Principles:|Clinical Signs:|$)", re.I)
_ASPCA_FIELD_RES = {
    "scientific_name": re.compile(r"Scientific Name:\s*(.+?)\s+Family:", re.I),
    "principles": re.compile(r"Toxic Principles:\s*(.+?)\s+Clinical Signs:", re.I),
    "clinical_signs": re.compile(r"Clinical Signs:\s*(.+?)(?:\s{2,}|\s+(?:Share|Related|Back to|Pet Care)\b|$)", re.I),
}


async def verify_species(name: str) -> Optional[Dict[str, Any]]:
    """
    Resolve a scientific name against GBIF's backbone taxonomy. Follows a synonym to its
    accepted name (e.g. Sansevieria trifasciata -> Dracaena trifasciata). Returns None
    when GBIF has no confident plant match - callers must treat that as "unverified",
    not as "wrong".
    """
    if not name:
        return None
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(GBIF_MATCH_URL, params={"name": name, "kingdom": "Plantae"})
            r.raise_for_status()
            m = r.json()
            if m.get("matchType") in (None, "NONE") or m.get("rank") not in ("SPECIES", "GENUS", "SUBSPECIES", "VARIETY", "FORM"):
                return None
            key = m.get("usageKey")
            accepted = m
            if m.get("status") == "SYNONYM" and m.get("acceptedUsageKey"):
                key = m["acceptedUsageKey"]
                a = await client.get(f"{GBIF_SPECIES_URL}/{key}")
                a.raise_for_status()
                accepted = a.json()
            classification = {
                rank: accepted.get(rank) or m.get(rank)
                for rank in ("kingdom", "phylum", "class", "order", "family", "genus")
                if accepted.get(rank) or m.get(rank)
            }
            return {
                "accepted_name": accepted.get("canonicalName") or accepted.get("scientificName"),
                "family": accepted.get("family") or m.get("family"),
                "classification": classification,
                "queried_name": name,
                "was_synonym": m.get("status") == "SYNONYM",
                "rank": accepted.get("rank"),
                "gbif_key": key,
                "source_url": f"https://www.gbif.org/species/{key}",
            }
    except Exception as e:
        print(f"GBIF verify error: {e}")
        return None


_WIKI_HEADERS = {"User-Agent": "Flourish/1.0 (plant care app; https://github.com/riju-talk/Flourish)"}
_WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"
_WIKI_SEARCH_URL = "https://en.wikipedia.org/w/rest.php/v1/search/title"


async def wikipedia_summary(name: str) -> Optional[Dict[str, Any]]:
    """
    Encyclopedic overview (extract, short description, thumbnail, link) from Wikipedia's
    free REST API. Tries the name as a page title first, then a title search for
    "<name> plant"; disambiguation pages are rejected. Returns None on any miss/error -
    it only enriches the lookup, it must never break it.
    """
    from urllib.parse import quote

    if not name or not name.strip():
        return None

    def _clean(page: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if page.get("type") != "standard" or not page.get("extract"):
            return None
        return {
            "title": page.get("title"),
            "description": page.get("description"),
            "extract": page["extract"],
            "url": (page.get("content_urls") or {}).get("desktop", {}).get("page"),
            "thumbnail": (page.get("thumbnail") or {}).get("source"),
        }

    try:
        async with httpx.AsyncClient(timeout=6, headers=_WIKI_HEADERS, follow_redirects=True) as client:
            r = await client.get(_WIKI_SUMMARY_URL + quote(name.strip().replace(" ", "_"), safe=""))
            if r.status_code == 200 and (page := _clean(r.json())):
                return page
            s = await client.get(_WIKI_SEARCH_URL, params={"q": f"{name} plant", "limit": 1})
            s.raise_for_status()
            pages = s.json().get("pages") or []
            if not pages:
                return None
            r = await client.get(_WIKI_SUMMARY_URL + quote(pages[0]["key"], safe=""))
            r.raise_for_status()
            return _clean(r.json())
    except Exception as e:
        print(f"Wikipedia lookup error: {e}")
        return None


def _parse_aspca(content: str) -> Optional[Dict[str, Any]]:
    text = re.sub(r"[ \t]+", " ", content)
    m = _ASPCA_TOXICITY_RE.search(text)
    if not m:
        return None
    verdict = m.group(2)
    low = verdict.lower()
    non_toxic_field = bool(m.group(1))

    def animal(a: str) -> str:
        if f"non-toxic to {a}" in low:
            return "safe"
        if f"toxic to {a}" in low:
            return "toxic"
        return "safe" if non_toxic_field and a in low else "unknown"

    dogs, cats = animal("dogs"), animal("cats")
    if dogs == "unknown" and cats == "unknown":
        return None
    out: Dict[str, Any] = {"dogs": dogs, "cats": cats, "horses": animal("horses")}
    for key, rx in _ASPCA_FIELD_RES.items():
        fm = rx.search(text)
        if fm:
            out[key] = fm.group(1).strip()
    if out.get("clinical_signs"):
        # The ASPCA appends a "[...]" excerpt cut and its poison-control boilerplate.
        out["clinical_signs"] = re.split(r"\s*\[\.\.\.\]|\s*If you suspect", out["clinical_signs"])[0].strip()
    return out


async def pet_toxicity(scientific_name: str, common_name: str = "") -> Optional[Dict[str, Any]]:
    """
    ASPCA pet-toxicity verdict for a plant, read from the ASPCA's own toxic/non-toxic
    plants pages (Tavily restricted to aspca.org). Only an individual plant page whose
    scientific name or genus matches is trusted - the ASPCA's long list pages and
    look-alike plants are skipped, because a wrong "safe" is worse than "unknown".
    """
    genus = (scientific_name or "").split(" ")[0].lower()
    names = [n.lower() for n in (scientific_name, common_name) if n]
    if not genus:
        return None
    results: List[Dict[str, Any]] = await TavilyService.search_raw(
        f"{common_name} {scientific_name} toxic to dogs cats".strip(), max_results=5, include_domains=["aspca.org"]
    )
    for r in results:
        url = r.get("url", "")
        if "/toxic-and-non-toxic-plants/" not in url:
            continue
        parsed = _parse_aspca(r.get("content") or "")
        if not parsed:
            continue
        page_sci = (parsed.get("scientific_name") or "").lower()
        text = (r.get("content") or "").lower()
        if page_sci.split(" ")[0] != genus and not any(n and n in text for n in names):
            continue
        parsed["source_url"] = url
        return parsed
    return None


def toxicity_block(aspca: Dict[str, Any]) -> Dict[str, Any]:
    """Map an ASPCA verdict to the lookup response's `toxicity` shape."""
    dogs, cats = aspca["dogs"], aspca["cats"]
    if "toxic" in (dogs, cats):
        pets = "toxic"
        who = " and ".join(a for a, v in (("dogs", dogs), ("cats", cats)) if v == "toxic")
        details = f"ASPCA lists this plant as toxic to {who}."
    elif dogs == cats == "safe":
        pets = "safe"
        details = "ASPCA lists this plant as non-toxic to dogs and cats."
    else:
        pets = "unknown"
        details = "ASPCA data is incomplete for this plant."
    if aspca.get("principles"):
        details += f" Toxic principle: {aspca['principles']}."
    if pets == "toxic" and aspca.get("clinical_signs"):
        details += f" Signs to watch for: {aspca['clinical_signs']}"
    return {
        "pets": pets,
        "dogs": dogs,
        "cats": cats,
        "humans": "unknown",
        "details": details.strip(),
        "source_url": aspca.get("source_url"),
    }


def _as_days(value: Any) -> Optional[int]:
    """Coerce an LLM/Perenual interval to a sane number of days, else None."""
    try:
        days = int(float(str(value).strip().split()[0]))
    except (ValueError, IndexError, TypeError):
        return None
    return days if 1 <= days <= 365 else None


async def enrich_plant_info(plant_info: Dict[str, Any], perenual: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Post-process a curated lookup so the result is checkable and actionable:
    species identity verified against GBIF, pet toxicity taken from the ASPCA instead
    of the model, and the watering/feeding intervals normalised to whole days.
    """
    import asyncio

    sci, com = plant_info.get("scientific_name") or "", plant_info.get("common_name") or ""
    species, aspca = await asyncio.gather(verify_species(sci), pet_toxicity(sci, com))

    if species:
        plant_info["scientific_name"] = species["accepted_name"] or sci
        plant_info["family"] = species["family"]
        plant_info["classification"] = species.get("classification") or {}
        plant_info["species_verified"] = {"source": "GBIF", "url": species["source_url"], "was_synonym": species["was_synonym"]}
        if species["was_synonym"]:
            plant_info["also_known_as"] = species["queried_name"]
    else:
        plant_info["species_verified"] = None

    if aspca:
        tox = toxicity_block(aspca)
        tox["humans"] = (plant_info.get("toxicity") or {}).get("humans", "unknown")
        plant_info["toxicity"] = tox
        # Toxicity is now sourced from the ASPCA, so it is no longer an AI-filled field.
        plant_info["ai_filled_fields"] = [f for f in plant_info.get("ai_filled_fields") or [] if f != "toxicity"]

    watering = plant_info.get("watering")
    if not isinstance(watering, dict):
        watering = plant_info["watering"] = {}
    water_days = _as_days(watering.get("interval_days"))
    if water_days is None and perenual and plant_info.get("scientific_name", "").lower() == str(perenual.get("scientific_name", "")).lower():
        water_days = _as_days(perenual.get("watering_frequency_days"))
    if water_days:
        watering["interval_days"] = water_days

    feeding = plant_info.get("fertilizing")
    feed_days = _as_days(feeding.get("interval_days")) if isinstance(feeding, dict) else None
    if feed_days and isinstance(feeding, dict):
        feeding["interval_days"] = feed_days

    plant_info["care_schedule"] = [
        {"task": t, "every_days": d, "label": f"{label} every {d} day{'s' if d != 1 else ''}"}
        for t, d, label in (("water", water_days, "Water"), ("fertilize", feed_days, "Fertilize"))
        if d
    ]
    return plant_info


# Care facts for a species barely change, and the Groq tier this app runs on is
# output-token-limited per minute, so a Groq-curated lookup is kept for a day. Only
# Groq-curated results are cached: the rule-based fallback is cheap to recompute and
# shouldn't outlive the rate-limit blip that produced it.
_LOOKUP_CACHE: Dict[str, tuple] = {}
_LOOKUP_TTL_SECONDS = 24 * 3600
_LOOKUP_CACHE_MAX = 200


async def lookup_plant(plant_name: str) -> Dict[str, Any]:
    """
    The full Explore lookup, shared by POST /api/plants/lookup and the plant MCP server:
    Perenual (care database) + Tavily (live web) -> Groq curation, with the deterministic
    extraction as fallback -> GBIF/ASPCA verification. Never raises for a bad Groq turn.
    """
    from .groq_service import GroqService
    from .perenual_service import PerenualService
    from .plant_lookup_service import curate_plant_info

    import asyncio
    import copy
    import time

    cache_key = " ".join(plant_name.lower().split())
    hit = _LOOKUP_CACHE.get(cache_key)
    if hit and time.monotonic() - hit[0] < _LOOKUP_TTL_SECONDS:
        return copy.deepcopy(hit[1])

    # Search the web with the alias-disambiguated name so both sources are grounded in
    # the same plant (e.g. "money plant" -> Epipremnum aureum). The query depends only
    # on the alias, not on Perenual's answer, so the two lookups run concurrently.
    search_query = PerenualService.resolve_alias(plant_name) or plant_name
    perenual_info, tavily_results, growing_results, wiki = await asyncio.gather(
        PerenualService.get_care_info(plant_name),
        TavilyService.search_raw(
            f"{search_query} plant care guide watering sunlight toxicity propagation native habitat"
        ),
        # Second, differently-angled search: the profile section (climate, soil, size,
        # pests, pruning, repotting) needs pages the care-guide query doesn't surface.
        TavilyService.search_raw(
            f"{search_query} temperature humidity soil mature size growth rate hardiness zone "
            "pruning repotting pests diseases",
            max_results=4,
        ),
        wikipedia_summary(search_query),
    )
    # The care synthesis and the extended profile read different evidence and are
    # independent, so they run concurrently; the profile is optional and failure-tolerant.
    plant_info, profile = await asyncio.gather(
        GroqService.curate_plant_lookup(plant_name, perenual_info, tavily_results),
        GroqService.curate_plant_profile(plant_name, perenual_info, growing_results + tavily_results, wiki),
    )
    curated_by_groq = plant_info is not None
    if not plant_info:
        plant_info = curate_plant_info(plant_name, perenual_info, tavily_results)
    plant_info["profile"] = profile
    plant_info["wikipedia"] = wiki
    sources: List[str] = []
    for url in [r.get("url") for r in tavily_results + growing_results] + [(wiki or {}).get("url")]:
        if url and url not in sources:
            sources.append(url)
    plant_info["sources"] = sources[:8]
    try:
        plant_info = await enrich_plant_info(plant_info, perenual_info)
    except Exception as e:
        print(f"Lookup enrichment skipped: {e}")

    if curated_by_groq:
        if len(_LOOKUP_CACHE) >= _LOOKUP_CACHE_MAX:
            _LOOKUP_CACHE.pop(min(_LOOKUP_CACHE, key=lambda k: _LOOKUP_CACHE[k][0]))
        _LOOKUP_CACHE[cache_key] = (time.monotonic(), copy.deepcopy(plant_info))
    return plant_info
