# Netcat Client

The **Netcat Client** is OctoPwn's "raw socket" interface — a way to open a single TCP socket to a target, send arbitrary bytes (text or hex), and watch whatever the other side sends back. Despite the name, **it is not a Netcat clone**: there are no listener modes, no port-forwards, no `-e` style command execution — just an explicit, scriptable line into a remote socket.

What makes it useful inside OctoPwn rather than `nc` from a terminal is that it rides the same target / proxy plumbing as every other client. **Pivoting through OctoPwn's proxy system works out of the box**, so a Netcat session can speak to an internal host through any active SOCKS proxy registered in OctoPwn (e.g. one created by [`createsocksproxy`](./ssh.md#createsocksproxy) on the SSH client).

---

## When to reach for it

- **Banner grabbing** that doesn't fit a dedicated scanner (custom service ports, weird protocols).
- **Manual protocol probing / handshakes** — sending crafted bytes to test a service's behaviour.
- **Quick port-open checks through a pivot** — `connect` succeeds or fails synchronously, so it doubles as a one-shot reachability test through OctoPwn's proxy chain.
- **Replaying a captured exchange** — feed bytes via `sendhex` or a file via `sendfile`, observe responses.

For anything heavier (mass scanning, fingerprinting, scripted protocol parsing) reach for the Scanners; this client is intentionally minimal.

---

## Authentication

None. The Netcat session is bound to a target (and optionally a proxy) at session-creation time; there is no credential and no protocol-level auth handshake. Whoever can reach the target through OctoPwn can use the socket.

---

## Session model

- One TCP socket per session. There is no listener mode — Netcat sessions are always **outbound** connects.
- After `connect`, a background reader task starts and pumps every byte from the socket back to the OctoPwn console for as long as the connection is alive.
- All "send" commands write to the same socket. There is no per-command target argument: target + proxy are picked when the Netcat client session is created (in the New Session dialog), not on each `send`.
- `disconnect` (or any unhandled read error) cancels the reader and tears the socket down.

---

## Commands

### CONNECTION

#### connect
Opens the TCP socket to the target (through the configured proxy if any) and starts the background reader. After `connect` returns OK, anything the remote side sends will be printed to the console — decoded as text using the current `encoding` if `binprint` is off, or hex-dumped if `binprint` is on (or if decoding fails). Doubles as a synchronous reachability check: if the target/port is unreachable, `connect` returns an error immediately.

#### disconnect
Closes the socket and cancels the background reader. Safe to call repeatedly; also called automatically when the reader hits EOF or an exception.

---

### SEND

All three send commands write to the same socket opened by `connect`. They differ only in **what bytes go on the wire**.

#### send
Encodes the supplied string using the current `encoding`, **appends the current `lineterm`**, and writes the result to the socket. This is the right command for text-oriented line-based protocols (HTTP request lines, SMTP, IMAP, IRC, …) where the server expects a terminator after each line.

##### Parameters
- **data**: The string to send. Encoded with `encoding`; `lineterm` is appended automatically.

#### sendhex
Decodes the supplied hex string into raw bytes and writes them to the socket **as-is** — no terminator, no encoding, no transformation. The right command for binary protocols, replaying captured payloads, or sending exact byte sequences.

##### Parameters
- **data**: Hex-encoded bytes (e.g. `48656c6c6f0d0a` for `Hello\r\n`). Whitespace inside the hex string is **not** stripped — pass it as one continuous run of hex digits.

!!! warning "No line terminator on `sendhex`"
    Unlike `send`, `sendhex` does not append `lineterm`. If your target needs CRLF after the payload, encode it into the hex string yourself (`...0d0a`).

#### sendfile
Reads a file from OctoPwn's working directory and streams it to the socket in fixed-size blocks. Each block is written **raw** — no terminator, no encoding — so this works for both text and binary payloads. The path is jailed to the working directory; attempts to escape (`..`, absolute paths outside workdir) are rejected.

