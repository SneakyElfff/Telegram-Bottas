import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import zoneinfo
from config.config import tz_map

logger = logging.getLogger(__name__)

def build_url(year: int, slug: str) -> str:
    return f"https://www.fia.com/news/f1-{year}-{slug}-schedule-press-conferences"

def fetch_schedule(url: str, event) -> str | None:
    try:
        req = requests.get(url, timeout=15)
        if req.status_code != 200:
            return None
    except Exception as e:
        logger.error(f"Error fetching schedule: {e}")
        return None

    soup = BeautifulSoup(req.text, "html.parser")

    title = soup.find("h2").get_text(strip=True) if soup.find("h2") else "F1 Schedule of Press Conferences"

    table = soup.find("table")
    if not table:
        return None

    message = [f"<b>{title}</b>"]

    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        date_cell = cells[0].get_text(strip=True)
        if not date_cell or "Thursday" not in date_cell:
            continue
        message.append(f"<u>{date_cell}</u>\n")

        time_cell = cells[1].get_text(separator="\n", strip=True)
        who_cell = cells[2].get_text(separator="\n", strip=True)

        time_list = [line.strip() for line in time_cell.split("\n") if line.strip()]
        who_list = [line.strip() for line in who_cell.split("\n") if line.strip()]

        time_formatted = []
        for t in time_list:
            t = t.replace("hrs", "").strip()
            if len(t) == 4 and t.isdigit():
                t = f"{t[:2]}:{t[2:]}"
                # TODO: allow subscribers to choose timezone
                t = convert_timezone(t, event, "Europe/Minsk")
            time_formatted.append(t)

        message.append(f"<b><i>{time_formatted[0]}</i></b>")
        for driver in who_list[:3]:
            message.append(f"  • {driver}")

        message.append(f"\n<b><i>{time_formatted[1]}</i></b>")
        for driver in who_list[3:6]:
            message.append(f"  • {driver}")

        break

    message.append(f'\n<a href="{url}">Source</a>')
    return "\n".join(message)

def convert_timezone(time: str, event, tz: str) -> str:
    try:
        naive_datetime = datetime.combine(event["EventDate"].date(), datetime.strptime(time, "%H:%M").time())
    except ValueError:
        logger.error(f"Error converting time")
        return time

    local_datetime = naive_datetime.replace(tzinfo=zoneinfo.ZoneInfo(tz_map.get(event["Location"], "UTC")))

    target_datetime = local_datetime.astimezone(zoneinfo.ZoneInfo(tz))
    target_time = target_datetime.strftime("%H:%M MSK")

    return target_time
