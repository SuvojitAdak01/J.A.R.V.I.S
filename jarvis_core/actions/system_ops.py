import datetime as dt

def get_current_time():
    now = dt.datetime.now()
    time_str = now.strftime("%I:%M %p")
    return f"The current time is {time_str}"

def get_current_date():
    now = dt.datetime.now()
    date_str = now.strftime("%A, %B, %d, %Y")
    return f"Today is {date_str}"

if __name__ == '__main__':
    print(get_current_time())
    print(get_current_date())