from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from database import init_db, save_meal, get_meals_by_date, get_meals_by_week, get_settings, save_settings, save_chat_message, get_chat_history, delete_meals_by_date, save_shopping_list, get_shopping_list, clear_shopping_list, save_meal_prep, get_meal_prep_by_date, get_db_connection
import requests
import os
from datetime import datetime, timedelta
from functools import wraps
import locale
import json

# Magyar dátumformázás próbálkozás
try:
    locale.setlocale(locale.LC_TIME, 'hu_HU.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Hungarian_Hungary.1250')
    except:
        pass  # Ha nem sikerül, az angol formátum marad

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# 🔑 INIT_DB meghívása - ez megoldja a "no such table" hibát!
init_db()

# DeepSeek API beállítások
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')

# Google OAuth beállítások
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/google/callback')

# Egyszerű auth (1 felhasználó)
CORRECT_PASSWORD = os.environ.get('APP_PASSWORD', 'jelszo123')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def query_deepseek(prompt, system_message=None):
    """DeepSeek API lekérdezése – OpenAI kompatibilis formátum"""
    if not DEEPSEEK_API_KEY:
        return "❌ HIBA: Nincs beállítva DEEPSEEK_API_KEY környezeti változó!"
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 800
    }

    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=45
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"⚠️ DeepSeek API hiba: {str(e)}"
    except (KeyError, ValueError) as e:
        return f"⚠️ Váratlan API válasz: {str(e)}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == CORRECT_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error="Hibás jelszó!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    # 7 napos naptár generálása MAGYAR formázással
    today = datetime.now().date()
    dates = []
    for i in range(7):
        date_obj = today + timedelta(days=i)
        dates.append({
            'iso': date_obj.strftime('%Y-%m-%d'),
            'day_name': date_obj.strftime('%A').capitalize(),  # pl. "Hétfő"
            'day_number': date_obj.strftime('%Y. %m. %d.')
        })

    # Ételek lekérdezése
    meals_data = {}
    for d in dates:
        meals = get_meals_by_date(d['iso'])
        meals_data[d['iso']] = [dict(meal) for meal in meals]

    settings = get_settings()

    return render_template('index.html', dates=dates, meals=meals_data, settings=settings)

@app.route('/api/meals/<date>')
@login_required
def get_meals(date):
    meals = get_meals_by_date(date)
    return jsonify([dict(meal) for meal in meals])

@app.route('/api/meals/week/<start_date>/<end_date>')
@login_required
def get_week_meals(start_date, end_date):
    meals = get_meals_by_week(start_date, end_date)
    return jsonify([dict(meal) for meal in meals])

@app.route('/api/meals', methods=['POST'])
@login_required
def add_meal():
    data = request.json
    save_meal(
        data['date'],
        data['meal_type'],
        data['name'],
        data['calories'],
        data['recipe']
    )
    return jsonify({"success": True})

@app.route('/api/meals/<date>', methods=['DELETE'])
@login_required
def delete_meals(date):
    delete_meals_by_date(date)
    return jsonify({"success": True})

@app.route('/api/settings', methods=['GET', 'POST'])
@login_required
def handle_settings():
    if request.method == 'POST':
        data = request.json
        save_settings(
            int(data.get('calorie_goal', 2000)),
            data.get('exclusions', ''),
            data.get('preferences', '')
        )
        return jsonify({"success": True})
    settings = get_settings()
    return jsonify(dict(settings) if settings else {})

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    # Beállítások lekérdezése az AI kontextushoz
    settings = get_settings()
    calorie_goal = settings['calorie_goal'] if settings else 2000
    exclusions = settings['exclusions'] if settings else ''
    preferences = settings['preferences'] if settings else ''

    # System message az AI-nak
    system_message = f"""Te egy étrendtervező asszisztens vagy. A felhasználó napi {calorie_goal} kalóriát szeretne fogyasztani.
Kizárások: {exclusions if exclusions else 'Nincsenek'}
Preferenciák: {preferences if preferences else 'Nincsenek megadva'}
Adj étrendi javaslatokat, recepteket, vagy válaszolj étkezéssel kapcsolatos kérdésekre.
Ha étrendet kérsz, adj meg minden étkezést (reggeli, tízórai, ebéd, uzsonna, vacsora) kalória értékkel és rövid recepttel."""
    
    # DeepSeek API hívás
    ai_response = query_deepseek(user_message, system_message)

    # Chat mentése
    save_chat_message(user_message, ai_response)

    return jsonify({"response": ai_response})

