# Flowith Benchmark

Public repository for the Flowith benchmark protocol, benchmark skills, and supporting specification.

This repository exists to keep the benchmark protocol versioned independently from application code and to avoid shipping it through the app's `resources/intelligence/skills/` auto-sync path.

## Scope

- Public benchmark skill definition
- Human-readable protocol reference
- Small usage examples for operators and agent builders

## Non-goals

- No Flowith app runtime code
- No bundled benchmark dataset or attachments
- No automatic in-app skill loading

## Files

- `SKILL.md`: agent-facing protocol skill
- `SPEC.md`: repository-level protocol notes
- `CHANGELOG.md`: protocol change history
- `examples/BENCHMARK_RUN_DONE.txt`: required summary block example

## Status

- Current protocol version: `0.1`
- Default public dataset variant: `AgentIF-OneDay`
- License: `MIT`
