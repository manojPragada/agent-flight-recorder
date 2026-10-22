"""Validate and summarize local agent traces. No provider integration required."""
import argparse
import json
import math
import sys
from collections import Counter
from dependencies import dependency_path
from tool_stats import tool_statistics

def summarize(trace):
    if not isinstance(trace,dict) or type(trace.get('version')) is not int or trace.get('version') != 1 or not isinstance(trace.get('spans'),list):
        raise ValueError('Expected version 1 and a spans array')
    ids=set();tools=Counter();duration=0;tokens=0;failures=0
    for span in trace['spans']:
        if not isinstance(span,dict):raise ValueError('Each span must be an object')
        identifier=span.get('id');tool=span.get('tool')
        if not isinstance(identifier,str) or not identifier or identifier in ids:raise ValueError('Span IDs must be unique non-empty strings')
        if not isinstance(tool,str) or not tool:raise ValueError('tool must be a non-empty string')
        ids.add(identifier)
        ms=span.get('duration_ms');count=span.get('tokens',0)
        if type(ms) not in (int,float) or not math.isfinite(ms) or ms<0:raise ValueError('duration_ms must be finite and non-negative')
        if type(count) is not int or count<0:raise ValueError('tokens must be a non-negative integer')
        if span.get('status') not in ('ok','error'):raise ValueError('status must be ok or error')
        tools[tool]+=1;duration+=ms;tokens+=count;failures+=span['status']=='error'
    spans = {span['id']: span for span in trace['spans']}
    roots = []
    max_depth = 0
    for identifier, span in spans.items():
        parent = span.get('parent_id')
        if parent is None:
            roots.append(identifier)
        elif not isinstance(parent, str) or parent not in spans:
            raise ValueError('parent_id must name an existing span or be null')
    for identifier in spans:
        seen = set()
        current = identifier
        while current is not None:
            if current in seen:
                raise ValueError('Span parent cycle detected')
            seen.add(current)
            current = spans[current].get('parent_id')
        max_depth = max(max_depth, len(seen))
    timed = [span for span in spans.values() if 'start_ms' in span]
    timing = None
    if timed:
        if len(timed) != len(spans):
            raise ValueError('Provide start_ms for every span or omit it from every span')
        intervals = []
        for span in timed:
            start = span['start_ms']
            if type(start) not in (int, float) or not math.isfinite(start) or start < 0:
                raise ValueError('start_ms must be finite and non-negative')
            end = start + span['duration_ms']
            if not math.isfinite(end):
                raise ValueError('Span end time must be finite')
            intervals.append((start, end))
        for span in timed:
            start = span['start_ms']
            end = start + span['duration_ms']
            if span.get('parent_id') is not None:
                parent = spans[span['parent_id']]
                if not (parent['start_ms'] <= start and end <= parent['start_ms'] + parent['duration_ms']):
                    raise ValueError('Child span must fall within its parent interval')
        intervals.sort()
        busy = 0
        left, right = intervals[0]
        for start, end in intervals[1:]:
            if start <= right:
                right = max(right, end)
            else:
                busy += right - left
                left, right = start, end
        busy += right - left
        timing = {'elapsed_ms': max(end for _, end in intervals) - intervals[0][0], 'busy_ms': busy}
    if not math.isfinite(duration):
        raise ValueError('Aggregated trace duration must be finite')
    return {'span_count':len(ids),'failures':failures,'summed_duration_ms':duration,'tokens':tokens,'tools':dict(sorted(tools.items())),
            'tool_stats': tool_statistics(trace['spans']),
            'root_span_ids': sorted(roots), 'max_depth': max_depth, 'timing': timing, 'critical_path': dependency_path(spans)}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('trace',help='JSON trace path, NDJSON path, or - for NDJSON stdin');p.add_argument('--ndjson',action='store_true',help='Read one span object per line; implied by trace -');p.add_argument('--html',metavar='OUTPUT',help='Write a standalone local timeline report');a=p.parse_args()
    try:
        if a.ndjson or a.trace=='-':
            from ingest import read_ndjson
            if a.trace=='-':trace=read_ndjson(sys.stdin)
            else:
                with open(a.trace,encoding='utf-8') as f:trace=read_ndjson(f)
        else:
            with open(a.trace,encoding='utf-8') as f:trace=json.load(f)
        summary=summarize(trace)
        if a.html:
            from viewer import render_viewer
            with open(a.html,'x',encoding='utf-8') as output:output.write(render_viewer(trace,summary))
        else:print(json.dumps(summary,indent=2))
        return 0
    except (OSError,ValueError) as exc:print(str(exc),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())



