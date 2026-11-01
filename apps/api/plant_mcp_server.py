"""
Flourish Plant Knowledge MCP server.

Exposes the same verified plant sources the app's Explore lookup uses, so any MCP
client (Claude Code, Claude Desktop, ...) can ask plant questions and get grounded,
source-linked answers instead of guesses:

  - lookup_plant      full curated care profile (Perenual + web + Groq, GBIF/ASPCA-verified)
  - verify_species    GBIF taxonomy check; resolves outdated names to the accepted one
  - pet_toxicity      ASPCA dog/cat toxicity verdict with toxic principle and symptoms
  - plant_care_facts  Perenual's structured watering / sunlight / care-level data

No user data is read or written - these are public-plant lookups only, so unlike
mcp_server.py (QA, per-call Firebase token) this server needs no credentials from the
caller. It does use the server-side TAVILY_API_KEY / PERENUAL_API_KEY / GROQ_API_KEY
from apps/api/.env.

Run with:  uv run python plant_mcp_server.py        (stdio transport)
"""

from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP

from api.services import plant_knowledge_service as knowledge
from api.services.perenual_service import PerenualService

mcp = FastMCP("flourish-plants")


@mcp.tool()
async def lookup_plant(plant_name: str) -> Dict[str, Any]:
    """
    Full, actionable care profile for a plant by common or scientific name: watering and
    feeding intervals in days, light placement, a first-week checklist, warning signs with
    fixes, propagation, pet toxicity (ASPCA) and a GBIF-verified species name. Fields the
    sources didn't cover are listed in `ai_filled_fields`.
    """
    return await knowledge.lookup_plant(plant_name)


@mcp.tool()
async def verify_species(scientific_name: str) -> Dict[str, Any]:
    """
    Check a scientific name against GBIF. Returns the accepted name, family and a GBIF
    link; `was_synonym` is true when the name given is outdated (e.g. Sansevieria
    trifasciata -> Dracaena trifasciata). `found: false` means GBIF has no confident
    plant match - the name may be misspelled or not a plant.
    """
    result = await knowledge.verify_species(scientific_name)
    return {"found": True, **result} if result else {"found": False, "queried_name": scientific_name}


@mcp.tool()
async def pet_toxicity(scientific_name: str, common_name: Optional[str] = "") -> Dict[str, Any]:
    """
    ASPCA toxicity verdict for dogs and cats ("toxic" | "safe" | "unknown"), with the toxic
    principle, clinical signs and the ASPCA page it came from. `found: false` when the
    ASPCA has no individual page for this plant - treat that as unknown, never as safe.
    """
    aspca = await knowledge.pet_toxicity(scientific_name, common_name or "")
    if not aspca:
        return {"found": False, "scientific_name": scientific_name}
    return {
        "found": True,
        **knowledge.toxicity_block(aspca),
        "toxic_principle": aspca.get("principles"),
        "clinical_signs": aspca.get("clinical_signs"),
    }


@mcp.tool()
async def plant_care_facts(plant_name: str) -> Dict[str, Any]:
    """
    Structured care facts from Perenual's plant database (watering frequency in days,
    sunlight, care level, native habitat). Perenual matches loosely, so check that the
    returned scientific_name is the plant you meant. `found: false` when it has no match.
    """
    facts = await PerenualService.get_care_info(plant_name)
    if not facts:
        return {"found": False, "plant_name": plant_name}
    # Perenual can match a species yet return none of its care fields; reporting that as
    # a hit would read as "no watering needed". Say so explicitly instead.
    if facts.get("watering_frequency_days") is None and not facts.get("sunlight"):
        return {"found": False, "plant_name": plant_name, "matched_species": facts.get("scientific_name"),
                "reason": "Perenual matched the species but returned no care details for it; use lookup_plant instead."}
    return {"found": True, **facts}


if __name__ == "__main__":
    mcp.run()
