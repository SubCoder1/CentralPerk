import datetime
import pytz


def activity(log):
    tz = pytz.timezone('Asia/Kolkata')

    duration = datetime.datetime.now().astimezone(tz) - log.astimezone(tz)
    days = duration.days
    mins = round(duration.seconds / 60)
    hours = round(mins / 60)

    if days:
        result = f"{days} days ago"
    elif hours:
        if hours > 1:
            result = f"{hours} hours ago"
        else:
            result = f"{hours} hour ago"
    elif mins:
        if mins > 1:
            result = f"{mins} minutes ago"
        else:
            result = f"{mins} minute ago"
    else:
        result = "seconds ago"
    
    return result
    
    