# Coercer Attack

The **Coercer** attack module is OctoPwn's multi-vector authentication-coercion
driver. Given a domain credential and one or more targets, it cycles through
**every known SMB-side coercion RPC** — PetitPotam (EFSRPC), PrinterBug (RPRN),
ShadowCoerce (FSRVP), DFSCoerce (DFSNM), Event Log (EVEN) — and tries to make the
target's `SYSTEM` account authenticate to a listener you choose.

It is the primary partner of the relay servers ([`RELAYSMB`](../servers/relaysmb.md),
[`RELAYLDAP`](../servers/relayldap.md), [`RELAYNTLMREFLECTION`](../servers/relayreflection.md))
and of the [`SPOOFER`](../servers/spoofer.md) module: spin up a listener, point
the coercer at a target, and the relay / spoofer captures the inbound NTLM
exchange.

| Vector | Group code  | RPC interface       | What it does                                                                              |
| ------ | ----------- | ------------------- | ----------------------------------------------------------------------------------------- |
| PetitPotam / EFSRPC  | `EFSR`     | `\PIPE\efsrpc` / `\PIPE\lsarpc` | Several `EfsRpc*` functions that take a UNC path → target authenticates to it.   |
| PrinterBug           | `RPRN`     | `\PIPE\spoolss`     | `RpcRemoteFindFirstPrinterChangeNotification[Ex]` (MS-RPRN spooler bug).                 |
| ShadowCoerce         | `FSRVP`    | `\PIPE\FssagentRpc` | `IsPathShadowCopied` / `IsPathSupported` (volume-shadow service).                        |
| DFSCoerce            | `DFSNM`    | `\PIPE\netdfs`      | `NetrDfsRemoveStdRoot` (DFS namespace management).                                       |
| EventLog (ELFR)      | `EVEN`     | `\PIPE\eventlog`    | `ElfrOpenBELW` — open backup event log over UNC path.                                    |

Within each group OctoPwn fires *all* the supported sub-functions, not just one
representative — so e.g. enabling `EFSR` actually exercises 9 different
`EfsRpc*` calls, any of which may succeed even if the others are patched.

---

## How it works

1. **SMB connect + login** with the supplied `credential` against the next
   target. **Authentication is required** — Coercer is a post-auth primitive
   (the target needs to authorize the underlying RPC bind first). Use the
   lowest-privilege account that gets a successful bind on the relevant pipe;
   the actual coercion functions usually accept any authenticated caller.
2. **Build the listener URL set** for `listenip`. By default the coercion
   library generates one URL per supported transport — `\\<listenip>\share` for
   SMB-flavoured paths, `http://<listenip>/coerce` for HTTP-flavoured paths,
   *etc.*
3. **For each protocol group in `protocols`**, run every sub-function of that
   group with each generated listener URL. Between successive coercion calls,
   wait `delay` milliseconds.
4. **Stop on first success per target by default**, unless `continueonsuccess`
   is `True`. "Success" here means the RPC returned an indication that the
   target *acted on* the UNC path — the actual NTLM authentication is then
   captured by your listener (relay server / spoofer / Responder), not by
   Coercer itself.

Coercer **does not own a listener**. It only triggers the auth — you must have
something else listening on `listenip`. The most common setups are:

- Coercer + [`RELAYSMB`](../servers/relaysmb.md) → SMB → relayed to another SMB
  target.
- Coercer + [`RELAYLDAP`](../servers/relayldap.md) → SMB → relayed to LDAP for
  ACL writes.
- Coercer + [`RELAYNTLMREFLECTION`](../servers/relayreflection.md) → SMB → CVE-2025-33073
  reflection back to the originating host.
- Coercer + [`SPOOFER`](../servers/spoofer.md) — to capture the NTLMv2 hash
  offline (instead of relaying).
- Coercer + Responder / Inveigh on a separate Linux box, when you want the
  capture to live outside OctoPwn.

When using marshalled DNS records (CVE-2025-33073), pass the marshalled name
*as the listener URL* — see the
[`NTLMREFLECTION` attack page](ntlmreflection.md) for the full chain that
automates this.

---

## When to choose which protocol group

The default `['EFSR','RPRN','FSRVP','EVEN','DFSNM']` covers everything. In real
operations, narrow it down:

- **`EFSR`** — most universal. Patched in stages over many years (PetitPotam
  patches), but new EfsRpc sub-functions keep being found. Often the only
  thing that works on fully patched 2022/2025 hosts.
- **`RPRN`** — only works when the **Print Spooler service is running**. On
  modern domain-joined workstations that's still the default; on hardened
  servers (especially DCs after the spooler was disabled per Microsoft's
  advisory) it's gone. Cheap to try.
- **`FSRVP`** — requires the **Volume Shadow Copy** service running. Often
  only enabled on file servers / backup hosts.
- **`DFSNM`** — only works on **DFS namespace servers** (typically DCs in
  most Windows domains). Very useful against DCs.
- **`EVEN`** — Event Log RPC; less commonly patched, less commonly disabled,
  but slightly slower path. Worth keeping.

---

## Prerequisites

- A **valid domain credential** that can bind the relevant RPC pipe. Most
  vectors accept any authenticated user; some (DFSNM in particular) want
  rights on the DFS namespace object — which any domain user has on default
  Microsoft DCs.
- **Outbound `445/TCP`** from the agent to every target (for the SMB binds
  used to deliver the coercion).
