# OpenScience AI Agent — MVP (portfolio + potencjalna praca magisterska)

**Status:** wersja demonstracyjna / proof of concept. Projekt niezależny — **nie jest usługą Biblioteki Nauki ani ICM UW**.

## Cel

Eksperymentalny agent AI, który korzysta z narzędzi do wyszukiwania publikacji i sprawdzania jakości metadanych. Wersja 0.1 obsługuje **syntetyczne rekordy testowe** (domyślnie) lub publiczne API OpenAlex; nie podłącza się do infrastruktury pracodawcy.

### Co już działa

- REST API w FastAPI + automatyczna dokumentacja `/docs`.
- `GET /api/search`: wyszukiwanie przykładów (offline) lub publikacji przez OpenAlex.
- `POST /api/quality`: jawna, deterministyczna analiza braków w metadanych.
- `POST /api/ask`: opcjonalny agent LLM z **realnym function/tool calling**, dwoma narzędziami i limitem wywołań. Domyślnie lokalny Ollama (brak opłat API); opcjonalnie płatny OpenAI API.
- Testy pytest, CI GitHub Actions, Dockerfile.

**Nie działa jeszcze:** integracja z Biblioteką Nauki, pełny RAG, deduplikacja, panel administracyjny, pomiar jakości agentów. To planowane etapy, nie część obecnego MVP.

## Uruchomienie — Docker Desktop / WSL (najprostszy start)

```bash
unzip openscience-ai-agent-starter.zip
cd openscience-ai-agent-starter
cp .env.example .env
docker compose up --build
```

Otwórz http://127.0.0.1:8000/docs — dalej możesz testować polecenia `curl` z poniższej sekcji.

## Uruchomienie bez Dockera — WSL/Linux

Wymagany Python 3.11+ (sprawdź `python3 --version`; Ubuntu 20.04 może mieć domyślnie starszego Pythona). Jeśli już rozpakowałeś projekt podczas uruchamiania Dockera, nie rozpakowuj go ponownie.

```bash
unzip openscience-ai-agent-starter.zip
cd openscience-ai-agent-starter
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Otwórz: http://127.0.0.1:8000/docs

W drugim terminalu:

```bash
curl 'http://127.0.0.1:8000/api/search?query=kubernetes'
pytest -q
```

Aby sprawdzić reguły jakości (bez LLM):

```bash
curl -s -X POST http://127.0.0.1:8000/api/quality \
  -H 'Content-Type: application/json' \
  -d '{"id":"demo","title":"Testowy artykuł","publication_year":2025,"doi":null,"authors":["A. Nowak"],"abstract":null,"source":"manual"}'
```

## Tryb Live — OpenAlex

W `.env` ustaw `DATA_BACKEND=openalex`. Opcjonalnie dodaj `OPENALEX_API_KEY` z własnego konta; serwis ma limity i zasady używania. W trybie live zapytania wysyłane są na zewnętrzne API, więc nie wprowadzaj danych wewnętrznych ani poufnych. Otwórz ponownie `/api/search?query=...`.

Dokumentacja: https://help.openalex.org/api/ oraz https://help.openalex.org/api/searching/.

## Włączenie lokalnego agenta AI — Ollama (bez opłat API)

Po zastosowaniu zmian w istniejącej konfiguracji dodaj do lokalnego `.env`:

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3:4b
OLLAMA_BASE_URL=http://ollama:11434/v1
```

Własny `OPENAI_API_KEY` nie jest potrzebny. W katalogu repozytorium:

```bash
docker compose up -d --build
docker compose exec ollama ollama pull qwen3:4b
docker compose exec ollama ollama list
```

Pierwsze uruchomienie pobierze model (~2.5 GB). Wymagane jest miejsce na dysku.
Nie uruchamiaj modelu `:cloud` — jest to usługa chmurowa.
Ollama dostępna jest w Compose jako `http://ollama:11434` i na lokalnym komputerze pod `http://127.0.0.1:11434`.

```bash
curl -s -X POST http://127.0.0.1:8000/api/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Znajdź publikacje o Kubernetes i oceń kompletność ich metadanych."}'
```

Agent wykorzystuje zgodne z OpenAI Responses API oraz wywołania funkcji. W trybie lokalnym nie wymaga klucza. Nie wystawiaj portu modelu ani endpointu agenta publicznie. Tryb OpenAI pozostaje opcjonalny, ale wymaga własnego klucza API i może generować opłaty.

## Testy / jakość

```bash
pytest -q
python -m compileall -q app
```

Testy są offline; nie dokonują wywołań do OpenAlex ani OpenAI. Wstępne testy oceniają jedynie reguły i API, **nie skuteczność systemu AI**.

## Kierunek rozwoju

1. MVP: wyszukiwanie + reguły + tool calling + testy (ten pakiet).
2. Adapter Biblioteki Nauki: dopiero po sprawdzeniu oficjalnego, dozwolonego interfejsu, polityki użycia i autoryzacji organizacyjnej; bez modyfikowania produkcji.
3. Deduplikacja DOI, normalizacja autorów, jakościowe reguły specyficzne dla schematów i typów rekordów.
4. Porównanie: reguły vs LLM vs rozwiązanie hybrydowe, anotowany zbiór, precision/recall/F1, analiza błędów, koszt i latency.
5. RAG dla opisów i dokumentacji, monitoring, konteneryzacja, raport naukowy.

## Pomysł na pracę magisterską

**„Ocena skuteczności podejścia hybrydowego (reguły walidacyjne + modele językowe) w wykrywaniu problemów jakości metadanych publikacji naukowych”.**

Pytania badawcze: czy LLM poprawia skuteczność wykrywania problemów względem reguł? Jakie błędy popełnia? Ile kosztuje analiza jednego rekordu? Czy wyniki są reprodukowalne? Należy uzgodnić temat i metodologię z promotorem oraz formalnie uregulować ewentualne wykorzystanie danych lub wiedzy wewnętrznej z pracy.

## Bezpieczeństwo i ograniczenia

- Używaj tylko publicznych danych i dozwolonych endpointów. Pliki `data/examples.json` są **syntetyczne** i służą do demonstracji.
- Wynik „quality score” to uproszczona heurystyka, **nie ocena wartości naukowej publikacji**. DOI i abstrakt mogą być prawidłowo nieobecne w pewnych typach rekordów.
- Tekst metadanych jest traktowany jako dane niezaufane, a nie instrukcje dla agenta.
- Klucz API trzymamy w `.env`; nie logujemy sekretów ani nie commitujemy danych pracodawcy.
- Endpoint `/api/ask` nie ma jeszcze uwierzytelniania ani rate limitu. **Nie wystawiaj go publicznie z działającym kluczem**; przeznaczony jest do lokalnego developmentu.
- Przed publicznym udostępnieniem repozytorium wybierz licencję i sprawdź prawa do wykorzystywanych danych.
