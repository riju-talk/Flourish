import asyncio
from unittest.mock import AsyncMock, patch

from api.services import plant_knowledge_service as k

TOXIC_PAGE = (
    "About Us Adopt # Golden Pothos Devils Ivy  Additional Common Names: Pothos  "
    "Scientific Name: Epipremnum aureum  Family: Araceae  Toxicity: Toxic to Dogs, Toxic to Cats  "
    "Toxic Principles: Insoluble calcium oxalates  Clinical Signs: Oral irritation, drooling, vomiting [...] "
    "If you suspect your pet may have ingested a toxic substance, call poison control."
)
SAFE_PAGE = (
    "# Chlorophytum  Scientific Name: Anthericum comosum  Family: Asparagaceae  "
    "Non-Toxicity: Non-Toxic to Dogs, Non-Toxic to Cats, Non-Toxic to Horses  Toxic Principles: None"
)


def test_parse_aspca_toxic_page():
    parsed = k._parse_aspca(TOXIC_PAGE)
    assert parsed["dogs"] == "toxic" and parsed["cats"] == "toxic"
    assert parsed["principles"] == "Insoluble calcium oxalates"
    assert parsed["clinical_signs"] == "Oral irritation, drooling, vomiting"  # boilerplate trimmed


def test_parse_aspca_safe_page():
    parsed = k._parse_aspca(SAFE_PAGE)
    assert parsed["dogs"] == "safe" and parsed["cats"] == "safe"


def test_parse_aspca_ignores_pages_without_a_verdict():
    assert k._parse_aspca("Toxic and Non-Toxic Plant List - Cats. Aloe, Dracaena, ...") is None


def test_toxicity_block_toxic_beats_safe():
    block = k.toxicity_block({"dogs": "safe", "cats": "toxic", "principles": "Saponins"})
    assert block["pets"] == "toxic" and "cats" in block["details"] and "Saponins" in block["details"]


def test_as_days_rejects_nonsense():
    assert k._as_days("7") == 7
    assert k._as_days("7 days") == 7
    assert k._as_days(14.0) == 14
    assert k._as_days("weekly") is None
    assert k._as_days(0) is None and k._as_days(9999) is None and k._as_days(None) is None


def test_pet_toxicity_skips_list_pages_and_other_genera():
    results = [
        {"url": "https://www.aspca.org/pet-care/animal-poison-control/cats-plant-list", "content": TOXIC_PAGE},
        {"url": "https://www.aspca.org/pet-care/aspca-poison-control/toxic-and-non-toxic-plants/aloe",
         "content": TOXIC_PAGE.replace("Epipremnum aureum", "Aloe vera").replace("Golden Pothos", "Aloe")},
    ]
    with patch.object(k.TavilyService, "search_raw", AsyncMock(return_value=results)):
        found = asyncio.run(k.pet_toxicity("Ficus lyrata", "fiddle leaf fig"))
    assert found is None  # a wrong "toxic"/"safe" for the wrong plant must never be returned


def test_enrich_overrides_toxicity_normalises_days_and_records_verification():
    info = {
        "common_name": "Snake Plant", "scientific_name": "Sansevieria trifasciata",
        "watering": {"interval_days": "14 days"},
        "fertilizing": {"interval_days": 30},
        "toxicity": {"pets": "safe", "humans": "toxic", "details": "model guess"},
        "ai_filled_fields": ["fertilizing", "toxicity"],
    }
    species = {"accepted_name": "Dracaena trifasciata", "family": "Asparagaceae", "queried_name": "Sansevieria trifasciata",
               "was_synonym": True, "source_url": "https://www.gbif.org/species/1"}
    aspca = {"dogs": "toxic", "cats": "toxic", "principles": "Saponins", "source_url": "https://aspca/x"}
    with patch.object(k, "verify_species", AsyncMock(return_value=species)), \
         patch.object(k, "pet_toxicity", AsyncMock(return_value=aspca)):
        out = asyncio.run(k.enrich_plant_info(info))

    assert out["scientific_name"] == "Dracaena trifasciata" and out["also_known_as"] == "Sansevieria trifasciata"
    assert out["toxicity"]["pets"] == "toxic" and out["toxicity"]["humans"] == "toxic"
    assert out["ai_filled_fields"] == ["fertilizing"]
    assert out["watering"]["interval_days"] == 14
    assert [c["label"] for c in out["care_schedule"]] == ["Water every 14 days", "Fertilize every 30 days"]


