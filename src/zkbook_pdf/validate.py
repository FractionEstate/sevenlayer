"""Documentation validation helpers for the ZK book project."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .buildlog import BuildLog


MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$", flags=re.MULTILINE)


@dataclass(slots=True)
class ValidationConfig:
    """Configuration for markdown validation workflows."""

    project_root: Path
    docs_root: Path
    log_path: Path


def slugify_heading(text: str) -> str:
    """Approximate GitHub heading anchor generation for Markdown headings."""

    slug = re.sub(r"`([^`]*)`", r"\1", text)
    slug = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", slug)
    slug = slug.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    return slug.strip("-")


def heading_anchors(path: Path) -> set[str]:
    """Return the anchor ids available in a markdown file."""

    text = path.read_text(encoding="utf-8")
    counts: Counter[str] = Counter()
    anchors: set[str] = set()
    for _, heading_text in HEADING_PATTERN.findall(text):
        base = slugify_heading(heading_text)
        if not base:
            continue
        suffix = counts[base]
        anchor = f"{base}-{suffix}" if suffix else base
        anchors.add(anchor)
        counts[base] += 1
    return anchors


def markdown_files(config: ValidationConfig) -> list[Path]:
    """Collect the markdown files that are part of the validation surface."""

    files = sorted(config.docs_root.rglob("*.md"))
    root_readme = config.project_root / "README.md"
    if root_readme.exists():
        files.insert(0, root_readme)
    return files


def validate_markdown_links(config: ValidationConfig, log: BuildLog) -> list[str]:
    """Validate local markdown links and heading fragments."""

    log.section("validator")
    files = markdown_files(config)
    errors: list[str] = []

    for path in files:
        text = path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_PATTERN.findall(text):
            if raw_target.startswith(("http://", "https://", "mailto:")):
                continue

            target_text, _, fragment = raw_target.partition("#")
            target_path = path if not target_text else (path.parent / target_text).resolve()

            if not target_path.exists():
                errors.append(
                    f"{path.relative_to(config.project_root)} -> missing target: {raw_target}"
                )
                continue

            if fragment:
                anchors = heading_anchors(target_path)
                if fragment not in anchors:
                    errors.append(
                        f"{path.relative_to(config.project_root)} -> missing anchor: "
                        f"{raw_target}"
                    )

    log.info(f"Scanned {len(files)} markdown file(s).")
    return errors


def run_validation(config: ValidationConfig) -> int:
    """Execute markdown validation and return a process-style exit code."""

    log = BuildLog(path=config.log_path)
    if not config.docs_root.exists():
        log.error(f"Documentation root not found: {config.docs_root}")
        return 1

    errors = validate_markdown_links(config, log)
    if errors:
        for error in errors:
            log.error(error)
        log.error(f"Validation failed with {len(errors)} error(s).")
        return 1

    log.info("Documentation validation completed successfully.")
    return 0