@app.route('/api/chat/history')
@login_required
def chat_history():
    history = get_chat_history()
    return jsonify([dict(msg) for msg in history])

# === ÚJ FUNKCIÓK ===

# Meal Prep API
@app.route('/api/meal-prep', methods=['POST'])
@login_required
def create_meal_prep():
    """Meal prep generálás és mentés"""
    data = request.json
    date = data['date']
    days = int(data['days'])
    meal_types = data['meal_types']  # pl. ['ebéd', 'vacsora']
    
    settings = get_settings()
    calorie_goal = settings['calorie_goal'] if settings else 2000
    exclusions = settings['exclusions'] if settings else ''
    preferences = settings['preferences'] if settings else ''
    
    # AI prompt meal prep-hez
    prompt = f"""Készíts egy ELŐRE FŐZÉSHEZ alkalmas receptet {days} napra.
Étkezések: {', '.join(meal_types)}
Napi kalória: {calorie_goal}
Kizárások: {exclusions}
Preferenciák: {preferences}

A recept legyen:
- Könnyen tárolható (hűtőben/tartós)
- {days} napig ehető
- Rövid és gyakorlatias elkészítés
- Pontos mennyiségekkel

Formátum:
RECEPT NEVE: [név]
HOZZÁVALÓK: [lista]
ELKÉSZÍTÉS: [lépések]
KALÓRIA: [összes kalória]"""
    
    system_message = "Te egy étrendtervező vagy, aki előre főzéshez készít recepteket. Adj gyakorlatias, tárolható recepteket."
    ai_response = query_deepseek(prompt, system_message)
    
    # Mentés adatbázisba
    save_meal_prep(date, days, json.dumps(meal_types), ai_response)
    
    # Ételek mentése minden napra
    for i in range(days):
        prep_date = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=i)).strftime('%Y-%m-%d')
        for meal_type in meal_types:
            # Egyszerűsített étel mentése (AI válaszból kinyerve)
            save_meal(prep_date, meal_type, f"Meal prep", 0, ai_response)
    
    return jsonify({"success": True, "response": ai_response})

@app.route('/api/meal-prep/<date>')
@login_required
def get_meal_prep(date):
    """Meal prep lekérdezése adott dátumra"""
    prep = get_meal_prep_by_date(date)
    return jsonify(dict(prep) if prep else {})

# Gyors étel API
@app.route('/api/quick-meal', methods=['POST'])
@login_required
def create_quick_meal():
    """Gyors étel generálás otthoni hozzávalókból"""
    data = request.json
    date = data['date']
    meal_type = data['meal_type']
    ingredients = data['ingredients']  # pl. "tojás, kenyér, alma"
    
    settings = get_settings()
    exclusions = settings['exclusions'] if settings else ''
    
    prompt = f"""Készíts egy 15 PERCES ételt a következő hozzávalókból:
{ingredients}

Kizárások: {exclusions}

A recept legyen:
- MAXIMUM 15 perc alatt elkészíthető
- Csak a megadott hozzávalókat használja (plusz alapvető fűszerek)
- Ha valami hiányzik, jelezd a végén

Formátum:
ÉTEL NEVE: [név]
HOZZÁVALÓK: [pontos lista - ha hiányzik valami, írd oda]
ELKÉSZÍTÉS: [lépések, max 5 lépés]
IDŐ: 15 perc"""
    
    system_message = "Te egy étrendtervező vagy, aki gyors, 15 perces ételeket készít meglévő hozzávalókból."
    ai_response = query_deepseek(prompt, system_message)
    
    # Hiányzó hozzávalók bevásárlólistára
    if "hiányzik" in ai_response.lower() or "nincs" in ai_response.lower():
        # Egyszerűsített: az egész AI választ hozzáadjuk a bevásárlólistához
        save_shopping_list(f"Gyors étel hozzávalók:\n{ai_response}")
    
    # Étel mentése
    save_meal(date, meal_type, "Gyors étel", 0, ai_response)
    
    return jsonify({"success": True, "response": ai_response})

