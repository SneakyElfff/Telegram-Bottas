import logging
import zoneinfo
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from config.config import tz_map, bot
from service.f1_service import get_next_event, get_fia_slug, is_race_week, get_local_pre_media_day
from service.fia_service import build_url, fetch_schedule
from storage.database import load_last_notified, get_subscribers, save_last_notified

logger = logging.getLogger(__name__)

class Monitor:
    def __init__(self):
        self.last_notified = load_last_notified()
        self.scheduler = BlockingScheduler(timezone="UTC")

    def _check(self):
        try:
            event = get_next_event()
            if event is None:
                logger.warning("The season is over - skipping check")
                return

            gp_name = event["EventName"]
            round_num = int(event["RoundNumber"])
            year = event["EventDate"].year

            if (self.last_notified["round"] == round_num and
                self.last_notified["year"] == year):
                logger.info(f"Already notified for {gp_name} - skipping check")
                return

            if not is_race_week(event):
                logger.info(f"{gp_name} is not this weekend - skipping check")
                return

            wednesday = get_local_pre_media_day(event)
            local_now = datetime.now(zoneinfo.ZoneInfo(tz_map.get(event["Location"], "UTC")))

            if local_now < wednesday:
                logger.info(f"Still waiting for the Wednesday announcement at {gp_name} - skipping check")
                return

            slug = get_fia_slug(gp_name)
            url = build_url(year, slug)
            logger.info(f"It's race week at {gp_name}. Checking schedule: {url}")

            message_text = fetch_schedule(url)

            if message_text:
                subscribers = get_subscribers(active_only=True)
                logger.info(f"Schedule found! Notifying {len(subscribers)} subscribers")

                for chat_id in subscribers:
                    try:
                        bot.send_message(chat_id, message_text, parse_mode="Markdown")
                    except Exception as e:
                        logger.warning(f"Failed to notify {chat_id}: {e}")

                self.last_notified = {"round": round_num, "year": year}
                save_last_notified(self.last_notified)
            else:
                logger.info(f"Press schedule not yet published")

        except Exception as e:
            logger.error(f"Monitor error: {e}", exc_info=True)

    def run(self):
        logger.info(f"Monitor started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        self.scheduler.add_job(
            self._check,
            trigger=CronTrigger(
                day_of_week="wed",
                hour="6-22",
                minute="0,30",
                timezone="UTC",
            ),
            id="monitor-check",
            name="F1 Press Schedule Check",
            max_instances=1,
            misfire_grace_time=600,
        )

        self.scheduler.start()