from collections import defaultdict
import re
from datetime import datetime


# Day abbreviation mapping and ordering
day_order = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


# Convert time to 24-hour format
def convert_to_24h(time_str: str):
    # If time starts with 12 or 00, the AM/PM is dropped for some reason
    if time_str.startswith("00"):
        time_str = time_str + " AM"
    elif time_str.startswith("12"):
        time_str = time_str + " PM"

    return datetime.strptime(time_str.strip(), "%I:%M %p").strftime("%H:%M")


# Function to parse the string into a dictionary
def parse_opening_hours(opening_hours_str):
    day_abbreviations = {
        "Monday": "Mo",
        "Tuesday": "Tu",
        "Wednesday": "We",
        "Thursday": "Th",
        "Friday": "Fr",
        "Saturday": "Sa",
        "Sunday": "Su",
    }
    opening_hours = {}
    entries = opening_hours_str.split(",")
    for entry in entries:
        day, hours = re.match(r"(\w+):\s?(.*)", entry).groups()
        # Split and convert each time range to 24-hour format
        time_ranges = hours.split("–")
        converted_times = [convert_to_24h(t) for t in time_ranges]
        opening_hours[day_abbreviations[day]] = ["-".join(converted_times)]
    return opening_hours


# Function to group consecutive days
def group_consecutive_days(days):
    grouped_days = []
    start_day = days[0]
    end_day = days[0]

    for i in range(1, len(days)):
        current_day = days[i]
        previous_day = days[i - 1]

        # Check if current day is consecutive to previous day
        if day_order.index(current_day) == day_order.index(previous_day) + 1:
            end_day = current_day  # Extend the range
        else:
            # Add the grouped range
            if start_day == end_day:
                grouped_days.append(start_day)
            else:
                grouped_days.append(f"{start_day}-{end_day}")
            start_day = current_day  # Reset the start of the new range
            end_day = current_day

    # Add the last range
    if start_day == end_day:
        grouped_days.append(start_day)
    else:
        grouped_days.append(f"{start_day}-{end_day}")

    return ",".join(grouped_days)


# Function to group days by opening hours
def group_opening_hours(opening_hours):
    hours_to_days = defaultdict(list)

    for day, hours in opening_hours.items():
        hours_str = ",".join(hours)  # Join hours with a comma for a unique key
        hours_to_days[hours_str].append(day)

    result = []
    for hours, days in hours_to_days.items():
        # Sort days according to the week order
        days.sort(key=lambda x: day_order.index(x))
        # Group consecutive days
        grouped_days = group_consecutive_days(days)
        result.append(f"{grouped_days} {hours.replace(',', ', ')}")

    return ";".join(result)
