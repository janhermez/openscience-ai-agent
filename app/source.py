import json
import os
from pathlib import Path

import httpx

from app.models import Work
from app.settings import backend

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "examples.json"


def _fixture(query: str, limit: int) -> list[Work]:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    q = query.casefold().strip()
    return [Work.model_validate(item) for item in data if q in (item.get("title") or "").casefold() or q in " ".join(item.get("authors") or []).casefold()][:limit]


async def search_works(query: str, limit: int = 5) -> list[Work]:
    query = query.strip()
    if not query or len(query) > 200:
        raise ValueError("Zapytanie musi mieć od 1 do 200 znaków")
    limit = max(1, min(int(limit), 20))
    if backend() == "fixture":
        return _fixture(query, limit)

    params: dict[str, str | int] = {"search": query, "per_page": limit}
    key = os.getenv("OPENALEX_API_KEY", "").strip()
    if key:
        params["api_key"] = key
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=False) as client:
        response = await client.get("https://api.openalex.org/works", params=params)
        response.raise_for_status()
        payload = response.json()
    works: list[Work] = []
    for item in payload.get("results", []):
        authors = [
            entry.get("author", {}).get("display_name", "")
            for entry in item.get("authorships", [])
            if entry.get("author", {}).get("display_name")
        ]
        works.append(Work(
            id=str(item.get("id") or ""),
            title=item.get("title") or item.get("display_name"),
            publication_year=item.get("publication_year"),
            doi=item.get("doi"),
            authors=authors,
            abstract=_decode_abstract(item.get("abstract_inverted_index")),
            source="openalex",
            url=item.get("id"),
        ))
    return works


def _decode_abstract(index: dict | None) -> str | None:
    """Reconstruct abstract text from OpenAlex's position-based inverted index."""
    if not index:
        return None
    positions: dict[int, str] = {}
    for word, offsets in index.items():
        for position in offsets:
            if isinstance(position, int) and 0 <= position < 20000:
                positions[position] = word
    if not positions:
        return None
    return " ".join(positions[position] for position in sorted(positions))
