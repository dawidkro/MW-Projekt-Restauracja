# MW-Projekt-Restauracja

Projekt w ramach Metod Wirtualizacji  

Użycie AI (Claude Opus, Sonnet 5.5):
- szkielet i dopracowywanie frontendu z biblioteką Streamlit (./frontend/app.py) 
- stworzenie docker-compose.yml
- ocena oraz sugestie do plików, m.in oba Dockerfile oraz backend (./backend/main.py); konkretnie implementacja requirements.txt

Format wymiany danych - JSON

GET /api/menu - Backend --> Frontend :
Zwraca obiekt w którym kluczem jest kategorią a wartością lista dań: 
```json
{
  "Przystawki": ["Talerz wędlin", "Talerz serów", "Zupka"],
  "Napoje": ["Cola", "Woda", "Sok pomarańczowy", "Kawa"],
  "Dania główne": ["Frytki", "Nuggetsy", "Pizza", "Burger", "Sushi"],
  "Deser": ["Sernik", "Murzynek"]
}
```
POST /api/orders - Frontend --> Backend:
Złożenie zamówienia gdzie ciało żądania wygląda tak:
```json
{
  "items": [
    { "name": "Pizza", "qty": 2 },
    { "name": "Cola",  "qty": 1 }
  ]
}
```
Odpowiedź, czyli zamówienie z nadanym numerem:

```json
{ "id": 1, "items": [{ "name": "Pizza", "qty": 2 }, { "name": "Cola", "qty": 1 }], "status": "nowe" }
```

GET /api/orders - Backend --> Frontend
Zwraca listę zamówień posortowaną po id, w tym samym formacie co odpowiedź z POST.
