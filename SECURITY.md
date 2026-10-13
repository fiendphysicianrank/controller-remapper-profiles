# Security Policy

## Scope

This project reads HID input and synthesizes virtual gamepad/keyboard
output. The attack surface that matters:

- **Profile loading.** YAML is parsed with `yaml.safe_load`. No
  `!!python/object` tags. If you find a path where a profile can trigger
  arbitrary import, that's a critical bug — email the maintainers, don't
  open a public issue.
- **IPC.** The tray app and the engine talk over a named pipe
  (`\\.\pipe\crmp-engine`). The ACL is restricted to the current user.
  Any report of cross-user pipe access is in scope.
- **Driver shims.** `vgamepad` installs a virtual bus driver. We do not
  ship or sign it. If you find our code invoking an unsigned kernel
  driver outside the documented install step, that's in scope.

## Out of scope

- Anti-cheat detection of the virtual pad. That's a game-vendor policy
  question, not a vulnerability in this codebase.
- Anything requiring an already-elevated attacker.

## Reporting

Open a private security advisory on the repo. We aim to respond within
72 hours. Please don't test against other people's machines.