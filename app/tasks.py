from datetime import datetime
import pytz

async def get_current_time(timezone: str = "UTC") -> str:
    """
    Simulated tool called by the LLM.
    """
    try:
        tz = pytz.timezone(timezone)
    except Exception:
        tz = pytz.UTC
    now = datetime.now(tz)
    return f"The current time in {timezone} is {now.strftime('%Y-%m-%d %H:%M:%S')}."