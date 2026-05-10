# RelayLDAP Server

The **RelayLDAP** server is the NTLM relay variant aimed at **LDAP / LDAPS / StartTLS**
back-ends. Inbound NTLM authentications are forwarded into a fresh `MSLDAPClientConnection`
against one of the configured `targets`, and on success the relayed connection is wrapped
into a real interactive **LDAP client session** in the project — already bound and ready
to issue queries, modify ACLs, write `msDS-AllowedToActOnBehalfOfOtherIdentity`, enroll
certificates, and so on.

| Inbound listener (front)                     | Outbound target (back)                         |
| -------------------------------------------- | ---------------------------------------------- |
| `smb`, `http`, `https`, `httpproxy`, `mssql` | LDAP / LDAPS / StartTLS on `targets`           |

The listener side is **shared** with the rest of the relay family — see the
**"Listener-side parameters (shared)"** section in [`RELAYSMB`](relaysmb.md#listener-side-parameters-shared)
for the full reference. This page documents only the LDAP-specific parameters and
behaviour, plus the constraints that matter for LDAP relaying specifically.

---

## Why LDAP relaying is special

Among the relay variants, LDAP is the one with the most fragile cross-protocol matrix and
the highest payoff. A successful LDAP relay against a Domain Controller hands you a bound
LDAP session as the relayed account — and from there you can perform virtually every
ACL-based AD attack:

- Add yourself / your computer to a privileged group.
- Set `msDS-AllowedToActOnBehalfOfOtherIdentity` on a target computer
  (RBCD → S4U2self → S4U2proxy).
- Enroll a certificate (Shadow Credentials via `msDS-KeyCredentialLink`, or push a
  certificate into a user object via the LDAP client's certify flows).
- Disable account flags, change `userAccountControl`, push GPO links, etc.

…provided two things hold on the DC:

1. **LDAP signing is *not* enforced.** Microsoft hardened this on most modern DCs. If
   `msldap.connection` reports a signing/integrity error during bind, the DC rejects
   unsigned LDAP and the relay is dead in the water.
2. **For LDAPS, channel binding is *not* enforced.** Channel-binding tokens (EPA) bind
   the NTLM MIC to the TLS exterior; an attacker MitM that replaces the TLS endpoint
   cannot reproduce it. Modern DCs default this on; older / unpatched ones do not.

Pre-flight with [`ldapsig`](../scanners/ldapsig.md) to detect signing-enforcement
posture before relying on a target.

!!! warning "Cross-protocol relay rules"
    Because OctoPwn's LDAP relay uses NTLM in **SICILY** mode (the legacy "raw NTLM
    bind" protocol that LDAP exposes alongside SASL), it bypasses some of SPNEGO's
    cross-protocol restrictions. In practice the most reliable inbound path is **HTTP**
    (or HTTPS / HTTP-proxy) — coerced via WebDAV. SMB-in → LDAP-out is blocked by the
    NTLM MIC + channel-binding values that modern Windows clients add to SMB-bound
    NTLM blobs. **Run with `servertypes=http,https,httpproxy`** for LDAP relaying
    unless you have a specific reason to keep SMB on.

---

## Operational requirements

The same requirements as the rest of the relay family apply — see
[`RELAYSMB` Operational requirements](relaysmb.md#operational-requirements). Two
LDAP-specific considerations:

- **You don't need the SMB listener.** Disable it (`servertypes=http,https,httpproxy`)
  so port `445` on the agent doesn't conflict with anything *and* you don't waste relays
  on traffic that won't translate to LDAP.
- **DC reachability.** The agent must reach `389/TCP` (or `636/TCP` for LDAPS) on the
  Domain Controllers in `targets`. If the agent is behind a wsnet proxy, set
  `connectproxy` so the outbound LDAP connection routes through it as well.

---

## Relay-specific parameters

These are the parameters unique to **`RELAYLDAP`**. See
[`RELAYSMB`](relaysmb.md#listener-side-parameters-shared) for the listener-side parameters
shared by every relay variant.

### Normal parameters

#### `targets`
Comma-separated list of LDAP servers (DC FQDNs / IPs) to relay to. **Required.** Walked
round-robin: each new captured authentication is sent to the next entry.

#### `ldapprotocol`
Default: `LDAP`. One of:

| Value      | Outbound transport             | Outbound port   |
| ---------- | ------------------------------ | --------------- |
| `LDAP`     | Plain LDAP                      | `389/TCP`       |
| `LDAPS`    | LDAP over TLS                   | `636/TCP`       |
| `STARTTLS` | Plain LDAP upgraded with StartTLS | `389/TCP`     |

The relay performs the bind in **SICILY** (raw NTLM) mode regardless of protocol; the
choice only changes the transport that wraps it. `STARTTLS` is the most common modern
path: many DCs require *integrity*, and StartTLS satisfies that requirement without
forcing the relay through `636`.

### Advanced parameters

#### `connectproxy`
Proxy ID for the **outbound** LDAP connection. Independent from `serverproxy`. On WASM
this is auto-set to `0` if unset.

---

## Commands

The standard `ScannerConsoleBase` command set applies (`setparam`, `getparam`, `params`,
`info`, `serve`, `stop`, `historylist`, …):

#### `serve`
Bring up the configured listeners and the relay-handler task. Each captured authentication
is shuttled into `handle_ldap_relay`, which opens an outbound LDAP connection per target
and (on success) spawns a fresh interactive LDAP client session.

#### `stop`
Stop all listener tasks and the relay-handler task. Interactive LDAP sessions spawned by
previous successful relays are **not** closed.

---

## Typical workflow

1. **Identify LDAP-signing-permissive DCs.** Run [`ldapsig`](../scanners/ldapsig.md)
   against all DCs in scope. Anything that reports signing as *not enforced* is a
   candidate.
2. **Start `RELAYLDAP`** with `targets=<filtered DC list>`,
   `ldapprotocol=STARTTLS`, and `servertypes=http,https,httpproxy`. Leave the SMB
   listener off — it just creates noise that won't translate.
3. **Coerce HTTP-bound authentications.** WebDAV is the canonical path: from an
   [SMB client](../clients/smb.md) session, run `coerce` and point the target at the
   agent IP using a WebDAV-style UNC (`\\agent@80\share\file`). Browser-pop pop-ups,
   AutoDiscover, and ADCS Web Enrollment paths also fit.
4. **Watch the relay console.** A successful relay prints `LDAP connection OK!` (with
   `debug=True`) and a new session ID. Switch to that session — you have a bound LDAP
   client on the relayed DC, ready for ACL writes, RBCD, Shadow Credentials, etc.
5. **Drive the post-bind attack from the spawned LDAP session.** See the
   [LDAP client documentation](../clients/ldap.md) for the available LDAP commands —
   `addgroupmember`, `setrbcd`, `addshadowcred`, `cve202233679`, certificate enrollment
   via the Certify subsystem, etc.

---

## Limitations & gotchas

- **LDAP-signing-enforced DCs reject the bind.** With `debug=True` you will see the
  bind error in the server console. Pre-filter with [`ldapsig`](../scanners/ldapsig.md).
- **LDAPS with channel-binding (EPA) enforced** breaks the `LDAPS` path. Use
  `STARTTLS` first if you have a choice — many older DCs require integrity but not
  EPA, and StartTLS satisfies the former without triggering the latter.
- **SMB-in → LDAP-out is generally blocked.** The MIC and channel-binding values
  Windows attaches to SMB-bound NTLM defeat the relay. Disable the SMB listener for
  LDAP relays.
- **Round-robin target rotation** means a single inbound auth is relayed to one
  target, not all of them. To hit every DC you need many inbound auths.
- **No automatic post-bind action.** Unlike `RELAYSMB` (which auto-runs `regdump` /
  `dpapisecrets`) and `RELAYESC8` (which produces a PFX), `RELAYLDAP` simply spawns
  an interactive session — what to do next is up to you. Plan the LDAP commands
  before starting the relay so you can act fast on a successful bind.
