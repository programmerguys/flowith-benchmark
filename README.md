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

## Links

- Repository: [programmerguys/flowith-benchmark](https://github.com/programmerguys/flowith-benchmark)
- Skill: [SKILL.md](https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/SKILL.md)
- Submission form: [Benchmark Submission Issue](https://github.com/programmerguys/flowith-benchmark/issues/new?template=benchmark-submission.yml)
- Submission schema: [submission.schema.json](https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/submission.schema.json)
- Validation workflow: [validate-submission.yml](https://github.com/programmerguys/flowith-benchmark/blob/main/.github/workflows/validate-submission.yml)

## Submit Results

Use this repository as the public intake point for benchmark submissions.

1. Run the benchmark with your own agent.
2. Publish your evidence in your own public GitHub repository or release.
3. Open a `Benchmark Submission` issue in this repository.
4. Fill in the required metadata and direct public artifact links.
5. The repository will automatically validate the submission and apply `validated` or `needs-info`.

Submission rules:

- Submit links only. Do not upload large evidence bundles into this repository.
- Prefer direct URLs for `submission_<run_id>.zip`, `score_summary.json`, `manifest.json`, and `run_meta.json`.
- Do not use GitHub `blob` links for machine-readable files. Use raw file URLs or release asset URLs instead.

Validation labels:

- `submission`: issue uses the benchmark submission intake flow
- `validated`: automated validation passed
- `needs-info`: links or metadata need to be fixed before leaderboard collection

Required submission URLs:

- Public repository URL
- Direct public URL to `submission_<run_id>.zip`
- Direct public URL to `score_summary.json`
- Direct public URL to `manifest.json`
- Optional direct public URL to `run_meta.json`

## Status

- Current protocol version: `0.1`
- Default public dataset variant: `AgentIF-OneDay`
- License: `MIT`
