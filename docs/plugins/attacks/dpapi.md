# DPAPI Attack

The **DPAPI** attack is OctoPwn's automated, multi-target, end-to-end DPAPI looter. It
authenticates over SMB to each target as a local admin and, in a single pass per host,
extracts and decrypts:

| Source                                                                  | What you get                                                                            |
| ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Per-user `…\AppData\…\Microsoft\Protect\…` master keys                  | DPAPI master keys for every interactive user that has logged on                         |
| Per-user `…\AppData\…\Microsoft\Credentials\` credential blobs          | Saved Windows credentials (network shares, RDP, basic-auth caches), incl. domain creds  |
| Per-user `…\AppData\Local\Google\Chrome\User Data\…\(Login Data\|Cookies)` | Chrome login data + cookies blobs (decrypted with the matching master key)            |
| `Windows\System32\config\systemprofile\AppData\…\Protect`               | SYSTEM context master keys                                                              |
| `Windows\System32\Microsoft\Protect\S-1-5-18\User`                      | LSA-protected SYSTEM master keys (the real "machine DPAPI" loot)                        |
| `Windows\System32\config\systemprofile\AppData\…\Credentials`           | SYSTEM credential blobs                                                                 |
| Remote registry: SAM / SYSTEM / SECURITY / SOFTWARE hives               | SYSTEM DPAPI prekeys (machine secret), used to decrypt the SYSTEM master keys           |
| `Windows\System32\wbem\Repository\OBJECTS.DATA` (the WMI / SCCM CIM DB) | **SCCM secrets** — Network Access Account creds, Task Sequences, Collection Variables, "Other Secrets" |

Decrypted user credentials and SCCM Network Access Account credentials are
**automatically added to the [Credentials Hub](../../user-guide/credentials.md)** with
`stype = password`, `source = DPAPI`. Master keys, cookies, and other artifacts are
yielded as result rows and shown in the session window.

For raw DPAPI blob handling without the SMB / multi-host harness, see the
[DPAPI utility](../utils/dpapi.md).

---

## How it works

1. **SMB connect + login** with the supplied `credential` against the next target.
   Anything short of local-admin will fail to read the SYSTEM secrets — the user
   directories will still be readable in many configurations, but the master keys
   for those users cannot be decrypted without SYSTEM context.
2. **Remote registry** is opened (using `RemoteRegistry.from_smb_connection`) and the
   SAM / SYSTEM / SECURITY hives' secrets are pulled into a `pypykatz.dpapi.DPAPI`
   object — this gives the **DPAPI prekeys** required to decrypt SYSTEM master keys.
   This step uses the in-memory remote-registry path
   (no files dropped on disk; same engine as [`smbregdump2`](smbregdump2.md)).
3. **Filesystem walk over `\\<host>\C$`** to collect:
    - Every user folder under `C:\Users\` (excluding `All Users`, `Default*`, `Public`,
      and any `.NET*`).
    - For each user: `AppData\(Roaming|Local)\Microsoft\Protect`,
      `AppData\(Roaming|Local)\Microsoft\Credentials`,
      `AppData\Local\Google\Chrome\User Data\(Local State|Default\Login Data|Default\Cookies)`.
    - SYSTEM master keys / credentials under `C:\Windows\System32\…`.
    - The full `OBJECTS.DATA` WMI repository file (often hundreds of MB on managed
      hosts — be patient).
   Every blob is downloaded once, hex-encoded, kept in RAM, and the temporary file is
   deleted from the agent host.
4. **Master-key decryption.** For each `Protect\<SID>\<MK_GUID>` blob, OctoPwn tries:
    - SYSTEM prekeys for SYSTEM blobs.
    - Cached domain backup keys (if the operator has previously dumped them via
      DCSync — see [`DCSYNC`](dcsync.md)).
    - User passwords (only when the operator has supplied a cleartext password — *see
      "Practical scenarios" below*).
5. **Credential-blob decryption.** Each `Credentials\<GUID>` blob is decrypted with the
   matching master key. Domain-style credentials (`type=2`) — typical for saved RDP
   sessions, mapped network drives with `cmdkey`, etc. — are parsed into
   `domain\username:password` and added to the Credentials Hub directly.
6. **SCCM / WMI Object DB harvest.** `OBJECTS.DATA` is regex-scanned for the four
   `<PolicySecret>` patterns Microsoft uses to embed DPAPI-encrypted secrets in CIM:

    | CIM data type        | Regex hook                                                               | What it usually contains                                  |
    | -------------------- | ------------------------------------------------------------------------ | --------------------------------------------------------- |
    | NAA Credentials      | `CCM_NetworkAccessAccount.*<PolicySecret>...<PolicySecret>...`           | The **Network Access Account** username + password used by SCCM clients to fetch packages — usually a privileged service account. |
    | Task Sequences       | `</SWDReserved>.*<PolicySecret>...`                                      | Task-sequence variables, often containing local-admin / domain credentials embedded in deployment workflows. |
    | Collection Variables | `CCM_CollectionVariable\x00\x00<name>\x00\x00...<PolicySecret>...`       | Per-collection variables; often hold service-account passwords for build automation. |
    | Other Secrets        | `<PolicySecret>...` (catch-all)                                          | Anything else SCCM dropped into a `<PolicySecret>` blob.   |

   Each match is decrypted with `dpapi.decrypt_blob_bytes` (using the SYSTEM master
   keys we just decrypted in step 4). NAA credentials are auto-added to the
   Credentials Hub; the rest are emitted as result rows for manual review.

---

## Practical scenarios

1. **Local-admin foothold (most common).** Run the attack with any local-admin
   credential; you get every SYSTEM secret on the box plus every saved credential of
   every user that ever logged on. SCCM-managed hosts additionally yield NAA + task
   sequence secrets.
2. **Domain backup keys ("God Mode").** Once you have replication rights, run
   [`DCSYNC`](dcsync.md) and let OctoPwn store the domain DPAPI backup keys. From that
   point on, every subsequent `DPAPI` run can decrypt **any** user's master keys on
   any domain-joined host — even users you have never seen log on. Required for the
   "extract roaming-profile credentials of users with no local LSASS context"
   workflow.
3. **Cleartext-password decryption of a specific user.** Currently the
   per-user-password decryption path requires the user's *cleartext* password (not the
   NT hash) and is only invoked if the operator manually wires it in — the high-level
   attack module does not yet expose a cleartext-password parameter on the session
   window. For that workflow, drive the [DPAPI utility](../utils/dpapi.md) directly.

---

## Prerequisites

- **Local admin** on every target. Without local admin, the SYSTEM master keys cannot
  be decrypted, the SCCM `OBJECTS.DATA` is unreadable, and most user folders are
  off-limits anyway.
- **Remote Registry service** must be running on the target. The DPAPI attack does
  *not* enable it itself; if it's not running, the SYSTEM-prekey extraction step will
  fail and you will see "Failed to read registry hive" errors. To enable it manually,
  use [`serviceen RemoteRegistry`](../clients/smb.md#serviceen) from the
  [SMB client](../clients/smb.md), or run [`smbregdump`](smbregdump.md) /
  [`smbregdump2`](smbregdump2.md) first (both will start the service if it's stopped).
- **Outbound `445/TCP`** from the agent to every target. Proxy through wsnet if
  needed.
- **Defender** / EDR may flag the registry hive reads or the bulk file pulls. The
  attack does not bypass any AV — if a target has detection, you will see opaque
  failures during the registry step.

---

## Parameters

### Normal parameters

#### `credential`
ID of the credential to authenticate over SMB. Must be local-admin on the targets.

#### `targets`
List of targets. Standard list / file / `all` syntax — see
[scanner targets](../scanners/baseline.md) for the full grammar.

#### `skipusers`
Default: `False`. When `True`, only the SYSTEM-context loot is collected — no walk
under `C:\Users\`, no Chrome / Credentials per-user blobs. Useful for bulk runs when
you only care about machine accounts and SCCM secrets and want to keep the per-host
runtime short.

### Advanced parameters

The standard credentialled-SMB scanner parameter set: `authtype`, `dialect`,
`krbetypes`, `krbrealm`, `maxruntime`, `proxy`, `resultsfile`, `showerrors`, `timeout`,
`workercount`, `wsnetreuse`. See [SMB client → authentication](../clients/smb.md#authentication)
for the auth-related ones; defaults are fine for everything else.

---

## See also

- [DPAPI utility](../utils/dpapi.md) — interactive single-blob / single-user DPAPI work,
  domain-backup-key import, manual master-key prekey juggling.
- [`smbregdump`](smbregdump.md) / [`smbregdump2`](smbregdump2.md) — pull SAM / LSA /
  DCC secrets without the DPAPI machinery if all you want is the local hash list.
- [`DCSYNC`](dcsync.md) — get the domain DPAPI backup keys for "God Mode" decryption
  of every user's blobs across the domain.
- [Operational Guidance for Offensive User DPAPI Abuse](https://posts.specterops.io/operational-guidance-for-offensive-user-dpapi-abuse-1fb7fac8b107)
  — SpecterOps' canonical reference.
