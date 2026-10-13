"""Profile loading, hot reload, and validation. YAML only, safe_load."""
from __future__ import annotations

import logging
import threading
from pathlib import Path

import yaml
from pydantic import ValidationError

from crmp.config.migrations import migrate
from crmp.config.schema import PROFILE_SCHEMA_VERSION, Profile

log = logging.getLogger(__name__)


class ProfileStore:
    """Thread-safe profile registry. Reload is atomic: new dict swaps in."""

    def __init__(self, root: Path) -> None:
        self._root = root
        self._lock = threading.RLock()
        self._profiles: dict[str, Profile] = {}
        self._errors: dict[str, str] = {}

    @property
    def profiles(self) -> dict[str, Profile]:
        with self._lock:
            return dict(self._profiles)

    def reload(self) -> None:
        fresh: dict[str, Profile] = {}
        errors: dict[str, str] = {}
        if not self._root.exists():
            log.warning("profile root %s does not exist", self._root)
        else:
            for path in sorted(self._root.glob("*.yaml")):
                if path.name.startswith("_"):
                    continue
                try:
                    fresh[path.stem] = self._load_one(path)
                except (ValidationError, yaml.YAMLError, ValueError) as exc:
                    errors[path.stem] = str(exc)
                    log.error("failed to load %s: %s", path.name, exc)
        with self._lock:
            self._profiles = fresh
            self._errors = errors
        log.info("loaded %d profiles (%d errors)", len(fresh), len(errors))

    def _load_one(self, path: Path) -> Profile:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(f"{path.name}: top-level must be a mapping")
        raw = migrate(raw, path.stem)
        prof = Profile.model_validate(raw)
        if prof.schema_version != PROFILE_SCHEMA_VERSION:
            raise ValueError(
                f"{path.name}: schema v{prof.schema_version} != v{PROFILE_SCHEMA_VERSION}"
            )
        return prof

    def validate_all(self) -> dict[str, str]:
        with self._lock:
            return dict(self._errors)

    def resolve(self, process: str, window_title: str) -> Profile | None:
        """Return the first profile whose match block fires. None = passthrough."""
        import re
        with self._lock:
            candidates = list(self._profiles.values())
        for prof in candidates:
            for rule in prof.match:
                if rule.any:
                    return prof
                if rule.process and rule.process == process.lower():
                    return prof
                if rule.window_title and re.search(rule.window_title, window_title, re.I):
                    return prof
        return None