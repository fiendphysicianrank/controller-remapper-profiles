"""Forward-migrate old profile dicts to PROFILE_SCHEMA_VERSION."""
from __future__ import annotations

import logging

from crmp.config.schema import PROFILE_SCHEMA_VERSION

log = logging.getLogger(__name__)


def migrate(raw: dict, name: str) -> dict:
    version = int(raw.get("schema_version", 1))
    if version > PROFILE_SCHEMA_VERSION:
        raise ValueError(f"{name}: profile is newer than this build (v{version})")

    if version < 2:
        # v1 -> v2: `bindings` was a flat dict {source: target}.
        flat = raw.pop("bindings", {})
        if isinstance(flat, dict):
            raw["bindings"] = [
                {"source": s, "target": t} for s, t in flat.items()
            ]
        raw["schema_version"] = 2

    if version < 3:
        # v2 -> v3: `match` was a single dict, now a list of MatchRule.
        m = raw.get("match")
        if isinstance(m, dict):
            raw["match"] = [m]
        raw["schema_version"] = 3

    return raw