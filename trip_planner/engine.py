"""Shared factual constraints, candidate scoring, and feasibility checks."""
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
import csv
import io
import heapq
import math
from statistics import mean

from .data import number
from .profiles import preference_components, mapping_debug

STOPS_PER_DAY = 3
DAY_START = 9 * 60
DAY_END = 22 * 60
TRANSFER_MINUTES = 30


@dataclass(frozen=True)
class TripRequest:
    birth_country: str
    start_date: date
    end_date: date
    budget: float = 500
    adults: int = 1
    children: int = 0
    youngest_age: int | None = None
    oldest_age: int | None = None

    @property
    def days(self):
        return (self.end_date - self.start_date).days + 1

    @property
    def travelers(self):
        return self.adults + self.children

    def validate(self):
        if not self.birth_country.strip():
            raise ValueError('Choose a birth country.')
        if type(self.start_date) is not date or type(self.end_date) is not date:
            raise ValueError('Start Date and End Date are required.')
        if self.end_date < self.start_date:
            raise ValueError('End Date must be on or after Start Date.')
        if not 1 <= self.days <= 14:
            raise ValueError('The supported trip length is 1 to 14 days, inclusive.')
        if not math.isfinite(self.budget) or self.budget < 0:
            raise ValueError('The total group budget must be finite and nonnegative.')
        if (not isinstance(self.adults, int) or not isinstance(self.children, int)
                or self.adults < 1 or self.children < 0 or self.travelers > 50):
            raise ValueError('Use at least one adult and no more than 50 travelers.')
        for age in (self.youngest_age, self.oldest_age):
            if age is not None and (type(age) is not int or not 0 <= age <= 120):
                raise ValueError('Optional ages must be integers from 0 to 120.')
        if self.youngest_age is not None and self.oldest_age is not None and self.youngest_age > self.oldest_age:
            raise ValueError('Youngest age must be no greater than oldest age.')
        if self.oldest_age is not None and self.oldest_age < 18:
            raise ValueError('Oldest age must include the adult traveler (18+).')
        if self.youngest_age is not None and ((self.children and self.youngest_age >= 18)
                or (not self.children and self.youngest_age < 18)):
            raise ValueError('Youngest age must agree with the child count (children are under 18).')



def unique_inventory(items):
    """Stable deduplication before counts or means; duplicate names cannot inflate fit."""
    seen_ids, seen_names, result = set(), set(), []
    for item in sorted(items, key=lambda i: (i['CityName'].casefold(), i['ItemId'])):
        identity = (item['CityName'].strip().casefold(), item['ItemName'].strip().casefold())
        if item['ItemId'] not in seen_ids and identity not in seen_names:
            result.append(item)
            seen_ids.add(item['ItemId'])
            seen_names.add(identity)
    return result


def group_cost(item, request):
    # No child discount is invented; source Price is assumed per traveler.
    return round(item['Price'] * request.travelers, 2)


def date_available(item, request, offset):
    day = request.start_date + timedelta(days=offset)
    return availability_overlaps(item, day, day)


def availability_overlaps(item, start, end):
    lower, upper = item.get('available_from'), item.get('available_until')
    return (type(lower) is date and type(upper) is date and lower <= upper
            and lower <= end and upper >= start)


def filter_by_trip_dates(items, trip_start, trip_end):
    """Inclusive overlap; unknown or reversed normalized bounds are excluded."""
    if type(trip_start) is not date or type(trip_end) is not date or trip_end < trip_start:
        raise ValueError('A valid inclusive trip date range is required.')
    return [i for i in items if availability_overlaps(i, trip_start, trip_end)]


def slot(item, cursor):
    close = item['closes'] + (1440 if item['closes'] < item['opens'] else 0)
    begin = max(cursor, item['opens'])
    end = begin + math.ceil(item['DurationMinutes'])
    return (begin, end) if end <= min(close, DAY_END) else None


def group_compatible(item, request):
    if request.youngest_age is not None and item['MinAge'] > request.youngest_age:
        return False
    if request.oldest_age is not None and item['MaxAge'] < request.oldest_age:
        return False
    if item['MaxAge'] < 18 or suitability(item.get('SuitableForAdults')) == 0:
        return False
    if request.children and (item['MinAge'] >= 18 or suitability(item.get('SuitableForChildren')) == 0):
        return False
    if (request.children and request.youngest_age is not None and request.youngest_age < 3
            and suitability(item.get('SuitableForInfants')) == 0):
        return False
    return True


def suitability(value):
    if str(value).casefold() in ('true', 'false'):
        return float(str(value).casefold() == 'true')
    score = number(value)
    return score if score is not None and 0 <= score <= 1 else .5


