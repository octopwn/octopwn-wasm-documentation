# RelaySMB Server

The **RelaySMB** server is OctoPwn's NTLM relay variant aimed at **SMB targets**. It runs a
set of front-end listeners (SMB, HTTP, HTTPS, HTTP-proxy by default), waits for an inbound
NTLM authentication, and on success forwards the in-flight NTLM exchange into a fresh SMB
connection against one of the configured targets. Every successful relay spawns a real
interactive **SMB2 client session** in the project — already authenticated, already attached
to the new target — and (by default) immediately runs registry and DPAPI secrets dumps
against the relayed host.

| Inbound listener (front)                     | Outbound target (back) |
| -------------------------------------------- | ---------------------- |
| `smb`, `http`, `https`, `httpproxy`, `mssql` | SMB on `targets`       |

The listener side is **shared** with the rest of the relay family
([`RELAYLDAP`](relayldap.md), [`RELAYMSSQL`](relaymssql.md),
[`RELAYESC8`](relayesc8.md), [`RELAYNTLMREFLECTION`](relayreflection.md)) — the only thing
that changes between variants is what gets done with the relayed authentication on the
back-end. The full description of the listener-side parameters lives at the bottom of this
page; the sibling pages link back here for the deep dive.

---

## How it works

1. Bring up one or more listeners (SMB / HTTP / HTTPS / HTTP-proxy / MSSQL) on the agent host.
2. A victim authenticates to one of those listeners — typically because they were coerced
   (PrinterBug, MS-EFSRPC, WebDAV, etc.) or because their name resolution was poisoned
   by the [Spoofer server](spoofer.md).
3. The incoming NTLM challenge / response is **not validated locally**; it is shuttled into
   a fresh outbound SMB connection (`aiosmb.SMBConnection`) opened against the next target
   in `targets`. Targets are walked round-robin (`itertools.cycle`).
4. On the outbound side OctoPwn forces `nosign=True`, so the relay only succeeds against
   targets where SMB signing is **not enforced**.
5. The captured Net-NTLM hash is added to the project's **Credentials Hub** with
   `source = RELAYED`, deduplicated against existing entries.
6. A `SHARE_ENUM_ALL` is issued as a *liveness check* — if listing shares works, the relay
   is considered successful.
7. A new **SMB2 client session** is created with `description = RELAYED`, attached to the
   relayed connection via `setup_relay()`. This session behaves like any other interactive
   SMB client — you get a fully featured SMB console, file browser, registry dumper, etc.
8. **Auto-loot** (default ON for both): `regdump` triggers `regdump2` against the relayed
   host (SAM / LSA / DCC / cached secrets), and `dpapisecrets` triggers
   `dpapisecretsremoteregdump` (DPAPI master keys harvested through the remote registry
   path). If the relayed account is a local administrator on the target, you walk away
   with offline-crackable secrets without a single extra command.

!!! warning "SMB-to-SMB only works when signing is *not* enforced"
    NTLM relay against SMB has the same fundamental constraint as ntlmrelayx: if the target
    SMB server enforces signing, the relayed session is dropped during negotiation and you
    will see `list_shares` fail in the relay-server console. Run [`smbsig`](../scanners/smbsig.md)
    against your target list first to filter out enforced hosts.

!!! warning "Cross-protocol relay is restricted"
    NTLMv2 with the **MIC** present (modern Windows clients without CVE-2019-1040) cannot
    be cross-protocol-relayed: SMB-in → SMB-out works, HTTP-in → SMB-out works for many
    HTTP coercion paths but fails when the client adds a target binding. If a relay is
    silently rejected at the auth-handshake stage, enable `debug` on the server and watch
    for `ntlm_data` warnings.

---

## Operational requirements

The relay listeners run **inside the OctoPwn agent**, not in the browser. That means the
agent host has to satisfy a handful of constraints, and most "the server starts but no
authentication ever lands" tickets boil down to one of these.

### 1. Privileged ports

Out of the box the listeners use:

| Listener   | Default port | Privileged?              |
| ---------- | ------------ | ------------------------ |
| SMB        | `445/TCP`    | **Yes** (port < 1024)    |
| HTTP       | `80/TCP`     | **Yes**                  |
| HTTPS      | `443/TCP`    | **Yes**                  |
| HTTP-proxy | `8080/TCP`   | No                       |
| MSSQL      | `1433/TCP`   | No                       |

To bind any of the privileged ports the agent must be running as `root`/Administrator, or
on Linux the Python interpreter must hold `CAP_NET_BIND_SERVICE`
(`setcap cap_net_bind_service=+ep <python-interpreter>`).

