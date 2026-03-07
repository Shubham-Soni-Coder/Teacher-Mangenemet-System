from datetime import datetime

try:
    from zoneinfo import ZoneInfo

    IST = ZoneInfo("Asia/Kolkata")

    def now_ist():
        return datetime.now(IST)

except Exception:
    # fallback if timezone database missing
    from datetime import timedelta, timezone

    IST = timezone(timedelta(hours=5, minutes=30))

    def now_ist():
        return datetime.now(IST)
