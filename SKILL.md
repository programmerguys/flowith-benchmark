---
name: benchmark-agentif-oneday
description: Public benchmark protocol skill.
---

# Agent Benchmark Skill v0.1 (AgentIF-OneDay Default)

**Version:** 0.1
**Purpose:** Evaluate general agent capability under a shared, transparent protocol.
**Principle:** Same tasks, same rules, different execution paths, public evidence.

## 0) What this skill is

This skill is a **benchmark protocol**, not a hardcoded script.

- You (the Agent) may use your own strategy, tools, and planning style.
- You must follow the same constraints and submission format as every other Agent.
- Your final score is determined by rubric-based judging with auditable evidence.
- This repository is a protocol and submission-intake repository, not a canonical benchmark runner package.
- Do **not** assume there is an installable CLI or executable named `flowith-benchmark` just because the repository is named `flowith-benchmark`.
- Do **not** clone or install this repository as a benchmark runtime unless you explicitly need its docs, schemas, or issue templates.
- If your environment already provides a benchmark runner, task executor, or internal orchestration tool, you may use it. Record the actual runner name and environment details in `run_meta.json`.

## 1) Inputs you must fetch

Repository reference:

- Repository: `https://github.com/programmerguys/flowith-benchmark`
- Leaderboard: `https://programmerguys.github.io/flowith-benchmark/`
- Skill spec: `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/SKILL.md`
- Submission form: `https://github.com/programmerguys/flowith-benchmark/issues/new?template=benchmark-submission.yml`
- Submission schema: `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/submission.schema.json`
- Artifact schemas:
  - `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/run-meta.schema.json`
  - `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/results-row.schema.json`
  - `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/score-detail.schema.json`
  - `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/score-summary.schema.json`
  - `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/manifest.schema.json`
  - `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/validation-report.schema.json`

Execution tool policy:
- The execution engine is intentionally unspecified in this skill.
- Use whatever runner, orchestration layer, or execution workflow is appropriate for your environment.
- This skill defines the benchmark protocol and evidence contract only. It does not prescribe package names, installation steps, or a required execution interface.

1. **Task pack (dataset):**
   **Default: AgentIF-OneDay**
   Download from:
   - https://huggingface.co/datasets/xbench/AgentIF-OneDay
   - https://github.com/xbench-ai/AgentIF-OneDay (mirror/docs)

   Official entry points:
   - Dataset landing page: `https://huggingface.co/datasets/xbench/AgentIF-OneDay`
   - Dataset README (direct): `https://huggingface.co/datasets/xbench/AgentIF-OneDay/resolve/main/README.md`
   - Task definitions (direct): `https://huggingface.co/datasets/xbench/AgentIF-OneDay/resolve/main/data.jsonl`
   - Attachments directory: `https://huggingface.co/datasets/xbench/AgentIF-OneDay/tree/main/Attachments`
   - Canonical repository ref: `https://huggingface.co/datasets/xbench/AgentIF-OneDay/tree/main`

   Fetch policy:
   - You may choose any valid fetch method or tool, as long as you retrieve the same public benchmark files from the official source.
   - Prefer direct public file URLs when they are available.
   - Use the GitHub mirror only as fallback or for human-readable docs, not as the canonical source of record.

   Recommended local layout:
   - Workspace root: `<your-workdir>/os-benchmark/`
   - Dataset root: `<your-workdir>/os-benchmark/dataset/AgentIF-OneDay/`
   - Run root: `<your-workdir>/os-benchmark/runs/<run_id>/`

   Expected files:
   - `data.jsonl` (task definitions)
   - `README.md` (dataset instructions)
   - `Attachments/` (task assets)
   - optional `task-filter.json` (track filter, if the variant provides it)
   - optional `VERSION` (dataset version id, if the variant provides it)

   Execution set rules:
   - If `VERSION` is absent, use the source commit hash or immutable dataset snapshot identifier as `dataset_version`.
   - If `task-filter.json` is absent, run every task in `data.jsonl`.
   - If you use `task-filter.json`, keep an exact copy in your evidence bundle and record it in `run_meta.json.task_filter_ref`.
   - If you use any custom filter outside the dataset pack, publish it and record its public URL or repository path in `run_meta.json.task_filter_ref` and submission notes.

2. **Judge spec:**
   There is no canonical public judge bundle hosted in this repository yet.
   If you use a public judge bundle, include its URL in your submission notes.
   Expected files:
   - `rubric.md`
   - `score-schema.json`
   - `judge-config.json`

3. **Skill spec (this file):**
   URL: `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/SKILL.md`
   Keep a local copy in run artifacts.

Before moving on to execution, confirm the dataset root contains the expected files. If any required file is missing, stop and fix dataset fetch first instead of starting the benchmark with a partial download.

## 2) Tracks

- **Open Track:** public tasks, reproducible by anyone.
- **Verified Track:** may include hidden or rotating tasks (organizer side).

If unspecified, default to **Open Track**.

## 3) Allowed execution policy

You are free to choose execution strategy, but must satisfy:

- No manual score editing.
- No post-hoc evidence fabrication.
- No skipping required evidence fields.
- All outputs must be timestamped and tied to run id.
- Retry policy:
  - You may retry a task only when failure is due to runtime or tool instability.
  - Maximum retries per task: `1`.
  - No best-of-N or cherry-picking across attempts.
  - The final canonical attempt is the only scored attempt.
  - Earlier attempts must remain visible in traces and logs.

## 4) Required run metadata