- **Inbound traffic from the target to your listener** — `445/TCP`,
  `80/TCP` and/or `139/TCP` depending on the listener type. If the target
  cannot reach you, no auth gets captured even if Coercer reports the RPC
  call succeeded.
- A **listener** running on `listenip` (relay server / spoofer / external
  capture tool).

---

## Parameters

### Normal parameters

#### `credential`
Credential ID for SMB authentication against the targets. Any low-privilege
domain user normally suffices.

#### `targets`
List of targets. Standard list / CIDR / file / `all` syntax.

#### `listenip`
The address the target should authenticate **to**. This is what gets baked
into the coerced UNC paths / HTTP URLs. Three flavours:

- **An IP address** (`192.168.56.42`) — simplest, target authenticates
  directly to that IP.
- **A hostname** that resolves on the target — useful when targets cannot
  see the agent IP directly but a NetBIOS / LLMNR / DNS poisoner can resolve
  the name to your listener (pair with [`SPOOFER`](../servers/spoofer.md) for
  an end-to-end OctoPwn chain).
- **A marshalled DNS name** (e.g.
  `localhost1UWhRCAAAAAAAAAAAAAAAAAAAAAAAAAAAAwbEAYBAAAA`) — the CVE-2025-33073
  trick. Used by [`NTLMREFLECTION`](ntlmreflection.md) automatically; you can
  use it manually here as well by setting it as `listenip` after pre-creating
  the matching DNS record with [`dnsadd`](../clients/ldap.md#dnsadd).

#### `protocols`
Default: `['EFSR','RPRN','FSRVP','EVEN','DFSNM']` (all). Empty list also means
"all". Narrow down per the table above.

#### `delay`
Default: `100`. Milliseconds between successive coercion attempts. Raise this
on rate-limited / monitored hosts; lower for fast smoke tests.

#### `continueonsuccess`
Default: `False`. When `True`, Coercer keeps firing every remaining vector
even after one succeeded against a given target — useful when you want to
see *all* the paths that work (research / reporting use case), not just
the first one.

### Advanced parameters

The standard credentialled-SMB scanner parameter set: `authtype`, `dialect`,
`krbetypes`, `krbrealm`, `maxruntime`, `proxy`, `resultsfile`, `showerrors`,
`timeout`, `workercount`, `wsnetreuse`. See
[SMB client → authentication](../clients/smb.md#authentication) for the
auth-related ones.

---

## Typical workflows

### 1. Pure capture (offline cracking)

1. Start [`SPOOFER`](../servers/spoofer.md) on `listenip` to capture NTLMv2.
2. Run Coercer with `listenip = <agent IP>` against your target list.
3. NTLMv2 hashes show up in the Credentials Hub — crack offline.

### 2. Cross-protocol relay (most common)

1. Start [`RELAYLDAP`](../servers/relayldap.md) (or
   [`RELAYSMB`](../servers/relaysmb.md), [`RELAYMSSQL`](../servers/relaymssql.md),
   [`RELAYESC8`](../servers/relayesc8.md), …) on `listenip`.
2. Run Coercer with `listenip = <agent IP>`.
3. The relay server receives the auth, relays it to its configured
   `targets`, and emits whatever the post-auth module produces (new SMB
   session, new PFX, ACL change, *etc.*).

### 3. NTLM reflection (CVE-2025-33073)

Use the [`NTLMREFLECTION` attack](ntlmreflection.md) — it wires the Coercer,
[`RELAYNTLMREFLECTION`](../servers/relayreflection.md), [`dnsadd`](../clients/ldap.md#dnsadd)
and the marshalled-name listener together for you.

---

## Limitations and caveats

- **Coercer does not authenticate the inbound NTLM exchange itself.** If
  nothing is listening on `listenip`, the coercion succeeds but the NTLM
  packet vanishes into the void. Always check that your relay / spoofer is up
  and bound first.
- **A "successful" coercion call doesn't always mean the target authenticated.**
  Some RPC functions return success on bad UNC paths (target processes the
  request, fails to fetch, never opens the SMB connection). Cross-check with
  the listener log.
- **Patches catch up.** EFSR / PetitPotam in particular has had multiple
  rounds of partial patches over the years; some targets will accept some
  sub-functions but not others. The default behaviour of trying every
  sub-function in a group is intentional — leave it on unless you have a
  specific reason to narrow down.
- **Spooler / VSS / DFS dependencies.** `RPRN` needs Print Spooler; `FSRVP`
  needs VSS; `DFSNM` needs the netdfs pipe (DFS namespaces). Check what's
  actually running on the target with the
  [`smbspooler`](../scanners/smbspooler.md) and similar scanners before
  blaming Coercer.

---

## See also

- [`RELAYSMB`](../servers/relaysmb.md) / [`RELAYLDAP`](../servers/relayldap.md)
  / [`RELAYMSSQL`](../servers/relaymssql.md) / [`RELAYESC8`](../servers/relayesc8.md)
  / [`RELAYNTLMREFLECTION`](../servers/relayreflection.md) — the relay servers
  Coercer feeds into.
- [`SPOOFER`](../servers/spoofer.md) — for offline NTLMv2 capture instead of
  relay.
- [`NTLMREFLECTION` attack](ntlmreflection.md) — fully automated CVE-2025-33073
  chain (uses Coercer internally).
- [`smbspooler` scanner](../scanners/smbspooler.md) — pre-flight check for
  PrinterBug feasibility.
- [SMB client → `printerbug`](../clients/smb.md) — single-vector coercion
  primitives without the multi-target harness.
