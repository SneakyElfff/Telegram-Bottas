import fastf1
from datetime import date, timedelta
from zoneinfo import ZoneInfo
import logging

logger = logging.getLogger(__name__)

def get_f1_calendar(year: int = 2026):
    """
    Returns list of dicts like:
    {
        'round': 1,
        'name': 'Australian Grand Prix',
        'official_name': 'Australian Grand Prix',
        'location': 'Melbourne',
        'country': 'Australia',
        'friday_local': date(2026, 3, 6),
        'tz': 'Australia/Melbourne'
    }
    """
    try:
        fastf1.Cache.enable_cache('../fastf1_cache')
        schedule = fastf1.get_event_schedule(year)
    except Exception as e:
        logger.error(f"Failed to load F1 calendar: {e}")
        return []

    events = []

    for _, row in schedule.iterrows():
        if int(row['RoundNumber']) == 0:
            continue

        race_date = row['EventDate'].date()

        friday_offset = 2

        first_day = race_date - timedelta(days=friday_offset)

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

        tz_name = tz_map.get(row['Location'], 'UTC')
        if tz_name == 'UTC':
            logger.warning(f"No timezone for {row['Location']} – using UTC")

        events.append({
            'round': int(row['RoundNumber']),
            'name': row['EventName'],
            'official_name': row['OfficialEventName'] if 'OfficialEventName' in row else row['EventName'],
            'location': row['Location'],
            'country': row['Country'],
            'friday_local': first_day,
            'tz': tz_name
        })

    return events