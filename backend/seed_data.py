import psycopg
import random
from datetime import datetime, timedelta
from database import get_connection

# Списки для генерации случайных данных
first_names = ["Иван", "Алексей", "Мария", "Анна", "Дмитрий", "Елена", "Сергей", "Ольга", "Андрей", "Татьяна"]
last_names = ["Иванов", "Смирнов", "Кузнецова", "Попов", "Васильева", "Петров", "Соколова", "Михайлов", "Новикова", "Федоров"]
domains = ["mail.ru", "yandex.ru", "gmail.com"]

def generate_random_phone():
    # Генерирует номер вида +79991234567
    return f"+79{random.randint(100000000, 999999999)}"

def seed_database():
    conn = get_connection()
    
    with conn.cursor() as cur:
        # 1. Получаем ID магазинов из базы, чтобы знать, куда привязывать события
        cur.execute("SELECT id, name FROM shops")
        shops = cur.fetchall() 
        # shops будет выглядеть так: [(1, 'Спортмастер'), (2, 'Кофейня'), (3, 'Кинотеатр')]
        
        # 2. Генерируем 20 клиентов (имитация сбора из CRM)
        print("Генерация клиентов...")
        client_ids = []
        for _ in range(20):
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            phone = generate_random_phone()
            email = f"user{random.randint(100, 999)}@{random.choice(domains)}"
            
            # Добавляем клиента и сразу забираем его новый ID
            cur.execute(
                "INSERT INTO clients (full_name, phone, email) VALUES (%s, %s, %s) RETURNING id",
                (name, phone, email)
            )
            client_id = cur.fetchone()[0]
            client_ids.append(client_id)

        # 3. Генерируем события (имитация сбора из Касс и API бронирований)
        print("Генерация событий (визиты и покупки)...")
        event_types = ["purchase", "visit", "booking"]
        
        # Для каждого клиента генерируем от 1 до 5 случайных событий
        for client_id in client_ids:
            num_events = random.randint(1, 5)
            
            for _ in range(num_events):
                # Выбираем случайный магазин
                shop_id, shop_name = random.choice(shops)
                
                # Выбираем тип события
                event_type = random.choice(event_types)
                
                # Сумма покупки 
                amount = round(random.uniform(500.0, 15000.0), 2) if event_type == "purchase" else 0.0
                
                # Случайная дата за последние 30 дней
                random_days_ago = random.randint(0, 30)
                event_date = datetime.now() - timedelta(days=random_days_ago)
                
                cur.execute("""
                    INSERT INTO events (client_id, shop_id, event_type, amount, event_date)
                    VALUES (%s, %s, %s, %s, %s)
                """, (client_id, shop_id, event_type, amount, event_date))

        # сохраняем всё в бд
        conn.commit()
        print("База данных успешно заполнена тестовыми данными!")

    conn.close()

if __name__ == "__main__":
    seed_database()