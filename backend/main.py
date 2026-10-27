from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import get_connection

app = FastAPI()

# --- НАСТРОЙКА CORS (ОЧЕНЬ ВАЖНО!) ---
# Без этого React не сможет отправить запрос на бэкенд
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Разрешаем всем 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модель данных (как будут выглядеть данные от фронта)
class Client(BaseModel):
    name: str
    email: str

# 1. ПОЛУЧИТЬ ВСЕХ КЛИЕНТОВ (Кнопка "Показать данные")
@app.get("/api/clients")
def get_clients():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, email FROM clients ORDER BY id")
        # Превращаем кортежи в словари для React
        clients = [{"id": row[0], "name": row[1], "email": row[2]} for row in cur.fetchall()]
    conn.close()
    return clients

# 2. ДОБАВИТЬ КЛИЕНТА (Кнопка "Создать")
@app.post("/api/clients")
def create_client(client: Client):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO clients (name, email) VALUES (%s, %s) RETURNING id",
            (client.name, client.email)
        )
        new_id = cur.fetchone()[0]
        conn.commit()
    conn.close()
    return {"id": new_id, "message": "Клиент добавлен"}

# 3. ОБНОВИТЬ КЛИЕНТА (Кнопка "Редактировать")
@app.put("/api/clients/{client_id}")
def update_client(client_id: int, client: Client):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE clients SET name = %s, email = %s WHERE id = %s",
            (client.name, client.email, client_id)
        )
        conn.commit()
    conn.close()
    return {"message": "Клиент обновлен"}

# 4. УДАЛИТЬ КЛИЕНТА (Кнопка "Удалить")
@app.delete("/api/clients/{client_id}")
def delete_client(client_id: int):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM clients WHERE id = %s", (client_id,))
        conn.commit()
    conn.close()
    return {"message": "Клиент удален"}



@app.get("/api/recommendations/cinema")
def get_cinema_recommendations():
    conn = get_connection()
    with conn.cursor() as cur:
        # Сложный SQL-запрос: ищем тех, у кого есть события в магазинах 1 и 2, 
        # но НЕТ событий в магазине 3.
        cur.execute("""
            SELECT DISTINCT c.id, c.full_name, c.phone 
            FROM clients c
            JOIN events e1 ON c.id = e1.client_id AND e1.shop_id = 1
            JOIN events e2 ON c.id = e2.client_id AND e2.shop_id = 2
            WHERE c.id NOT IN (
                SELECT client_id FROM events WHERE shop_id = 3
            );
        """)
        clients = [{"id": row[0], "full_name": row[1], "phone": row[2]} for row in cur.fetchall()]
    conn.close()
    return clients


# --- ПОЛУЧИТЬ ИСТОРИЮ ВИЗИТОВ КЛИЕНТА (Лента событий) ---
@app.get("/api/clients/{client_id}/history")
def get_client_history(client_id: int):
    conn = get_connection()
    with conn.cursor() as cur:
        # Объединяем таблицу событий с таблицей магазинов, чтобы получить названия
        cur.execute("""
            SELECT e.id, s.name AS shop_name, e.event_type, e.amount, e.event_date
            FROM events e
            JOIN shops s ON e.shop_id = s.id
            WHERE e.client_id = %s
            ORDER BY e.event_date DESC
        """, (client_id,))
        
        events = []
        for row in cur.fetchall():
            events.append({
                "event_id": row[0],
                "shop_name": row[1],
                "event_type": row[2],
                "amount": float(row[3]),
                "event_date": row[4].strftime("%Y-%m-%d %H:%M")
            })
    conn.close()
    return events