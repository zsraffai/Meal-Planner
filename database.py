import os
import sqlite3
from datetime import datetime
import json

def get_db_connection():
    """Abszolút elérési út a meals.db-hez"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'meals.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Adatbázis inicializálása"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ételek tábla
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            name TEXT NOT NULL,
            calories INTEGER,
            recipe TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Beállítások tábla
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            calorie_goal INTEGER DEFAULT 2000,
            exclusions TEXT,
            preferences TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Chat előzmények tábla
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Bevásárlólista tábla (ÚJ)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shopping_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Meal prep tábla (ÚJ)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal_prep (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            days INTEGER NOT NULL,
            meal_types TEXT NOT NULL,  -- JSON array
            recipe TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Google OAuth token tábla (ÚJ)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS google_oauth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,  -- Egyszerűsített: 1 felhasználó
            access_token TEXT,
            refresh_token TEXT,
            token_expiry TIMESTAMP,
            connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Alapértelmezett beállítások beszúrása
    cursor.execute('SELECT COUNT(*) FROM settings')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO settings (calorie_goal, exclusions, preferences)
            VALUES (2000, '', '')
        ''')

    # Alapértelmezett Google OAuth rekord
    cursor.execute('SELECT COUNT(*) FROM google_oauth')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO google_oauth (user_id, access_token, refresh_token)
            VALUES (1, NULL, NULL)
        ''')

    conn.commit()
    conn.close()

def save_meal(date, meal_type, name, calories, recipe):
    """Étel mentése"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO meals (date, meal_type, name, calories, recipe)
        VALUES (?, ?, ?, ?, ?)
    ''', (date, meal_type, name, calories, recipe))
    conn.commit()
    conn.close()

def get_meals_by_date(date):
    """Ételek lekérdezése dátum alapján"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM meals WHERE date = ? ORDER BY id', (date,))
    meals = cursor.fetchall()
    conn.close()
    return meals

def get_meals_by_week(start_date, end_date):
    """Ételek lekérdezése hét alapján"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM meals
        WHERE date BETWEEN ? AND ?
        ORDER BY date, id
    ''', (start_date, end_date))
    meals = cursor.fetchall()
    conn.close()
    return meals

def get_settings():
    """Beállítások lekérdezése"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM settings ORDER BY id DESC LIMIT 1')
    settings = cursor.fetchone()
    conn.close()
    return settings

def save_settings(calorie_goal, exclusions, preferences):
    """Beállítások mentése"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE settings
        SET calorie_goal = ?, exclusions = ?, preferences = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = (SELECT MAX(id) FROM settings)
    ''', (calorie_goal, exclusions, preferences))
    conn.commit()
    conn.close()

def save_chat_message(message, response):
    """Chat üzenet mentése"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (message, response)
        VALUES (?, ?)
    ''', (message, response))
    conn.commit()
    conn.close()

def get_chat_history():
    """Chat előzmények lekérdezése"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat_history ORDER BY timestamp DESC LIMIT 50')
    messages = cursor.fetchall()
    conn.close()
    return messages

def delete_meals_by_date(date):
    """Ételek törlése dátum alapján"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM meals WHERE date = ?', (date,))
    conn.commit()
    conn.close()

# === ÚJ FUNKCIÓK ===

def save_shopping_list(item):
    """Bevásárlólista elem hozzáadása"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO shopping_list (item)
        VALUES (?)
    ''', (item,))
    conn.commit()
    conn.close()

def get_shopping_list():
    """Bevásárlólista lekérdezése"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM shopping_list ORDER BY added_at DESC')
    items = cursor.fetchall()
    conn.close()
    return items

def clear_shopping_list():
    """Bevásárlólista törlése"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM shopping_list')
    conn.commit()
    conn.close()

def save_meal_prep(date, days, meal_types, recipe):
    """Meal prep mentése"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO meal_prep (date, days, meal_types, recipe)
        VALUES (?, ?, ?, ?)
    ''', (date, days, meal_types, recipe))
    conn.commit()
    conn.close()

def get_meal_prep_by_date(date):
    """Meal prep lekérdezése dátum alapján"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM meal_prep WHERE date = ? ORDER BY id DESC LIMIT 1', (date,))
    prep = cursor.fetchone()
    conn.close()
    return prep

def save_google_oauth(access_token, refresh_token, token_expiry):
    """Google OAuth token mentése"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE google_oauth
        SET access_token = ?, refresh_token = ?, token_expiry = ?
        WHERE user_id = 1
    ''', (access_token, refresh_token, token_expiry))
    conn.commit()
    conn.close()

def get_google_oauth():
    """Google OAuth token lekérdezése"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM google_oauth WHERE user_id = 1')
    oauth = cursor.fetchone()
    conn.close()
    return oauth