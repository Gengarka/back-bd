import psycopg

# Настройки подключения к БД
DB_CONFIG = {
    "dbname": "hackathon_db",
    "user": "postgres",
    "password": "kuertoV90!", 
    "host": "127.0.0.1",
    "port": "5432"
}

def get_connection():
    return psycopg.connect(**DB_CONFIG)