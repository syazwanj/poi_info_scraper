from collections import defaultdict
from itertools import groupby
import pandas as pd

# Day mapping (Monday to Sunday)
days_map = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


# Format time
def format_time(hour, minute):
    return f"{hour:02}:{minute:02}"


# Parse JSON periods into a structured dictionary of opening hours
def parse_opening_hours(json_data):
    # Day mapping (Sunday = 0 shifted to Monday-first order)
    days_map = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]

    # Create DataFrame
    df = pd.DataFrame(
        [
            {
                "day": days_map[period["open"]["day"]],
                "hours": f"{period['open']['hour']:02}:{period['open']['minute']:02}-"
                f"{period['close']['hour']:02}:{period['close']['minute']:02}",
            }
            for period in json_data["periods"]
        ]
    )

    # Sort days in Monday-first order
    df["day_index"] = df["day"].apply(lambda d: (days_map.index(d) + 1) % 7)
    df = df.sort_values("day_index").drop(columns="day_index")

    # Group by hours and aggregate days
    grouped = df.groupby("hours")["day"].apply(list).reset_index()

    grouped["formatted_days"] = grouped["day"].apply(format_days)

    # Ensure Sunday ('Su') is always the last group in output
    grouped["sort_key"] = grouped["day"].apply(
        lambda days: 7 if "Su" in days else min(days_map.index(d) for d in days)
    )
    grouped = grouped.sort_values("sort_key").drop(columns="sort_key")

    # Generate final output string
    output = ";".join(
        f"{row['formatted_days']} {row['hours']}" for _, row in grouped.iterrows()
    )
    print(output)
    return output


def format_days(days):
    days = sorted(
        days, key=lambda d: days_map.index(d)
    )  # Ensure days are sorted correctly
    ranges, temp = [], [days[0]]
    for i in range(1, len(days)):
        if (
            days_map.index(days[i]) - days_map.index(temp[-1])
        ) % 7 == 1:  # Check for consecutive days
            temp.append(days[i])
        else:
            ranges.append(temp)
            temp = [days[i]]
    ranges.append(temp)
    return ",".join(["-".join([r[0], r[-1]] if len(r) > 1 else r) for r in ranges])
