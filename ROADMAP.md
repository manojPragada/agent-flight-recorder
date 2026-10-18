# Roadmap

## Completed

- [x] Runnable standard-library CLI foundation
- [x] Behavioral tests and documented local examples
- [x] Input handling, explicit limitations and setup guide

## Next

- [x] Add validated parent spans and optional relative timestamps
- [ ] Add dependency-based critical-path analysis
- [ ] Build local interactive timeline and failure inspector
- [ ] Add optional SDK adapters and streaming trace ingestion

## Continuity

Initial foundation implemented and checked on 2026-10-17. Inspect current code and commits before continuing. Prioritize the first unchecked item and keep improvements small enough to verify. No visual dashboard has been implemented.


2026-10-18: Added parent validation, cycle detection, hierarchy metrics and interval-union timing. Ten tests pass. Critical-path analysis remains pending; next define dependencies explicitly rather than summing inclusive parent/child durations.
