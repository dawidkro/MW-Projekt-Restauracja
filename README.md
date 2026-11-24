MW-Projekt-Restauracja
Projekt w ramach Metod Wirtualizacji. Temat: zamówienia w restauracji (kuchnia), działające podobnie jak kiosk w McDonaldzie. Obsługa składa zamówienie z menu, a kuchnia widzi listę zamówień i usuwa zamówienia wydane.
Jak uruchomić
```bash
git clone https://github.com/dawidkro/MW-Projekt-Restauracja.git
cd MW-Projekt-Restauracja
cp .env.example .env        # opcjonalnie: własne hasła (bez .env compose użyje wartości domyślnych)
docker compose up --build
```
frontend: http://localhost:8501
backend (API): http://localhost:8000, dokumentacja Swagger: http://localhost:8000/api/docs
Baza tworzy tabele i dane startowe z `backend/init.sql` tylko przy pierwszym starcie (pusty wolumen). Po zmianie `init.sql` trzeba usunąć wolumen:
```bash
docker compose down -v
docker compose up --build
```
Architektura
```
przeglądarka ──► frontend (Streamlit, :8501) ──HTTP/JSON──► backend (FastAPI, :8000) ──► db (MariaDB, bez portu)
```
Kontener	Obraz	Port na hoście	Rola
`frontend`	własny `frontend/Dockerfile` (python:3.12-slim + Streamlit)	8501	dwa widoki: Obsługa i Kuchnia; łączy się tylko z backendem (`BACKEND_URL`)
`backend`	własny `backend/Dockerfile` (python:3.12-slim + FastAPI)	8000	REST API i walidacja; jedyny kontener, który łączy się z bazą
`db`	oficjalny `mariadb:lts`	brak	dane na nazwanym wolumenie `dbdata`; dostępna dla backendu po nazwie `db` w sieci compose
Kolejność startu pilnują healthchecki: backend czeka, aż `db` będzie zdrowa (`healthcheck.sh`), a frontend czeka na zdrowy backend (`GET /health`).
Konfiguracja przez zmienne środowiskowe (plik `.env`, wzór w `.env.example`): `DB_ROOT_PASSWORD`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`. Backend dostaje dodatkowo `DB_HOST` i `DB_PORT`, a frontend `BACKEND_URL`.
Baza danych
Schemat i dane startowe: `backend/init.sql`.
```
orders 1 ──< N order_items
```
Tabela	Kolumny	Powiązania
`orders`	`id`, `status` (domyślnie `nowe`)	jedno zamówienie
`order_items`	`id`, `order_id`, `name`, `qty`	`order_id` → `orders.id` (`ON DELETE CASCADE`)
Jedno zamówienie ma wiele pozycji (relacja 1:N przez klucz obcy `order_id`).
Usunięcie zamówienia usuwa jego pozycje (`ON DELETE CASCADE`).
Dane startowe: jedno przykładowe zamówienie (2× Pizza, 1× Cola).
Menu (kategorie i dania) jest zdefiniowane w backendzie (słownik `MENU` w `backend/main.py`).
Widoki frontendu
Obsługa: menu pobierane z `GET /api/menu`, zakładki z kategoriami, koszyk w panelu bocznym (dodawanie i „−”), przycisk „Zamów” wysyła `POST /api/orders`.
Kuchnia: lista zamówień z `GET /api/orders`, odświeżana co 3 s; przycisk „Usuń” usuwa zamówienie (`DELETE /api/orders/{id}`).
API
Format wymiany danych: JSON.
Metoda	Ścieżka	Opis	Kody
GET	`/health`	stan backendu i połączenia z bazą	200, 503
GET	`/api/menu`	menu pogrupowane po kategoriach	200
GET	`/api/orders`	lista zamówień	200
GET	`/api/orders/{id}`	jedno zamówienie	200, 404, 422
POST	`/api/orders`	nowe zamówienie	201, 400, 422
DELETE	`/api/orders/{id}`	usunięcie zamówienia z pozycjami	204, 404, 422
Kody błędów:
400: danie spoza menu (`{"detail": "Nie ma w menu: Hot dog"}`).
404: zamówienie o podanym `id` nie istnieje.
422: automatyczna walidacja FastAPI/pydantic, czyli `qty` ≤ 0, puste `items`, brakujące pole, niepoprawny JSON albo `id` niebędące liczbą.
Gotowe komendy curl do pokazu: `curle.txt`.
GET /api/menu
Zwraca obiekt, w którym kluczem jest kategoria, a wartością lista dań:
```json
{
  "Przystawki": ["Talerz wędlin", "Talerz serów", "Zupka"],
  "Napoje": ["Cola", "Woda", "Sok pomarańczowy", "Kawa"],
  "Dania główne": ["Frytki", "Nuggetsy", "Pizza", "Burger", "Sushi"],
  "Deser": ["Sernik", "Murzynek"]
}
```
POST /api/orders
Złożenie zamówienia. Ciało żądania:
```json
{
  "items": [
    { "name": "Pizza", "qty": 2 },
    { "name": "Cola",  "qty": 1 }
  ]
}
```
Walidacja: `items` musi mieć co najmniej 1 pozycję, `qty` musi być > 0 (inaczej 422), a `name` musi być daniem z menu (inaczej 400). Odpowiedź 201, czyli zamówienie z nadanym numerem:
```json
{ "id": 1, "items": [{ "name": "Pizza", "qty": 2 }, { "name": "Cola", "qty": 1 }], "status": "nowe" }
```
GET /api/orders
Zwraca listę zamówień posortowaną po `id`, każde w tym samym formacie co odpowiedź z POST.
GET /api/orders/{id}
Zwraca jedno zamówienie w tym samym formacie co odpowiedź z POST. Jeśli zamówienia o takim `id` nie ma, zwraca 404. Frontend z tego endpointu nie korzysta, można go sprawdzić w `/api/docs` lub curlem.
DELETE /api/orders/{id}
Usuwa zamówienie razem z jego pozycjami (przycisk „Usuń” w widoku Kuchnia). Odpowiedź 204 bez treści, a jeśli zamówienia o takim `id` nie ma, zwraca 404.
GET /health
Healthcheck backendu (używany w `docker-compose.yml`). Zwraca 200 i `{ "status": "ok" }`, gdy backend działa i ma połączenie z bazą. Jeśli baza nie odpowiada, zwraca 503.
Użycie AI
Claude (Opus, Sonnet 5.5):
szkielet i dopracowywanie frontendu z biblioteką Streamlit (`./frontend/app.py`)
stworzenie `docker-compose.yml`
ocena oraz sugestie do plików, m.in. obu Dockerfile oraz backendu (`./backend/main.py`); konkretnie implementacja `requirements.txt`
Claude Opus 5.5 (przygotowanie do KM3): przegląd repo pod wymagania KM3, wskazanie błędu po commicie `420a681` (odwołanie do zakomentowanej funkcji `lifespan`, przez które backend nie startował), plan prac, przeredagowanie README
