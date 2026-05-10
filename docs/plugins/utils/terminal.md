# Terminal Utility

The **Terminal** utility opens an **interactive PTY shell** inside an OctoPwn
window — a real, full-featured `bash` process driven through the GUI's
embedded xterm.js terminal. It mirrors the in-window terminal experience the
[SSH client](../clients/ssh.md) provides, but for the **OctoPwn host itself**
rather than a remote machine.

This is intentionally a small util: there is one user-facing command,
[`ptyshell`](#ptyshell). The sub-commands `sendchar`, `resize`, and
`stopterminal` are wired into the GUI's xterm.js plumbing and you should
not need to call them by hand.

!!! warning "Enterprise / server build only"
    The util shells out to `/bin/bash` via `pty.openpty()`. There is no
    such thing in the browser sandbox — the WASM build cannot use this util.
    On Linux / macOS server installs it works out of the box; on Windows
    it requires a POSIX-flavoured runtime (WSL, Cygwin, etc.).

---

## What the GUI gives you

When `ptyshell` is invoked, the OctoPwn GUI opens a new window with a full
xterm.js terminal connected to the spawned bash process. You get:

- Real PTY semantics — colours, line editing, ncurses apps (`htop`, `vim`,
  `tmux`, …) all work.
- Live resize: dragging the window propagates a `TIOCSWINSZ` to the PTY so
  ncurses apps redraw correctly.
- One terminal per `ptyshell` invocation — you can have several open at the
  same time, each with its own session ID.
- Closing the window terminates the bash process (and any child it has
  spawned that's still attached to the PTY).

Outside the GUI (text-only console, automation scripts) the util is not
useful — there is no scriptable wrapper around the streaming PTY data.

---

## Parameters

| Parameter | Default | Purpose |
| --- | --- | --- |
| `command` | none | Reserved — would let you start `ptyshell` with a non-default command. Currently the spawned process is hard-coded to `/bin/bash`. |
| `debug` | `True` | Print debug messages from the util. |

---

## Commands

### GENERIC

#### ptyshell
`ptyshell()` — spawn a new bash PTY. The util:

1. Allocates a master/slave PTY pair (`pty.openpty()`).
2. Starts `/bin/bash` with the slave end as its stdin/stdout/stderr,
   inside a fresh session (`os.setsid`) so the PTY becomes its
   controlling terminal.
3. Returns a session ID and tells the GUI to open a new xterm.js window
   bound to that ID.

From the GUI side, every keystroke is base64-wrapped and sent to the util,
which writes it straight to the master FD. Output from bash is read off the
master FD by an `add_reader` callback and streamed back to the GUI window
the same way. Window resize events are forwarded as `TIOCSWINSZ` ioctls.

---

## When to use it

- **Quick local commands** without leaving the OctoPwn UI — running a
  one-off `nmap` / `crackmapexec` / `pkexec`-elevated shell next to your
  current OctoPwn project.
- **Debugging plugins / WSNet daemon issues** — having a shell on the
  OctoPwn host in the same browser tab is a much shorter context-switch
  than alt-tabbing to a separate terminal app.
- **Driving local cracking** alongside the [HASHCAT utility](hashcat.md) —
  e.g. for managing wordlists, checking the potfile, or running auxiliary
  tools.

---

## Limitations and caveats

- **POSIX only.** Uses `pty`, `fcntl`, `termios`, `os.setsid`. Windows
  hosts need a POSIX runtime.
- **No persistence.** Closing the window closes the PTY; there is no
  detach / reattach (yet). Use `tmux` / `screen` *inside* the bash session
  if you need that.
- **Inherits OctoPwn's privileges.** The bash process runs as the user
  OctoPwn is running as. If you started OctoPwn as root, you get a root
  shell — be deliberate about that.
- **Output is not echoed to the OctoPwn console** — only to the xterm.js
  window. Programmatic capture of session output is not supported.
- **The `command` parameter is currently unused.** Custom shells (`zsh`,
  `fish`, `python -i`, `tmux attach`) can't be set this way yet — the
  spawned binary is hard-coded.

---

## See also

- [SSH client](../clients/ssh.md) — for the same kind of interactive PTY
  experience, but against a *remote* host. Same xterm.js front-end.
- [Plugin Loader](pluginloader.md) — if you find yourself opening a local
  shell to invoke a fixed sequence of commands repeatedly, write a plugin
  instead.
