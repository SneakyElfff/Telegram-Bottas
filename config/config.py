import logging
import os
from pathlib import Path
import telebot 
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable not set")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

bot = telebot.TeleBot(TOKEN)

tz_map = {
    'Melbourne': 'Australia/Melbourne',
    'Shanghai': 'Asia/Shanghai',
    'Suzuka': 'Asia/Tokyo',
    'Sakhir': 'Asia/Bahrain',
    'Jeddah': 'Asia/Riyadh',
    'Miami Gardens': 'America/New_York',
    'Montréal': 'America/Toronto',
    'Monte Carlo': 'Europe/Monaco',
    'Barcelona': 'Europe/Madrid',
    'Spielberg': 'Europe/Vienna',
    'Silverstone': 'Europe/London',
    'Spa-Francorchamps': 'Europe/Brussels',
    'Budapest': 'Europe/Budapest',
    'Zandvoort': 'Europe/Amsterdam',
    'Monza': 'Europe/Rome',
    'Madrid': 'Europe/Madrid',
    'Baku': 'Asia/Baku',
    'Marina Bay': 'Asia/Singapore',
    'Austin': 'America/Chicago',
    'Mexico City': 'America/Mexico_City',
    'São Paulo': 'America/Sao_Paulo',
    'Las Vegas': 'America/Los_Angeles',
    'Lusail': 'Asia/Qatar',
    'Yas Marina': 'Asia/Dubai',

    # Fallback
    '': 'UTC'
}

logging.basicConfig(
    level=logging.INFO,
    format = '%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler()]
)