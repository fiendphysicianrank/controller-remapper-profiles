"""Translate physical pad events through the active profile to virtual output."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from crmp.config.loader import ProfileStore
from crmp.config.schema import Axis, Binding, Button, Profile
from crmp.hid.events import AxisEvent, ButtonEvent, PadEvent
from crmp.hid.virtual_pad import VirtualPad

log = logging.getLogger(__name__)


@dataclass(slots=True)
class _CompiledBinding:
    source: str
    target: str
    deadzone: float
    curve: float
    invert: bool


class InputDispatcher:
    """Holds the compiled binding table for the currently active profile."""

    def __init__(self, store: ProfileStore) -> None:
        self._store = store
        self._pad = VirtualPad()
        self._active: Profile | None = None
        self._table: dict[str, _CompiledBinding] = {}

    @property
    def active_profile(self) -> str | None:
        return self._active.name if self._active else None

    def activate(self, profile: Profile | None) -> None:
        if profile is self._active:
            return
        self._active = profile
        self._table.clear()
        if profile is None:
            log.info("profile cleared — passthrough mode")
            return
        for b in profile.bindings:
            self._table[b.source.value] = _CompiledBinding(
                source=b.source.value,
                target=b.target.value,
                deadzone=b.deadzone,
                curve=b.curve,
                invert=b.invert,
            )
        log.info("activated profile %s (%d bindings)", profile.name, len(self._table))

    def handle(self, event: PadEvent) -> None:
        if self._active is None:
            self._pad.emit_raw(event)
            return
        key = event.source.value
        binding = self._table.get(key)
        if binding is None:
            return  # swallowed: profile owns this pad
        if isinstance(event, ButtonEvent):
            self._pad.set_button(binding.target, event.pressed)
        elif isinstance(event, AxisEvent):
            value = _apply_curve(event.value, binding.deadzone, binding.curve, binding.invert)
            self._pad.set_axis(binding.target, value)


def _apply_curve(value: float, deadzone: float, curve: float, invert: bool) -> float:
    """Deadzone -> radial rescale -> power curve -> optional invert. Output in [-1, 1]."""
    mag = abs(value)
    if mag <= deadzone:
        return 0.0
    rescaled = (mag - deadzone) / (1.0 - deadzone)
    shaped = rescaled ** curve
    out = shaped if value >= 0 else -shaped
    return -out if invert else out