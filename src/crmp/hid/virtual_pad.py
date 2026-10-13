"""Virtual gamepad output. Backed by vgamepad's ViGEm bus on Windows."""
from __future__ import annotations

import logging
import sys

from crmp.hid.events import AxisEvent, ButtonEvent, PadEvent

log = logging.getLogger(__name__)

_BUTTON_MAP = {
    "a": "XUSB_GAMEPAD_A",
    "b": "XUSB_GAMEPAD_B",
    "x": "XUSB_GAMEPAD_X",
    "y": "XUSB_GAMEPAD_Y",
    "lb": "XUSB_GAMEPAD_LEFT_SHOULDER",
    "rb": "XUSB_GAMEPAD_RIGHT_SHOULDER",
    "back": "XUSB_GAMEPAD_BACK",
    "start": "XUSB_GAMEPAD_START",
    "ls": "XUSB_GAMEPAD_LEFT_THUMB",
    "rs": "XUSB_GAMEPAD_RIGHT_THUMB",
    "dpad_up": "XUSB_GAMEPAD_DPAD_UP",
    "dpad_down": "XUSB_GAMEPAD_DPAD_DOWN",
    "dpad_left": "XUSB_GAMEPAD_DPAD_LEFT",
    "dpad_right": "XUSB_GAMEPAD_DPAD_RIGHT",
}


class VirtualPad:
    """Thin wrapper. No-op stub on non-Windows so parsers/tests import cleanly."""

    def __init__(self) -> None:
        self._pad = None
        self._buttons: dict[str, bool] = {}
        self._axes: dict[str, float] = {}
        if sys.platform == "win32":
            import vgamepad as vg  # type: ignore[import-not-found]
            self._pad = vg.VX360Gamepad()
        else:
            log.warning("VirtualPad running in stub mode (non-Windows host)")

    def emit_raw(self, event: PadEvent) -> None:
        if isinstance(event, ButtonEvent):
            self.set_button(event.source.value, event.pressed)
        else:
            self.set_axis(event.source.value, event.value)

    def set_button(self, target: str, pressed: bool) -> None:
        self._buttons[target] = pressed
        if self._pad is None:
            return
        vg_name = _BUTTON_MAP.get(target)
        if vg_name is None:
            log.debug("unmapped button target %s", target)
            return
        import vgamepad as vg  # type: ignore[import-not-found]
        flag = getattr(vg.XUSB_BUTTON, vg_name)
        if pressed:
            self._pad.press_button(flag)
        else:
            self._pad.release_button(flag)
        self._pad.update()

    def set_axis(self, target: str, value: float) -> None:
        self._axes[target] = value
        if self._pad is None:
            return
        if target == "left_x":
            self._pad.left_joystick(x_value=int(value * 32767), y_value=int(self._axes.get("left_y", 0.0) * 32767))
        elif target == "left_y":
            self._pad.left_joystick(x_value=int(self._axes.get("left_x", 0.0) * 32767), y_value=int(value * 32767))
        elif target == "right_x":
            self._pad.right_joystick(x_value=int(value * 32767), y_value=int(self._axes.get("right_y", 0.0) * 32767))
        elif target == "right_y":
            self._pad.right_joystick(x_value=int(self._axes.get("right_x", 0.0) * 32767), y_value=int(value * 32767))
        elif target == "trigger_l":
            self._pad.left_trigger(value=int(max(0.0, value) * 255))
        elif target == "trigger_r":
            self._pad.right_trigger(value=int(max(0.0, value) * 255))
        self._pad.update()