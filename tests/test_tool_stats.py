import unittest
from app import summarize


def span(identifier, tool, duration, status='ok', **extra):
    return dict(id=identifier, tool=tool, duration_ms=duration, status=status, **extra)


class ToolStatisticsTests(unittest.TestCase):
    def test_empty_trace(self):
        self.assertEqual(summarize({'version': 1, 'spans': []})['tool_stats'], {})

    def test_calls_failures_tokens_and_nearest_rank(self):
        spans = [span(str(i), 'search', i, 'error' if i == 20 else 'ok', tokens=i)
                 for i in range(1, 21)]
        stats = summarize({'version': 1, 'spans': spans})['tool_stats']['search']
        self.assertEqual(stats, dict(calls=20, failures=1, error_rate=.05, tokens=210,
                                    summed_duration_ms=210, min_duration_ms=1,
                                    max_duration_ms=20, p50_duration_ms=10, p95_duration_ms=19))

    def test_single_zero_duration_call(self):
        stats = summarize({'version': 1, 'spans': [span('a', 'model', 0)]})['tool_stats']['model']
        self.assertEqual(stats['p95_duration_ms'], 0)
        self.assertEqual(stats['tokens'], 0)

    def test_tools_are_sorted_and_case_sensitive(self):
        spans = [span('a', 'z', 1), span('b', 'A', 2), span('c', 'a', 3)]
        self.assertEqual(list(summarize({'version': 1, 'spans': spans})['tool_stats']), ['A', 'a', 'z'])

    def test_inclusive_parent_duration_not_mislabelled_elapsed(self):
        spans = [span('root', 'agent', 10), span('child', 'agent', 4, parent_id='root')]
        summary = summarize({'version': 1, 'spans': spans})
        self.assertEqual(summary['tool_stats']['agent']['summed_duration_ms'], 14)
        self.assertIsNone(summary['timing'])

    def test_aggregate_overflow_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Aggregated trace duration'):
            summarize({'version': 1, 'spans': [span('a', 'x', 1e308), span('b', 'x', 1e308)]})
