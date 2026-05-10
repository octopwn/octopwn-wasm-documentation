# Domain Utility

The **DOMAIN** utility is OctoPwn's **AD attack-path engine**. It loads a
domain model (from a live LDAP session and/or a BloodHound zip) and on top
of that model offers two things:

1. **Path queries** — shortest-path / all-paths / path-to-DA, returned in
   BloodHound-compatible step form, with attack-plan annotations marking
   which edges are *viable* (we know how to abuse them) and which are
   *dangerous* (would burn the target if traversed).
2. **Edge exploitation** — given a source SID and a target SID with a
   known abusable edge between them, the util will execute the attack
   end-to-end using existing OctoPwn primitives (LDAP modifications,
   targeted kerberoasting, ShadowCreds, ReadLAPS, DCSync, …) and then
   **roll back** any reversible changes (DACL restoration, owner
   restoration, group membership removal).

It is the orchestration layer that ties [BLOODHOUND](bloodhound.md),
[LDAP](../clients/ldap.md), and the various per-attack modules
([`SHADOWCREDS`](../attacks/shadowcreds.md),
[`KERBEROAST`](../attacks/kerberoast.md),
[`DCSYNC`](../attacks/dcsync.md), …) into something an analyst can drive
from a single util session.

---

## Conceptual model

The util maintains a **DomainManager** that holds:

- A graph of objects (users, groups, computers, OUs, GPOs, domains) with
  ACL / membership / trust edges between them, loaded either from LDAP or
  from a BloodHound zip.
- A mapping from **OctoPwn credential IDs** to the domain SIDs / DNs they
  belong to. This is what lets a path-finding query say "from CID 12 to
  DA" — internally it resolves CID 12 to its SID, then searches.
- Per-domain plumbing (LDAP target ID, credential ID, proxy ID) so that
  when the util needs to act *as* a particular SID it can spin up the
  right LDAP/SMB session transparently.

