import datetime
import wikipediaapi

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


def get_todays_wiki():

    wiki_init = wikipediaapi.Wikipedia(user_agent='Weeknum/1.2.0 (twilight0@vivaldi.net), a cross-platform app built using open source tools', language='en')

    page_py = wiki_init.page('Wikipedia:On_this_day/Today')

    return page_py.text.replace(' [talk ·  edit ·  history]', '')
