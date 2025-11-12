import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

    BOT_NAME = "Saline"
    BOT_LOCATION = "West Bengal, Kolkata"

    SOCIAL_MEDIA = {
        'threads': 'https://www.threads.com/@saline_vtul',
        'instagram': 'https://www.instagram.com/saline_vtul'
    }

    PREMIUM_PRICE = 99
    FREE_MESSAGE_LIMIT = 5
    REFERRAL_POINTS = 5

    SUPPORTED_LANGUAGES = ['en', 'hi', 'hi-en', 'bn']
    TONES = ['flirting', 'bold', 'love_guru', 'friendly']
