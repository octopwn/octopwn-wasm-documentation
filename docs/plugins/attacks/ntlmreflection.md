# NTLMReflection Attack

The **NTLMReflection** attack module is OctoPwn's one-button orchestrator for the
end-to-end **CVE-2025-33073** exploit chain. It does, in a single attack session,
what would otherwise require five separate tools running in lockstep:

1. Pre-flight scans the candidate target list with the
   [`ntlmreflection` scanner](../scanners/ntlmreflection.md) and keeps only the
   hosts marked `VULNERABLE = yes` / `maybe`.
2. Adds the **`localhost1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAwbEAYBAAAA`**
   marshalled DNS record to the AD-integrated DNS zone via the
   [LDAP client](../clients/ldap.md)'s
   [`dnsadd`](../clients/ldap.md#dnsadd) — pointing it at the agent's
   `listenip`. (Uses CredMarshalTargetInfo encoding so the victim's SMB client
   treats the listener as a local-machine target and engages the
   `NTLMSSP_NEGOTIATE_LOCAL_CALL` flow.)
3. Spawns a [`RELAYNTLMREFLECTION`](../servers/relayreflection.md) server pinned to
   `listenip`.
4. Spawns a [`COERCER`](coercer.md) attack pointed at the marshalled DNS name as
   the listener — every coercion path the coercer knows about is fired against
   every vulnerable target.
5. The relay server completes the local-auth dance and returns a
   `NT AUTHORITY\SYSTEM` SMB session per coerced host, which is then
   auto-followed by `regdump` + `dpapi` post-auth modules (per the relay
   server's own behaviour).

In **continuous mode**, the attack also registers a global "new target added"
hook so that every target the operator drops into the project after the attack
started is automatically queued, scanned, and (if vulnerable) attacked — without
any further interaction.

For the *theory* behind why this works (CVE-2025-33073, marshalled DNS records,
`NTLMSSP_NEGOTIATE_LOCAL_CALL`, post-patch bypass via CVE-2026-24294, the
WebClient cross-protocol path, *etc.*), see the
[`RELAYNTLMREFLECTION` server page](../servers/relayreflection.md) — that's where
the protocol-level details live; this page documents the *attack-driver* that
wires it all together.

---

## How it works

The attack is structured around `NTLMReflectionAttackCore` in
`octopwn/common/attacks/ntlmreflection/`. A single run executes the following
batch (and re-runs it for each new target queue when continuous mode is on):

1. **Vulnerability scan.** A hidden
   [`NTLMREFLECTION` scanner](../scanners/ntlmreflection.md) session is spawned
   and pointed at the queued targets. It probes each host's SMB build / patch
   level and records `VULNERABLE = yes` / `maybe` / `no`. Only `yes` and
   `maybe` hosts proceed.

   ??? note "Why pre-scan?"
       The CVE-2025-33073 condition is *not* "any unsigned SMB target". The
       relevant code path was patched in May 2025 and the bypass
       (CVE-2026-24294) only works against specific patch ranges. Firing the
       chain blindly against patched hosts wastes operator time and lights up
       the target's security telemetry. The scanner does the cheap version
       check up front so the loud part only happens against viable targets.

2. **DNS record add.** The attack's hidden LDAP client session connects to
   `dctarget` and calls `dnsadd` with:
    - `target = localhost1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAwbEAYBAAAA`
      (the marshalled DNS record — `localhost` + the
      [`CredMarshalTargetInfo`](https://learn.microsoft.com/en-us/windows/win32/api/wincred/nf-wincred-credmarshalcredentialw)
      blob that flips the `NTLMSSP_NEGOTIATE_LOCAL_CALL` bit on the SMB client).
    - `ip = listenip` (where the agent's relay server is listening).
   OctoPwn tries every combination of `(forest=False/True, legacy=False/True)`
   until one succeeds — DNS write semantics differ across forests / legacy
   zones.

   !!! warning "DNS propagation delay"
       The code currently has its propagation `asyncio.sleep` commented out, but
       AD-integrated DNS records can take up to two minutes to be served by all
       DCs. If the coercion immediately following this step fails with name
       resolution errors, wait a minute and re-run the attack — the DNS record
       persists across runs.

3. **Relay server start.** A hidden
   [`RELAYNTLMREFLECTION`](../servers/relayreflection.md) server is created and
   `do_serve()` is called. The relay listens for inbound SMB connections, accepts
   the `NTLMSSP_NEGOTIATE_LOCAL_CALL` handshake, completes the reflection and
   issues the post-auth modules (regdump / dpapi) as `SYSTEM` against the
   originating host.

4. **Coercion.** A hidden [`COERCER`](coercer.md) attack is spawned. Its
   `listenip` is set to the **marshalled DNS name** (not the IP) — so victims
   resolve the name via the AD DNS we just poisoned, get back the agent's IP,
   then build SMB sessions whose target name is the marshalled string. That
   string is what triggers the local-call NTLM handshake on the victim. Every
   coercion vector COERCER knows (PetitPotam / EFSRPC, DFSCoerce, ShadowCoerce,
   PrinterBug, …) is fired against every vulnerable target.

5. **Wait and clean up.** The coercion phase has a 120-second hard timeout. When
   it finishes (or times out), the relay server is stopped and the batch is
   complete. In continuous mode the loop re-arms; otherwise the attack session
   exits.

---

## Continuous mode (the killer feature)

With `continousattack = True`, the attack registers a global target-added hook on
the project. From then on:

- Any target added to the project (manually, via a scanner like
  [`portscan`](../scanners/portscan.md), via [`smbfinger`](../scanners/smbfinger.md),
  *etc.*) is queued.
- After a 10-second debounce (lets a burst of additions accumulate), the queued
  targets are re-scanned for vulnerability and a new batch fires.
- The DNS record and relay server are kept across batches — no re-setup cost.
- The attack runs until you stop the session.

This turns the attack into a **passive-interception trap**: leave it running
during a wider scan, and any newly-discovered, vulnerable host gets owned for
free as it shows up in the project.

---

## Prerequisites

- A **valid domain credential** — used both for the LDAP `dnsadd` and as the
  authenticated identity that drives the COERCER. **Any** authenticated user
  account is enough; `Authenticated Users` can write DNS records by default.
- A **Domain Controller target** (`dctarget`) reachable via LDAP / LDAPS.
- A **listenip** that:
    - is bindable on the agent host on `445/TCP`,
    - is reachable from every target that will be coerced,
    - and resolves correctly when DNS hands out the marshalled name (so —
      same broadcast domain, or routable from the targets, *no NAT in between*
      unless you have explicit forwarding).
- **At least one CVE-2025-33073-vulnerable host** in the target set. The
  [`ntlmreflection` scanner](../scanners/ntlmreflection.md) tells you which
  builds qualify.
- **WSNET agent** running with sufficient privileges to bind `445/TCP` on the
  listening interface (which usually means: not a Windows host where the SMB
  driver is already bound).

---

## Parameters

### Normal parameters

#### `dctarget`
Target ID of the Domain Controller used for LDAP `dnsadd`. Required.

#### `credential`
Credential ID for the LDAP bind and as the authenticated identity for COERCER.

#### `listenip`
IP address the agent will bind the relay server to and which the marshalled DNS
record will resolve to. Required.

#### `attacktargets`
Comma-separated list of target IDs / IPs / hostnames to attack. Required when
`continousattack = False`; optional when continuous mode is on (it can be empty
and the attack will only fire on newly-added targets).

#### `continousattack`
Default: `False`. When `True`, the attack stays alive after the first batch
finishes and keeps a target-added hook on the project so that any new target
becomes a candidate.

#### `protocol`
Default: `LDAP`. Currently has no effect on the attack flow — kept for forward
compatibility. Leave at default.

### Advanced parameters

The standard `ScannerBaseParameters` set: `maxruntime`, `resultsfile`,
`showerrors`, `timeout`, `workercount`, `wsnetreuse`. See the
[scanner parameters reference](../scanners/baseline.md). Defaults are fine.

---

## Output

You see three things in flight:

1. The **vulnerability scan progress** — which hosts were probed and which were
   marked vulnerable.
2. The **relay server's session log** (the same output you'd get from running
   [`RELAYNTLMREFLECTION`](../servers/relayreflection.md) standalone) — every
   incoming local-call NTLM handshake, every successful relay, every post-auth
   `regdump` / `dpapi` result.
3. **New SMB sessions** appearing in the Sessions Window for each successfully
   relayed host. These are full local-admin (in fact, `SYSTEM` over SMB)
   sessions you can use immediately with the [SMB client](../clients/smb.md) for
   `cmdexec`, `psexec`, *etc.*

---

## Limitations and caveats

- **SMB signing on the victim breaks everything.** This is the core mitigation
  for CVE-2025-33073 and every variant. If `SIGNING_REQUIRED = True` shows up in
  the [`smbsig`](../scanners/smbsig.md) results for a host, this attack will
  not work against it.
- **The DNS record is persistent.** It stays in the zone after the attack ends.
  Either remove it manually via the
  [LDAP client](../clients/ldap.md)'s `dnsdel`, or accept that it sits in the
  AD DNS zone as a forensic artifact pointing at your old `listenip`.
- **The attack does not enable any guardrails.** If you point it at production
  with continuous mode on, every new target you scan will be coerced. Treat it
  like a live exploit.
- **Coercion is not silent.** The COERCER step generates noisy authentication
  logs (4624 / 4625 with the marshalled name as the target) on every host it
  hits. Mature SOCs will pick this up — this is a fast attack, not a stealthy
  one.
- **Single-listener architecture.** The relay server binds one IP / port. You
  can't fan out across multiple `listenip`s from a single attack session — run
  multiple `NTLMREFLECTION` attack sessions if you need to cover multiple
  network segments.

---

## See also

- [`RELAYNTLMREFLECTION` server](../servers/relayreflection.md) — the relay
  server underneath the hood. The protocol-level theory of CVE-2025-33073 (and
  the post-patch bypass CVE-2026-24294) lives there.
- [`ntlmreflection` scanner](../scanners/ntlmreflection.md) — the pre-flight
  vulnerability check used internally by this attack.
- [`COERCER`](coercer.md) — the coercion driver fired internally; see its page
  for the list of supported coercion vectors.
- [`smbsig` scanner](../scanners/smbsig.md) — to understand which hosts in your
  target list are signing-required (and therefore immune to this attack).
- [Synacktiv: NTLM reflection is dead, long live NTLM reflection](https://www.synacktiv.com/en/publications/ntlm-reflection-is-dead-long-live-ntlm-reflection-an-in-depth-analysis-of-cve-2025) — the canonical reference.
