import copy
import json
import unittest

from tools.check_roadmap import PBIS, validate_pbis


class RoadmapTests(unittest.TestCase):
    def setUp(self):
        self.pbis = json.loads(PBIS.read_text())

    def test_dependency_order_is_valid(self):
        order = validate_pbis(self.pbis)
        self.assertEqual(len(order), 28)
        for pbi in self.pbis:
            for dep in pbi['deps']:
                self.assertLess(order.index(dep), order.index(pbi['key']))

    def test_bad_references_and_cycles_are_rejected(self):
        mutations = [
            lambda p: p[0]['deps'].append('missing'),
            lambda p: p[0]['deps'].append(p[0]['key']),
            lambda p: p[0]['deps'].append(p[1]['key']),
            lambda p: p.append(copy.deepcopy(p[0])),
            lambda p: p[1].__setitem__('number', p[0]['number']),
            lambda p: p[0].__setitem__('epic', 9),
            lambda p: p[1]['deps'].append(p[1]['deps'][0]),
            lambda p: p[0].__setitem__('criteria', []),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(case=index):
                pbis = copy.deepcopy(self.pbis)
                mutate(pbis)
                with self.assertRaises(ValueError):
                    validate_pbis(pbis)

    def test_validation_preserves_plan(self):
        original = copy.deepcopy(self.pbis)
        validate_pbis(self.pbis)
        self.assertEqual(original, self.pbis)
