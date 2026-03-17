from service.f1_calendar import get_f1_calendar

GPS = {event['name']: event for event in get_f1_calendar(2026)}

print(GPS)