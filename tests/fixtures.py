from datetime import date, timedelta


def item(**overrides):
    return dict(ItemId='a', ItemName='Museum', ItemDescription='A source activity.',
                CityName='Culture City', category='cultural', budget='low',
                IsActive=True, IsFamilySuitable=True, IsSeniorsSuitable=True,
                environment='Indoor', MinAge=0, MaxAge=90, Price=10,
                SuitableForAdults=.9, SuitableForChildren=.8, SuitableForInfants=.5,
                DurationMinutes=60, PopularityScore=.8, AvgRating=4, source_row=2,
                available_from=date(2026, 1, 1), available_until=date(2026, 12, 31),
                opens=540, closes=1320) | overrides


def evidence(label, value, country='Test', eligible='TRUE'):
    return {'Birth Country': country, 'ISO3': 'TST', **label,
            'WVS-Derived Signal (%)': str(value), 'Global Baseline (%)': '50',
            'Relative vs Global (pp)': str(value - 50), 'Eligible for Ranking': eligible,
            'Raw N': '500', 'Effective N': '400', 'Question Coverage (%)': '100', 'Country Rank': '1'}


def wvs_fixture():
    return {
        'CATEGORY_RESULTS': [evidence({'Category': 'Cultural'}, 90), evidence({'Category': 'Nature'}, 10),
                             evidence({'Category': 'Cultural'}, 10, 'Other'), evidence({'Category': 'Nature'}, 90, 'Other')],
        'HOBBY_RESULTS': [evidence({'Hobby': 'Museums & Exhibitions'}, 90), evidence({'Hobby': 'Guided Heritage Tours'}, 90),
                          evidence({'Hobby': 'Enjoying Nature'}, 10), evidence({'Hobby': 'National Parks'}, 10)],
        'ENVIRONMENT_RESULTS': [evidence({'Environment': 'Indoor'}, 90), evidence({'Environment': 'Outdoor'}, 10)]}


def inventory():
    result = []
    for city, category, environment in [('Culture City', 'cultural', 'Indoor'),
                                         ('Nature City', 'nature', 'Outdoor'),
                                         ('Adventure City', 'adventure', 'Both')]:
        for index in range(4):
            result.append(item(ItemId=f'{city}-{index}', ItemName=f'{city} activity {index}',
                               CityName=city, category=category, environment=environment))
    return result


def valid_output(package, city_index=0):
    city = package['candidate_cities'][city_index]
    alternatives = [c['city'] for c in package['candidate_cities'] if c['city'] != city['city']]
    return {'selected_destination': city['city'], 'destination_reasoning': ['TEST MOCK decision, not real LLM output.'],
            'alternative_destination': alternatives[0] if alternatives else None,
            'itinerary': [{'day': day + 1, 'date': (date.fromisoformat(package['trip_start']) + timedelta(days=day)).isoformat(), 'activities': [{'item_id': city['candidate_activities'][day]['ItemId'],
                                                         'start_time': '09:00', 'reason': 'TEST MOCK activity.'}]}
                          for day in range(package['trip_days'])]}


class MockProvider:
    """Test-only stub, intentionally able to choose a city other than rank one."""
    def __init__(self, city_index=1):
        self.city_index = city_index
        self.packages = []

    def generate(self, package):
        self.packages.append(package)
        output = valid_output(package, min(self.city_index, len(package['candidate_cities']) - 1))
        return {'output': output, 'provider': 'TEST MOCK', 'model': 'test-model', 'is_mock': True,
                'latency_seconds': 0, 'usage': None, 'prompt_version': 'test'}
