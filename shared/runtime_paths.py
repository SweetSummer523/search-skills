from __future__ import annotations

import os
from pathlib import Path


_PLACEHOLDER_MARKERS = (
    "your-",
    "replace-",
    "replace_",
    "example",
    "placeholder",
    "changeme",
    "change-me",
    "change_me",
    "<",
)


def repo_root_from(script_file: str | Path) -> Path:
    path = Path(script_file).resolve()
    return path.parents[2]


def _expand_env_path(name: str) -> Path | None:
    value = os.environ.get(name)
    if not value:
        return None
    return Path(value).expanduser()


def _first_existing(paths: list[Path]) -> Path | None:
    seen: set[str] = set()
    for path in paths:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        if path.exists():
            return path
    return None


def default_workspace() -> Path:
    for env_name in ("SEARCH_SKILLS_WORKSPACE", "AGENT_WORKSPACE", "OPENCLAW_WORKSPACE"):
        if path := _expand_env_path(env_name):
            return path

    home = Path.home()
    candidates = [
        home / ".agent-skills" / "workspace",
        home / ".openclaw" / "workspace",
    ]
    existing = _first_existing(candidates)
    return existing or candidates[0]


def search_credentials_candidates(script_file: str | Path | None = None) -> list[Path]:
    candidates: list[Path] = []

    if script_file is not None:
        repo_root = repo_root_from(script_file)
        candidates.append(repo_root / "search-layer" / "search.json")

    for env_name in ("SEARCH_SKILLS_CREDENTIALS", "AGENT_CREDENTIALS_PATH"):
        if path := _expand_env_path(env_name):
            candidates.append(path)

    cwd = Path.cwd()
    candidates.append(cwd / "credentials" / "search.json")

    if script_file is not None:
        candidates.append(repo_root / "credentials" / "search.json")

    home = Path.home()
    candidates.extend(
        [
            home / ".agent-skills" / "credentials" / "search.json",
            home / ".openclaw" / "credentials" / "search.json",
        ]
    )

    return candidates


def find_search_credentials(script_file: str | Path | None = None) -> Path | None:
    return _first_existing(search_credentials_candidates(script_file))


def is_configured_value(value: str | None) -> bool:
    if value is None:
        return False
    text = value.strip()
    if not text:
        return False

    lowered = text.lower()
    if lowered in {"null", "none", "unset", "todo", "tbd"}:
        return False

    return not any(marker in lowered for marker in _PLACEHOLDER_MARKERS)


def find_skill_script(
    script_file: str | Path,
    *,
    skill_name: str,
    relative_path: str,
) -> Path | None:
    relative = Path(relative_path)
    candidates: list[Path] = []

    for env_name in ("SEARCH_SKILLS_ROOT", "AGENT_SKILLS_ROOT"):
        if root := _expand_env_path(env_name):
            candidates.append(root / skill_name / relative)

    repo_root = repo_root_from(script_file)
    candidates.append(repo_root / skill_name / relative)
    candidates.append(Path.cwd() / skill_name / relative)

    home = Path.home()
    candidates.extend(
        [
            home / ".agent-skills" / skill_name / relative,
            home / ".openclaw" / "workspace" / "skills" / skill_name / relative,
        ]
    )

    return _first_existing(candidates)
