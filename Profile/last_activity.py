import datetime
import pytz


def activity(log):
    tz = pytz.timezone('Asia/Kolkata')

    duration = datetime.datetime.now().astimezone(tz) - log.astimezone(tz)
    print(duration)
    days = duration.days
    mins = round(duration.seconds / 60)
    hours = round(mins / 60)

    print(f"Hours = {hours}, mins = {mins}")

    if days:
        result = f"{days} days ago"
    elif hours:
        if hours > 1:
            result = f"{hours} hours ago"
        else:
            result = f"{hours} hour ago"
    elif mins:
        result = f"{mins} minutes ago"
    else:
        result = "seconds ago"
    
    print(result)
    return result
    
    