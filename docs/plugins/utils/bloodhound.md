# BloodHound Utility

The **BloodHound** utility is OctoPwn's collector for
[BloodHound CE](https://github.com/SpecterOps/BloodHound) — it produces a
**BloodHound-compatible zip** from a live AD environment that can be
ingested directly into BloodHound CE / Legacy. It is the spiritual
replacement of the older JackDaw util (which used a SQLite DB and its own
graphing layer); the new BLOODHOUND util drops the OctoPwn-specific DB and
defers analysis to BloodHound itself.

Three things differentiate the OctoPwn collector from a standalone
BloodHound ingestor:

1. **It uses your existing OctoPwn sessions** — pass in a credential ID,
   target ID, optional proxy ID, and the util builds an internal LDAP /
   SMB factory from your project's Credentials and Targets. No separate
   credential plumbing.
2. **SMB enrichment is split** into a sessions phase
   (`collect_smb_sessions`) and a registry-groups phase
   (`collect_smb_groups`) so you can run the cheap LDAP-only collection
   first and decide whether you want the noisy, time-consuming SMB
   enrichment afterwards.
3. **Trust-following is built in** — `follow_trusts=True` walks the trust
   graph during LDAP collection, so a single command captures the
   reachable forest, not just the seed domain.

---

## How it works

The flow has three independent phases. `collect_all` orchestrates all
three; you can also call them one at a time for finer control.

### Phase 1 — LDAP collection (`collect_ldap`)

Runs [`MSLDAPDump2Bloodhound`](https://github.com/skelsec/msldap) against
the LDAP target. Produces the canonical BloodHound zip with users, groups,
computers, OUs, GPOs, ACLs, trusts, etc. The zip path is stored in the
util's `zipfilepath` parameter for the next phases.

Honours `follow_trusts` — when enabled, the collector queries trusted
domains' DCs over the same authenticated LDAP session and adds them to
the zip. Disable it for single-domain collections (faster, smaller zip,
fewer potential errors against unreachable trust partners).

### Phase 2 — SMB sessions (`collect_smb_sessions`)

Reads the computer / user objects out of the LDAP zip, fires an
[`SMBSESSION`](../scanners/smbsession.md) scanner against every computer
to enumerate active logon sessions over SMB, then **rewrites** the
computer JSON entries inside the zip to add the `Sessions: { Collected:
true, Results: [...] }` block BloodHound expects.

This is the noisy half — every host is touched over SMB. Tune
`worker_count` to match the environment and the operator's risk
tolerance.

### Phase 3 — SMB local groups (`collect_smb_groups`)

For every computer in the zip, opens an SMB connection (using the
configured credential and proxy) and queries the **remote registry** for:

- Active registry sessions → `RegistrySessions`
- Local BUILTIN groups and members → `LocalGroups`
- Per-well-known group memberships → `LocalAdmins` (S-1-5-32-544),
  `RemoteDesktopUsers` (555), `DcomUsers` (562), `PSRemoteUsers` (580)

The zip is rewritten in place again, this time injecting the per-host
`LocalGroups` / `LocalAdmins` / `RemoteDesktopUsers` / `DcomUsers` /
`PSRemoteUsers` / `RegistrySessions` blocks.

### Targets bonus — `addtargets`

Once you have a BloodHound zip (yours or someone else's) you can call
[`addtargets`](#addtargets) to import every computer object as a target
into the project's [Targets window](../../user-guide/target.md) — handy
for prepping a project for further enumeration / attacks.

---

## Parameters

| Parameter | Default | Purpose |
| --- | --- | --- |
| `hidewindows` | `True` | Hide the auto-created LDAP / SMB sessions in the GUI. |
| `zipfilepath` | none | Path to the BloodHound zip file. Set automatically by `collect_ldap` / `load`; can be overridden manually. |
| `smbsessionsid` | none | Reuse an existing `SMBSESSION` scanner ID for `collect_smb_sessions`. Auto-created if unset. |

---

## Commands

### LOAD

#### load
`load(zipfilepath)` — load an existing BloodHound zip into the util
**without re-collecting**. Use this when you have a zip from a previous
run (or from another tool) and just want to enrich it with SMB
sessions / groups, or to add its computers as targets.

The path is normalised to OctoPwn's working directory, validated as a
real BHZip archive, and stored as the session `zipfilepath` parameter for
subsequent commands.

### ENUM

#### addtargets
`addtargets()` — populate the [Targets window](../../user-guide/target.md)
with every computer in the loaded zip, attaching the appropriate
`source = BLOODHOUND:<zip>` provenance.

### COLLECT

#### collect_all
`collect_all(cid, tid, smbcid=None, pid=None, follow_trusts=True, ldapprotocol='LDAP', ldapauthproto='NTLM', ldapkrbetypes=None, smbprotocol='SMB', smbauthproto='NTLM', smbkrbetypes=None, worker_count=100)` —
run all three phases in order.

- `cid` / `tid` — credential and target IDs for LDAP.
- `smbcid` — credential ID for SMB (defaults to `cid` if unset).
- `pid` — proxy ID; passed to both LDAP and SMB factories.
- `ldapprotocol` — `LDAP`, `LDAPS`, or `LDAPSTARTTLS`.
- `smbprotocol` — `SMB`, `SMB2`, or `SMB3`. (`SMB` is "auto" — the same
  meaning as in the [SMB client](../clients/smb.md), not "SMB1".)
- `ldapauthproto` / `smbauthproto` — `NTLM`, `KERBEROS`, etc. — anything
  the underlying `asyauth` library accepts.
- `ldapkrbetypes` / `smbkrbetypes` — comma-separated Kerberos etypes if
  you need to pin them.
- `worker_count` — concurrency for the SMB phases (sessions and groups).
  100 is aggressive; halve it for fragile networks.

#### collect_ldap
Phase 1 only. Same arguments as `collect_all`, minus the SMB-specific
ones. Returns the path to the produced zip and stores it in
`zipfilepath`.

#### collect_smb_sessions
Phase 2 only. Requires `zipfilepath` to be set (either by a previous
`collect_ldap` or by `load`). Re-uses an `SMBSESSION` scanner if
`smbsessionsid` is set, otherwise creates one transparently.

#### collect_smb_groups
Phase 3 only. Same prerequisite — `zipfilepath` must be set. Walks the
zip, hits each computer's remote registry, rewrites the zip with the new
`LocalGroups` / `Sessions` / etc. blocks.

---

## Operational notes

- **Trust-following can be a footgun.** A misconfigured trust target that
  the operator has no creds for will produce errors during LDAP collection
  but the run continues. Watch the session output if you're collecting in
  a multi-forest environment.
- **The zip is rewritten in place.** Phases 2 and 3 produce a tmp zip and
  atomically replace the original. If you want to keep the
  LDAP-only zip alongside the enriched one, copy `zipfilepath` aside
  before running the SMB phases.
- **Hide-windows defaults to true** so a `collect_all` does not litter
  your GUI with auto-created LDAP / SMB sessions. They still exist in the
  project (and in the Hub) — just collapsed.
- **`SMBSESSION` re-use.** Setting `smbsessionsid` lets you reuse a
  scanner with custom timeouts / worker counts that you've already tuned.
- **Output goes to the working directory.** The zip filename is generated
  by the underlying `MSLDAPDump2Bloodhound` (timestamped) and stored as
  `zipfilepath`; copy it out of the project if you need to take it
  elsewhere.

---

## Limitations and caveats

- **No support for AzureHound output.** This util is purely an on-prem AD
  collector. Use [ROADtools](roadtools.md) for the Azure / Entra side.
- **No certificate-services collection** beyond what's already in
  `MSLDAPDump2Bloodhound` (which does cover ADCS templates and CAs).
  ADCS-specific reconnaissance is handled by the
  [`ESC1`](../attacks/esc1.md) / [`ESC4`](../attacks/esc4.md) attack
  modules.
- **No GPO enumeration over SMB.** GPOs are picked up via LDAP only; the
  GPP `cpassword` use-case is covered by
  [`gppassword`](pypykatz.md#gppassword) on a manually-fetched GPO XML.
- **Not safe to run against the same zip from multiple sessions.**
  Phases 2 and 3 do read-modify-write of the zip and will race. Sequence
  them or copy the zip first.

---

## See also

- [Neo4j utility](neo4j.md) — once the zip is ingested into BloodHound
  CE's Neo4j, query it without leaving OctoPwn.
- [DOMAIN utility](domain.md) — uses the BloodHound zip for shortest-path
  + edge-aware exploitation orchestration (no Neo4j required).
- [`SMBSESSION` scanner](../scanners/smbsession.md) — what
  `collect_smb_sessions` drives under the hood.
- [Targets window](../../user-guide/target.md) — destination for the
  `addtargets` command.
- [BloodHound CE](https://github.com/SpecterOps/BloodHound) — what
  consumes the produced zip.
