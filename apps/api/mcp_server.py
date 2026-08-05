"""
Flourish QA MCP server.

A real Model Context Protocol server (not the /api/mcp REST routes, which are just
REST endpoints labeled "MCP" - see docs/02-Tech-Stack-Architecture.md §1) that lets an
MCP client (Claude Code, Claude Desktop, etc.) drive agentic QA against a running
Flourish backend: check liveness, inspect the route contract, and exercise
authenticated flows end-to-end using a Firebase ID token supplied per call.

No credentials are stored in this server - the QA operator/agent passes a Firebase ID
token (e.g. from a dedicated QA account) to the authenticated tools at call time.

Run with:  python mcp_server.py
Configure FLOURISH_API_BASE_URL to point at the backend under test (defaults to the
local dev server).
"""

import os
import time
from typing import Any, Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP

API_BASE_URL = os.getenv("FLOURISH_API_BASE_URL", "http://localhost:8000")

mcp = FastMCP("flourish-qa")

def _auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}

@mcp.tool()
async def check_health() -> Dict[str, Any]:
    """Check the Flourish backend's liveness via GET /health."""
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10) as client:
        start = time.monotonic()
        response = await client.get("/health")
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        return {
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "body": _safe_json(response)
        }

@mcp.tool()
async def check_api_contract() -> Dict[str, Any]:
    """
    Fetch the live OpenAPI schema (GET /openapi.json) and confirm the routes that
    Flourish's core loop depends on are present. Flags anything missing so QA can
    catch an accidental route removal/rename before it ships.
    """
    critical_routes = [
        ("GET", "/api/auth/profile"),
        ("POST", "/api/auth/profile"),
        ("GET", "/api/plants/"),
        ("GET", "/api/tasks/today"),
        ("POST", "/api/tasks/{task_id}/complete"),
        ("GET", "/api/leaderboard/leaderboard"),
        ("GET", "/api/notifications/"),
        ("GET", "/health"),
    ]

    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10) as client:
        response = await client.get("/openapi.json")
        response.raise_for_status()
        schema = response.json()

    paths = schema.get("paths", {})
    missing = []
    present = []
    for method, path in critical_routes:
        methods = paths.get(path, {})
        if method.lower() in methods:
            present.append(f"{method} {path}")
        else:
            missing.append(f"{method} {path}")

    return {
        "route_count": len(paths),
        "critical_routes_present": present,
        "critical_routes_missing": missing,
        "contract_ok": len(missing) == 0
    }

@mcp.tool()
async def list_routes() -> List[str]:
    """List every route the live backend actually exposes (from its OpenAPI schema)."""
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10) as client:
        response = await client.get("/openapi.json")
        response.raise_for_status()
        schema = response.json()

    routes = []
    for path, methods in schema.get("paths", {}).items():
        for method in methods:
            routes.append(f"{method.upper()} {path}")
    return sorted(routes)

@mcp.tool()
async def authenticated_request(
    method: str,
    path: str,
    firebase_id_token: str,
    json_body: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Make a single authenticated request against the Flourish API using a caller-
    supplied Firebase ID token (e.g. from a QA test account) - for exercising any
    endpoint (create a plant, complete a task, check a leaderboard row, etc.) during
    an agentic QA session. Never persists the token.
    """
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=15) as client:
        start = time.monotonic()
        response = await client.request(
            method.upper(),
            path,
            headers=_auth_headers(firebase_id_token),
            json=json_body
        )
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        return {
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "body": _safe_json(response)
        }

@mcp.tool()
async def run_smoke_suite(firebase_id_token: str) -> Dict[str, Any]:
    """
    Run a small end-to-end smoke suite against the core plant-care loop using a
    caller-supplied Firebase ID token: profile, plants, today's tasks, leaderboard,
    notifications. Reports pass/fail and latency per step - a quick agentic QA gate
    after a deploy or a risky change.
    """
    steps = [
        ("profile", "GET", "/api/auth/profile"),
        ("plants", "GET", "/api/plants/"),
        ("today_tasks", "GET", "/api/tasks/today"),
        ("leaderboard", "GET", "/api/leaderboard/leaderboard"),
        ("notifications", "GET", "/api/notifications/"),
    ]

    results = []
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=15) as client:
        for name, method, path in steps:
            start = time.monotonic()
            try:
                response = await client.request(method, path, headers=_auth_headers(firebase_id_token))
                latency_ms = round((time.monotonic() - start) * 1000, 1)
                results.append({
                    "step": name,
                    "passed": response.status_code < 400,
                    "status_code": response.status_code,
                    "latency_ms": latency_ms
                })
            except Exception as e:
                results.append({"step": name, "passed": False, "error": str(e)})

    return {
        "all_passed": all(r.get("passed") for r in results),
        "steps": results
    }

def _safe_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return response.text[:500]

if __name__ == "__main__":
    mcp.run()
