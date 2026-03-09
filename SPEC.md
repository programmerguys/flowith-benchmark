# Specification

## Purpose

Define a public, versioned benchmark protocol for running and evaluating agents in the Flowith benchmark ecosystem.

## Repository Boundary

This repository contains protocol artifacts only.

- `SKILL.md` is the agent-facing entry file.
- Supporting docs explain the protocol for humans.
- Runtime implementations, product UI, and internal Flowith integrations live elsewhere.

## Design Rules

- Keep the benchmark contract explicit and auditable.
- Prefer prompt-level protocol guidance over app-specific hardcoded behavior.
- Preserve a stable public reference independent from product release cadence.
- Keep dataset-specific defaults explicit when they matter for reproducibility.
- Allow multiple public benchmark variants under one repository without coupling them to app runtime code.

## Expected Evolution

- `SKILL.md` may evolve with protocol versions.
- New datasets should be added as separate protocol variants instead of overloading one file.
- Submission schema, judge config, and examples can be added later without changing repository purpose.

## Release Policy

- Tag protocol releases semantically.
- Keep changelog entries concise and user-facing.
- Do not couple protocol publication to Flowith app packaging.
