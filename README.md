# Agent Flight Recorder

Validate a portable local agent trace and inspect call counts, failures, token totals and tool usage.

**Status:** runnable CLI plus standalone local timeline report. No hosted demo is available. Examples use synthetic offline data. Python 3.10+; standard library only. Validated with Python 3.12.

## Quick start

```bash
git clone https://github.com/manojPragada/agent-flight-recorder.git
cd agent-flight-recorder
python --version
python app.py examples/trace.json
```

Use `python3` if your system does not provide `python`. No package installation or API key is needed.

## Usage and behavior

Trace format: a JSON object with `version: 1` and `spans`. Each span needs unique string `id`, string `tool`, non-negative finite `duration_ms`, `status` (`ok` or `error`), and optional non-negative integer `tokens`.

Run `python app.py --help` for available options.

For append-friendly or piped traces, use provider-neutral NDJSON with one span object per line. Blank lines are ignored, each line is capped at 256 KiB, and a run is capped at 10,000 spans before the normal trace validation runs:

```bash
python app.py spans.ndjson --ndjson
cat spans.ndjson | python app.py -
```

This is finite stream ingestion, not a listening service or an SDK integration. Input is never sent elsewhere.

## Dependency-free instrumentation

`TraceRecorder` provides an optional context manager and decorator for code you control. It records tool names, nested parent IDs, relative timing, status and explicitly supplied token counts in the same provider-neutral format:

```python
from instrumentation import TraceRecorder

recorder = TraceRecorder()
with recorder.span("agent", span_id="run-1"):
    with recorder.span("local-search"):
        pass
trace = recorder.trace()
```

Arguments, return values and exception messages are deliberately not captured. The adapter does not monkey-patch SDKs, send telemetry, infer token counts or write files. Pass its returned trace to the normal validator before persistence.

### Optional OpenAI Responses adapter

`openai_adapter.record_response_call` wraps a synchronous `client.responses.create`-compatible callable. It records elapsed time and the completed response's documented `usage.input_tokens + usage.output_tokens`; prompts, arguments, output text, IDs and exception messages are never copied into the trace. The OpenAI package is optional and is not imported by this project:

```python
response = record_response_call(recorder, client.responses.create, model="...", input="...")
```

Streaming responses are intentionally unsupported because usage is not available until completion. Treat reported tokens as provider metadata, not a billing calculation.

`anthropic_adapter.record_message_call` provides the same synchronous, content-free boundary for `client.messages.create`. Its reported total includes documented input, cache-creation, cache-read and output token fields. The Anthropic package remains optional and is never imported by this project. This total is trace metadata, not a price calculation.

## Interactive local timeline

```bash
python app.py examples/trace.json --html trace-report.html
```

Open `trace-report.html` in a browser. The standalone report shows summary metrics, proportional timing bars and an interactive failures-only filter. It has no external fonts, scripts, analytics or network requests. Existing output files are not overwritten. Timeline positioning uses `start_ms` when supplied; traces without timestamps place spans at the same origin, so the report does not invent execution order.

## Hierarchy and timing

Spans may include `parent_id` pointing to another span, or null for a root. Unknown parents and cycles are rejected. `root_span_ids` and `max_depth` summarize the validated hierarchy (roots have depth 1).

Optional `start_ms` is a non-negative offset from a shared trace origin. Supply it for **all spans or none**. When supplied, child intervals must fit within their parent. The summary adds `timing.elapsed_ms` (last end minus first start) and `timing.busy_ms` (union of span intervals, excluding idle gaps). Parent and overlapping child durations are never counted twice in busy time. These metrics are not a dependency-based critical path. Without timestamps `timing` is null.

## Explicit dependency-path analysis

Leaf spans may declare `depends_on: ["predecessor-id"]`. Once any leaf declares this field, omitted leaf dependencies mean no predecessors. The summary adds `critical_path.duration_ms` and `critical_path.span_ids`: the longest sum of leaf durations over the declared acyclic graph, with deterministic lexical tie-breaking. Inclusive parent spans are excluded to avoid counting their work twice. Dependencies must name leaves; missing IDs, duplicate edges and cycles are rejected. When timestamps exist, each predecessor must end before its successor starts.

This is a duration-weighted dependency path, not measured wall-clock latency: idle gaps and scheduling delays are excluded. Failed spans are included. Without explicit dependencies the value is null; the tool does not infer causality from hierarchy or timing.

## Development and verification

```bash
python -m unittest discover -s tests -v
python -m compileall -q app.py dependencies.py ingest.py instrumentation.py tool_stats.py viewer.py tests
```

Tests exercise trace validation, hierarchy and overlapping/disjoint interval calculations without network access. There is no build step or configured linter; compilation is a syntax check, not linting.

## Configuration

Configuration is provided through CLI arguments. No environment variables, `.env` file, credentials or external services are required. `.env.example` documents this intentionally empty configuration contract.

## Structure

```text
app.py          CLI and trace validation
tool_stats.py   per-tool latency, failures and reported-token aggregation
dependencies.py leaf-span dependency analysis
ingest.py       bounded provider-neutral NDJSON reader
instrumentation.py dependency-free context manager/decorator adapter
openai_adapter.py opt-in synchronous Responses API timing/usage adapter
anthropic_adapter.py opt-in synchronous Anthropic Messages timing/usage adapter
viewer.py       standalone interactive HTML timeline renderer
examples/       synthetic example inputs
tests/          behavioral unit tests
ROADMAP.md      completed work and prioritized next steps
.env.example    configuration notes
```



## Architecture

The summary includes `tool_stats`, sorted by exact (case-sensitive) tool name: calls, failures, error rate (0–1), reported tokens, summed/min/max durations and nearest-rank p50/p95 durations. For N calls, percentile p selects sorted index `ceil(N*p)-1`; small samples are not reliable performance estimates. Metrics include every recorded span, including inclusive parent spans, so their sums are not elapsed time and may double-count nested work or tokens. There is no provider billing inference. Non-finite aggregate duration is rejected rather than emitting invalid JSON. `tool_stats.py` keeps aggregation separate from validation and dependency analysis.

The dependency-free CLI in app.py validates and summarizes traces; dependencies.py analyzes declared dependency paths and tool_stats.py aggregates tool metrics. Trace files are read only when requested. No provider SDK or network service is involved. A package and UI remain future work; see the roadmap.

## Limitations

`summed_duration_ms` sums span durations; overlapping calls mean this is not wall-clock runtime. Tokens are supplied by the trace author, not measured by this tool. No live agent integrations or visual dashboard yet. Dependency-path analysis requires explicit leaf-span dependencies. Do not place secrets in traces.

## Running and deployment

Run locally from the repository using the commands above. No hosted deployment has been configured. Do not expose a development process publicly. A web deployment guide will be added when a web application actually exists.

## Troubleshooting

- **Python not found:** install Python 3.10+ or try `python3`.
- **File not found:** run from the repository root or provide an absolute input path.
- **Invalid input:** inspect the error printed to standard error and compare with the examples.
- **Permission denied:** choose a folder you own; avoid running as administrator.

## Contributing and credits

Open an issue describing the observed behavior, expected result and a minimal synthetic example. Keep changes focused, include behavioral tests, run the checks above, and update this README when commands or capabilities change. Do not submit credentials or private input files.

Implementation and synthetic examples are original to this repository. There are no third-party runtime dependencies or media assets. A redistribution license has not yet been selected; public visibility alone does not grant an open-source license.



