"""Advisory single-activity time windows; never filters or selects candidates."""
from datetime import date, timedelta
import math
from .data import parse_time
from .engine import clock_string


def scheduling_windows(activity, package):
    constraints = package['planning_constraints']
    opening, closing = parse_time(activity['opens']), parse_time(activity['closes'])
    day_start, day_end = parse_time(constraints['day_start']), parse_time(constraints['day_end'])
    duration = math.ceil(activity['DurationMinutes'])
    usable_hours = None not in (opening, closing, day_start, day_end) and opening != closing
    earliest = latest = None
    if usable_hours:
        effective_close = closing + (1440 if closing < opening else 0)
        earliest = max(opening, day_start)
        latest = min(effective_close, day_end) - duration
    start = date.fromisoformat(package['trip_start'])
    available_from = date.fromisoformat(activity['available_from'])
    available_until = date.fromisoformat(activity['available_until'])
    rows = []
    for offset in range(package['trip_days']):
        day = start + timedelta(days=offset)
        reason = ('outside_availability' if not available_from <= day <= available_until
                  else 'unusable_hours' if not usable_hours
                  else 'duration_exceeds_window' if earliest > latest else None)
        row = {'date': day.isoformat(), 'schedulable': reason is None}
        if reason:
            row['reason'] = reason
        else:
            row.update(earliest_start=clock_string(earliest), latest_start=clock_string(latest))
        rows.append(row)
    return rows
