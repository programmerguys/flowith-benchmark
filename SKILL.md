---
name: benchmark-agentif-oneday
description: Public benchmark protocol skill for Flowith OS Agent evaluation.
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

## 1) Inputs you must fetch

Repository reference:

- Repository: `https://github.com/programmerguys/flowith-benchmark`
- Leaderboard: `https://programmerguys.github.io/flowith-benchmark/`
- Skill spec: `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/SKILL.md`
- Submission form: `https://github.com/programmerguys/flowith-benchmark/issues/new?template=benchmark-submission.yml`
- Submission schema: `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/submission.schema.json`

1. **Task pack (dataset):**
   **Default: AgentIF-OneDay**
   Download from:
   - https://huggingface.co/datasets/xbench/AgentIF-OneDay
   - https://github.com/xbench-ai/AgentIF-OneDay (mirror/docs)

   Expected files:
   - `data.jsonl` (task definitions)
   - `task-filter.json` (optional track filter)
   - `attachments/` (task assets)
   - `VERSION` (dataset version id)

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

You may retry tasks when failure is due to runtime/tool instability, but retries must be logged.

## 4) Required run metadata

For each benchmark run, generate:

- `run_id` (globally unique)
- `agent_name`
- `agent_version`
- `model_name` / `model_version` (if applicable)
- `skill_version` (this doc version)
- `dataset_version`
- `track` (open/verified)
- `start_time` / `end_time` / `timezone`
- `environment` (OS/tool/runtime summary)

Save as: `run_meta.json`

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

Save per task as JSONL row in `results.jsonl`.

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

Save as:
- `score_detail.json`
- `score_summary.json`

## 8) Self-check before submission

Before packaging, run validation:

1. Schema validation against `https://raw.githubusercontent.com/programmerguys/flowith-benchmark/main/schemas/submission.schema.json`
2. File completeness check
3. Hash manifest generation
4. Reproducibility sanity check (can another evaluator parse all records?)

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
4. Fill in agent name, agent version, protocol version, run id, score, pass rate, repository URL, ref, and evidence links.
5. Wait for automated validation. The repository will apply `validated` or `needs-info`.

Rules:

- Use direct public file URLs for machine-readable artifacts.
- Do not submit GitHub `blob` links for JSON files.
- If your submission changes, edit the issue instead of opening a duplicate.
