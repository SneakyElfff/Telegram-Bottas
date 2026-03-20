import os
import fastf1
import pandas as pd
from datetime import datetime, timedelta
import logging
from config.config import tz_map, DATA_DIR

logger = logging.getLogger(__name__)

os.makedirs(str(DATA_DIR / 'fastf1_cache'), exist_ok=True)
fastf1.Cache.enable_cache(str(DATA_DIR / 'fastf1_cache'))

days_to_wed = 4

def get_next_event():
    year = datetime.now().year

    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
    except Exception as e:
        logger.error(f"Failed to load F1 calendar: {e}")
        return None

    if schedule.empty:
        logger.info(f"No events found for year {year}")
        return None

    next_event = schedule[pd.to_datetime(schedule["EventDate"]) > pd.Timestamp.now(tz="UTC").to_datetime64()]

    if next_event.empty:
        logger.info(f"No more upcoming events in {year}")
        return None

    return next_event.iloc[0]

def is_race_week(event: pd.Series) -> bool:
    if event is None:
        return False

    start_day = pd.to_datetime(event["Session1DateUtc"])
    today = pd.Timestamp.now(tz="UTC")

    start_day_iso = start_day.isocalendar()
    today_iso = today.isocalendar()

    if today_iso[:2] == start_day_iso[:2]:
        return True

    return False


def get_fia_slug(event_name: str) -> str:
    return event_name.lower().replace(" grand prix", "-gp").replace(" ", "-")

def get_local_pre_media_day(event) -> datetime:
    race_local = event['Session5Date']
    wednesday = race_local - timedelta(days=days_to_wed)
    return wednesday.replace(hour=0, minute=0, second=0, microsecond=0)

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