##### Parameters
- **filepath**: Path to the local file inside OctoPwn's working directory (e.g. `/browserfs/volatile/payload.bin`).
- **blocksize** *(optional, default `1024`)*: Number of bytes read and sent per write call. Larger values mean fewer syscalls; smaller values mean finer-grained progress through the file (useful when the remote side rate-limits or has small receive buffers).

---

### ENCODINGS

Three stateful settings that change how subsequent traffic is encoded / decoded. **Each call without an argument prints the current value** without changing it — handy for verifying state.

#### encoding
Sets (or shows) the text codec used by `send` for outgoing data and by the background reader for incoming data when `binprint` is off. Defaults to `ascii`.

##### Parameters
- **encoding** *(optional)*: A Python codec name (e.g. `ascii`, `utf-8`, `latin-1`, `utf-16-le`). Omit to print the current value.

#### lineterm
Sets (or shows) the line terminator appended by `send`. Defaults to `\r\n` (a real two-byte CR+LF).

##### Parameters
- **lineterm** *(optional)*: The terminator string. Omit to print the current value.

!!! warning "Escape sequences are NOT interpreted from the console"
    The console parser uses `shlex.split`, which doesn't expand backslash escapes. Typing `lineterm \r\n` from the console sets the terminator to the **literal four-character string `\r\n`**, not to CR+LF. The default value (`\r\n` set in code) is the real two-byte CR+LF; if you need to switch to LF-only or some other terminator, do it from a Python plugin / the IDE so you can pass actual byte values.

#### binprint
Toggles how incoming data is rendered. With `binprint` off (default) the reader tries to decode incoming bytes as text using the current `encoding`, falling back to a hex dump if decoding fails. With `binprint` on, the reader **always** hex-dumps incoming data — useful when speaking a binary protocol where occasional ASCII-looking bytes would otherwise be misrendered.

##### Parameters
- **binprint** *(optional)*: `1` to enable, `0` to disable. Omit to print the current value.

---

## Pivoting through an OctoPwn proxy

Because the Netcat client uses the same factory machinery as every other client, the proxy you select for the session at creation time is honoured by `connect`. Typical workflow:

1. Stand up a pivot (e.g. log in to an SSH session and run [`createsocksproxy`](./ssh.md#createsocksproxy)) — note the new proxy ID from the Proxy Window.
2. Create a new Netcat session against an internal target, **selecting that proxy** in the session settings.
3. `connect` — the TCP connect goes through the pivot rather than your operator workstation.

The same applies to any OctoPwn proxy chain (multi-hop, mixed proxy types) — the Netcat client doesn't see the difference.

---

## Limitations & gotchas

- **No listener mode.** Connections are always outbound. There's no `-l` equivalent — use one of the OctoPwn server modules if you need to receive a callback.
- **No `-e` / command execution.** Sending bytes to a remote shell still requires the remote side to actually run a shell — Netcat won't bind one for you on either end.
- **No port forwarding.** This client is purely a single TCP socket. For pivoting *out of* OctoPwn, use the proxy system (e.g. `createsocksproxy` on SSH) and select the proxy for whichever client / scanner needs to ride through it.
- **No TLS.** The socket is plain TCP. For HTTPS-style targets you'll need a dedicated client outside Netcat — there is currently no generic TLS-wrapped raw-socket client in OctoPwn.
- **No half-close / shutdown.** You can't `shutdown(SHUT_WR)` to signal end-of-input while keeping the read side open — only `disconnect` (full close) is exposed.
- **`send` always appends `lineterm`.** If you need to emit a partial line or a payload without a terminator, use `sendhex` (or `sendfile`).
- **Lineterm escape-sequence gotcha**: see the warning under [`lineterm`](#lineterm) above — `\r\n` typed from the console is taken literally.
- **No reconnect on remote close.** When the server closes the socket the reader exits and the session disconnects; you'll need to `connect` again to reopen.
