from collections import defaultdict
import json

# Mapping of day numbers to abbreviations
day_abbreviations = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]

# Function to format time in 24-hour format


def format_time(hour, minute):
    return f"{hour:02}:{minute:02}"

# Parse JSON periods into a structured dictionary of opening hours


# Parse JSON periods into a structured dictionary of opening hours
def parse_opening_hours(json_data):
    opening_hours = defaultdict(list)
    for period in json_data["periods"]:
        open_day = day_abbreviations[period["open"]["day"]]
        close_day = day_abbreviations[period["close"]["day"]]

        # Convert opening and closing times to "HH:MM" format
        open_time = format_time(
            period["open"]["hour"], period["open"]["minute"])
        close_time = format_time(
            period["close"]["hour"], period["close"]["minute"])

        # Format as a single time range string
        hours_range = f"{open_time}-{close_time}"

        # Group by the time range
        opening_hours[hours_range].append(open_day)
    return opening_hours

# Function to group consecutive days


def group_consecutive_days(days):
    day_order = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

    # Sort days in the regular order first
    days.sort(key=lambda d: day_order.index(d))

    # Ensure "Sa" and "Su" are always at the end if they are present
    weekdays = [day for day in days if day not in ["Sa", "Su"]]
    weekends = [day for day in days if day in ["Sa", "Su"]]

    grouped_days = []
    if weekdays:
        start_day = weekdays[0]
        end_day = weekdays[0]

        for i in range(1, len(weekdays)):
            current_day = weekdays[i]
            previous_day = weekdays[i - 1]

            # Check if current day is consecutive to the previous day
            if day_order.index(current_day) == day_order.index(previous_day) + 1:
                end_day = current_day
            else:
                # Append range or single day
                if start_day == end_day:
                    grouped_days.append(start_day)
                else:
                    grouped_days.append(f"{start_day}-{end_day}")
                start_day = current_day
                end_day = current_day

        # Append the final range for weekdays
        if start_day == end_day:
            grouped_days.append(start_day)
        else:
            grouped_days.append(f"{start_day}-{end_day}")

    # Append weekends as a separate group
    if weekends:
        if len(weekends) == 2:
            grouped_days.append("Sa-Su")
        else:
            grouped_days.append(weekends[0])

    return ', '.join(grouped_days)

# Function to format the grouped opening hours


def format_grouped_opening_hours(opening_hours):
    result = []
    for hours, days in opening_hours.items():
        grouped_days = group_consecutive_days(days)
        result.append(f"{grouped_days} {hours}")
    return "; ".join(result)
