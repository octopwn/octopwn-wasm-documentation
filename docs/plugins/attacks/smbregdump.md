# SMBRegDump Attack

The **SMBRegDump** attack is OctoPwn's "classic" remote registry secrets dumper —
modeled on Impacket's `secretsdump.py` "registry" technique. It saves the `SAM`,
`SYSTEM` and `SECURITY` hives to disk on the **target** under
`C:\Windows\Temp\<random>.<random>` via the Remote Registry RPC (`SaveKey`), reads them
back over SMB, parses them with `pypykatz`, deletes the dump files, and stores every
recovered hash / cached credential in the [Credentials Hub](../../user-guide/credentials.md)
under the appropriate credential type (`nt`, `lm`, `dcc`, …).

| Step                          | Where                              |
| ----------------------------- | ---------------------------------- |
| Save hive to file             | Target: `C:\Windows\Temp\` (writable by SYSTEM) |
| Read file back                | Over SMB (`C$` admin share)        |
| Parse + extract secrets       | OctoPwn agent (in-memory)          |
| Delete remote files           | Target: same `C:\Windows\Temp\` path |

!!! tip "Touchy disk vs. no-touchy disk"
    SMBRegDump **writes to the target's disk**. That's an artifact in
    `C:\Windows\Temp\` (deleted at the end, but visible to file-system auditing in
    between) plus matching Remote Registry / SMB log entries. If you want a
    no-touch alternative, use [`smbregdump2`](smbregdump2.md), which uses the
    in-memory remote-registry path
    (modifies the security descriptors of the protected keys, reads them in place,
    restores the descriptors). Both produce the same secrets.

---

## How it works

1. **SMB connect + login** with the supplied `credential` against the next target.
   Local-admin is required for both the `SaveKey` RPC and the `C$` read-back.
2. **Check Remote Registry service status.** If it's not `RUNNING`, OctoPwn enables
   it and starts it via DCERPC (the same mechanism as `serviceen RemoteRegistry`
   from the [SMB client](../clients/smb.md#serviceen)), then waits `srvwaittime`
   seconds for the service to come up.
3. **Dump the hives.** For each of `HKLM\SAM`, `HKLM\SYSTEM`, `HKLM\SECURITY`,
   OctoPwn issues `BaseRegSaveKey` to write the hive to a file with a randomised
   `<4 bytes hex>.<3 bytes hex>` name in `C:\Windows\Temp\`. After issuing all three
   saves, OctoPwn waits `srvwaittime` seconds again to let Windows finish flushing
   the file to disk.
4. **Read back over SMB**, parse the hives with `pypykatz.OffineRegistry`, then
   `delete` the temporary files via SMB (`DELETE` flag on close). If any deletion
   fails it is reported but does not abort — go clean up manually if so.
5. **Store recovered secrets** in the Credentials Hub (machine account NT hash,
   local user NT hashes, DCC2 hashes, LSA secrets, anything else `pypykatz` finds in
   the hives).

---

## Prerequisites

- **Local admin** on every target. Required for `BaseRegSaveKey` *and* for
  `C$` read access.
- **Outbound `445/TCP`** from the agent to the targets.
- **Remote Registry service** must be enable-able. On most Windows hosts it is
  disabled by default but startable by SCM-write-capable accounts (i.e. local
  admins). On heavily hardened hosts the service may be `Disabled` (not just
  `Stopped`) — in which case it will fail to enable and the attack errors out.
- **`C:\Windows\Temp\` writeable by SYSTEM** (the default) and not under EDR
  watchful eye for new file creation. This is the loud step.

---

## Parameters

### Normal parameters

#### `credential`
Credential ID to authenticate over SMB. Must be local-admin on the targets.

#### `targets`
List of targets — standard list / CIDR / file / `all` syntax.

#### `srvwaittime`
Default: `10`. Seconds to wait both for the Remote Registry service to come up after
being enabled **and** for Windows to flush the dumped hives to disk. The default is
generous; lower it if you're scanning many hosts at low EDR risk and want speed,
raise it on slow / busy targets.

### Advanced parameters

The standard credentialled-SMB scanner parameter set: `authtype`, `dialect`,
`krbetypes`, `krbrealm`, `maxruntime`, `proxy`, `resultsfile`, `showerrors`, `timeout`,
`workercount`, `wsnetreuse`. See [SMB client → authentication](../clients/smb.md#authentication)
for the auth-related ones.

---

## See also

- [`smbregdump2`](smbregdump2.md) — in-memory variant; same outputs, no disk
  artifacts.
- [`DPAPI`](dpapi.md) — superset attack that also runs the registry secrets path
  *and* harvests user / SYSTEM DPAPI blobs and SCCM secrets in one go.
- [SMB client](../clients/smb.md) — for manual `regdump` / `regdump2` invocations
  against a single host without the multi-target harness.