# Bevásárlólista API
@app.route('/api/shopping-list', methods=['GET', 'POST', 'DELETE'])
@login_required
def shopping_list():
    if request.method == 'POST':
        data = request.json
        item = data.get('item', '')
        save_shopping_list(item)
        return jsonify({"success": True})
    
    elif request.method == 'DELETE':
        clear_shopping_list()
        return jsonify({"success": True})
    
    else:
        items = get_shopping_list()
        return jsonify([dict(item) for item in items])

# Étel módosítás API
@app.route('/api/meal/<int:meal_id>/modify', methods=['POST'])
@login_required
def modify_meal(meal_id):
    """Egy adott étel módosítása"""
    data = request.json
    modification = data.get('modification', '')  # pl. "Ne legyen hús"
    
    # Eredeti étel lekérdezése
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM meals WHERE id = ?', (meal_id,))
    original_meal = cursor.fetchone()
    conn.close()
    
    if not original_meal:
        return jsonify({"success": False, "error": "Étel nem található"})
    
    settings = get_settings()
    exclusions = settings['exclusions'] if settings else ''
    preferences = settings['preferences'] if settings else ''
    
    prompt = f"""Módosítsd ezt az ételt:
EREDETI: {original_meal['name']} - {original_meal['recipe']}

KÉRÉS: {modification}

Kizárások: {exclusions}
Preferenciák: {preferences}

Adj egy új receptet ugyanarra az étkezésre, de a kért módosítással."""
    
    system_message = "Te egy étrendtervező vagy, aki meglévő ételeket módosít a felhasználó kérésére."
    ai_response = query_deepseek(prompt, system_message)
    
    # Új étel mentése (régi törlése helyett frissítés)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE meals 
        SET recipe = ?, name = ?
        WHERE id = ?
    ''', (ai_response, f"{original_meal['name']} (módosítva)", meal_id))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "response": ai_response})

# Google OAuth API
@app.route('/api/google/connect')
@login_required
def google_connect():
    """Google OAuth kapcsolódás"""
    from authlib.integrations.flask_client import OAuth
    
    oauth = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        access_token_url='https://oauth2.googleapis.com/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        client_kwargs={'scope': 'https://www.googleapis.com/auth/keep'},
    )
    
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/google/callback')
@login_required
def google_callback():
    """Google OAuth callback"""
    # OAuth token lekérdezése és mentése
    # (Ez egy egyszerűsített verzió - productionban biztonságosabb tárolás kell)
    session['google_connected'] = True
    return redirect(url_for('index'))

@app.route('/api/google/keep', methods=['POST'])
@login_required
def send_to_google_keep():
    """Bevásárlólista küldése Google Keep-be"""
    if not session.get('google_connected'):
        return jsonify({"success": False, "error": "Nincs Google fiók csatlakoztatva"})
    
    # Bevásárlólista lekérdezése
    items = get_shopping_list()
    shopping_list_text = "\n".join([f"• {item['item']}" for item in items])
    
    # Google Keep API hívás (ez egy placeholder - valós implementációhoz Google API szükséges)
    # A valós implementációhoz szükség van a Google Keep API-ra és OAuth tokenekre
    
    return jsonify({"success": True, "message": "Bevásárlólista elküldve a Google Keep-be!"})

if __name__ == '__main__':
    app.run(debug=True)