from datetime import date
from itertools import combinations
import unittest
from trip_planner.engine import TripRequest, daily_anchors, cheapest_feasible_anchors, item_components, weighted_score
from tests.fixtures import item


class AnchorTests(unittest.TestCase):
    def setUp(self):
        self.req = TripRequest('Test',date(2026,6,1),date(2026,6,2),budget=100)
        self.resolved = {'weights':{'quality':1},'wvs_profile':None}

    def test_relevance_beats_free_within_total_budget(self):
        items=[item(ItemId='free',Price=0,PopularityScore=.1),
               item(ItemId='better',Price=60,PopularityScore=.9),
               item(ItemId='best',Price=40,PopularityScore=1)]
        self.assertEqual(set(daily_anchors(items,self.req,self.resolved).values()),{'better','best'})
        items[1]['Price']=61
        self.assertEqual(set(daily_anchors(items,self.req,self.resolved).values()),{'free','best'})

    def test_quality_then_cost_then_id_ties(self):
        resolved={'weights':{'group':1},'wvs_profile':None}
        items=[item(ItemId='a',Price=0,PopularityScore=.1),item(ItemId='b',Price=20,PopularityScore=1),
               item(ItemId='c',Price=10,PopularityScore=1),item(ItemId='d',Price=10,PopularityScore=1)]
        self.assertEqual(set(daily_anchors(items,self.req,resolved).values()),{'c','d'})
        items[1]['Price']=10
        self.assertEqual(set(daily_anchors(list(reversed(items)),self.req,resolved).values()),{'b','c'})

    def test_exact_objective_matches_exhaustive_small_case(self):
        items=[item(ItemId=str(i),Price=(i*17)%65,PopularityScore=(i%4)/4,
                    available_until=date(2026,6,1) if i%3==0 else date(2026,12,31)) for i in range(8)]
        options=[]
        for subset in combinations(items,2):
            if len(cheapest_feasible_anchors(subset,self.req)) != 2: continue
            components=[item_components(i,self.req,self.resolved) for i in subset]
            key=(sum(round(weighted_score(c,self.resolved['weights'])*10**10) for c in components),
                 sum(round(c['quality']*10**10) for c in components),-sum(round(i['Price']*100) for i in subset))
            options.append((key,tuple(sorted(i['ItemId'] for i in subset))))
        expected=sorted(options,key=lambda x:(tuple(-v for v in x[0]),x[1]))[0][1]
        actual=daily_anchors(items,self.req,self.resolved)
        self.assertEqual(tuple(sorted(actual.values())),expected)
