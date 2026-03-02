import sys
import os

# Útvonal hozzáadása
path = os.path.expanduser('~/meal-planner')
if path not in sys.path:
    sys.path.insert(0, path)

# DEEPSEEK API kulcs beállítása (CSERÉLD KI A SAJÁT KULCSODRA!)
os.environ['DEEPSEEK_API_KEY'] = 'sk-0e3ddd0f26d0422fb40ec3bf124c2701'

# Google OAuth beállítások (CSERÉLD KI A SAJÁT KULCSODRA!)
os.environ['GOOGLE_CLIENT_ID'] = 'your-google-client-id'
os.environ['GOOGLE_CLIENT_SECRET'] = 'your-google-client-secret'
os.environ['GOOGLE_REDIRECT_URI'] = 'https://yourdomain.com/auth/google/callback'

from app import app as application