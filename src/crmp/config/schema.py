"""Pydantic models for profile YAML. Bump PROFILE_SCHEMA_VERSION on change."""
from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

PROFILE_SCHEMA_VERSION = 3


class Button(StrEnum):
    A = "a"
    B = "b"
    X = "x"
    Y = "y"
    LB = "lb"
    RB = "rb"
    LT = "lt"
    RT = "rt"
    BACK = "back"
    START = "start"
    LS = "ls"
    RS = "rs"
    DPAD_UP = "dpad_up"
    DPAD_DOWN = "dpad_down"
    DPAD_LEFT = "dpad_left"
    DPAD_RIGHT = "dpad_right"


class Axis(StrEnum):
    LEFT_X = "left_x"
    LEFT_Y = "left_y"
    RIGHT_X = "right_x"
    RIGHT_Y = "right_y"
    TRIGGER_L = "trigger_l"
    TRIGGER_R = "trigger_r"


class MatchRule(BaseModel):
    """First matching rule in a profile wins. All fields optional."""
    process: str | None = None
    window_title: str | None = None
    any: bool = False

    @field_validator("process")
    @classmethod
    def _lower_basename(cls, v: str | None) -> str | None:
        return v.lower() if v else v


class Binding(BaseModel):
    """One logical action -> one physical output."""
    source: Button | Axis
    target: Button | Axis
    deadzone: Annotated[float, Field(ge=0.0, le=0.95)] = 0.08
    curve: Annotated[float, Field(ge=0.5, le=3.0)] = 1.0
    invert: bool = False


class Profile(BaseModel):
    schema_version: int = PROFILE_SCHEMA_VERSION
    name: str
    match: list[MatchRule] = Field(default_factory=list)
    bindings: list[Binding] = Field(default_factory=list)
    rumble_scale: Annotated[float, Field(ge=0.0, le=2.0)] = 1.0
    notes: str = ""

    def target_summary(self) -> str:
        if not self.match:
            return "always-on"
        parts = []
        for m in self.match:
            if m.any:
                parts.append("*")
            elif m.process:
                parts.append(f"proc={m.process}")
            elif m.window_title:
                parts.append(f"title~{m.window_title!r}")
        return ", ".join(parts) or "unmatched"