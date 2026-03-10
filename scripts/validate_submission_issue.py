#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


FIELD_MAP = {
    "Agent Name": "agent_name",
    "Agent Version": "agent_version",
    "Benchmark Variant": "benchmark_variant",
    "Track": "track",
    "Skill Version": "skill_version",
    "Dataset Version": "dataset_version",
    "Run ID": "run_id",
    "Total Score": "total_score",
    "Pass Rate": "pass_rate",
    "Runtime (ms)": "runtime_ms",
    "Cost (USD)": "cost_usd",
    "Submission Repository URL": "submission_repo_url",
    "Submission Ref": "submission_ref",
    "Submission Package URL": "submission_package_url",
    "Score Summary URL": "score_summary_url",
    "Manifest URL": "manifest_url",
    "Run Metadata URL": "run_meta_url",
    "Additional Notes": "notes",
}

REQUIRED_FIELDS = [
    "agent_name",
    "agent_version",
    "benchmark_variant",
    "track",
    "skill_version",
    "dataset_version",
    "run_id",
    "total_score",
    "pass_rate",
    "submission_repo_url",
    "submission_ref",
    "submission_package_url",
    "score_summary_url",
    "manifest_url",
]

MACHINE_READABLE_URL_FIELDS = {
    "submission_package_url",
    "score_summary_url",
    "manifest_url",
    "run_meta_url",
}

