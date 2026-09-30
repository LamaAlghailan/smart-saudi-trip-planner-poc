import unittest
from trip_planner.profiles import semantic_mapping, preference_components
from tests.fixtures import item


class MappingTests(unittest.TestCase):
    def mapping(self, category, name, description=''):
        return semantic_mapping(item(category=category, ItemName=name, ItemDescription=description))

    def test_mall(self):
        result = self.mapping('urban', 'Uneyzah Mall')
        self.assertEqual(result['category_priors'], ['shopping'])
        self.assertEqual(result['hobby_priors'], ['Shopping & Malls'])

    def test_hiking(self):
        self.assertEqual(self.mapping('adventure', 'Mountain Hiking Trail')['hobby_priors'], ['Hiking'])

    def test_water(self):
        for name in ('Snorkeling and Diving', 'Boat Trip', 'Island Exploration'):
            self.assertEqual(self.mapping('adventure', name)['hobby_priors'], ['Beach & Water Activities'])
        for category in ('beach', 'waterfront', 'marina'):
            self.assertEqual(self.mapping(category, 'Destination')['category_priors'], ['beach'])

    def test_museum(self):
        self.assertEqual(self.mapping('cultural', 'Regional Museum')['hobby_priors'], ['Museums & Exhibitions'])

    def test_generic_urban_and_unknown(self):
        for category in ('urban', 'unknown', 'leisure', 'family', 'adventure'):
            record = item(category=category, ItemName='Destination', ItemDescription='A local experience')
            self.assertEqual(semantic_mapping(record)['category_priors'], [])
            self.assertEqual(preference_components(record, {'categories': {}, 'hobbies': {}, 'environments': {}}),
                             {'category': .5, 'hobby': .5, 'environment': .5})

    def test_family_nature_and_scenery_not_hiking(self):
        for category, name in [('family', 'Family Picnic'), ('leisure', 'Mountain Drive'), ('adventure', 'Mountain Cable Car')]:
            result = self.mapping(category, name)
            self.assertEqual(result['category_priors'], ['nature'])
            self.assertNotIn('Hiking', result['hobby_priors'])
        result = self.mapping('adventure', 'Desert Safari', 'Camel rides and desert dunes')
        self.assertEqual(result['category_priors'], ['nature'])

    def test_food_and_entertainment_consistency(self):
        result = self.mapping('food & entertainment', 'Traditional Food Experience')
        self.assertEqual(result['category_priors'], ['food'])
        self.assertEqual(result['hobby_priors'], ['Luxury Dining'])
        result = self.mapping('food & entertainment', 'Dining and Theme Park')
        self.assertEqual(result['category_priors'], ['food', 'entertainment'])
        self.assertEqual(result['hobby_priors'], ['Luxury Dining', 'Festivals & Theme Parks'])
