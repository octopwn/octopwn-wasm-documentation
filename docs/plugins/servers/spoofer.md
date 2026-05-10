# Spoofer Server (LLMNR + mDNS + NBT-NS)

The **Spoofer Server** is OctoPwn's unified Layer-2 name-resolution poisoner. A single
session brings up **three** UDP listeners side by side and feeds them all from the same
configuration:

| Listener | Port      | Discovery model         | Privileged?              |
| -------- | --------- | ----------------------- | ------------------------ |
| LLMNR    | `5355/UDP` | IPv4/IPv6 multicast      | No                       |
| mDNS     | `5353/UDP` | IPv4/IPv6 multicast      | No                       |
| NBT-NS   | `137/UDP`  | IPv4 broadcast           | **Yes** (port < 1024)    |

It runs in two modes:

- **Analysis mode** (default) — log every name-resolution request that reaches the host.
  No replies are sent. Every requesting IP is automatically added to the project's
  Targets pane (`source = LLMNR / MDNS / NBTNS`), so just *listening* gives you free
  passive recon of which hosts are confused about names on the segment.
- **Spoof mode** — for matching requests, send a forged answer pointing the victim at the
  IP of your choice (the agent host itself, by default). The victim then connects to
  whatever auth-collection / relay server you have running on that IP.

---

## How this differs from Responder / Inveigh / ntlmrelayx

If you have used Responder before, the OctoPwn split will feel unusual. Responder is a
single binary that does **both** the poisoning **and** the auth-collection (rogue
SMB / HTTP / LDAP / MSSQL / WPAD servers, hash logging, basic relaying). OctoPwn deliberately
splits these into two layers:

- **This server** is *only* the L2 poisoner — it answers LLMNR / mDNS / NBT-NS queries.
  It does **not** speak SMB, HTTP, LDAP, etc. and it does **not** capture NTLM hashes by
  itself.
- The actual auth-handling and hash collection happens in separate relay servers —
  [`RELAYSMB`](relaysmb.md), [`RELAYLDAP`](relayldap.md),
  [`RELAYMSSQL`](relaymssql.md), [`RELAYESC8`](relayesc8.md), and
  [`RELAYNTLMREFLECTION`](relayreflection.md). Each of those is its own session and
  listens on its own port.

To get the Responder workflow you would expect — *"I just want to spoof everyone and
catch hashes"* — start **two** sessions: this Spoofer (with `spoof=True`) and at minimum
a `RELAYSMB` server. The Spoofer sends victims to the agent's IP; the `RELAYSMB` server
on `445/TCP` catches the resulting SMB authentication.

Other concrete differences:

| Topic                                | Responder / Inveigh                                    | OctoPwn Spoofer                                                          |
| ------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------------------------ |
| Where it runs                        | Native binary on the attacker box                      | Inside the OctoPwn agent process (browser-only WASM cannot do raw sockets) |
| Concurrency                          | One binary runs everything                             | Spoofer = poisoning only; Relay servers = separate sessions              |
| Hash logging                         | Files in the working directory                         | Goes through the project; the relay servers also auto-store credentials  |
| Selective spoofing                   | `--analyze` / `-w` flags, hard-coded blacklist          | `spooftable` DSL — `host,ip;host,ip;...` with `*` wildcard and `SELF`     |
| Free recon                           | Log file you have to grep                              | Every requester is auto-added to the project Targets pane                |
| Native-responder coexistence         | Responder kills/refuses-to-start on conflicts          | Same constraint, but no built-in conflict killer — see "Operational requirements" |

---

## Operational requirements

Before you start a Spoofer session, please confirm all of the following — this is the
single biggest source of "the server starts but I never see anything" tickets.

### 1. The Spoofer runs on the agent host, not in the browser

Like every other server in OctoPwn, the Spoofer's UDP listeners are bound by the OctoPwn
agent that the project is connected to. In a typical setup that is:

- **Pro / WASM mode**: the wsnet agent on whichever native host you are using to bridge
  the browser to the network.
- **Enterprise mode**: the OctoPwn server process on whichever host it is deployed.

A purely browser-only deployment with no native bridge **cannot** run this server —
`get_localip()` returns `None` under Emscripten and every protocol bails with
"Could not determine local IP address!". The session will start, but the listeners will
silently refuse to spoof.

### 2. Privileged port for NBT-NS

NBT-NS uses `137/UDP`, which is below 1024 and therefore privileged on every modern OS:

