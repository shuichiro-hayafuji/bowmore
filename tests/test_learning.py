import copy
import unittest

from bowmore.learning import read_catalog, select_for_stages, select_pattern, validate_catalog


class LearningTests(unittest.TestCase):
    def setUp(self):
        self.catalog = read_catalog()

    def test_initial_profiles_never_cross_stage_boundary(self):
        for profile, stages in self.catalog['initial_stage_assignments'].items():
            eligible = {p['id'] for p in self.catalog['patterns'] if p['stage'] in stages}
            draws = {select_pattern(self.catalog, profile, seed)['id'] for seed in range(1000)}
            self.assertEqual(draws, eligible)
            self.assertEqual(len(eligible), 50)

    def test_current_stages_override_initial_profile(self):
        for stage in ('short_response', 'give_reasons', 'express_opinion', 'handle_questions'):
            self.assertEqual(select_for_stages(self.catalog, [stage], 17)['stage'], stage)
        self.assertEqual(select_for_stages(self.catalog, ['express_opinion'], 42),
                         select_for_stages(self.catalog, ['express_opinion'], 42))

    def test_invalid_inputs_fail_clearly(self):
        for stages in ([], 'short_response', ['unknown'], [None], [True]):
            with self.subTest(stages=stages), self.assertRaises(ValueError):
                select_for_stages(self.catalog, stages)
        with self.assertRaises(ValueError):
            select_pattern(self.catalog, 'unknown')

    def test_selection_does_not_modify_catalog(self):
        original = copy.deepcopy(self.catalog)
        select_for_stages(self.catalog, ['give_reasons'], 1)
        self.assertEqual(self.catalog, original)

    def test_corrupted_catalog_is_rejected(self):
        def replace(field, value):
            return lambda c: c['patterns'][0].__setitem__(field, value)
        mutations = [
            lambda c: c.__setitem__('schema_version', 2),
            lambda c: c['patterns'].pop(),
            replace('id', self.catalog['patterns'][1]['id']),
            replace('title', self.catalog['patterns'][1]['title']),
            replace('mode', self.catalog['patterns'][1]['mode']),
            replace('mode', 'unknown'),
            replace('stage', 'unknown'),
            replace('stage', 'give_reasons'),
            replace('topic_id', 'EXTRA'),
            replace('duration_minutes', True),
            replace('steps', None),
            replace('goal', ' '),
            lambda c: c['patterns'][0]['steps'][0].__setitem__('minutes', True),
            lambda c: c['patterns'][0]['steps'][0].__setitem__('minutes', -1),
            lambda c: c['patterns'][0]['steps'][0].__setitem__('minutes', 3),
            lambda c: c['patterns'][0]['steps'][0].__setitem__('task', ' '),
            lambda c: c['patterns'][0]['steps'].reverse(),
            lambda c: c.__setitem__('initial_stage_assignments', {}),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(case=index):
                catalog = copy.deepcopy(self.catalog)
                mutate(catalog)
                with self.assertRaises(ValueError):
                    validate_catalog(catalog)


if __name__ == '__main__':
    unittest.main()
