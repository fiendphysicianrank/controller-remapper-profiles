"""Physical pad reader. Uses XInput via ctypes; emits PadEvent into a queue."""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import logging
import queue
import sys
import threading
import time

from crmp.config.schema import Axis, Button
from crmp.hid.events import AxisEvent, ButtonEvent, PadEvent

log = logging.getLogger(__name__)

_XINPUT_DLL = "xinput1_4.dll"
_POLL_HZ = 250.0

_BUTTON_BITS: tuple[tuple[int, Button], ...] = (
    (0x1000, Button.A),
    (0x2000, Button.B),
    (0x4000, Button.X),
    (0x8000, Button.Y),
    (0x0100, Button.LB),
    (0x0200, Button.RB),
    (0x0020, Button.BACK),
    (0x0010, Button.START),
    (0x0040, Button.LS),
    (0x0080, Button.RS),
    (0x0001, Button.DPAD_UP),
    (0x0002, Button.DPAD_DOWN),
    (0x0004, Button.DPAD_LEFT),
    (0x0008, Button.DPAD_RIGHT),
)


class _XInputState(ctypes.Structure):
    _fields_ = [("dwPacketNumber", wt.DWORD), ("Gamepad", ctypes.c_byte * 16)]


class PadReader(threading.Thread):
    """Daemon thread. Pushes PadEvent onto `out` queue. Stops on `stop_evt`."""

    def __init__(self, out: queue.Queue[PadEvent], stop_evt: threading.Event, slot: int = 0) -> None:
        super().__init__(name="crmp-pad-reader", daemon=True)
        self._out = out
        self._stop = stop_evt
        self._slot = slot
        self._prev_buttons = 0
        self._prev_axes: dict[str, float] = {}

    def run(self) -> None:
        if sys.platform != "win32":
            log.warning("PadReader disabled on non-Windows host")
            return
        xinput = ctypes.windll.LoadLibrary(_XINPUT_DLL)
        state = _XInputState()
        interval = 1.0 / _POLL_HZ
        while not self._stop.is_set():
            if xinput.XInputGetState(self._slot, ctypes.byref(state)) == 0:
                self._diff(state)
            time.sleep(interval)

    def _diff(self, state: _XInputState) -> None:
        gp = bytes(state.Gamepad)
        buttons = int.from_bytes(gp[4:6], "little")
        ts = time.perf_counter_ns()
        changed = buttons ^ self._prev_buttons
        for bit, btn in _BUTTON_BITS:
            if changed & bit:
                self._out.put(ButtonEvent(btn, bool(buttons & bit), ts))
        self._prev_buttons = buttons

        lx = _stick(gp[6:8])
        ly = _stick(gp[8:10])
        rx = _stick(gp[10:12])
        ry = _stick(gp[12:14])
        lt = gp[14] / 255.0
        rt = gp[15] / 255.0
        for axis, val in (
            (Axis.LEFT_X, lx), (Axis.LEFT_Y, ly),
            (Axis.RIGHT_X, rx), (Axis.RIGHT_Y, ry),
            (Axis.TRIGGER_L, lt), (Axis.TRIGGER_R, rt),
        ):
            if abs(val - self._prev_axes.get(axis.value, 0.0)) > 0.005:
                self._prev_axes[axis.value] = val
                self._out.put(AxisEvent(axis, val, ts))


def _stick(raw: bytes) -> float:
    v = int.from_bytes(raw, "little", signed=True)
    return max(-1.0, v / 32767.0)
</｜｜DSML｜｜ parameter>
</｜｜DSML｜｜ invoke>
</｜｜DSML｜｜ calls>