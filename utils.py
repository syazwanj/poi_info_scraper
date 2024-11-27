from collections import defaultdict
import re
from datetime import datetime


# Day abbreviation mapping and ordering
day_order = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


# Convert time to 24-hour format
def convert_to_24h(index: int, time_str: str):
    # If open and end time are both within AM or within PM, the first AM/PM is dropped.
    if time_str.startswith("12") and ("AM" not in time_str or "PM" not in time_str):
        if index == 0:  # Open time
            time_str += " PM"
        elif index == 1:  # Close time
            time_str += " AM"

    return datetime.strptime(time_str.strip(), "%I:%M %p").strftime("%H:%M")


# Function to parse the string into a dictionary
def parse_opening_hours(opening_hours_list: list[str]):
    day_abbreviations = {
        0: "Mo",
        1: "Tu",
        2: "We",
        3: "Th",
        4: "Fr",
        5: "Sa",
        6: "Su",
    }
    opening_hours = {}
    for day_index, day in enumerate(opening_hours_list):
        day = day.encode("ascii", "ignore").decode("ascii")
        print(day)
        entries = re.match(r"(\d+:\d+\w+-\d+:\d+\w+)", day)
        print(entries)
        entries = entries.groups()
        print(entries)
        for entry in entries:
            # Split and convert each time range to 24-hour format
            hours = entry.split("–")
            converted_times = [
                convert_to_24h(index, t) for index, t in enumerate(hours)
            ]
            opening_hours[day_abbreviations[day_index]] = ["-".join(converted_times)]
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
