"""Typed pad events. Frozen, hashable, cheap to allocate."""
from __future__ import annotations

from dataclasses import dataclass

from crmp.config.schema import Axis, Button


@dataclass(frozen=True, slots=True)
class ButtonEvent:
    source: Button
    pressed: bool
    timestamp_ns: int


@dataclass(frozen=True, slots=True)
class AxisEvent:
    source: Axis
    value: float  # normalized [-1.0, 1.0]
    timestamp_ns: int


PadEvent = ButtonEvent | AxisEvent