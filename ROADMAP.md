# Roadmap

## Completed

- [x] Runnable standard-library CLI foundation
- [x] Behavioral tests and documented local examples
- [x] Input handling, explicit limitations and setup guide

## Next

- [x] Add validated parent spans and optional relative timestamps
- [x] Add explicit leaf-dependency critical-path analysis
- [x] Build local interactive timeline and failure inspector
- [x] Add bounded provider-neutral NDJSON stream ingestion
- [x] Add dependency-free instrumentation adapter
- [x] Add an opt-in synchronous OpenAI Responses adapter
- [ ] Add another provider adapter only when its stable usage contract can be tested

## Continuity

2026-10-25: Added an optional duck-typed OpenAI Responses adapter that records timing and documented input/output token totals without importing the SDK or retaining request/response content. Streaming is unsupported. Next: another isolated provider adapter only when its usage contract can be tested.

2026-10-24: Added a dependency-free context-manager/decorator adapter that records nested provider-neutral spans, elapsed timing, declared tokens and failures without capturing arguments, results or exception text. Next: isolated opt-in vendor adapters built on this contract.

2026-10-22: Added append-friendly NDJSON file/stdin ingestion with line numbers, 256 KiB event bounds and a 10,000-span cap before normal validation. Next: isolated optional SDK adapters that emit this provider-neutral format.

2026-10-21: Added a standalone, responsive offline timeline report with trace metrics, proportional timing bars and a keyboard-accessible failure filter. Output is created exclusively and contains no external assets or requests. Next: optional SDK adapters and streaming ingestion.

2026-10-20: Added per-tool latency percentiles, failure rates and reported-token totals with explicit inclusive-span semantics; rejected aggregate duration overflow. Six regression tests added. Next: interactive timeline/failure inspector; this remains a CLI report, not a dashboard.

Initial foundation implemented and checked on 2026-10-17. Inspect current code and commits before continuing. Prioritize the first unchecked item and keep improvements small enough to verify. No visual dashboard has been implemented.


2026-10-18: Added parent validation, cycle detection, hierarchy metrics and interval-union timing. Ten tests pass. Critical-path analysis remains pending; next define dependencies explicitly rather than summing inclusive parent/child durations.


2026-10-19: Added duration-weighted critical paths over explicitly declared leaf dependencies, graph validation and timing-consistency checks. Inclusive parent durations and idle time are excluded. Next: local timeline viewer.

