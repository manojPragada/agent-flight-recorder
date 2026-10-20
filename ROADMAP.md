# Roadmap

## Completed

- [x] Runnable standard-library CLI foundation
- [x] Behavioral tests and documented local examples
- [x] Input handling, explicit limitations and setup guide

## Next

- [x] Add validated parent spans and optional relative timestamps
- [x] Add explicit leaf-dependency critical-path analysis
- [ ] Build local interactive timeline and failure inspector
- [ ] Add optional SDK adapters and streaming trace ingestion

## Continuity

2026-10-20: Added per-tool latency percentiles, failure rates and reported-token totals with explicit inclusive-span semantics; rejected aggregate duration overflow. Six regression tests added. Next: interactive timeline/failure inspector; this remains a CLI report, not a dashboard.

Initial foundation implemented and checked on 2026-10-17. Inspect current code and commits before continuing. Prioritize the first unchecked item and keep improvements small enough to verify. No visual dashboard has been implemented.


2026-10-18: Added parent validation, cycle detection, hierarchy metrics and interval-union timing. Ten tests pass. Critical-path analysis remains pending; next define dependencies explicitly rather than summing inclusive parent/child durations.


2026-10-19: Added duration-weighted critical paths over explicitly declared leaf dependencies, graph validation and timing-consistency checks. Inclusive parent durations and idle time are excluded. Next: local timeline viewer.