- **Linux**: run the agent as `root`, or grant the agent process
  `CAP_NET_BIND_SERVICE` (`setcap cap_net_bind_service=+ep <python-interpreter>`).
- **macOS**: run the agent as `root` (`sudo`).
- **Windows**: run the agent as Administrator. Note that on Windows the **NetBIOS Helper**
  service (`lmhosts`) typically has port 137 already bound; see point 4.

LLMNR (`5355/UDP`) and mDNS (`5353/UDP`) are unprivileged, so the spoofer can still bring
those two up if NBT-NS fails to bind — the failure is logged but does not abort the
session.

### 3. The agent must be on the same broadcast / multicast segment as the victims

Name-resolution poisoning is a Layer-2 game: LLMNR and mDNS rely on IPv4/IPv6 multicast,
NBT-NS on IPv4 subnet broadcast. The agent host has to be on the **same VLAN / subnet** as
the victims you want to poison. Routed pivots, VPN tunnels and similar Layer-3 transports
do not carry these queries, so an agent dropped onto a flat user VLAN works; an agent
sitting in a DMZ does not.

### 4. Conflicts with the host's own name-resolution stack

Whichever ports the host already has bound, the Spoofer cannot also bind. Common offenders:

- **Linux**: `systemd-resolved` listens on `5355/UDP` for LLMNR; Avahi listens on
  `5353/UDP` for mDNS. Stop or disable them on the agent host before starting the
  Spoofer (`systemctl stop systemd-resolved avahi-daemon`).
- **macOS**: `mDNSResponder` (Bonjour) owns `5353/UDP`. There is no clean way to share
  it with another listener; macOS is generally a poor agent host for the Spoofer.
- **Windows**: the **DNS Client** service handles LLMNR (5355) and the **TCP/IP NetBIOS
  Helper** (`lmhosts`) handles NBT-NS (137). Disable both services to free the ports.

If a port is held by the host, the corresponding listener will fail with
`Failed to start <PROTO> server!` and the Spoofer will continue with whatever it
*could* bind.

### 5. Set `localip` and `interface` explicitly

The `localip` parameter is what the spoofed answers will point victims at, and the
`interface` parameter is what the listeners bind to. Both default to `None` — meaning
"auto-detect" — which works on most native agents but is fragile when:

- The agent host has multiple interfaces / addresses.
- The agent is reached via a wsnet proxy (the auto-detected address may be the wsnet
  endpoint, not the address victims can actually reach).
- You explicitly want victims to authenticate to a different host than the one running
  the Spoofer (e.g. the host running your `RELAYSMB` server).

When in doubt, set both. `localip` is also the IP that `SELF` in the `spooftable` resolves
to.

---

## Parameters

All parameters are exposed in the session settings panel and can also be set with
`setparam <name> <value>` from the console.

### Normal parameters

#### `spoof`
Boolean. When `False` (default) the server runs in **analysis mode**: it observes and
logs every name-resolution query it sees but does not respond. Set to `True` to start
sending forged answers based on `spooftable`.

The `spoof` command toggles this on directly.

#### `spooftable`
A small DSL describing **which** queries to answer and **with what IP**. Format:

```
<match>,<respond_with>;<match>,<respond_with>;...
```

