# SMBRegDump2 Attack

The **SMBRegDump2** attack is OctoPwn's "no-touchy disk" remote registry secrets
dumper. Instead of dumping `SAM` / `SYSTEM` / `SECURITY` to a file on the target
(the [`smbregdump`](smbregdump.md) approach), it works **entirely through the
Remote Registry RPC interface**: it temporarily widens the security descriptor on
the protected keys, reads them in-place over RPC, restores the original descriptors,
and parses the bytes locally. Same recovered secrets, no `C:\Windows\Temp\` artifact,
no file flush window.

This is the same engine that powers the [SMB client](../clients/smb.md)'s `regdump2`
command and the in-memory step of the [`DPAPI`](dpapi.md) attack — wrapped here as a
multi-target scanner-style executor. Hashes / cached credentials end up in the
[Credentials Hub](../../user-guide/credentials.md) with `source = REGDUMP`.

| Attack                          | Disk artifact on target | RPC noise                | Defender visibility                           |
| ------------------------------- | ----------------------- | ------------------------ | --------------------------------------------- |
| [`smbregdump`](smbregdump.md)   | **Yes** (`C:\Windows\Temp\<random>`) | `BaseRegSaveKey`         | Low–medium (file-creation event in `Temp`)    |
| **`smbregdump2`** (this one)    | **No**                  | Per-key DACL change + `RegQueryValue` | Medium (security-descriptor change events)    |

Pick `smbregdump2` by default on engagements that care about file-system telemetry;
pick `smbregdump` only on hosts where the security-descriptor manipulation path is
blocked or where you want the registry hives in their on-disk form for offline
post-processing.

---

## How it works

1. **SMB connect + login** with the supplied `credential` against the next target.
   Local admin is required: the attack relies on the fact that local administrators
   can re-write security descriptors on protected registry keys even when they
   cannot read the keys.
2. **`RemoteRegistry.from_smb_connection(connection)`** opens the Remote Registry
   RPC pipe. If the service is stopped, OctoPwn enables and starts it (same path
   as [`smbregdump`](smbregdump.md)), waiting `srvwaittime` seconds for the service
   to come up.
3. **For each protected key** (the `SAM`, `LSA` and `Domain Cache` subtrees that
   normally only `SYSTEM` can read):
    - Save the current security descriptor.
    - Replace it with one that grants the relayed local-admin user `READ` access.
    - `RegQueryValue` the key.
    - Restore the original security descriptor.
4. **Parse the queried values** with `pypykatz` — same parser as
   [`smbregdump`](smbregdump.md), so the recovered secrets are identical.
5. **Two-shot retry.** The whole connect → enable RR → dump cycle runs at most
   twice; if the first attempt fails (e.g. RR was just enabled and is racing the
   first read), the second attempt will usually succeed once the service is fully
   up. After two failed attempts the host is reported as failed and the scan moves
   on.
6. **Store recovered secrets** in the Credentials Hub (machine account NT hash,
   local user NT hashes, DCC2 hashes, LSA secrets).

---

## Prerequisites

- **Local admin** on every target.
- **Outbound `445/TCP`** from the agent.
- **Remote Registry service** must be enable-able. Same constraint as
  [`smbregdump`](smbregdump.md); on heavily hardened hosts where the service is set
  to `Disabled` (not `Stopped`), the attack will error out.
- **The target's `pypykatz`-parseable hive layout.** Very old Windows versions
  (NT 4 / 2000-era forensic targets) and some non-standard reg-protected
  configurations may not parse — `smbregdump` (the on-disk variant) is more tolerant
  for those edge cases.

---

## Parameters

### Normal parameters

#### `credential`
Credential ID to authenticate over SMB. Must be local-admin on the targets.

#### `targets`
List of targets — standard list / CIDR / file / `all` syntax.

#### `srvwaittime`
Default: `10`. Seconds to wait for the Remote Registry service to come up after
being enabled. Lower for fast targets, raise for slow / busy hosts.

### Advanced parameters

The standard credentialled-SMB scanner parameter set: `authtype`, `dialect`,
`krbetypes`, `krbrealm`, `maxruntime`, `proxy`, `resultsfile`, `showerrors`, `timeout`,
`workercount`, `wsnetreuse`. See [SMB client → authentication](../clients/smb.md#authentication)
for the auth-related ones.

---

## See also

- [`smbregdump`](smbregdump.md) — disk-touching variant; same outputs, useful when
  the no-touch path fails.
- [`DPAPI`](dpapi.md) — runs this exact engine *plus* the DPAPI / SCCM harvest in a
  single pass.
- [SMB client](../clients/smb.md) — `regdump2` command for the same operation
  against a single host without the multi-target harness.
