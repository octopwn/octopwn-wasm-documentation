# Attacks

OctoPwn's **Attacks** are one-button orchestrators for higher-level, multi-step
techniques — the post-exploitation moves you'd otherwise stitch together by
hand from the [Clients](../clients/overview.md), [Scanners](../scanners/index.md)
and [Servers](../servers/overview.md). Each attack is configured like a scanner
(parameters in a session window, results land in the
[Credentials Hub](../../user-guide/credentials.md)), but instead of "find
hosts that match X" it does "perform multi-stage technique X end to end".

Examples of what's automated:

- The full **DCSync** flow with optional LDAP-driven user filtering.
- The full **CVE-2025-33073 NTLM-reflection** chain (DNS write → relay
  server → coerce → SYSTEM session per target).
- **AD CS ESC1 / ESC4** including template-flag flip + restore.
- **Resource-Based Constrained Delegation** including machine-account
  creation + cleanup.
- **Shadow Credentials** including `msDS-KeyCredentialLink` write +
  restore + UnPAC the Hash.

Hits — NT hashes, AES keys, PFX credentials, service tickets, community
strings, NTP roast hashes — are stored automatically in the
[Credentials Hub](../../user-guide/credentials.md) for immediate use by any
downstream client / scanner / attack / server.

---

## AD credentials and secrets

| Attack                          | What it does                                                                                          |
| ------------------------------- | ----------------------------------------------------------------------------------------------------- |
| [`KERBEROAST`](kerberoast.md)   | SPN-roast **and** AS-REP-roast every eligible user across all etypes (RC4 / AES128 / AES256).         |
| [`DCSYNC`](dcsync.md)           | Pull every NT / AES / DPAPI key out of AD via DRSGetNCChanges. Optional LDAP filter for scope.        |
| [`ADSPRAY`](adspray.md)         | Lockout-aware password spray (passwords *or* NT hashes) across all enabled domain users.              |
| [`PRE2K`](pre2k.md)             | Find machine accounts whose password is still the legacy "lowercased name" default.                   |
| [`TIMEROAST`](timeroast.md)     | Unauthenticated NTP-RID-roast against DCs; recovers computer-account hashes for offline cracking.     |

## AD CS (Active Directory Certificate Services)

| Attack                  | What it does                                                                                            |
| ----------------------- | ------------------------------------------------------------------------------------------------------- |
| [`ESC1`](esc1.md)       | Enroll a SAN-supplying certificate as any user via a vulnerable template (CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT). |
| [`ESC4`](esc4.md)       | When you can *write* the template object: temporarily enable ESC1, run ESC1, restore.                   |

For the HTTP / Web-Enrollment AD CS variant (ESC8), see the
[`RELAYESC8` server](../servers/relayesc8.md).

## Kerberos delegation

| Attack                                       | What it does                                                                                              |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| [`RBCD`](rbcd.md)                            | Resource-Based Constrained Delegation: create a machine, write `msDS-AllowedToActOnBehalfOfOtherIdentity`, S4U, restore. |
| [`SHADOWCREDS`](shadowcreds.md)              | Plant a `msDS-KeyCredentialLink` entry on a target user/computer, PKINIT, UnPAC the hash, restore.        |
| [`CONSTRAINEDDELEG`](constraineddeleg.md)    | Use an already-configured constrained-delegation right (S4U2Self → S4U2Proxy) to impersonate any user.    |

## Coercion and relay

| Attack                              | What it does                                                                                                            |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| [`COERCER`](coercer.md)             | Multi-vector coercion driver — fires PetitPotam (EFSRPC), PrinterBug (RPRN), ShadowCoerce (FSRVP), DFSCoerce (DFSNM), EventLog (EVEN). |
| [`NTLMREFLECTION`](ntlmreflection.md) | One-button CVE-2025-33073 chain: scan → DNS write → relay server → COERCER → SYSTEM session per vulnerable target.       |

For the listener side of these coercions, see the
[server pages](../servers/overview.md): [`SPOOFER`](../servers/spoofer.md),
[`RELAYSMB`](../servers/relaysmb.md), [`RELAYLDAP`](../servers/relayldap.md),
[`RELAYMSSQL`](../servers/relaymssql.md), [`RELAYESC8`](../servers/relayesc8.md),
[`RELAYNTLMREFLECTION`](../servers/relayreflection.md).

## SMB host secrets

| Attack                              | What it does                                                                                                  |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| [`SMBREGDUMP`](smbregdump.md)       | Dump SAM / SYSTEM / SECURITY hives via `BaseRegSaveKey` to disk on the target, read back, parse, delete.       |
| [`SMBREGDUMP2`](smbregdump2.md)     | Same secrets, no disk artifact — temporarily widens registry security descriptors and reads in-place.         |
| [`DPAPI`](dpapi.md)                 | Full DPAPI loot: master keys + credentials + Chrome blobs + SCCM (Network Access Account, Task Sequences, …). |

## Edge cases

| Attack                          | What it does                                                                                  |
| ------------------------------- | --------------------------------------------------------------------------------------------- |
| [`SNMPBRUTE`](snmpbrute.md)     | Brute-force SNMPv2c community strings against `161/UDP`.                                       |
| [`IPMIHASH`](ipmihash.md)       | Capture IPMI 2.0 RAKP hashes (one of the few pre-auth, no-creds-needed wins on bare-metal).   |

---

## Choosing the right attack

A few rules of thumb that come up in real engagements:

- **You have a domain user but no admin anywhere** → run [`KERBEROAST`](kerberoast.md)
  + [`ADSPRAY`](adspray.md) + [`PRE2K`](pre2k.md) + [`TIMEROAST`](timeroast.md)
  in parallel as a fan-out. Then look at AD CS templates with the
  [LDAP client](../clients/ldap.md) — if any is ESC1-vulnerable, run
  [`ESC1`](esc1.md).
- **You have local admin on one machine, want lateral movement** → run
  [`DPAPI`](dpapi.md) (covers DPAPI + SCCM + registry secrets in one pass).
- **You have replicating-rights on the domain** → run [`DCSYNC`](dcsync.md);
  one shot, pulls everything.
- **You have *any* domain user and a vulnerable subnet** → run
  [`NTLMREFLECTION`](ntlmreflection.md) in continuous mode. Auto-owns every
  CVE-2025-33073-vulnerable host that gets added to the project.
- **You can write to a target user's `msDS-KeyCredentialLink` ACL** → run
  [`SHADOWCREDS`](shadowcreds.md). Cleanest user takeover primitive in AD.
- **You can write to a target machine's `msDS-AllowedToActOnBehalfOfOtherIdentity`
  ACL** → run [`RBCD`](rbcd.md). Cleanest machine takeover primitive.

Each attack page lists its prerequisites, the exact LDAP / SMB / RPC
operations it performs, the credentials it produces, and the manual
client-side equivalents you'd use for full control instead.
