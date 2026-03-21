import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def build_url(year: int, slug: str) -> str:
    return f"https://www.fia.com/news/f1-{year}-{slug}-schedule-press-conferences"

def fetch_schedule(url: str) -> str | None:
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

    message = [f"**{title}**"]

    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        date_cell = cells[0].get_text(strip=True)
        if not date_cell or "Thursday" not in date_cell:
            continue
        message.append(f"**{date_cell}**\n")

        time_cell = cells[1].get_text(separator="\n", strip=True)
        who_cell = cells[2].get_text(separator="\n", strip=True)

        time_list = [line.strip() for line in time_cell.split("\n") if line.strip()]
        who_list = [line.strip() for line in who_cell.split("\n") if line.strip()]

        time_formatted = []
        for t in time_list:
            t = t.replace("hrs", "").strip()
            if len(t) == 4 and t.isdigit():
                t = f"{t[:2]}:{t[2:]}"
            time_formatted.append(t)

        message.append(f"**{time_formatted[0]}**")
        for driver in who_list[:3]:
            message.append(f"  • {driver}")

        message.append(f"**{time_formatted[1]}**")
        for driver in who_list[3:6]:
            message.append(f"  • {driver}")

        break

    message.append("\nSource: " + url)
    return "\n".join(message)