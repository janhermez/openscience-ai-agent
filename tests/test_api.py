import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_search_fixture(monkeypatch):
    monkeypatch.setenv("DATA_BACKEND", "fixture")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/search", params={"query": "Kubernetes"})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(item["source"] == "fixture" for item in response.json())


@pytest.mark.asyncio
async def test_quality_api():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/quality", json={"id": "demo", "title": "Article"})
    assert response.status_code == 200
    assert response.json()["work_id"] == "demo"


@pytest.mark.asyncio
async def test_agent_requires_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/ask", json={"question": "Find articles about Kubernetes"})
    assert response.status_code == 503
