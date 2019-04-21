import datetime
import pytz


def activity(log):
    tz = pytz.timezone('Asia/Kolkata')
    time_now = datetime.datetime.now().astimezone(tz=tz)

    duration = time_now - log
    days = duration.days
    mins = round(duration.seconds / 60)
    hours = round(mins / 60)

    if days:
        result = f"{days} days ago"
    elif hours:
        result = f"{hours} minutes ago"
    elif mins:
        result = f"{mins} minutes ago"
    else:
        result = "seconds ago"
    
    return result
    
    