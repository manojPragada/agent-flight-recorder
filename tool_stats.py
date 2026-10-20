"""Deterministic per-tool metrics over validated spans (not wall-clock time)."""
import math


def tool_statistics(spans):
    groups = {}
    for span in spans:
        groups.setdefault(span['tool'], []).append(span)
    result = {}
    for tool, items in sorted(groups.items()):
        durations = sorted(item['duration_ms'] for item in items)
        total = sum(durations)
        if not math.isfinite(total):
            raise ValueError('Aggregated tool duration must be finite')
        failures = sum(item['status'] == 'error' for item in items)
        result[tool] = {
            'calls': len(items), 'failures': failures,
            'error_rate': failures / len(items),
            'tokens': sum(item.get('tokens', 0) for item in items),
            'summed_duration_ms': total,
            'min_duration_ms': durations[0], 'max_duration_ms': durations[-1],
            'p50_duration_ms': durations[math.ceil(len(items) * .50) - 1],
            'p95_duration_ms': durations[math.ceil(len(items) * .95) - 1],
        }
    return result