You can move them to high ports with `smbserverport` / `httpserverport` / `httpsserverport`
(see "Listener-side parameters" below) — but moving the SMB port off `445` only works for
coercion paths that let you specify an explicit port (e.g. WebDAV via
`\\host@8080\share\...`). PrinterBug and similar protocols always come back to `445`.

### 2. Conflicts with native services

Whichever ports the host already has bound, the relay cannot also bind:

- **Windows**: the **Server** service owns `445`. Disabling it is intrusive and not always
  reversible without a reboot. In practice, **the SMB listener is impractical on a Windows
  agent** — use a Linux agent for relay work.
- **Linux**: Samba's `smbd` if installed; `apache`/`nginx`/`lighttpd` if a web server is
  running. Stop them before starting the relay.
- **macOS**: `smbd` (`/usr/sbin/smbd`), Apple's web stack, etc. Generally a poor agent
  host for relays.

When a listener fails to bind, the rest still come up — the relay session does not abort.
Watch the server console output at startup for `... server failed to start! Reason: ...`.

### 3. WASM / browser-only deployments

A pure-browser deployment with no native bridge cannot host these listeners — sockets are
not available. In WASM mode, the agent (wsnet) is doing the binding on its own host; the
project just steers it through the wsnet proxy. When `platform.system() == 'Emscripten'`
and `connectproxy` is unset, OctoPwn auto-fills it with proxy `0` so the outbound SMB
connection on the back-end also goes through the same agent.

### 4. The agent IP must be reachable from the victims

Whatever address the victims use to reach the relay (the IP they were coerced or poisoned
to) must be reachable on the right port. If you're behind NAT or a wsnet proxy, set
`serverproxy` / `connectproxy` to route both halves of the connection through the right
agent.

---

## Relay-specific parameters

These are the parameters unique to **`RELAYSMB`**. The full list of the shared
listener-side parameters (`servertypes`, `serverip`, `*serverport`, `serverproxy`,
`debug`, `ntlmallowguest`, `ntlmreflection`) is at the bottom of this page.

### Normal parameters

#### `targets`
Comma-separated list of SMB targets to relay to. Hostnames or IP addresses. **Required.**
The list is walked round-robin: each new inbound auth is sent to the next entry.

#### `regdump`
Default: `True`. After a successful relay, automatically run `regdump2` against the
relayed host. This dumps `SAM`, `LSA`, cached domain credentials and the machine account
secrets via the remote registry — same as
`secretsdump.py -just-dc-user '*' <host>` would on Linux, but using the relayed session
instead of a credential.

Set this to `False` if you only want the relayed shell and want to dump manually later
(e.g. you are worried about EDR noise or want the connection idle for further use).

#### `dpapisecrets`
Default: `True`. After a successful relay, automatically run
`dpapisecretsremoteregdump` against the relayed host — extract DPAPI master keys via the
remote registry path. Combined with `regdump`, this is what gives you offline-crackable
DPAPI loot from a single relayed admin auth.

### Advanced parameters

#### `connectproxy`
Proxy ID to use for the **outbound** SMB connection to `targets`. This is independent of
`serverproxy` (which is the listener-side proxy). On WASM this is auto-set to `0` if
unset, so the outbound traffic also goes through the wsnet agent.

---

## Listener-side parameters (shared)

Every relay variant shares this set of listener parameters. They configure **what the
agent listens on**, not what it relays to.

### Normal parameters

#### `servertypes`
List of front-end listeners to start. Default: `smb,http,https,httpproxy`. Valid entries:

| Value       | Listener                  | Default port   |
| ----------- | ------------------------- | -------------- |
| `smb`       | NTLM-relaying SMB server  | `445/TCP`      |
| `http`      | NTLM-relaying HTTP server | `80/TCP`       |
| `https`     | NTLM-relaying HTTPS server (snake-oil cert) | `443/TCP` |
| `httpproxy` | NTLM-relaying HTTP proxy  | `8080/TCP`     |
| `mssql`     | NTLM-relaying TDS server  | `1433/TCP`     |

For SMB targeting, `smb` is essential and `http` / `https` are useful (PrinterBug,
WebDAV-coercion, browser-pop pop-ups, AutoDiscover, etc.). `httpproxy` matters if you
plan to advertise the agent via WPAD; `mssql` is irrelevant here and can be turned off
to avoid the port conflict if SQL Server runs on the agent host.

#### `serverip`
IP address to bind the listeners to. Default `0.0.0.0` (all interfaces). Set this to the
agent's actual interface IP if you have multiple NICs and want to avoid binding on the
wrong one.