def group_affinity(item, request):
    adult = suitability(item.get('SuitableForAdults'))
    child = suitability(item.get('SuitableForChildren'))
    if request.children and request.youngest_age is not None and request.youngest_age < 3:
        child = min(child, suitability(item.get('SuitableForInfants')))
    return (request.adults * adult + request.children * child) / request.travelers


def item_components(item, request, resolved):
    return {**(preference_components(item, resolved['wvs_profile']) if resolved['wvs_profile'] else {}),
            'group': group_affinity(item, request),
            'quality': .6 * item['PopularityScore'] + .4 * item['AvgRating'] / 5}


def weighted_score(components, weights):
    return 100 * sum(components[key] * weight for key, weight in weights.items())


def distribution(items, key):
    counts = Counter(i[key] for i in items)
    return {name: count / len(items) for name, count in sorted(counts.items())} if items else {}


def cheapest_feasible_anchors(items, request):
    """Minimum-cost distinct activity/day matching, a pre-ranking feasibility check.

    Unit-capacity min-cost flow supplies a witness of at least one affordable visit
    per day. This does not schedule a multi-stop itinerary or reward extra stock.
    """
    items = sorted(items, key=lambda i: i['ItemId'])
    sink = 1 + request.days + len(items)
    graph = [[] for _ in range(sink + 1)]
    links = []
    def edge(a, b, cost):
        forward = [b, len(graph[b]), 1, cost]
        backward = [a, len(graph[a]), 0, -cost]
        graph[a].append(forward)
        graph[b].append(backward)
        return forward
    for day in range(request.days):
        edge(0, 1 + day, 0)
        for index, item in enumerate(items):
            if date_available(item, request, day):
                link = edge(1 + day, 1 + request.days + index, round(group_cost(item, request) * 100))
                links.append((day, item['ItemId'], link))
    for index in range(len(items)):
        edge(1 + request.days + index, sink, 0)
    potentials = [0] * len(graph)
    spent = 0
    for _ in range(request.days):
        distances = [math.inf] * len(graph)
        previous = [None] * len(graph)
        distances[0] = 0
        queue = [(0, 0)]
        while queue:
            distance, node = heapq.heappop(queue)
            if distance != distances[node]:
                continue
            for index, (target, _, capacity, cost) in enumerate(graph[node]):
                next_distance = distance + cost + potentials[node] - potentials[target]
                if capacity and next_distance < distances[target]:
                    distances[target] = next_distance
                    previous[target] = (node, index)
                    heapq.heappush(queue, (next_distance, target))
        if previous[sink] is None:
            break
        extra_cost = distances[sink] + potentials[sink] - potentials[0]
        if spent + extra_cost > math.floor(request.budget * 100 + 1e-7):
            break
        spent += extra_cost
        for node, distance in enumerate(distances):
            if distance < math.inf:
                potentials[node] += distance
        node = sink
        while node != 0:
            parent, index = previous[node]
            link = graph[parent][index]
            link[2] -= 1
            graph[node][link[1]][2] += 1
            node = parent
    return {day: item_id for day, item_id, link in links if link[2] == 0}


