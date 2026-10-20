"""Longest weighted dependency path over validated leaf spans."""
import math


def dependency_path(spans):
    parents = {span['parent_id'] for span in spans.values() if span.get('parent_id') is not None}
    leaves = {identifier: span for identifier, span in spans.items() if identifier not in parents}
    for identifier, span in spans.items():
        dependencies = span.get('depends_on', [])
        if not isinstance(dependencies, list) or not all(isinstance(value, str) for value in dependencies):
            raise ValueError('depends_on must be an array of leaf span IDs')
        if len(set(dependencies)) != len(dependencies):
            raise ValueError('depends_on must not contain duplicate IDs')
        if identifier in parents and dependencies:
            raise ValueError('Dependency edges are supported on leaf spans only')
        if any(dependency not in leaves for dependency in dependencies):
            raise ValueError('Every dependency must name an existing leaf span')
    if not any('depends_on' in span for span in leaves.values()):
        return None
    pending = set(leaves)
    best = {}
    while pending:
        ready = sorted(identifier for identifier in pending if all(dep in best for dep in leaves[identifier].get('depends_on', [])))
        if not ready:
            raise ValueError('Span dependency cycle detected')
        for identifier in ready:
            span = leaves[identifier]
            candidates = [best[dep] for dep in span.get('depends_on', [])]
            if candidates:
                duration, path = min(candidates, key=lambda item: (-item[0], item[1]))
            else:
                duration, path = 0, []
            duration += span['duration_ms']
            if not math.isfinite(duration):
                raise ValueError('Dependency path duration must be finite')
            for predecessor in span.get('depends_on', []):
                previous = leaves[predecessor]
                if 'start_ms' in span and previous['start_ms'] + previous['duration_ms'] > span['start_ms']:
                    raise ValueError('A dependent span starts before its predecessor ends')
            best[identifier] = duration, path + [identifier]
            pending.remove(identifier)
    if not best:
        return {'duration_ms': 0, 'span_ids': []}
    duration, path = min(best.values(), key=lambda item: (-item[0], item[1]))
    return {'duration_ms': duration, 'span_ids': path}

