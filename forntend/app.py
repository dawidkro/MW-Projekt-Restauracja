import streamlit as st

menu = {
    "Burgery": ["Cheeseburger", "Burger z boczkiem", "Wege burger"],
    "Napoje": ["Cola", "Woda", "Sok pomarańczowy", "Kawa"],
    "Dodatki": ["Frytki", "Nuggetsy"],
}

zakladki = st.tabs(list(menu.keys()))

for zakladka, (kategoria, dania) in zip(zakladki, menu.items()):
    with zakladka:
        kolumny = st.columns(3)
        for i, danie in enumerate(dania):
            if kolumny[i % 3].button(danie, key=danie, width="stretch"):
                st.toast(f"Dodano: {danie}")
