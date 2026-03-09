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
    "Protocol Version": "protocol_version",
    "Run ID": "run_id",
    "Total Score": "total_score",
    "Pass Rate": "pass_rate",
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
    "protocol_version",
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


def parse_float(value: str) -> float | None:
    try:
        return float(value.strip())
    except ValueError:
        return None


def normalize_pass_rate(value: str) -> float | None:
    normalized = value.strip()
    if normalized.endswith("%"):
        return parse_float(normalized[:-1].strip())

    parsed = parse_float(normalized)
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


def main() -> int:
    args = parse_args()
    body = os.environ.get("ISSUE_BODY", "")
    issue_number = os.environ.get("ISSUE_NUMBER", "")
    issue_title = os.environ.get("ISSUE_TITLE", "")

    parsed = parse_issue_form(body)
    errors: list[str] = []
    warnings: list[str] = []
    link_checks: dict[str, Any] = {}

    for field in REQUIRED_FIELDS:
        if not parsed.get(field, "").strip():
            errors.append(f"`{field}` is required.")

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

    normalized_payload = {
        "agent_name": parsed.get("agent_name", "").strip(),
        "agent_version": parsed.get("agent_version", "").strip(),
        "benchmark_variant": parsed.get("benchmark_variant", "").strip(),
        "protocol_version": parsed.get("protocol_version", "").strip(),
        "run_id": parsed.get("run_id", "").strip(),
        "total_score": total_score,
        "pass_rate_percent": round(pass_rate_percent, 4) if pass_rate_percent is not None else None,
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
    }

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
