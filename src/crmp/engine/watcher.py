"""Poll the foreground window and hot-swap the active profile."""
from __future__ import annotations

import logging
import time

from crmp.config.loader import ProfileStore
from crmp.engine.dispatcher import InputDispatcher
from crmp.utils.win_focus import foreground_process_and_title

log = logging.getLogger(__name__)


class ForegroundWatcher:
    """Poll at poll_hz. Cheap: only re-resolves when the foreground pid changes."""

    def __init__(self, store: ProfileStore, dispatcher: InputDispatcher, poll_hz: float = 4.0) -> None:
        self._store = store
        self._dispatcher = dispatcher
        self._interval = 1.0 / poll_hz
        self._last_key: tuple[str, str] | None = None

    def run_forever(self) -> None:
        log.info("watcher started (%.1f Hz)", 1.0 / self._interval)
        while True:
            try:
                self.tick()
            except Exception:  # noqa: BLE001 — never let the loop die
                log.exception("watcher tick failed; continuing")
            time.sleep(self._interval)

    def tick(self) -> None:
        process, title = foreground_process_and_title()
        key = (process, title)
        if key == self._last_key:
            return
        self._last_key = key
        profile = self._store.resolve(process, title)
        self._dispatcher.activate(profile)