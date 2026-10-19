import os

import requests
import streamlit as st

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")  # zmienna srodowiskowa jest w docker-compose.yml
API_MENU = BACKEND + "/api/menu"
API_ORDERS = BACKEND + "/api/orders"


def wyslij(metoda, url, dane=None):
    try:
        return requests.request(metoda, url, json=dane, timeout=5)
    except requests.RequestException:
        st.error(f"Brak połączenia z backendem ({url})")
        st.stop()

widok = st.sidebar.radio("Widok", ["Obsługa", "Kuchnia"], horizontal=True)

if widok == "Kuchnia":
    st.title("Kuchnia")

    @st.fragment(run_every="3s")
    def zamowienia():
        lista = wyslij("GET", API_ORDERS).json() 
        if not lista:
            st.info("Brak zamówień.")
            return
        for zam in lista:
            with st.container(border=True):
                st.subheader(f"Zamówienie nr {zam['id']}")
                st.caption(f"Status: {zam['status']}")
                for pozycja in zam["items"]:
                    st.write(f"{pozycja['qty']}× {pozycja['name']}")

    zamowienia()
    st.stop()  

menu = wyslij("GET", API_MENU).json()

if "koszyk" not in st.session_state:
    st.session_state.koszyk = {}
koszyk = st.session_state.koszyk


zakladki = st.tabs(list(menu.keys()))

for zakladka, dania in zip(zakladki, menu.values()):
    with zakladka:
        kolumny = st.columns(3)

        for i, danie in enumerate(dania):
            if kolumny[i % 3].button(danie, key=danie, width="stretch"):
                koszyk[danie] = koszyk.get(danie, 0) + 1
                st.toast(f"Dodano: {danie}")


with st.sidebar:
    if "komunikat" in st.session_state:
        st.success(st.session_state.pop("komunikat"))

    st.header("Zamówienie")
    if not koszyk:
        st.write("Zamówienie jest puste. Wybierz coś z menu.")

    for danie, ilosc in list(koszyk.items()):
        opis, minus = st.columns([4, 1])
        opis.write(f"{ilosc}× {danie}")
        if minus.button("−", key=f"minus-{danie}"):
            koszyk[danie] -= 1
            if koszyk[danie] == 0:
                del koszyk[danie]
            st.rerun()

    if st.button("Zamów", type="primary", width="stretch", disabled=not koszyk):
        zamowienie = {"items": [{"name": d, "qty": q} for d, q in koszyk.items()]}
        odp = wyslij("POST", API_ORDERS, zamowienie)
        if odp.status_code == 201:
            numer = odp.json()["id"]
            st.session_state.komunikat = f"Zamówienie nr {numer} wysłane do kuchni!"
            koszyk.clear()
            st.rerun()
        else:
            st.error(f"Backend odrzucił zamówienie ({odp.status_code})")