TRACK_VALUES = {"open", "verified"}
SHA256_RE = re.compile(r"^[A-Fa-f0-9]{64}$")
HEADINGS_RE = re.compile(r"^###\s+(.*?)\s*$")
NO_RESPONSE_RE = re.compile(r"^_No response_\s*$", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def clean_value(value: str) -> str:
    cleaned = value.strip()
    if NO_RESPONSE_RE.match(cleaned):
        return ""
    return cleaned


def parse_issue_form(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_heading: str | None = None
    buffer: list[str] = []

    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        match = HEADINGS_RE.match(line.strip())
        if match:
            if current_heading is not None:
                sections[current_heading] = clean_value("\n".join(buffer))
            current_heading = match.group(1).strip()
            buffer = []
            continue
        if current_heading is not None:
            buffer.append(line)

    if current_heading is not None:
        sections[current_heading] = clean_value("\n".join(buffer))

    normalized: dict[str, str] = {}
    for heading, key in FIELD_MAP.items():
        normalized[key] = sections.get(heading, "")
    return normalized


def parse_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def parse_int(value: Any) -> int | None:
    parsed = parse_float(value)
    if parsed is None or not parsed.is_integer():
        return None
    return int(parsed)


def normalize_track(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    if not normalized:
        return None
    return normalized


def normalize_pass_rate(value: Any) -> float | None:
    if isinstance(value, str):
        normalized = value.strip()
        if normalized.endswith("%"):
            return parse_float(normalized[:-1].strip())
        parsed = parse_float(normalized)
    else:
        parsed = parse_float(value)

    if parsed is None:
        return None
    if 0 <= parsed <= 1:
        return parsed * 100
    return parsed


def validate_url(url: str, field_name: str) -> tuple[list[str], list[str], dict[str, Any] | None]:
    errors: list[str] = []
    warnings: list[str] = []

    if not url:
        return errors, warnings, None

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        errors.append(f"`{field_name}` must be a valid public http/https URL.")
        return errors, warnings, None

    if field_name in MACHINE_READABLE_URL_FIELDS and "github.com" in parsed.netloc and "/blob/" in parsed.path:
        errors.append(
            f"`{field_name}` must be a direct file URL, not a GitHub blob page. Use raw or release asset links."
        )
        return errors, warnings, None

    if field_name == "submission_package_url" and not parsed.path.lower().endswith(".zip"):
        warnings.append("`submission_package_url` does not end with `.zip`. Ensure it points to the submission package directly.")

    if field_name in {"score_summary_url", "manifest_url", "run_meta_url"} and parsed.path:
        if not parsed.path.lower().endswith(".json"):
            warnings.append(f"`{field_name}` does not end with `.json`. Ensure it points to a machine-readable JSON file.")

    reachability = fetch_url(url)
    if not reachability["ok"]:
        errors.append(f"`{field_name}` is not publicly reachable: {reachability['error']}")

    return errors, warnings, reachability


def fetch_url(url: str) -> dict[str, Any]:
    headers = {"User-Agent": "flowith-benchmark-validator"}
    methods = ["HEAD", "GET"]

    for method in methods:
        request = urllib.request.Request(url, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return {
                    "ok": True,
                    "method": method,
                    "status": response.status,
                    "final_url": response.geturl(),
                }
        except urllib.error.HTTPError as error:
            if method == "HEAD" and error.code in {403, 405}:
                continue
            return {
                "ok": False,
                "method": method,
                "status": error.code,
                "error": f"HTTP {error.code}",
            }
        except urllib.error.URLError as error:
            return {
                "ok": False,
                "method": method,
                "error": str(error.reason),
            }
        except Exception as error:  # noqa: BLE001
            return {
                "ok": False,
                "method": method,
                "error": str(error),
            }

    return {
        "ok": False,
        "method": "HEAD",
        "error": "unreachable",
    }


def fetch_json(url: str) -> tuple[list[str], dict[str, Any] | None]:
    headers = {
        "User-Agent": "flowith-benchmark-validator",
        "Accept": "application/json,text/plain,*/*",
    }
    request = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            raw_body = response.read()
            body = raw_body.decode(charset, errors="replace")
            return [], {
                "ok": True,
                "status": response.status,
                "final_url": response.geturl(),
                "body": body,
            }
    except urllib.error.HTTPError as error:
        return [f"failed to fetch JSON: HTTP {error.code}"], None
    except urllib.error.URLError as error:
        return [f"failed to fetch JSON: {error.reason}"], None
    except Exception as error:  # noqa: BLE001
        return [f"failed to fetch JSON: {error}"], None


def require_non_empty_string(data: dict[str, Any], key: str, source: str, errors: list[str]) -> str | None:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"`{source}` must include a non-empty string `{key}`.")
        return None
    return value.strip()


def require_number(
    data: dict[str, Any],
    key: str,
    source: str,
    errors: list[str],
    *,
    minimum: float | None = None,
    maximum: float | None = None,
    integer: bool = False,
) -> float | int | None:
    parsed = parse_int(data.get(key)) if integer else parse_float(data.get(key))
    if parsed is None:
        expected = "integer" if integer else "number"
        errors.append(f"`{source}` must include a valid {expected} `{key}`.")
        return None
    if minimum is not None and parsed < minimum:
        errors.append(f"`{source}` field `{key}` must be greater than or equal to {minimum}.")
    if maximum is not None and parsed > maximum:
        errors.append(f"`{source}` field `{key}` must be less than or equal to {maximum}.")
    return parsed


def validate_score_summary_document(data: Any) -> tuple[list[str], list[str], dict[str, Any] | None]:
    source = "score_summary.json"
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        return [f"`{source}` must be a JSON object."], warnings, None

    normalized: dict[str, Any] = {
        "run_id": require_non_empty_string(data, "run_id", source, errors),
        "agent_name": require_non_empty_string(data, "agent_name", source, errors),
        "agent_version": require_non_empty_string(data, "agent_version", source, errors),
        "benchmark_variant": require_non_empty_string(data, "benchmark_variant", source, errors),
        "skill_version": require_non_empty_string(data, "skill_version", source, errors),
        "dataset_version": require_non_empty_string(data, "dataset_version", source, errors),
    }

    track = normalize_track(data.get("track"))
    if track not in TRACK_VALUES:
        errors.append(f"`{source}` field `track` must be one of: {', '.join(sorted(TRACK_VALUES))}.")
    normalized["track"] = track

    normalized["total_score"] = require_number(data, "total_score", source, errors, minimum=0)
    normalized["pass_rate"] = require_number(data, "pass_rate", source, errors, minimum=0, maximum=100)
    normalized["task_count"] = require_number(data, "task_count", source, errors, minimum=0, integer=True)
    normalized["hard_fail_count"] = require_number(data, "hard_fail_count", source, errors, minimum=0, integer=True)
    normalized["needs_review_count"] = require_number(data, "needs_review_count", source, errors, minimum=0, integer=True)

    runtime_value = data.get("runtime_ms")
    if runtime_value is not None:
        normalized["runtime_ms"] = require_number(data, "runtime_ms", source, errors, minimum=0, integer=True)
    else:
        normalized["runtime_ms"] = None

    cost_value = data.get("cost_usd")
    if cost_value is not None:
        normalized["cost_usd"] = require_number(data, "cost_usd", source, errors, minimum=0)
    else:
        normalized["cost_usd"] = None

    return errors, warnings, normalized


def validate_run_meta_document(data: Any) -> tuple[list[str], list[str], dict[str, Any] | None]:
    source = "run_meta.json"
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        return [f"`{source}` must be a JSON object."], warnings, None

    normalized: dict[str, Any] = {
        "run_id": require_non_empty_string(data, "run_id", source, errors),
        "agent_name": require_non_empty_string(data, "agent_name", source, errors),
        "agent_version": require_non_empty_string(data, "agent_version", source, errors),
        "benchmark_variant": require_non_empty_string(data, "benchmark_variant", source, errors),
        "skill_version": require_non_empty_string(data, "skill_version", source, errors),
        "dataset_version": require_non_empty_string(data, "dataset_version", source, errors),
        "task_filter_ref": require_non_empty_string(data, "task_filter_ref", source, errors),
        "start_time": require_non_empty_string(data, "start_time", source, errors),
        "end_time": require_non_empty_string(data, "end_time", source, errors),
        "timezone": require_non_empty_string(data, "timezone", source, errors),
    }

    track = normalize_track(data.get("track"))
    if track not in TRACK_VALUES:
        errors.append(f"`{source}` field `track` must be one of: {', '.join(sorted(TRACK_VALUES))}.")
    normalized["track"] = track

    environment = data.get("environment")
    if isinstance(environment, str):
        if environment.strip():
            normalized["environment"] = environment.strip()
        else:
            errors.append(f"`{source}` field `environment` must not be empty.")
            normalized["environment"] = None
    elif isinstance(environment, dict):
        os_name = require_non_empty_string(environment, "os", f"{source}.environment", errors)
        runtime_name = require_non_empty_string(environment, "runtime", f"{source}.environment", errors)
        normalized["environment"] = {
            "os": os_name,
            "runtime": runtime_name,
            "tools": environment.get("tools"),
            "notes": environment.get("notes"),
        }
    else:
        errors.append(f"`{source}` field `environment` must be a string or object.")
        normalized["environment"] = None

    retry_policy = data.get("retry_policy")
    if not isinstance(retry_policy, dict):
        errors.append(f"`{source}` field `retry_policy` must be an object.")
        normalized["retry_policy"] = None
    else:
        max_retries = require_number(
            retry_policy,
            "max_retries_per_task",
            f"{source}.retry_policy",
            errors,
            minimum=0,
            maximum=1,
            integer=True,
        )
        score_mode = retry_policy.get("score_mode")
        if score_mode != "final_attempt_only":
            errors.append(f"`{source}` field `retry_policy.score_mode` must be `final_attempt_only`.")
        normalized["retry_policy"] = {
            "max_retries_per_task": max_retries,
            "score_mode": score_mode,
            "notes": retry_policy.get("notes"),
        }

    return errors, warnings, normalized


def validate_manifest_document(data: Any) -> tuple[list[str], list[str], dict[str, Any] | None]:
    source = "manifest.json"
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        return [f"`{source}` must be a JSON object."], warnings, None

    generated_at = require_non_empty_string(data, "generated_at", source, errors)
    hash_algorithm = data.get("hash_algorithm")
    if hash_algorithm != "sha256":
        errors.append(f"`{source}` field `hash_algorithm` must be `sha256`.")

    files = data.get("files")
    if not isinstance(files, list) or not files:
        errors.append(f"`{source}` field `files` must be a non-empty array.")
        return errors, warnings, None

    normalized_files: list[dict[str, Any]] = []
    file_paths: list[str] = []

    for index, entry in enumerate(files):
        if not isinstance(entry, dict):
            errors.append(f"`{source}` entry #{index + 1} must be an object.")
            continue
        path = entry.get("path")
        sha256 = entry.get("sha256")
        size_bytes = entry.get("size_bytes")

        if not isinstance(path, str) or not path.strip():
            errors.append(f"`{source}` entry #{index + 1} must include a non-empty string `path`.")
            continue
        if not isinstance(sha256, str) or not SHA256_RE.match(sha256):
            errors.append(f"`{source}` entry `{path}` must include a 64-character hex `sha256`.")
        if not isinstance(size_bytes, int) or size_bytes < 0:
            errors.append(f"`{source}` entry `{path}` must include a non-negative integer `size_bytes`.")

        normalized_files.append(
            {
                "path": path.strip(),
                "sha256": sha256,
                "size_bytes": size_bytes,
            }
        )
        file_paths.append(path.strip())

    required_suffixes = [
        "run_meta.json",
        "results.jsonl",
        "score_detail.json",
        "score_summary.json",
        "validation_report.json",
    ]
    for suffix in required_suffixes:
        if not any(path.endswith(suffix) for path in file_paths):
            warnings.append(f"`{source}` does not list a file ending with `{suffix}`.")

    normalized = {
        "generated_at": generated_at,
        "hash_algorithm": hash_algorithm,
        "files": normalized_files,
    }
    return errors, warnings, normalized


def fetch_and_validate_json(
    url: str,
    field_name: str,
    validator: Any,
) -> tuple[list[str], list[str], dict[str, Any] | None]:
    fetch_errors, response = fetch_json(url)
    if fetch_errors:
        return [f"`{field_name}` {fetch_errors[0]}"], [], None
    assert response is not None

    try:
        data = json.loads(response["body"])
    except json.JSONDecodeError as error:
        return [f"`{field_name}` does not contain valid JSON: {error.msg}."], [], None

    document_errors, document_warnings, normalized = validator(data)
    errors = [f"`{field_name}` {message}" for message in document_errors]
    warnings = [f"`{field_name}` {message}" for message in document_warnings]
    return errors, warnings, normalized


def compare_string_field(
    errors: list[str],
    reference_value: str | None,
    document_value: str | None,
    *,
    reference_label: str,
    document_name: str,
    document_field: str,
) -> None:
    if not reference_value or not document_value:
        return
    if reference_value.strip() != document_value.strip():
        errors.append(f"`{document_name}` field `{document_field}` does not match `{reference_label}`.")


def compare_number_field(
    errors: list[str],
    reference_value: float | int | None,
    document_value: float | int | None,
    *,
    reference_label: str,
    document_name: str,
    document_field: str,
    tolerance: float = 1e-4,
) -> None:
    if reference_value is None or document_value is None:
        return
    if abs(float(reference_value) - float(document_value)) > tolerance:
        errors.append(f"`{document_name}` field `{document_field}` does not match `{reference_label}`.")


def main() -> int:
    args = parse_args()
    body = os.environ.get("ISSUE_BODY", "")
    issue_number = os.environ.get("ISSUE_NUMBER", "")
    issue_title = os.environ.get("ISSUE_TITLE", "")

    parsed = parse_issue_form(body)
    errors: list[str] = []
    warnings: list[str] = []
    link_checks: dict[str, Any] = {}
    documents: dict[str, Any] = {}

    for field in REQUIRED_FIELDS:
        if not parsed.get(field, "").strip():
            errors.append(f"`{field}` is required.")

    track = normalize_track(parsed.get("track", ""))
    if track not in TRACK_VALUES:
        errors.append(f"`track` must be one of: {', '.join(sorted(TRACK_VALUES))}.")

    total_score = parse_float(parsed.get("total_score", ""))
    if total_score is None:
        errors.append("`total_score` must be a number.")
    elif total_score < 0:
        errors.append("`total_score` must be greater than or equal to 0.")

    pass_rate_percent = normalize_pass_rate(parsed.get("pass_rate", ""))
    if pass_rate_percent is None:
        errors.append("`pass_rate` must be numeric or percent-formatted.")
    elif pass_rate_percent < 0 or pass_rate_percent > 100:
        errors.append("`pass_rate` must resolve to a percentage between 0 and 100.")

    runtime_ms = None
    if parsed.get("runtime_ms", "").strip():
        runtime_ms = parse_int(parsed.get("runtime_ms", ""))
        if runtime_ms is None or runtime_ms < 0:
            errors.append("`runtime_ms` must be a non-negative integer when provided.")

    cost_usd = None
    if parsed.get("cost_usd", "").strip():
        cost_usd = parse_float(parsed.get("cost_usd", ""))
        if cost_usd is None or cost_usd < 0:
            errors.append("`cost_usd` must be a non-negative number when provided.")

    for field in [
        "submission_repo_url",
        "submission_package_url",
        "score_summary_url",
        "manifest_url",
        "run_meta_url",
    ]:
        field_errors, field_warnings, result = validate_url(parsed.get(field, "").strip(), field)
        errors.extend(field_errors)
        warnings.extend(field_warnings)
        if result is not None:
            link_checks[field] = result

    score_summary_doc: dict[str, Any] | None = None
    if parsed.get("score_summary_url", "").strip() and link_checks.get("score_summary_url", {}).get("ok"):
        doc_errors, doc_warnings, score_summary_doc = fetch_and_validate_json(
            parsed["score_summary_url"].strip(),
            "score_summary_url",
            validate_score_summary_document,
        )
        errors.extend(doc_errors)
        warnings.extend(doc_warnings)
        if score_summary_doc is not None:
            documents["score_summary"] = score_summary_doc

    manifest_doc: dict[str, Any] | None = None
    if parsed.get("manifest_url", "").strip() and link_checks.get("manifest_url", {}).get("ok"):
        doc_errors, doc_warnings, manifest_doc = fetch_and_validate_json(
            parsed["manifest_url"].strip(),
            "manifest_url",
            validate_manifest_document,
        )
        errors.extend(doc_errors)
        warnings.extend(doc_warnings)
        if manifest_doc is not None:
            documents["manifest"] = manifest_doc

    run_meta_doc: dict[str, Any] | None = None
    if parsed.get("run_meta_url", "").strip() and link_checks.get("run_meta_url", {}).get("ok"):
        doc_errors, doc_warnings, run_meta_doc = fetch_and_validate_json(
            parsed["run_meta_url"].strip(),
            "run_meta_url",
            validate_run_meta_document,
        )
        errors.extend(doc_errors)
        warnings.extend(doc_warnings)
        if run_meta_doc is not None:
            documents["run_meta"] = run_meta_doc

    if score_summary_doc is not None:
        compare_string_field(errors, parsed.get("agent_name"), score_summary_doc.get("agent_name"), reference_label="issue field `agent_name`", document_name="score_summary.json", document_field="agent_name")
        compare_string_field(errors, parsed.get("agent_version"), score_summary_doc.get("agent_version"), reference_label="issue field `agent_version`", document_name="score_summary.json", document_field="agent_version")
        compare_string_field(errors, parsed.get("benchmark_variant"), score_summary_doc.get("benchmark_variant"), reference_label="issue field `benchmark_variant`", document_name="score_summary.json", document_field="benchmark_variant")
        compare_string_field(errors, track, score_summary_doc.get("track"), reference_label="issue field `track`", document_name="score_summary.json", document_field="track")
        compare_string_field(errors, parsed.get("skill_version"), score_summary_doc.get("skill_version"), reference_label="issue field `skill_version`", document_name="score_summary.json", document_field="skill_version")
        compare_string_field(errors, parsed.get("dataset_version"), score_summary_doc.get("dataset_version"), reference_label="issue field `dataset_version`", document_name="score_summary.json", document_field="dataset_version")
        compare_string_field(errors, parsed.get("run_id"), score_summary_doc.get("run_id"), reference_label="issue field `run_id`", document_name="score_summary.json", document_field="run_id")
        compare_number_field(errors, total_score, score_summary_doc.get("total_score"), reference_label="issue field `total_score`", document_name="score_summary.json", document_field="total_score")
        compare_number_field(errors, pass_rate_percent, score_summary_doc.get("pass_rate"), reference_label="issue field `pass_rate`", document_name="score_summary.json", document_field="pass_rate")

        if runtime_ms is not None and score_summary_doc.get("runtime_ms") is None:
            errors.append("`runtime_ms` was provided in the issue, but `score_summary.json` does not include `runtime_ms`.")
        compare_number_field(errors, runtime_ms, score_summary_doc.get("runtime_ms"), reference_label="issue field `runtime_ms`", document_name="score_summary.json", document_field="runtime_ms")

        if cost_usd is not None and score_summary_doc.get("cost_usd") is None:
            errors.append("`cost_usd` was provided in the issue, but `score_summary.json` does not include `cost_usd`.")
        compare_number_field(errors, cost_usd, score_summary_doc.get("cost_usd"), reference_label="issue field `cost_usd`", document_name="score_summary.json", document_field="cost_usd")

    if run_meta_doc is not None:
        compare_string_field(errors, parsed.get("agent_name"), run_meta_doc.get("agent_name"), reference_label="issue field `agent_name`", document_name="run_meta.json", document_field="agent_name")
        compare_string_field(errors, parsed.get("agent_version"), run_meta_doc.get("agent_version"), reference_label="issue field `agent_version`", document_name="run_meta.json", document_field="agent_version")
        compare_string_field(errors, parsed.get("benchmark_variant"), run_meta_doc.get("benchmark_variant"), reference_label="issue field `benchmark_variant`", document_name="run_meta.json", document_field="benchmark_variant")
        compare_string_field(errors, track, run_meta_doc.get("track"), reference_label="issue field `track`", document_name="run_meta.json", document_field="track")
        compare_string_field(errors, parsed.get("skill_version"), run_meta_doc.get("skill_version"), reference_label="issue field `skill_version`", document_name="run_meta.json", document_field="skill_version")
        compare_string_field(errors, parsed.get("dataset_version"), run_meta_doc.get("dataset_version"), reference_label="issue field `dataset_version`", document_name="run_meta.json", document_field="dataset_version")
        compare_string_field(errors, parsed.get("run_id"), run_meta_doc.get("run_id"), reference_label="issue field `run_id`", document_name="run_meta.json", document_field="run_id")

    if score_summary_doc is not None and run_meta_doc is not None:
        compare_string_field(errors, score_summary_doc.get("agent_name"), run_meta_doc.get("agent_name"), reference_label="score_summary.json field `agent_name`", document_name="run_meta.json", document_field="agent_name")
        compare_string_field(errors, score_summary_doc.get("agent_version"), run_meta_doc.get("agent_version"), reference_label="score_summary.json field `agent_version`", document_name="run_meta.json", document_field="agent_version")
        compare_string_field(errors, score_summary_doc.get("benchmark_variant"), run_meta_doc.get("benchmark_variant"), reference_label="score_summary.json field `benchmark_variant`", document_name="run_meta.json", document_field="benchmark_variant")
        compare_string_field(errors, score_summary_doc.get("track"), run_meta_doc.get("track"), reference_label="score_summary.json field `track`", document_name="run_meta.json", document_field="track")
        compare_string_field(errors, score_summary_doc.get("skill_version"), run_meta_doc.get("skill_version"), reference_label="score_summary.json field `skill_version`", document_name="run_meta.json", document_field="skill_version")
        compare_string_field(errors, score_summary_doc.get("dataset_version"), run_meta_doc.get("dataset_version"), reference_label="score_summary.json field `dataset_version`", document_name="run_meta.json", document_field="dataset_version")
        compare_string_field(errors, score_summary_doc.get("run_id"), run_meta_doc.get("run_id"), reference_label="score_summary.json field `run_id`", document_name="run_meta.json", document_field="run_id")

    normalized_payload = {
        "agent_name": parsed.get("agent_name", "").strip(),
        "agent_version": parsed.get("agent_version", "").strip(),
        "benchmark_variant": parsed.get("benchmark_variant", "").strip(),
        "track": track,
        "skill_version": parsed.get("skill_version", "").strip(),
        "dataset_version": parsed.get("dataset_version", "").strip(),
        "run_id": parsed.get("run_id", "").strip(),
        "total_score": total_score,
        "pass_rate_percent": round(pass_rate_percent, 4) if pass_rate_percent is not None else None,
        "runtime_ms": runtime_ms,
        "cost_usd": cost_usd,
        "submission_repo_url": parsed.get("submission_repo_url", "").strip(),
        "submission_ref": parsed.get("submission_ref", "").strip(),
        "submission_package_url": parsed.get("submission_package_url", "").strip(),
        "score_summary_url": parsed.get("score_summary_url", "").strip(),
        "manifest_url": parsed.get("manifest_url", "").strip(),
        "run_meta_url": parsed.get("run_meta_url", "").strip() or None,
        "notes": parsed.get("notes", "").strip(),
    }

    result = {
        "ok": len(errors) == 0,
        "status_label": "validated" if len(errors) == 0 else "needs-info",
        "issue": {
            "number": issue_number,
            "title": issue_title,
        },
        "errors": errors,
        "warnings": warnings,
        "parsed": normalized_payload,
        "link_checks": link_checks,
        "documents": documents,
    }

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