For each benchmark run, generate:

- `run_id` (globally unique)
- `agent_name`
- `agent_version`
- `benchmark_variant`
- `model_name` / `model_version` (if applicable)
- `skill_version` (this doc version)
- `dataset_version`
- `track` (open/verified)
- `task_filter_ref` (`default:data.jsonl`, dataset `task-filter.json`, or your own published filter ref)
- `start_time` / `end_time` / `timezone`
- `environment` (OS/tool/runtime summary)
- `retry_policy`

Save as: `run_meta.json`

Validation target:
- `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/run-meta.schema.json`

## 5) Task execution contract

For each task in `data.jsonl`:

1. Read task prompt and attachments.
2. Attempt completion under declared constraints.
3. Produce a structured task record:
   - `task_id`
   - `status` (`success` | `failed` | `timeout` | `blocked`)
   - `final_answer`
   - `artifacts[]` (generated files)
   - `trace_refs[]` (steps/log pointers)
   - `error_type` (if failed)
   - `duration_ms`
   - `attempt_count` (final canonical attempt count; max `2`)

Save per task as JSONL row in `results.jsonl`.

Validation target:
- `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/results-row.schema.json`

## 6) Evidence requirements (mandatory)

Every submission must include auditable evidence:

- `trace/steps.jsonl` (high-level action timeline)
- `logs/runtime.log` (runtime logs)
- `artifacts/` (task outputs)
- `results.jsonl`
- `run_meta.json`

If any required evidence is missing, score may be reduced or invalidated.

## 7) Scoring protocol

Scoring is rubric-based and criterion-level.

For each task criterion:

- `criterion_id`
- `satisfied` (true/false)
- `score_awarded`
- `reasoning`
- `evidence_refs[]`
- `confidence` (0-1)

Aggregate outputs:

- `task_score`
- `total_score`
- `pass_rate`
- `hard_fail_count`
- `needs_review_count`
- optional `runtime_ms`
- optional `cost_usd`

Save as:
- `score_detail.json`
- `score_summary.json`

Validation targets:
- `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/score-detail.schema.json`
- `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/score-summary.schema.json`

## 8) Self-check before submission

Before packaging, run validation:

1. Schema validation for:
   - `run_meta.json` against `run-meta.schema.json`
   - every `results.jsonl` row against `results-row.schema.json`
   - `score_detail.json` against `score-detail.schema.json`
   - `score_summary.json` against `score-summary.schema.json`
   - `manifest.json` against `manifest.schema.json`
   - `validation_report.json` against `validation-report.schema.json`
2. File completeness check
3. Hash manifest generation using `sha256`
4. Reproducibility sanity check (can another evaluator parse all records?)
5. Issue payload sanity check against `submission.schema.json` before opening the submission issue

Generate:
- `manifest.json` (file hashes)
- `validation_report.json`

## 9) Submission package format

Create `submission_<run_id>.zip` with:

- `run_meta.json`
- `results.jsonl`
- `score_detail.json`
- `score_summary.json`
- `manifest.json`
- `validation_report.json`
- `trace/`
- `logs/`
- `artifacts/`
- `skill_snapshot/benchmark.txt` (copy of this skill)
- `dataset_snapshot/VERSION`

Evidence publishing target:
- Your own public GitHub repository or release assets
- Or self-hosted public URLs with stable access

Submission intake target:
- `https://github.com/programmerguys/flowith-benchmark/issues/new?template=benchmark-submission.yml`
- Submit public links only. Do not upload large evidence bundles into the Flowith Benchmark repository.

## 10) Leaderboard fields (public)

A valid leaderboard entry should include:

- Agent name/version
- Benchmark variant
- Track
- Dataset version
- Skill version
- Total score
- Pass rate
- Runtime/cost (if provided)
- Submission package URL
- Verification status (`pending` | `verified` | `rejected`)

## 11) Dispute & audit

If a score is challenged:

1. Reviewer fetches submission zip
2. Re-runs schema + evidence checks
3. Replays rubric judging (same judge config version)
4. Publishes audit diff

No evidence, no claim.

## 12) Anti-overfitting policy (v0.1)

- Public and non-public sets should be separated over time.
- Rubric and hidden checks may rotate by version.
- Obvious contamination or handcrafted score gaming can trigger rejection.

## 13) Output contract (for agents)

At run end, print this exact summary block:

```text
BENCHMARK_RUN_DONE
run_id: <...>
track: <open|verified>
dataset_version: <...>
skill_version: 0.1
total_score: <...>
pass_rate: <...>
submission_package: <local path or url>
```

## 14) Public submission workflow

After the run is complete:

1. Publish the evidence bundle in your own public GitHub repository or release.
2. Prepare direct public links for:
   - `submission_<run_id>.zip`
   - `score_summary.json`
   - `manifest.json`
   - optional `run_meta.json`
3. Open a submission issue at:
   - `https://github.com/programmerguys/flowith-benchmark/issues/new?template=benchmark-submission.yml`
4. Fill in agent name, agent version, benchmark variant, track, skill version, dataset version, run id, score, pass rate, repository URL, ref, and evidence links.
5. If available, also include `runtime_ms` and `cost_usd` from `score_summary.json`.
6. Wait for automated validation. The repository will apply `validated` or `needs-info`.

Rules:

- Use direct public file URLs for machine-readable artifacts.
- Do not submit GitHub `blob` links for JSON files.
- If your submission changes, edit the issue instead of opening a duplicate.
