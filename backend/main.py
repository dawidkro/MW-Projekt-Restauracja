import os
from contextlib import asynccontextmanager

import pymysql
from pymysql.cursors import DictCursor
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field


def connect():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "app"),
        password=os.getenv("DB_PASSWORD", "apppass"),
        database=os.getenv("DB_NAME", "restaurant"),
        charset="utf8mb4",
        cursorclass=DictCursor,  # wiersze jako slowniki
    )


def get_db():
    conn = connect()
    try:
        yield conn
    finally:
        conn.close() 


# SCHEMA = [
#     """
#     CREATE TABLE IF NOT EXISTS orders (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         status VARCHAR(32) NOT NULL DEFAULT 'nowe'
#     ) ENGINE=InnoDB
#     """,
#     """
#     CREATE TABLE IF NOT EXISTS order_items (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         order_id INT NOT NULL,
#         name VARCHAR(100) NOT NULL,
#         qty INT NOT NULL,
#         FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
#     ) ENGINE=InnoDB
#     """,
# ]


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     conn = connect()
#     try:
#         with conn.cursor() as cur:
#             for stmt in SCHEMA:
#                 cur.execute(stmt)
#         conn.commit()
#     finally:
#         conn.close()
#     yield



MENU = {
    "Przystawki": ["Talerz wędlin", "Talerz serów", "Zupka"],
    "Napoje": ["Cola", "Woda", "Sok pomarańczowy", "Kawa"],
    "Dania główne": ["Frytki", "Nuggetsy", "Pizza", "Burger", "Sushi"],
    "Deser": ["Sernik", "Murzynek"],
}

DOSTEPNE_DANIA = set()
for dania in MENU.values():
    DOSTEPNE_DANIA.update(dania)


class OrderItem(BaseModel):
    name: str
    qty: int = Field(gt=0)  # qty > 0 - funkcja pydantic


class OrderIn(BaseModel):
    items: list[OrderItem] = Field(min_length=1)   # items > 1 - funkcja pydantic


class OrderOut(BaseModel):
    id: int
    items: list[OrderItem]
    status: str


app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json", lifespan=lifespan)


@app.get("/health")
def health():
    # backend jest zdrowy gdy zdrowa jest tez baza
    try:
        conn = connect()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        finally:
            conn.close()
    except pymysql.MySQLError:
        raise HTTPException(status_code=503, detail="Brak połączenia z bazą danych")
    return {"status": "ok"}


@app.get("/api/menu")
def get_menu():
    return MENU


@app.post("/api/orders", response_model=OrderOut, status_code=201)
def create_order(order: OrderIn, conn=Depends(get_db)):
    for item in order.items:
        if item.name not in DOSTEPNE_DANIA:
            raise HTTPException(status_code=400, detail=f"Nie ma w menu: {item.name}")

    with conn.cursor() as cur:
        cur.execute("INSERT INTO orders (status) VALUES (%s)", ("nowe",))
        order_id = cur.lastrowid
        cur.executemany(
            "INSERT INTO order_items (order_id, name, qty) VALUES (%s, %s, %s)",
            [(order_id, i.name, i.qty) for i in order.items],
        )
    conn.commit()

    return {
        "id": order_id,
        "items": [i.model_dump() for i in order.items],
        "status": "nowe",
    }


@app.get("/api/orders", response_model=list[OrderOut])
def list_orders(conn=Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute("SELECT id, status FROM orders ORDER BY id")
        orders = cur.fetchall()

        cur.execute("SELECT order_id, name, qty FROM order_items ORDER BY id")
        items = cur.fetchall()

    by_order = {o["id"]: [] for o in orders}
    for it in items:
        by_order[it["order_id"]].append({"name": it["name"], "qty": it["qty"]})

    return [{"id": o["id"], "status": o["status"], "items": by_order[o["id"]]} for o in orders]


@app.get("/api/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int, conn=Depends(get_db)):
    with conn.cursor() as cur:
        cur.execute("SELECT id, status FROM orders WHERE id = %s", (order_id,))
        order = cur.fetchone()
        if order is None:
            raise HTTPException(status_code=404, detail=f"Nie ma zamówienia nr {order_id}")

        cur.execute(
            "SELECT name, qty FROM order_items WHERE order_id = %s ORDER BY id",
            (order_id,),
        )
        items = cur.fetchall()

    return {"id": order["id"], "status": order["status"], "items": items}


@app.delete("/api/orders/{order_id}", status_code=204)
def delete_order(order_id: int, conn=Depends(get_db)):
    with conn.cursor() as cur:
        # pozycje z order_items usuwa baza (ON DELETE CASCADE)
        usuniete = cur.execute("DELETE FROM orders WHERE id = %s", (order_id,))
    conn.commit()

    if usuniete == 0:
        raise HTTPException(status_code=404, detail=f"Nie ma zamówienia nr {order_id}")
