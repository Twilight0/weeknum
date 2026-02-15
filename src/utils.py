import datetime
import sys
import os

# Helper to get week and year from a date
def get_week_and_year(date):
    iso_cal = date.isocalendar()
    return iso_cal[1], iso_cal[0]


# Helper to get start and end dates of a week
def get_date_range(year, week, week_start='monday'):

    week_starts = {"monday": 0, "sunday": 6, "saturday": 5}
    weekday = week_starts.get(week_start, 0)
    start_iso = datetime.date.fromisocalendar(year, week, 1)
    current_weekday = start_iso.weekday()
    days_to_subtract = (current_weekday - weekday) % 7
    start = start_iso - datetime.timedelta(days=days_to_subtract)
    end = start + datetime.timedelta(days=6)

    return start, end
