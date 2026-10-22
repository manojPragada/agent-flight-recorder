"""Bounded, provider-neutral NDJSON span ingestion."""
import json

def read_ndjson(stream, max_spans=10000, max_line_bytes=262144):
    spans=[]
    for line_number,line in enumerate(stream,1):
        if len(line.encode('utf-8'))>max_line_bytes:raise ValueError(f'Line {line_number} exceeds 256 KiB')
        if not line.strip():continue
        try:span=json.loads(line)
        except json.JSONDecodeError as exc:raise ValueError(f'Line {line_number} is not valid JSON: {exc.msg}') from None
        if not isinstance(span,dict):raise ValueError(f'Line {line_number} must be a JSON object')
        spans.append(span)
        if len(spans)>max_spans:raise ValueError(f'Trace exceeds {max_spans:,} spans')
    return {'version':1,'spans':spans}