def test_enrich_survives_when_both_sources_are_down():
    info = {"common_name": "Mystery", "scientific_name": "Nope nope"}
    with patch.object(k, "verify_species", AsyncMock(return_value=None)), \
         patch.object(k, "pet_toxicity", AsyncMock(return_value=None)):
        out = asyncio.run(k.enrich_plant_info(info))
    assert out["species_verified"] is None and out["care_schedule"] == []


def test_lookup_cache_serves_repeat_searches_without_calling_groq_again():
    k._LOOKUP_CACHE.clear()
    curated = {"common_name": "Pothos", "scientific_name": "Epipremnum aureum", "quick_start": ["x"]}
    with patch.object(k.TavilyService, "search_raw", AsyncMock(return_value=[])), \
         patch("api.services.perenual_service.PerenualService.get_care_info", AsyncMock(return_value=None)), \
         patch("api.services.groq_service.GroqService.curate_plant_lookup", AsyncMock(return_value=dict(curated))) as groq,          patch("api.services.groq_service.GroqService.curate_plant_profile", AsyncMock(return_value=None)),          patch.object(k, "wikipedia_summary", AsyncMock(return_value=None)), \
         patch.object(k, "enrich_plant_info", AsyncMock(side_effect=lambda info, p=None: info)):
        first = asyncio.run(k.lookup_plant("Pothos"))
        first["image_url"] = "mutated-by-the-route"          # the route mutates its result
        second = asyncio.run(k.lookup_plant("  pothos "))     # same plant, different spelling
    assert groq.await_count == 1
    assert "image_url" not in second                          # cache hands out copies
    k._LOOKUP_CACHE.clear()


def test_lookup_cache_ignores_rule_based_fallback_results():
    k._LOOKUP_CACHE.clear()
    with patch.object(k.TavilyService, "search_raw", AsyncMock(return_value=[])), \
         patch("api.services.perenual_service.PerenualService.get_care_info", AsyncMock(return_value=None)), \
         patch("api.services.groq_service.GroqService.curate_plant_lookup", AsyncMock(return_value=None)),          patch("api.services.groq_service.GroqService.curate_plant_profile", AsyncMock(return_value=None)),          patch.object(k, "wikipedia_summary", AsyncMock(return_value=None)), \
         patch.object(k, "enrich_plant_info", AsyncMock(side_effect=lambda info, p=None: info)):
        asyncio.run(k.lookup_plant("fern"))
    assert k._LOOKUP_CACHE == {}  # a rate-limited fallback must not stick for a day


def test_lookup_attaches_profile_wikipedia_and_merged_sources():
    k._LOOKUP_CACHE.clear()
    wiki = {"title": "Pothos", "extract": "x", "url": "https://en.wikipedia.org/wiki/Pothos", "thumbnail": None, "description": None}
    profile = {"overview": "A trailing vine.", "growing": {"temperature": "18-27 C"}}
    care = [{"title": "c", "url": "https://a.example/care", "content": "c"}]
    grow = [{"title": "g", "url": "https://b.example/grow", "content": "g"}, {"title": "dup", "url": "https://a.example/care", "content": "d"}]
    search = AsyncMock(side_effect=[care, grow])
    curated = {"common_name": "Pothos", "scientific_name": "Epipremnum aureum"}
    with patch.object(k.TavilyService, "search_raw", search),          patch("api.services.perenual_service.PerenualService.get_care_info", AsyncMock(return_value=None)),          patch("api.services.groq_service.GroqService.curate_plant_lookup", AsyncMock(return_value=dict(curated))),          patch("api.services.groq_service.GroqService.curate_plant_profile", AsyncMock(return_value=profile)),          patch.object(k, "wikipedia_summary", AsyncMock(return_value=wiki)),          patch.object(k, "enrich_plant_info", AsyncMock(side_effect=lambda info, p=None: info)):
        out = asyncio.run(k.lookup_plant("Pothos"))
    assert out["profile"] == profile and out["wikipedia"] == wiki
    assert out["sources"] == ["https://a.example/care", "https://b.example/grow", "https://en.wikipedia.org/wiki/Pothos"]
    k._LOOKUP_CACHE.clear()


def test_wikipedia_summary_rejects_disambiguation_and_errors():
    class Resp:
        def __init__(self, status, data): self.status_code, self._d = status, data
        def json(self): return self._d
        def raise_for_status(self): pass
    class Client:
        def __init__(self, *a, **kw): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False
        async def get(self, url, **kw):
            if "summary" in url:
                return Resp(200, {"type": "disambiguation", "extract": "may refer to"})
            return Resp(200, {"pages": []})
    with patch.object(k.httpx, "AsyncClient", Client):
        assert asyncio.run(k.wikipedia_summary("Pothos")) is None
    assert asyncio.run(k.wikipedia_summary("  ")) is None
