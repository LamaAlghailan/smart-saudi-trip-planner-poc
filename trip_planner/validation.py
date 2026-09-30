"""Independent grounding and factual checks on LLM output; no silent repairs."""
from collections import Counter
from datetime import date, timedelta
import math

from jsonschema import Draft202012Validator

from .data import parse_time
from .engine import (DAY_END, DAY_START, STOPS_PER_DAY, TRANSFER_MINUTES,
                     clock_string, date_available, group_compatible, group_cost)
from .llm import response_schema


def validate_llm_output(output, retrieval, request, inventory):
    package = retrieval['candidate_package']
    candidate_cities = {c['city'] for c in package['candidate_cities']}
    supplied_ids = {a['ItemId'] for c in package['candidate_cities'] for a in c['candidate_activities']}
    source = {i['ItemId']: i for i in inventory}
    violations, warnings, grounded, selected_ids, invalid_ids, unknown_ids, unsupplied_ids = [], [], [], [], [], [], []
    def fail(code, detail):
        violations.append({'code': code, 'detail': detail})
    for error in Draft202012Validator(response_schema()).iter_errors(output):
        fail('schema', f'{list(error.absolute_path)}: {error.message}')
    body = output if isinstance(output, dict) else {}
    city = body.get('selected_destination')
    if not isinstance(city, str) or city not in candidate_cities:
        fail('city_not_supplied', 'Selected destination is not one of the supplied candidate cities.')
    alternative = body.get('alternative_destination')
    if alternative is not None and (not isinstance(alternative, str) or alternative not in candidate_cities or alternative == city):
        fail('invalid_alternative', 'Alternative must be a different supplied city or null.')
    itinerary = body.get('itinerary', [])
    if not isinstance(itinerary, list):
        itinerary = []
    days, names, total_cost = [], [], 0.0
    for entry in itinerary:
        if not isinstance(entry, dict):
            continue
        day = entry.get('day')
        day_valid = type(day) is int and 1 <= day <= request.days
        if not day_valid:
            fail('invalid_day', 'Itinerary day is outside the requested trip.')
        else:
            days.append(day)
        try:
            actual_date = date.fromisoformat(entry.get('date', ''))
        except (TypeError, ValueError):
            actual_date = None
        if actual_date is None or not request.start_date <= actual_date <= request.end_date:
            fail('itinerary_date', 'Every itinerary date must be a valid date within the trip range.')
        if day_valid and actual_date != request.start_date + timedelta(days=day - 1):
            fail('day_date_mismatch', 'Calendar date must match the numbered trip day.')
        activities = entry.get('activities', [])
        if not isinstance(activities, list):
            continue
        if not 1 <= len(activities) <= STOPS_PER_DAY:
            fail('daily_activity_count', f'Each day requires 1–{STOPS_PER_DAY} activities.')
        cursor = DAY_START
        for activity in activities:
            if not isinstance(activity, dict):
                continue
            item_id = activity.get('item_id')
            if not isinstance(item_id, str):
                fail('invalid_item_id_type', 'ItemId must be a string.')
                continue
            selected_ids.append(item_id)
            if item_id not in source:
                unknown_ids.append(item_id)
                fail('unknown_item_id', f'{item_id} is not in the validated tourism inventory.')
            if item_id not in supplied_ids:
                unsupplied_ids.append(item_id)
                fail('item_not_supplied', f'{item_id} was not supplied to the LLM.')
            if item_id not in source or item_id not in supplied_ids:
                invalid_ids.append(item_id)
                continue
            item = source[item_id]
            names.append((item['CityName'].casefold(), item['ItemName'].strip().casefold()))
            if item['CityName'] != city:
                fail('wrong_city', f'{item_id} does not belong to the selected destination.')
            if not item['IsActive']:
                fail('inactive', f'{item_id} is inactive.')
            if not group_compatible(item, request):
                fail('traveler_suitability', f'{item_id} violates the factual age or group constraints.')
            price = group_cost(item, request)
            total_cost += price
            if actual_date is None or not date_available(item, request, (actual_date - request.start_date).days):
                fail('date_availability', f'{item_id} is unavailable on the specified travel day.')
            start = parse_time(activity.get('start_time'))
            if start is None:
                fail('invalid_start_time', f'{item_id} has an invalid start time.')
                continue
            finish = start + math.ceil(item['DurationMinutes'])
            close = item['closes'] + (1440 if item['closes'] < item['opens'] else 0)
            if start < max(DAY_START, item['opens']) or finish > min(DAY_END, close):
                fail('opening_hours', f'{item_id} falls outside opening hours or the daily planning window.')
            if start < cursor:
                fail('overlap_or_transfer', f'{item_id} overlaps an earlier visit or violates the transfer buffer.')
            cursor = max(cursor, finish + TRANSFER_MINUTES)
            grounded.append({**item, 'day': day, 'group_cost': price,
                             'date': (request.start_date + timedelta(days=day - 1)).isoformat()
                                     if day_valid and request.start_date else None,
                             'start': clock_string(start), 'end': clock_string(finish),
                             'start_minute': start, 'end_minute': finish,
                             'llm_reason': activity.get('reason', '')})
    duplicates = sorted(i for i, n in Counter(selected_ids).items() if n > 1)
    duplicate_names = [list(name) for name, n in Counter(names).items() if n > 1]
    if duplicates or duplicate_names:
        fail('duplicate_attractions', 'ItemIds or normalized attraction names are repeated.')
    if sorted(days) != list(range(1, request.days + 1)):
        fail('trip_days', 'The itinerary must contain each requested day exactly once.')
    if not selected_ids:
        fail('empty_itinerary', 'No activities were returned.')
    total_cost = round(total_cost, 2)
    if total_cost > request.budget:
        fail('budget', f'Group cost SAR {total_cost:.2f} exceeds budget SAR {request.budget:.2f}.')
    if request.youngest_age is None or request.oldest_age is None:
        warnings.append('One or both ages not supplied: exact age bounds NOT FULLY CHECKED.')
    return {'valid': not violations, 'constraint_violations': violations, 'warnings': warnings,
            'invalid_item_ids': sorted(set(invalid_ids)), 'unknown_item_ids': sorted(set(unknown_ids)),
            'unsupplied_item_ids': sorted(set(unsupplied_ids)), 'duplicate_item_ids': duplicates,
            'duplicate_attraction_names': duplicate_names, 'selected_item_ids': selected_ids,
            'total_group_cost': total_cost, 'validated_itinerary': grounded if not violations else []}