### Advanced parameters

#### `smbserverport` / `httpserverport` / `httpsserverport` / `httpproxyserverport` / `mssqlserverport`
Listening ports for each front-end protocol. Defaults: `445`, `80`, `443`, `8080`, `1433`.
Useful when the standard port is already taken, or when you intentionally want to use a
high port from a coercion path that supports it (e.g. `\\host@8080\...` for WebDAV).

#### `serverproxy`
Proxy ID for the **listener** side. Tells the wsnet agent where to expose the listening
sockets — typically the same agent that the project is connected through. On WASM this
is auto-set to `0` if unset.

#### `ntlmallowguest`
Default: `True`. Allow inbound clients that authenticate as Guest. Most Windows hosts
silently fall back to Guest when the supplied credential is wrong; relaying a Guest
session is rarely useful but the credential is stored for visibility. Set to `False`
to hard-drop those.

#### `ntlmreflection`
Default: `False`. Allow the NTLM relay engine to accept relays where the auth target is
the **same machine** that initiated the connection (NTLM reflection). This is what
`RELAYNTLMREFLECTION` enables under the hood; on `RELAYSMB`, leaving it `False` matches
the historical safe default.

#### `debug`
Default: `False`. Enable verbose tracebacks and per-connection logging on the server
console. Indispensable when relays are silently rejected — turn this on first before
opening a support thread.

---

## Commands

The standard `ScannerConsoleBase` commands apply (`setparam`, `getparam`, `params`,
`info`, `serve`, `stop`, `historylist`, …). The relay-specific entry point is:

#### `serve`
Start the listeners with the configured parameters. Equivalent to clicking **Start** on
the session window. Internally calls `do_serve` and creates one `asyncio` task per
listener plus one task that drains the auth-relay queue and calls `handle_smb_relay`
for each captured authentication.

#### `stop`
Stop all listener tasks and the relay-handler task. The interactive client sessions
spawned by previous successful relays are **not** closed — they remain available in the
project as normal SMB2 sessions you can keep using.

---

## Typical workflow

1. **Pick the agent host carefully.** Linux, ports `80/443/445/8080` free, and same VLAN
   as your victims (or directly reachable from the coercion source).
2. **Filter the target list.** Run [`smbsig`](../scanners/smbsig.md) against your
   intended `targets` and keep only the hosts where signing is *not enforced*.
3. **Start `RELAYSMB`** with `targets=<filtered list>`. Leave `regdump=True` and
   `dpapisecrets=True` if you want auto-loot; set them to `False` if you want quiet
   relays for follow-up commands.
4. **Drive authentication into the listener.** Three common ways:
   - Run [`Spoofer`](spoofer.md) in spoof mode in a separate session — LLMNR / mDNS /
     NBT-NS poisoning will steer mistyped names to the agent.
   - Coerce a specific target with `coerce` from an [SMB client](../clients/smb.md)
     session (PrinterBug, MS-EFSRPC, MS-DFSNM, …).
   - Coerce via a malicious file path (`\\agent\share\file.lnk` in an emailed
     document, an `img` element pointing at the agent, etc.).
5. **Watch the relay console.** A successful relay prints `SMB relay worked!` and a new
   session ID. Switch to that session — you have a live SMB2 client on the relayed host.
6. **Iterate.** Adjust `targets` or restart with new ones; previous interactive sessions
   stay open.

---

## Limitations & gotchas

- **Signing-enforced targets are silently rejected.** The first sign is `list_shares`
  failing in `debug` mode. Pre-filter with [`smbsig`](../scanners/smbsig.md).
- **NTLMv2 + MIC + channel binding** on modern, patched clients defeats most
  cross-protocol paths. SMB-in → SMB-out is fine; HTTP-in → SMB-out is fragile.
- **`nosign=True`** is hard-coded on the outbound side. There is no way to negotiate
  signing on the relayed connection — the assumption is "signing is off".
- **Guest auth** is allowed by default and floods the credential database with
  `Guest::DOMAIN:...:fullhash`. Set `ntlmallowguest=False` for a tidier project.
- **The auto-loot pair (`regdump` + `dpapisecrets`) is loud** — full registry hive
  parsing and DPAPI master key extraction are visible to any half-decent EDR. Disable
  both for stealthier engagements.
- **Targets are walked round-robin.** A single victim authentication relays to **one**
  target, not all of them. To hit every target you need either many victim
  authentications or a poisoning loop that keeps generating them.
- **Listeners that fail to bind do not abort the session.** Always re-read the server
  console at startup to confirm which listeners actually came up.
