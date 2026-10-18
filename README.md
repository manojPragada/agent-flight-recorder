# Agent Flight Recorder

Validate a portable local agent trace and inspect call counts, failures, token totals and tool usage.

**Status:** runnable CLI foundation. No hosted demo or dashboard is available yet. Examples use synthetic offline data. Python 3.10+; standard library only. Validated with Python 3.12.

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

## Hierarchy and timing

Spans may include `parent_id` pointing to another span, or null for a root. Unknown parents and cycles are rejected. `root_span_ids` and `max_depth` summarize the validated hierarchy (roots have depth 1).

Optional `start_ms` is a non-negative offset from a shared trace origin. Supply it for **all spans or none**. When supplied, child intervals must fit within their parent. The summary adds `timing.elapsed_ms` (last end minus first start) and `timing.busy_ms` (union of span intervals, excluding idle gaps). Parent and overlapping child durations are never counted twice in busy time. These metrics are not a dependency-based critical path. Without timestamps `timing` is null.

## Development and verification

```bash
python -m unittest discover -s tests -v
python -m compileall -q app.py tests
```

Tests exercise trace validation, hierarchy and overlapping/disjoint interval calculations without network access. There is no build step or configured linter; compilation is a syntax check, not linting.

## Configuration

Configuration is provided through CLI arguments. No environment variables, `.env` file, credentials or external services are required. `.env.example` documents this intentionally empty configuration contract.

## Structure

```text
app.py          CLI and core domain functions
examples/       synthetic example inputs
tests/          behavioral unit tests
ROADMAP.md      completed work and prioritized next steps
.env.example    configuration notes
```



## Architecture

A single dependency-free module exposes importable core functions and a CLI entry point. Filesystem and network access occur only when the corresponding commands run. This small foundation will be split into a package, integrations and UI as those features arrive; see the roadmap.

## Limitations

`summed_duration_ms` sums span durations; overlapping calls mean this is not wall-clock runtime. Tokens are supplied by the trace author, not measured by this tool. No live agent integrations or visual dashboard yet. Critical-path analysis is not implemented. Do not place secrets in traces.

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