def daily_anchors(items, request, resolved=None):
    """Exact branch-and-bound over activity sets, with date matching per set.

    Lexicographic objective: total relevance, quality, negative cost, ItemIds.
    Cheapest matching is used only to prove feasibility and seed the search.
    Scores use 10 decimal places, consistent with existing ranking precision.
    """
    if resolved is None:
        from .profiles import BASIC, resolve_profile
        resolved = resolve_profile(None, BASIC)
    items = [i for i in items if i['IsActive'] and group_compatible(i, request)
             and slot(i, DAY_START) is not None and group_cost(i, request) <= request.budget]
    witness = cheapest_feasible_anchors(items, request)
    if len(witness) != request.days:
        return witness
    scale = 10**10
    records = []
    for item in items:
        components = item_components(item, request, resolved)
        records.append((item, round(weighted_score(components, resolved['weights']) * scale),
                        round(components['quality'] * scale), round(group_cost(item, request)*100)))
    records.sort(key=lambda row: (-row[1], -row[2], row[3], row[0]['ItemId']))
    selected = {v for v in witness.values()}
    initial = [r for r in records if r[0]['ItemId'] in selected]
    best = (sum(r[1] for r in initial), sum(r[2] for r in initial), -sum(r[3] for r in initial))
    best_ids = tuple(sorted(selected))
    best_assignment = witness
    budget = math.floor(request.budget*100 + 1e-7)
    def search(index, chosen, relevance, quality, cost):
        nonlocal best, best_ids, best_assignment
        needed = request.days-len(chosen)
        remaining = records[index:]
        if cost > budget or len(remaining) < needed:
            return
        if needed == 0:
            objective = (relevance, quality, -cost)
            ids = tuple(sorted(r[0]['ItemId'] for r in chosen))
            if objective < best or (objective == best and ids >= best_ids):
                return
            assignment = cheapest_feasible_anchors([r[0] for r in chosen], request)
            if len(assignment) == request.days:
                best, best_ids, best_assignment = objective, ids, assignment
            return
        min_cost = sum(sorted(r[3] for r in remaining)[:needed])
        if cost + min_cost > budget:
            return
        upper = (relevance + sum(r[1] for r in remaining[:needed]),
                 quality + sum(sorted((r[2] for r in remaining), reverse=True)[:needed]),
                 -(cost + min_cost))
        if upper < best:
            return
        smallest_ids = tuple(sorted([r[0]['ItemId'] for r in chosen] + sorted(r[0]['ItemId'] for r in remaining)[:needed]))
        if upper == best and smallest_ids >= best_ids:
            return
        row = records[index]
        search(index+1, chosen+[row], relevance+row[1], quality+row[2], cost+row[3])
        search(index+1, chosen, relevance, quality, cost)
    search(0, [], 0, 0, 0)
    return best_assignment


def rank_candidate_cities(items, request, resolved):
    """No count feature: normalized compatibility, means, and city-name tie-break."""
    by_city = defaultdict(list)
    for item in unique_inventory(items):
        if (item['IsActive'] and slot(item, DAY_START) is not None
                and any(date_available(item, request, offset) for offset in range(request.days))):
            by_city[item['CityName']].append(item)
    rankings, pools = [], {}
    for city, available in sorted(by_city.items()):
        compatible = [i for i in available if group_compatible(i, request)]
        candidates = [i for i in compatible if group_cost(i, request) <= request.budget]
        if not candidates:
            continue
        anchors = daily_anchors(candidates, request, resolved)
        if len(anchors) != request.days:
            continue
        components = [item_components(i, request, resolved) for i in candidates]
        fits = {key: mean(c[key] for c in components) for key in components[0]}
        # Both the fraction passing group constraints and the mean group suitability
        # are bounded 0..1. Neither raw inventory nor log inventory enters the score.
        fits['group'] = .5 * len(compatible) / len(available) + .5 * fits['group']
        contributions = {key: 100 * weight * fits[key] for key, weight in resolved['weights'].items()}
        # Complete-day feasibility is a constraint, never a preference bonus.
        if len(anchors) != request.days:
            continue
        rankings.append({'city': city, 'retrieval_score': sum(contributions.values()), 'components': fits,
                         'contributions': contributions,
                         'supports_all_days': len(anchors) == request.days,
                         'daily_anchor_ids': anchors,
                         'available_count': len(available), 'candidate_count': len(candidates),
                         'category_distribution': distribution(candidates, 'category'),
                         'environment_distribution': distribution(candidates, 'environment'),
                         'budget_distribution': distribution(candidates, 'budget'),
                         'group_compatible_fraction': len(compatible) / len(available)})
        pools[city] = candidates
    rankings.sort(key=lambda r: (-round(r['retrieval_score'], 10), r['city'].casefold(), r['city']))
    for index, row in enumerate(rankings, 1):
        row['rank'] = index
    return rankings, pools


def rank_candidate_activities(items, request, resolved):
    ranked = []
    for item in items:
        components = item_components(item, request, resolved)
        ranked.append({**item, 'group_cost': group_cost(item, request), 'components': components,
                       'mapping_debug': mapping_debug(item, resolved['wvs_profile']) if resolved['wvs_profile'] else None,
                       'retrieval_score': weighted_score(components, resolved['weights'])})
    return sorted(ranked, key=lambda i: (-round(i['retrieval_score'], 10), i['ItemId']))


def clock_string(minutes):
    return f'{minutes // 60:02d}:{minutes % 60:02d}'


def export_csv(stops):
    fields = ['day', 'date', 'start', 'end', 'ItemId', 'ItemName', 'CityName',
              'category', 'environment', 'Price', 'group_cost', 'DurationMinutes', 'retrieval_score']
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    for row in stops:
        writer.writerow({k: ("'" + v if isinstance(v, str) and v.startswith(('=', '+', '-', '@')) else v)
                         for k, v in row.items()})
    return output.getvalue().encode('utf-8-sig')