- Multiple entries are separated by `;`.
- Each entry has two comma-separated parts:
  - **`<match>`** — the queried hostname to react to. Use `*` to match every query.
    Matching is case-insensitive (uppercase for NBT-NS, lowercase for LLMNR / mDNS, per
    each protocol's own conventions).
  - **`<respond_with>`** — the IP to put in the answer. Use `SELF` to mean
    "whatever `localip` resolves to on the agent". Otherwise use a literal IPv4 or IPv6
    address.

Default: `*,SELF` — answer every query with the agent's local IP. The default is wide
on purpose; once you understand which hosts are interesting, narrow it down.

Examples:

```
*,SELF
fileserver,SELF
fileserver,SELF;wpad,10.0.0.5
*,10.10.10.10
contoso-dc,SELF;intranet,10.0.0.7
```

The `spooftarget <host> [<ip>]` command appends a single entry to the table without
having to retype the whole DSL.

#### `localip`
Local IP address to advertise in spoofed answers. Required when running through a wsnet
proxy or whenever the auto-detected source IP is wrong (see "Operational requirements
§5"). The literal `SELF` keyword in `spooftable` resolves to this address.

#### `interface`
Interface / source address to bind the UDP listeners to. Defaults to the wildcard bind
on most platforms. Set this on multi-homed hosts to constrain the Spoofer to a single
network.

### Advanced parameters

#### `proxy`
Proxy ID to route the server's outbound traffic through. The Spoofer is mostly inbound
(it listens for queries and replies on the same socket), so this is rarely useful for
the poisoner itself, but it is exposed for symmetry with the other server modules.

#### `resultsfile`
Optional file in OctoPwn's `/browserfs/volatile` directory where structured results can
be persisted. The console output is the primary record either way.

---

## Commands

The Spoofer inherits the standard server console (`start`, `stop`, `setparam`,
`getparam`, `params`, `info`, …) and adds two convenience commands:

#### `spoof`
Equivalent to `setparam spoof True`. Flips the running session into spoofing mode
without stopping it.

#### `spooftarget <host> [<ip>]`
Append a single entry to `spooftable` without retyping the whole DSL. `<ip>` defaults
to `SELF`. Useful workflow:

```
spooftarget fileserver01           # spooftable becomes "*,SELF;fileserver01,SELF"
spooftarget wpad 10.10.10.20       # ...; wpad,10.10.10.20
```

(Note: `spooftarget` *appends*; if you want to start clean, set `spooftable` directly
with `setparam`.)

---

## Typical workflow

A standard Responder-style engagement maps to two or three OctoPwn sessions:

1. **Start the Spoofer in analysis mode** (`spoof=False`, default `spooftable`).
   Every requester is auto-added to the project's Targets pane with source label
   `LLMNR` / `MDNS` / `NBTNS`. Watch the console for a few minutes — you will see
   workstations asking for misspelled file shares, autodiscover URLs, retired servers,
   fat-fingered hostnames, and so on. These are your candidates.

2. **Decide what to poison.** A blanket `*,SELF` works against a quiet network but
   tends to be noisy on a busy LAN — every laptop's `wpad`, `isatap` and Bonjour
   chatter will get an answer. For a controlled test, point `spooftable` at one or
   two specific names you saw in step 1.

3. **Start the auth-collection servers.** This is where Responder users have to break
   their muscle memory: the Spoofer itself will not catch a single NTLM hash. You need
   one or more of the relay servers running on the agent's IP:
   - [`RELAYSMB`](relaysmb.md) on `445/TCP` — for the SMB-bound queries that LLMNR /
     NBT-NS poisoning usually triggers.
   - [`RELAYLDAP`](relayldap.md) on `389/TCP` — for clients that resolve DCs through
     name resolution.
   - [`RELAYMSSQL`](relaymssql.md) on `1433/TCP` — for SQL Browser-misled clients.
   - [`RELAYESC8`](relayesc8.md) on `80/TCP` (or `443/TCP`) — for AD CS Web Enrollment
     relays.
   - [`RELAYNTLMREFLECTION`](relayreflection.md) — for the NTLM-reflection self-relay
     path.

4. **Flip the Spoofer to spoof mode** (`spoof True` or `setparam spoof True`).
   Victims now get steered onto the agent's IP, where the relay servers handle the
   resulting authentication and either store the captured credentials or relay them
   onwards.

5. **Iterate on `spooftable`** based on what shows up in the relay-server consoles.
   Use `spooftarget` to add interesting names without touching the whole table.

---

## Limitations & gotchas

- **Browser-only / pure WASM cannot spoof.** `get_localip` returns `None` under
  Emscripten and the per-protocol handlers refuse to send forged answers in that case.
  Run the spoofer through a wsnet agent or on the enterprise-mode server.
- **No IPv6-only victims.** All three handlers attempt IPv4 answers first; IPv6 is
  supported in the answer construction code but only when the resolved `localip` is
  itself an IPv6 address. In practice the Spoofer is IPv4-first.
- **No `wpad`-aware logic.** Unlike Responder, the Spoofer does not have a built-in
  list of "always-spoof / never-spoof" names — `*,SELF` will happily answer
  `wpad`, `isatap`, broadcast Bonjour discovery, the lot. Narrow `spooftable` if this
  is a concern.
- **No NTLM hash storage in this server.** Captured Net-NTLM hashes appear in the
  consoles of the **relay servers**, not here.
- **The `proxy` parameter does not tunnel multicast.** UDP multicast and broadcast do
  not survive most proxy implementations; `proxy` is useful for outbound TCP relay
  servers, less so here.
- **Conflicts with the host's name-resolution stack** are by far the most common
  failure mode (see Operational requirements §4). When a listener fails to start, only
  the unaffected listeners run — the session does not abort.
