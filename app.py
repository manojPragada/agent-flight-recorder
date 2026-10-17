"""Validate and summarize local agent traces. No provider integration required."""
import argparse
import json
import math
import sys
from collections import Counter

def summarize(trace):
    if not isinstance(trace,dict) or trace.get('version') != 1 or not isinstance(trace.get('spans'),list):
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
    return {'span_count':len(ids),'failures':failures,'summed_duration_ms':duration,'tokens':tokens,'tools':dict(sorted(tools.items()))}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('trace');a=p.parse_args()
    try:
        with open(a.trace,encoding='utf-8') as f:trace=json.load(f)
        print(json.dumps(summarize(trace),indent=2));return 0
    except (OSError,ValueError) as exc:print(str(exc),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
