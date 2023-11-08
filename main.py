# Import necessary modules
import locale
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from conf import LINK_LIGA  # Import LINK_LIGA from the 'conf' module

# Get current year from current date
year = datetime.now().year
locale.setlocale(locale.LC_ALL, 'pt_PT.UTF-8')  # Set the locale to handle Portuguese date format

# Since there is no year information
current_year_months = [7, 8, 9, 10, 11, 12]
next_year_months = [1, 2, 3, 4, 5, 6]

# Fetch the content of the web page using requests
web_page_content = requests.get(LINK_LIGA).content

# Create a BeautifulSoup object to parse the HTML content
soup = BeautifulSoup(web_page_content, 'html.parser')

# Initialize an empty list to store game details
games = []

# Find all table rows with class 'match-played-item'
trs = soup.find_all("tr", class_="match-played-item")

# Iterate through each table row and extract game information
for tr in trs:
    # Extract the date and time information from the table cell
    date_time = tr.find("td", class_="hidden-md-down text-center item-click").text.strip()

    # Skip games with unknown start time
    if date_time == "--:--":
        continue

    # Split date and hour, and format them
    date, time = date_time.split(" ")
    hour, minute = time.replace("H", ":").split(":")
    date = datetime.strptime(date, "%d/%b")
    if date.month in current_year_months:
        date = date.replace(year=year)
    else:
        date = date.replace(year=year + 1)
    # Format the start and end datetime strings
    date = date.replace(hour=int(hour), minute=int(minute))
    dstart = date.strftime("%Y%m%dT%H%M%SZ")
    dtend = (date + timedelta(minutes=105)).strftime("%Y%m%dT%H%M%SZ")

    # Extract team names and create game summary and location
    op1 = tr.find("span", class_="hidden-md-down").text
    op2 = tr.find("td", class_="table-match-played-team item-click").text.strip()
    summary = f"{op1} vs. {op2}"
    location = f"Estádio do {op1}"

    # Create a unique ID for the game using date and team names
    uid = f"{date.strftime('%Y%m%d')}_{op1.replace(' ', '_')}_{op2.replace(' ', '_')}"

    # Append the game details to the 'games' list as a dictionary
    games.append({
        "uid": uid,
        "dtstart": dstart,
        "dtend": dtend,
        "summary": summary,
        "location": location
    })

# Create the beginning of the iCalendar content
calendar_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Liga Portugal//Calendário de Jogos//PT
"""

# Iterate through each game and add its details to the iCalendar content
for game in games:
    calendar_content += f"""BEGIN:VEVENT
UID:{game['uid']}
DTSTAMP:{datetime.now().strftime("%Y%m%dT%H%M%SZ")}
DTSTART:{game['dtstart']}
DTEND:{game['dtend']}
SUMMARY:{game['summary']}
LOCATION:{game['location']}
END:VEVENT
"""

# Add the end of the iCalendar content
calendar_content += """END:VCALENDAR"""

# Save the iCalendar content to a file named "calendar.ics"
with open("calendar.ics", "w") as f:
    f.write(calendar_content)