Everything is keyed on **SIDs** internally. The util has a `normalize`
helper that accepts either an `S-1-5-...` string or an OctoPwn CID (which
must have a SID populated on it — see [`enrichcid`](#enrichcid) below).

### Supported edges

The util explicitly knows how to walk these edges:

`forcechangepassword`, `addmember`, `addself`, `genericwrite`, `genericall`,
`writedacl`, `writeowner`, `getchangesall`, `getchanges`, `readlaps`.

These are the **viable** edges in the path planner. Edges like `memberof`,
`member`, `admincount`, `adminopcount` are flagged as **dangerous** —
the planner detects them but won't traverse without operator guidance.

---

## Parameters

| Parameter | Default | Purpose |
| --- | --- | --- |
| `pid` | none | Default proxy ID for spawned LDAP / SMB sessions. |
| `hidewindows` | `True` | Hide auto-created sessions in the GUI. |
| `do_bloodhound` | `True` | Build a BloodHound-style graph alongside the live LDAP model (enables path queries when initialised from LDAP). |
| `do_kerberoast` | `True` | Reserved for future automated multi-step planners (auto-attempt targeted kerberoasts during path exploitation). |
| `do_adcs` | `True` | Reserved for future ADCS-aware planning. |

---

## Commands

### LOAD

#### loadldap
`loadldap(sid)` — load the domain by reusing an existing **LDAP client
session**. `sid` here is an OctoPwn session ID (not a domain SID). The
util pulls the credential / target / proxy from that session, builds a
`DomainManager`, and runs an `add_domain_ldap` against the live DC.

This is the typical entry point — start an LDAP session, hand its session
ID to `loadldap`, and the rest of the util's queries become meaningful.

#### loadbloodhound
`loadbloodhound(filepath)` — load a BloodHound zip (the kind produced by
the [BLOODHOUND utility](bloodhound.md)) into the DomainManager. Useful
for offline analysis or for replaying a previously-collected snapshot
without touching the wire.

When loaded this way some attack commands won't have everything they need
(no live LDAP session means no in-place ACL writes); it's intended for
**path queries**, not for active exploitation.

### INFO

#### domaininfo
`domaininfo()` — print every domain currently loaded (forest root, child
domains, trusts pulled in via `follow_trusts`).

#### cidinfo
`cidinfo(cid)` — given an OctoPwn credential ID, print the user-info
record (DN, sAMAccountName, SID, group memberships, …) for the
corresponding AD object.

#### enrichcid
`enrichcid(cid)` — populate / refresh the SID and other AD metadata on
the given credential. Required before any of the path / attack commands
can use that credential as a source — they all key on SID and silently
skip credentials that don't have one.

#### enrichcredentials
`enrichcredentials()` — `enrichcid` over **every** Hub credential whose
`stype` is `PASSWORD`, `NT`, or `AES` and that doesn't yet have a SID.
Useful right after a fresh import of credentials (e.g. from
[NTDS](pypykatz.md#ntds) or [DCSync](../attacks/dcsync.md)) to make
them all routable in path queries.

### PATHS

All path commands send the result as a `PATH` window message to the GUI
(which renders it as a path graph) **and** return the raw paths to the
caller for scripting.

`name_cid_sid` arguments accept any of: a sAMAccountName / DN, a SID
(starts with `S-1-`), or an OctoPwn credential ID.

#### path
`path(dname_or_cid, sname_or_cid=None)` — shortest path between two
arbitrary nodes. With one argument, the second defaults to "any DA group".

#### pathtoda
`pathtoda(name_cid_sid=None)` — shortest path(s) from `name_cid_sid` to
a Domain Admin equivalent. After computing, the util runs
`analyze_paths` over the results and prints, per path, whether the path
is **viable** (we know how to walk every edge) and **dangerous** (some
hop would commit a noisy / irreversible action).

#### pathtodaall
`pathtodaall(name_cid_sid=None)` — every path to DA, not just the
shortest. Slower; use when the shortest path is non-viable and you want
the planner to find an alternative.

#### pathtodashortest
`pathtodashortest()` — global "anything → DA" view. No source filter;
returns the union of shortest DA-bound paths from every owned principal
the planner knows about.

### EDGES (advanced)

The following commands execute a single concrete edge against the
domain. They are the building blocks that
[`exploit_path`](#exploit_path) chains together; they can also be
invoked manually for one-shot exploitation.

All of them take SIDs (or CIDs that resolve to SIDs via
`enrichcid`) for `src` (the principal that holds the rights) and `dst`
(the target object).

#### forcechangepassword
`forcechangepassword(src, dst, password)` — `src` has
`User-Force-Change-Password` over `dst`; set `dst`'s password to
`password` and store the new credential.

#### targetedkerberoast
`targetedkerberoast(src, dst)` — abuse `WriteSPN`-equivalent rights to
**add a temporary SPN** to `dst`, kerberoast it, then **remove the SPN**.
The recovered hash is added to the Hub. Cross-domain trips are detected
automatically and routed through the right Kerberos session.

#### writedacl_targetedkerberoast
`writedacl_targetedkerberoast(src, dst)` — add full-control DACL,
targetedkerberoast, restore the original DACL on the way out. Use when
you have `WriteDACL` instead of `WriteSPN`.

#### shadowcreds
`shadowcreds(src, dst)` — full
[Shadow Credentials](../attacks/shadowcreds.md) chain: write a
`msDS-KeyCredentialLink`, PKINIT to get a TGT, UnPAC the hash, restore
the attribute on the way out.

#### writedacl_shadowcreds
`writedacl_shadowcreds(src, dst)` — same idea as above but starts from a
`WriteDACL` edge: grant full control first, then run shadowcreds, then
restore the original DACL.

#### addmember
`addmember(src, dst, newmember, newmembertype)` — add `newmember` to the
group `dst`. The corresponding context-manager flavour
(used by the path planner) **also removes `newmember` again on exit** so
the change isn't permanent.

#### writeownergroup
`writeownergroup(src, dst, newmember)` — change owner of group `dst` to
`src`, grant full control, add `newmember`, then restore the original
owner.

#### genericallgroup
`genericallgroup(src, dst, newmember)` — `GenericAll` over the group
`dst`: grant full control, add `newmember`, restore the DACL.

#### genericall_readlaps
`genericall_readlaps(src, dst, adminusername=None)` — `GenericAll` over
the computer `dst`: grant ReadLAPS rights, fetch the LAPS password,
restore the DACL.

#### readlaps
`readlaps(src, dst, adminusername=None)` — straight ReadLAPS when `src`
already has the right. If `adminusername` is set, the recovered LAPS
plaintext is stored as a `PASSWORD` credential for that user; otherwise
it's just printed.

#### dcsync
`dcsync(src, dst, targetusername=None)` — perform [DCSync](../attacks/dcsync.md)
against domain `dst` as `src`. If `targetusername` is unset, dumps the
full domain; otherwise just that user.

### PERSISTENCE

#### save
`save()` — serialise the loaded DomainManager state into the
`__domaindata` session parameter so it survives session restart / project
save-load.

### PATH EXPLOITATION

#### exploit_path
`exploit_path(steps)` — given an attack-plan list (the same shape
returned by `analyze_paths` / `pathtoda`), walk each step using the
matching edge function (`addmember`, `genericall`, `writeowner`,
`getchangesall`, `addself`, `genericwrite`, …) **as nested context
managers**.

Because each edge function is a context manager, the cleanup actions
(`AsyncExitStack`) run in **reverse order** when the chain finishes —
so DACLs / owners / group memberships changed at hop 3 are restored
before the hops 2 and 1 cleanups run, leaving the domain in its
original state if everything succeeds.

If any hop fails, the exit stack still unwinds the previous successful
hops in reverse order — the chain "self-cleans" on partial failure too.

---

## Operational notes

- **Resolve credentials first.** Path commands silently filter out
  credentials with no SID. Run `enrichcredentials` after every credential
  import.
- **Cross-domain hops** are recognised by SID prefix. The util will spin
  up an LDAP session pointed at the right domain transparently — make
  sure the seed credential has cross-domain rights before assuming it'll
  work.
- **Most edge commands have a "writedacl_" partner.** When you don't
  have the direct edge but you do have `WriteDACL`, use the partner — it
  grants the missing right just long enough to perform the action and
  then restores the original DACL.
- **Attack-plan annotations are advisory.** The planner is rule-based,
  not ML; it can mark a path as viable that fails at runtime (e.g. due
  to permission denied at the actual moment) and vice versa. Always
  review `analyze_paths` output before committing.
- **Cleanup is best-effort.** If the DC goes away mid-chain, the
  rollback tries the restore but the change may persist — review the
  affected objects manually.

---

## Limitations and caveats

- **`do_addself` is incomplete** in the current code base — it falls
  through to `addmember` semantics. Treat it as alpha.
- **`do_rbcd` is a TODO stub** — for actual RBCD use the dedicated
  [`RBCD` attack](../attacks/rbcd.md).
- **No GPO / OU edge support yet.** `genericwrite` / `genericall` over
  GPO / OU targets fall through to a "not supported" branch. Walking
  those edges requires manual orchestration via
  [`COERCER`](../attacks/coercer.md) / GPP / GPLink etc.
- **No tracking of permanent changes.** If you bypass the context
  manager flavour and call e.g. `addmember` directly, the cleanup does
  not run. Use `exploit_path` for any chain you want auto-rolled-back.
- **The graph layer expects BloodHound-compatible data.** Loading a
  custom graph format won't work — produce a BloodHound zip first, or
  rely on the live LDAP path.

---

## See also

- [BLOODHOUND utility](bloodhound.md) — produces the zip you can hand to
  `loadbloodhound`, and the LDAP / SMB session model `loadldap` builds on.
- [Neo4j utility](neo4j.md) — for ad-hoc Cypher queries against the same
  graph data once it's in BloodHound CE.
- [LDAP client](../clients/ldap.md) — every edge command spins up an LDAP
  session under the hood; the underlying primitives (`addusertogroup`,
  `addfullcontrolright`, `changeowner`, `addspn`, `delspn`,
  `setkeycredentiallink`, `grantreadlapsrights`, …) live there.
- [`KERBEROAST`](../attacks/kerberoast.md) /
  [`DCSYNC`](../attacks/dcsync.md) /
  [`SHADOWCREDS`](../attacks/shadowcreds.md) /
  [`RBCD`](../attacks/rbcd.md) — the attack modules whose semantics this
  util mirrors at the path-orchestration layer.
