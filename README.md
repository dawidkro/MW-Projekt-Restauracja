MW-Projekt-Restauracja
Projekt w ramach Metod Wirtualizacji. Temat: zamówienia w restauracji (kuchnia), działające podobnie jak kiosk w McDonaldzie. Obsługa składa zamówienie z menu, a kuchnia widzi listę zamówień, zmienia ich status i je usuwa.
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
`backend`	własny `backend/Dockerfile` (python:3.12-slim + FastAPI)	8000	REST API, walidacja, jedyny kontener, który rozmawia z bazą
`db`	oficjalny `mariadb:lts`	brak	dane na nazwanym wolumenie `dbdata`, dostępna dla backendu po nazwie `db` w sieci compose
Kolejność startu pilnują healthchecki: backend czeka, aż `db` będzie zdrowa (`healthcheck.sh`), a frontend czeka na zdrowy backend (`GET /health`).
Konfiguracja przez zmienne środowiskowe (plik `.env`, wzór w `.env.example`): `DB_ROOT_PASSWORD`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`. Backend dostaje też `DB_HOST` i `DB_PORT`, a frontend `BACKEND_URL`.
Baza danych
Schemat i dane startowe: `backend/init.sql`.
```
categories 1 ──< N dishes 1 ──< N order_items N >── 1 orders
```
Tabela	Kolumny	Powiązania
`categories`	`id`, `name`	kategorie menu (Przystawki, Napoje, Dania główne, Deser)
`dishes`	`id`, `category_id`, `name`	`category_id` → `categories.id`
`orders`	`id`, `status`	status: `nowe`, `w przygotowaniu`, `gotowe`
`order_items`	`id`, `order_id`, `dish_id`, `qty`	`order_id` → `orders.id` (`ON DELETE CASCADE`), `dish_id` → `dishes.id` (RESTRICT)
Usunięcie zamówienia usuwa jego pozycje (`ON DELETE CASCADE`).
Nie da się usunąć dania, które występuje w jakimś zamówieniu (klucz obcy bez CASCADE).
Dane startowe: pełne menu (4 kategorie, 14 dań) i jedno przykładowe zamówienie.
Widoki frontendu
Obsługa – menu pobierane z `GET /api/menu`, zakładki z kategoriami, koszyk w panelu bocznym (dodawanie i „−”), przycisk „Zamów” wysyła `POST /api/orders`.
Kuchnia – lista zamówień z `GET /api/orders`, odświeżana co 3 s. Przycisk „Oznacz: …” zmienia status (`PATCH /api/orders/{id}`), a przycisk „Usuń” usuwa zamówienie (`DELETE /api/orders/{id}`).
API
Format wymiany danych: JSON.
Metoda	Ścieżka	Opis	Kody
GET	`/health`	stan backendu i połączenia z bazą	200, 503
GET	`/api/menu`	menu z bazy pogrupowane po kategoriach	200
GET	`/api/orders`	lista zamówień	200
GET	`/api/orders/{id}`	jedno zamówienie	200, 400, 404
POST	`/api/orders`	nowe zamówienie	201, 400
PATCH	`/api/orders/{id}`	zmiana statusu zamówienia	200, 400, 404
DELETE	`/api/orders/{id}`	usunięcie zamówienia z pozycjami	204, 400, 404
Błędne dane wejściowe (zła wartość, brak pola, zły JSON, `id` niebędące liczbą) zwracają 400, a nieistniejące zamówienie 404. Gotowe komendy curl do pokazu: `curle.txt`.
GET /api/menu
Zwraca obiekt, w którym kluczem jest kategoria, a wartością lista dań (dane z tabel `categories` i `dishes`):
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
Walidacja: `items` musi mieć co najmniej 1 pozycję, `qty` > 0, a `name` musi być daniem z menu, inaczej 400. Odpowiedź 201, czyli zamówienie z nadanym numerem:
```json
{ "id": 1, "items": [{ "name": "Pizza", "qty": 2 }, { "name": "Cola", "qty": 1 }], "status": "nowe" }
```
GET /api/orders
Zwraca listę zamówień posortowaną po `id`, każde w tym samym formacie co odpowiedź z POST.
GET /api/orders/{id}
Zwraca jedno zamówienie w tym samym formacie co odpowiedź z POST. Jeśli zamówienia o takim `id` nie ma, zwraca 404.
PATCH /api/orders/{id}
Zmiana statusu (przycisk w widoku Kuchnia). Ciało żądania:
```json
{ "status": "w przygotowaniu" }
```
Dozwolone wartości: `nowe`, `w przygotowaniu`, `gotowe`, inne dają 400. Odpowiedź 200 ze zmienionym zamówieniem. Jeśli zamówienia nie ma, zwraca 404.
DELETE /api/orders/{id}
Usuwa zamówienie razem z jego pozycjami (przycisk „Usuń” w widoku Kuchnia). Odpowiedź 204 bez treści, a jeśli zamówienia o takim `id` nie ma, zwraca 404.
GET /health
Healthcheck backendu (używany w `docker-compose.yml`). Zwraca 200 i `{ "status": "ok" }`, gdy backend działa i ma połączenie z bazą. Jeśli baza nie odpowiada, zwraca 503.
Użycie AI
Claude Opus, Sonnet 5.5: szkielet i dopracowywanie frontendu z biblioteką Streamlit (`./frontend/app.py`)
stworzenie `docker-compose.yml`
ocena oraz sugestie do plików, m.in. obu Dockerfile oraz backendu (`./backend/main.py`); konkretnie implementacja `requirements.txt`
Claude Opus 5.5 (KM3): przegląd repo pod wymagania KM3, przeniesienie menu do bazy (tabele `categories` i `dishes`, `dish_id` w `order_items`, `SET NAMES` w `init.sql`), endpoint `PATCH /api/orders/{id}`, zamiana kodu 422 na 400, przyciski statusu w widoku Kuchnia, rozbudowa README i `curle.txt`
