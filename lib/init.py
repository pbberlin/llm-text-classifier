from   datetime import datetime, timedelta


lastLogTime = None

# start: reset
def logTimeSince(msg, startNew=False):

    global lastLogTime

    tNow = datetime.now()

    if startNew or lastLogTime is None:
        print(f"{msg}")
    else:
        duration = tNow - lastLogTime
        print(f"{msg} - took {duration.total_seconds()}s")


    lastLogTime = tNow
