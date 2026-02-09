import datetime

# Helper to get week and year from a date
def get_week_and_year(date):
    return date.isocalendar()[1], date.isocalendar()[0]


# Helper to get start and end dates of a week
def get_date_range(year, week, week_start='monday'):
    week_starts = {"monday": 0, "sunday": 6, "saturday": 5}
    weekday = week_starts.get(week_start, 0)
    start = datetime.date.fromisocalendar(year, week, 1)

    # Adjust to the preferred start
    start = start + datetime.timedelta(days=(weekday - start.weekday()) % 7)
    end = start + datetime.timedelta(days=6)

    return start, end
