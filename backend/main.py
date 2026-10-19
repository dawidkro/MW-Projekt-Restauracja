import json
import os
import redis

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    decode_responses=True,
)


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


app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

@app.get("/api/menu")
def get_menu():
    return MENU

@app.post("/api/orders", response_model=OrderOut, status_code=201)
def create_order(order: OrderIn):
    for item in order.items:
        if item.name not in DOSTEPNE_DANIA:
            raise HTTPException(status_code=400, detail=f"Nie ma w menu: {item.name}")

    order_id = r.incr("order:next_id")
    nowe = {"id": order_id,
            "items": [i.model_dump() for i in order.items],
            "status": "nowe"}
    
    r.hset("orders", order_id, json.dumps(nowe))
    return nowe

@app.get("/api/orders", response_model=list[OrderOut])
def list_orders():
    data = r.hgetall("orders")
    orders = [json.loads(v) for v in data.values()]
    orders.sort(key=lambda order: order["id"])
    return orders
