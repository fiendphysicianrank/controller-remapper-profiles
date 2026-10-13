# Contributing to controller-remapper-profiles

Thanks for poking at the remapper. This is a hobbyist desktop tool for
Windows that lets you bind any HID gamepad to any logical action, then
swap the whole binding set the moment a game window takes focus.

## Ground rules

- One feature per PR. Small diffs review fast.
- Every new binding backend needs a `tests/` case that exercises the
  device -> action translation table without a physical pad attached.
- Don't touch `src/crmp/config/schema.py` without bumping
  `PROFILE_SCHEMA_VERSION` and adding a migration in
  `src/crmp/config/migrations/`.
- Keep `src/crmp/hid/` free of Windows-only imports at module top level.
  The HID layer must import cleanly on Linux CI so the parser tests run.

## Dev setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
```

## Profile format

Profiles are YAML under `profiles/`. See `profiles/_example.yaml` for the
full field list. `match` blocks are evaluated top-to-bottom; first hit
wins. `process` matches on executable basename, `window_title` uses a
case-insensitive regex.

## Reporting bugs

Include: Windows build, pad model (VID/PID if you have it), the profile
YAML that misbehaved, and the tail of `logs/crmp.log`.