Notatki z zajęć – Dawid Kropiewnicki
Projekt: MW-Projekt-Restauracja – zamówienia w restauracji (kuchnia)
---
Zajęcia 1 – 6.10.2026
Co zrobiła grupa:
Utworzyliśmy grupę i wybraliśmy temat: zamówienia w restauracji (kuchnia), działające podobnie jak kiosk w McDonaldzie.
Założyliśmy wspólne repozytorium na GitHubie i dodaliśmy pierwszy opis w README.
Co zrobiłem ja:
Założyłem repozytorium `MW-Projekt-Restauracja` (pierwszy commit).
Plan na następne zajęcia:
Szkielet: trzy kontenery, frontend pobiera JSON z backendu, backend łączy się z bazą.
---
Zajęcia 3 – 20.10.2026 – KM1
Co zrobiła grupa :
Pierwsza wersja frontendu jako statyczna strona (`index.html` + `nginx.conf`). Zrezygnowaliśmy z niej na rzecz Streamlit.
Backend w FastAPI z menu i zamówieniami, dane w Redisie (`redis:7-alpine`, wolumen, healthcheck).
Dockerfile dla backendu i frontendu, `docker-compose.yml` z trzema serwisami.
Widok zamówień (Kuchnia) we frontendzie.
Co zrobiłem ja:
Usunąłem wersję z `index.html` i `nginx.conf` i dodałem zarys aplikacji do składania zamówień w Streamlit (`app.py`) razem z jej `Dockerfile` i `requirements.txt`.
Problemy:
Wrzuciłem pliki frontendu do katalogu z literówką (`forntend`). Przenieśliśmy je do `frontend`, a zły katalog usunęliśmy.
KM1:
---
Zajęcia 6 – 10.11.2026 – KM2
Co zrobiła grupa:
Hasła i nazwy w zmiennych środowiskowych: `.env` (w `.gitignore`) i wzór `.env.example`, odczyt w `docker-compose.yml`.
Skrypt `init.sql` (schemat i dane startowe) montowany do `/docker-entrypoint-initdb.d`.
`curle.txt` z komendami curl do prezentacji backendu.
Co zrobiłem ja:
Endpointy `GET /api/orders/{id}` (404 dla nieistniejącego zamówienia) i `DELETE /api/orders/{id}` (204 albo 404).
Endpoint `/health`, który sprawdza połączenie z bazą (200 albo 503).
Healthcheck backendu w `docker-compose.yml` korzystający z `/health`. Frontend czeka teraz na zdrowy backend (`depends_on: condition: service_healthy`).
Przycisk „Usuń” w widoku Kuchnia.
Opis nowych endpointów w README.
---
Zajęcia 8 – 24.11.2026 – KM3
Przygotowanie (24.11):
Przejrzałem repo pod wymagania KM3. Okazało się, że backend nie startuje: commit `420a681` zakomentował funkcję `lifespan`, ale `FastAPI(..., lifespan=lifespan)` dalej się do niej odwoływało. Przez `NameError` przy imporcie backend nie przechodził healthchecka, więc frontend też nie wstawał.
Poprawiłem to (`36aaa8f`) i usunąłem zakomentowany kod tworzenia schematu, bo robi to teraz `init.sql` (`74a9660`).
Przerobiłem README: instrukcja uruchomienia, architektura, opis bazy i relacji, widoki frontendu, tabela endpointów z kodami błędów.
Dodałem `__pycache__/` do `.gitignore`.
Stan wymagań KM3:
Baza: oficjalny `mariadb:lts`, nazwany wolumen `dbdata`, tabele `orders` i `order_items` (1:N, klucz obcy z `ON DELETE CASCADE`), `init.sql` ze schematem i danymi startowymi, brak opublikowanego portu.
Frontend: dwa widoki (Obsługa i Kuchnia), komunikacja tylko z API backendu, własny Dockerfile.
KM3:
