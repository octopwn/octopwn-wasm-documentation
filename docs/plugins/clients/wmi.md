# WMI Client

The **WMI Client** speaks Windows Management Instrumentation (`MS-WMI` over DCOM) against Windows hosts. It wraps `aiosmb`'s DCOM/WMI stack and provides the standard WMI surface — running WQL queries, executing commands via `Win32_Process.Create`, manipulating the registry via `StdRegProv`, managing VSS shadow copies, plus a curated set of enumeration helpers and an RDP-toggling toolkit.

The WMI client is one of OctoPwn's core lateral-movement primitives. Compared to the [WinRM client](./winrm.md), it operates over the older DCOM transport, has no need for `WinRM` to be enabled on the target, and exposes much richer enumeration surfaces — at the cost of being more verbose on the wire and easier to detect.

---

## Transport — what's actually on the wire

| Step | Destination                                                       | Purpose                                                                |
| ---- | ----------------------------------------------------------------- | ---------------------------------------------------------------------- |
| 1    | Target, **TCP/135** (Endpoint Mapper, `epmapper`)                 | DCOM activation handshake; resolves the dynamic port for the WMI service. |
| 2    | Target, **TCP/&lt;dynamic port&gt;** (typically in the 49xxx range) | DCERPC bind, authentication, and all WMI traffic (`IWbemServices` calls). |

Authentication is performed inside the DCERPC bind on the second connection — the same model as the [DCEDRSUAPI client](./dcedrsuapi.md). The default `PORT: 135` shown in the session's connection settings is the EPM port; the actual WMI port is discovered dynamically.

!!! info "Plan firewall scope accordingly"
    For this client to work, you need TCP reachability to the target on **port 135** *and* on its RPC dynamic port range (49152–65535 by default on modern Windows; legacy hosts may use 1024–5000). Hosts where only SMB (445) is reachable are not addressable through this client — use the [WinRM client](./winrm.md) (5985 / 5986) or the [SMB client](./smb.md)'s lateral-movement commands instead.

---

## Authentication

The WMI client supports the standard NTLM and Kerberos credential families. There is no anonymous / null-session authentication path — DCOM/WMI requires an authenticated principal.

| `atype`    | Underlying creds | Notes                                                                       |
| ---------- | ---------------- | --------------------------------------------------------------------------- |
| `NTLM`     | NTLM             | Negotiate-wrapped NTLM. Supports the full pass-the-hash family.              |
| `KERBEROS` | Kerberos         | Standard Kerberos auth. Requires reachability to the KDC.                    |

### NTLM credentials

| Secret type   | Description                                                          | Example                |
| ------------- | -------------------------------------------------------------------- | ---------------------- |
| `password`    | Cleartext password.                                                  | `username:Pa55w0rd!`   |
| `pwhex`       | Hex-encoded UTF-16LE password (for non-ASCII passwords).             | `username:70617373…`   |
| `nt`          | NT hash (pass-the-hash).                                             | `username:aad3b…`      |
| `rc4`         | RC4 (synonym for NT for the NTLM exchange).                          | `username:aad3b…`      |
| `agentproxy`  | Use a remote NTLM signer over the wsnet agent proxy.                 | n/a                    |
| `sspiproxy`   | Use the OS's SSPI session via the wsnet agent proxy (Windows agent). | n/a                    |

### Kerberos credentials

| Secret type     | Description                                                  | Example                              |
| --------------- | ------------------------------------------------------------ | ------------------------------------ |
| `password`      | Cleartext password.                                          | `username:Pa55w0rd!`                 |
| `pwhex`         | Hex-encoded UTF-16LE password.                               | `username:70617373…`                 |
| `nt` / `rc4`    | NT/RC4 hash.                                                 | `username:aad3b…`                    |
| `aes128`        | AES128 long-term key.                                        | `username:<32-hex>`                  |
| `aes256`        | AES256 long-term key.                                        | `username:<64-hex>`                  |
| `keytab`        | Kerberos keytab file in OctoPwn volatile storage.            | `/browserfs/volatile/admin.keytab`   |
| `keytabb64`     | Base64-encoded keytab inline.                                | `username:<b64>`                     |
| `ccache`        | MIT ccache file in OctoPwn volatile storage.                 | `/browserfs/volatile/krb5cc.ccache`  |
| `ccacheb64`     | Base64-encoded ccache inline.                                | `username:<b64>`                     |
| `kirbi`         | `.kirbi` ticket file (Rubeus-style).                         | `/browserfs/volatile/admin.kirbi`    |
| `kirbib64`      | Base64-encoded `.kirbi` inline.                              | `username:<b64>`                     |
| `pfxb64`        | Base64-encoded PFX (PKINIT certificate auth).                | `username:<b64>`                     |
| `agentproxy`    | Remote KDC over the wsnet agent proxy.                       | n/a                                  |
| `sspiproxy`     | OS SSPI session via wsnet agent proxy (Windows agent).       | n/a                                  |

!!! note "Required privileges"
    Most operations against the default `root\cimv2` namespace require local administrator rights on the target. Some namespaces (`SecurityCenter2`, `MicrosoftVolumeEncryption`, `MicrosoftDNS`) only exist on specific Windows editions or roles and will return `WBEM_E_INVALID_NAMESPACE` (`0x8004100e`) elsewhere — this is detected automatically and logged.

---

## Commands

### QUERY

#### query
Executes a raw WQL (WMI Query Language) statement against the active namespace (`root\cimv2` by default) and returns the result rows as JSON. This is the escape hatch when a curated `enum*` command doesn't exist for the data you need.

##### Parameters
- **query**: A WQL `SELECT` statement (e.g. `SELECT Name, ProcessId FROM Win32_Process WHERE Name LIKE '%lsass%'`).
- **to_print** *(optional, bool, default `True`)*: Whether to print the JSON result to the console.

---

### COMMAND EXECUTION

Three flavours of remote command execution. All three create a process via `Win32_Process.Create` (PID 0 of WMI's lineage); they differ in whether and how they retrieve standard output.

#### cmdexec
**Blind execution.** Spawns the command via `Win32_Process.Create` and returns immediately with the new PID and the method's return value. There is no output capture, no exit-code capture, and no completion signal — the caller has no visibility into what happened after the process started.

Use this when you only care that the command runs (planting a service, kicking off a scheduled task, dropping a file with `bitsadmin /transfer`) and don't need to read its output.

##### Parameters
- **command**: The full command line to execute (e.g. `cmd.exe /c whoami > C:\\Windows\\Temp\\out.txt`, `powershell -enc <b64>`).
- **to_print** *(optional, bool, default `True`)*: Whether to print the return value and PID.

#### cmdexecwithoutput
**Output-capturing execution via a registry exfil channel** for `cmd.exe` commands. The command is wrapped with `cmd.exe /Q /c`, its stdout+stderr redirected to a temp file, the temp file base64-encoded with `certutil -encodehex`, the encoded blob written to a randomly-named `HKLM\Software\Classes\<random>` registry value, then read back from that value via `StdRegProv`. The temp files and registry key are cleaned up afterwards.

Suitable for short, fast commands. Use [`pscmdexecwithoutput`](#pscmdexecwithoutput) for output that exceeds a single registry value's practical size limit.

##### Parameters
- **command**: The cmd.exe command (e.g. `whoami /all`, `ipconfig /all`, `systeminfo`).
- **exec_timeout** *(optional, int, default `5`)*: Seconds to wait for the command to complete before reading the registry. Increase this if the command takes longer to run, otherwise the read will fail and the data may be lost.
- **codec** *(optional, str, default `utf-8`)*: Decoder for the captured output.
- **to_print** *(optional, bool, default `True`)*: Whether to print the captured output.

!!! warning "Touches disk and the registry on the target"
    Both temp files (random UUIDs in `C:\Windows\Temp\`) and a registry key (`HKLM\Software\Classes\<random>`) are created and then deleted. Failed cleanups (e.g. AV killed `certutil` mid-flight) leave residual artifacts. The use of `certutil -encodehex` is also a well-known LOLBin signature.

#### pscmdexecwithoutput
**Output-capturing execution via a chunked registry exfil channel** for PowerShell commands. The command is run via `powershell -Command`, its output base64-encoded by PowerShell itself, then split into 16 KiB chunks and written to multiple registry values under a random `HKLM\Software\Classes\<random>` key. A REG_DWORD value records the total chunk count so the reader knows when to stop. OctoPwn reads each chunk back via `StdRegProv` and reassembles the original output.

Use when [`cmdexecwithoutput`](#cmdexecwithoutput) truncates or fails, or when the payload is naturally PowerShell.

##### Parameters
- **command**: The PowerShell one-liner. The `powershell -Command` prefix is added automatically if not already present.
- **exec_timeout** *(optional, int, default `5`)*: Seconds to wait between starting the command and reading the registry chunks. Increase for slow commands.
- **codec** *(optional, str, default `utf-16le`)*: Decoder. PowerShell's default redirected output is UTF-16LE with a BOM; the BOM is stripped automatically.
- **to_print** *(optional, bool, default `True`)*: Whether to print the reassembled output.

!!! tip "When to pick which `*exec*` variant"
    | Need                                                                              | Command                       |
    | --------------------------------------------------------------------------------- | ----------------------------- |
    | Fire and forget (planting tasks, kicking off long-running tools).                  | `cmdexec`                     |
    | Short cmd.exe / native binary output, latency-sensitive.                           | `cmdexecwithoutput`           |
    | PowerShell output, large payloads, structured data.                                | `pscmdexecwithoutput`         |

---

### SHADOW COPY

Volume Shadow Copy Service (VSS) operations via `Win32_ShadowCopy`. Useful for accessing locked files (`SAM`, `SYSTEM`, `NTDS.dit`) by reading their shadow-copy snapshots through SMB later.

#### shadowcopylist
Enumerates all existing VSS shadow copies on the target, including their device-object path (the form needed for SMB access — `\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy<n>`), the source volume, the install timestamp, and a derived `@GMT-YYYY.MM.DD-HH.MM.SS` label that matches the format used by SMB's previous-version share access.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print the formatted listing.

#### shadowcopycreate
Creates a new VSS shadow copy of the named volume. Returns the new shadow-copy ID and its `DeviceObject` path. Note that creating shadow copies often requires admin rights and can fail silently if the VSS service is not running or is misconfigured.

##### Parameters
- **volume**: Drive letter to snapshot (e.g. `C:`).
- **to_print** *(optional, bool, default `True`)*: Whether to print the created shadow copy details.

#### shadowcopydelete
Deletes a shadow copy by ID (as returned by `shadowcopylist` or `shadowcopycreate`).

##### Parameters
- **shadow_id**: The shadow copy ID (a `{...}` GUID string).
- **to_print** *(optional, bool, default `True`)*: Whether to print a confirmation message.

---

### ENUMERATION

A curated set of WQL queries dressed up as named commands. Each one targets a specific WMI class and prints a compact tabular or formatted output; all return JSON for scripting consumption.

| Command          | Source class / namespace                                          | What it returns                                                                  |
| ---------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `enumprocesses`  | `Win32_Process` (`root\cimv2`)                                    | PID, parent PID, image name, full command line.                                  |
| `enumservices`   | `Win32_Service` (`root\cimv2`)                                    | Service name, state, start mode, display name, binary path.                      |
| `sysinfo`        | `Win32_OperatingSystem` + `Win32_ComputerSystem` (`root\cimv2`)   | OS version, build, architecture, hostname, last boot, domain, RAM, CPU, model.   |
| `enumnetwork`    | `Win32_NetworkAdapterConfiguration` (`root\cimv2`)                | Adapters with IPs assigned, with MAC, IP, subnet, default gateway, DHCP, DNS.    |
| `enumusers`      | `Win32_LoggedOnUser` (`root\cimv2`)                               | Logged-on user → logon session associations.                                     |
| `enumav`         | `AntiVirusProduct` (`root\SecurityCenter2`)                       | Installed AV products, with parsed enabled/disabled and up-to-date state. **Client OS only** (Server editions don't expose this namespace). |
| `enumbitlocker`  | `Win32_EncryptableVolume` (`root\CIMv2\Security\MicrosoftVolumeEncryption`) | Per-volume BitLocker protection status and encryption method.            |
| `enumdns`        | `MicrosoftDNS_Zone` + `MicrosoftDNS_ResourceRecord` (`root\microsoftdns`) | DNS zones and record contents grouped by record type. **DC-only** namespace. Optional `domain` argument restricts to one zone. |
| `enumshares`     | `Win32_Share` (`root\cimv2`)                                      | Share name, local path, description, type (disk / IPC / printer).                |
| `enumsoftware`   | `Win32_Product` (`root\cimv2`)                                    | Installed MSI software with name, version, vendor, install date. **Slow** — see warning below. |
| `enumstartup`    | `Win32_StartupCommand` (`root\cimv2`)                             | Startup entries (Run keys, Startup folder, Run-Once, etc.) with command and user. |
| `enumdisks`      | `Win32_LogicalDisk` (`root\cimv2`)                                | Logical disks with type (local / network / removable / CD-ROM), size, free space, filesystem. |
| `enumpatches`    | `Win32_QuickFixEngineering` (`root\cimv2`)                        | Installed hotfixes / KB articles with description, install date, installer.      |

All `enum*` commands accept the same single optional parameter:

- **to_print** *(optional, bool, default `True`)*: Whether to print the formatted output. Returned JSON is unaffected.

`enumdns` additionally accepts:

- **domain** *(optional, str)*: Limit the dump to a single zone. If omitted, all zones are enumerated and dumped.

!!! warning "`enumsoftware` triggers Win32_Product side-effects"
    Querying `Win32_Product` causes the Windows Installer service to perform a **consistency check on every installed MSI package**, which can be slow (minutes) and may trigger application self-repair operations on misconfigured installs. This is a long-standing Microsoft-known behaviour, not an OctoPwn limitation. Prefer enumerating uninstall registry keys via [`regread`](#regread) (`HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall`) when speed matters.

!!! info "`enumav`, `enumbitlocker`, `enumdns` open separate WMI namespaces"
    These three commands open a new `IWbemServices` session against a non-default WMI namespace (`SecurityCenter2`, `MicrosoftVolumeEncryption`, `microsoftdns` respectively), perform their query, then disconnect. If the namespace doesn't exist on the target (e.g. `SecurityCenter2` on a Windows Server, `MicrosoftDNS` on a non-DC), the command returns an empty result with an explanatory message rather than failing.

---

### RDP MANAGEMENT

Toggle RDP and its security-related knobs via `StdRegProv` and `netsh`.

#### rdpenable
Enables Remote Desktop on the target by setting `HKLM\System\CurrentControlSet\Control\Terminal Server\fDenyTSConnections` to `0`. Optionally also enables the matching Windows Firewall rule group.

##### Parameters
- **firewall** *(optional, str, default `yes`)*: `yes` / `true` / `1` to enable the "remote desktop" firewall rule group via `netsh advfirewall firewall set rule group="remote desktop"`. Anything else skips the firewall step.
- **to_print** *(optional, bool, default `True`)*: Whether to print status messages.

#### rdpdisable
Disables Remote Desktop by setting `fDenyTSConnections` to `1`. Optionally also disables the matching firewall rule group.

##### Parameters
- **firewall** *(optional, str, default `yes`)*: As for `rdpenable` — controls whether the firewall rule group is also disabled.
- **to_print** *(optional, bool, default `True`)*: Whether to print status messages.

#### rdpstatus
Reports three pieces of RDP-relevant state read straight from the registry: whether RDP is enabled (`fDenyTSConnections`), the current listening port (`HKLM\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp\PortNumber`), and the configured Restricted Admin Mode value (`HKLM\System\CurrentControlSet\Control\Lsa\DisableRestrictedAdmin`).

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print the status block.

#### rdpramenable
Enables **Restricted Admin Mode** on the target by setting `HKLM\System\CurrentControlSet\Control\Lsa\DisableRestrictedAdmin` to `0`. With Restricted Admin Mode enabled, the [RDP client](./rdp.md) can authenticate using NT hashes / AES keys directly (pass-the-hash over RDP) instead of a cleartext password.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print a confirmation message.

!!! warning "Lowers the target's authentication security"
    Restricted Admin Mode disables outbound credential delegation from the RDP session and exposes a hash-only authentication path. It is rarely a good idea outside of an active engagement and should be disabled again with [`rdpramdisable`](#rdpramdisable) when finished.

#### rdpramdisable
Disables Restricted Admin Mode by **deleting** the `DisableRestrictedAdmin` registry value. The default Windows behaviour (no value present) is to disallow Restricted Admin Mode.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print a confirmation message.

---

### REGISTRY

A general-purpose registry interface backed by `StdRegProv`. Hive names are case-insensitive and accept both short (`HKLM`) and long (`HKEY_LOCAL_MACHINE`) forms; subkey separators can be either backslashes (`\`) or forward slashes (`/`).

| Hive alias | Long form              | StdRegProv hive ID |
| ---------- | ---------------------- | ------------------ |
| `HKCR`     | `HKEY_CLASSES_ROOT`    | `0x80000000`       |
| `HKCU`     | `HKEY_CURRENT_USER`    | `0x80000001`       |
| `HKLM`     | `HKEY_LOCAL_MACHINE`   | `0x80000002`       |
| `HKU`      | `HKEY_USERS`           | `0x80000003`       |
| `HKCC`     | `HKEY_CURRENT_CONFIG`  | `0x80000005`       |

Supported value types: `REG_SZ`, `REG_EXPAND_SZ`, `REG_BINARY`, `REG_DWORD`, `REG_MULTI_SZ`, `REG_QWORD`. Type aliases for `regwrite` accept the full name (`reg_dword`) or the short form (`dword`).

#### regread
Reads from the registry. With no `value` argument, lists all subkeys and values under the given key (auto-detecting each value's type via `EnumValues` and reading it with the matching getter). With a `value` argument, reads that specific value (auto-detecting its type, defaulting to `REG_SZ` if the value's type cannot be determined).

##### Parameters
- **keypath**: Full registry path including hive (e.g. `HKLM\Software\Microsoft\Windows NT\CurrentVersion`).
- **value** *(optional, str)*: Specific value name to read. Omit to enumerate the entire key.
- **to_print** *(optional, bool, default `True`)*: Whether to print the result.

#### regwrite
Writes a value to the registry. The value type is auto-detected: if the value already exists, its existing type is reused; otherwise, integer-looking data becomes `REG_DWORD` and everything else becomes `REG_SZ`. Pass `type` explicitly to override.

##### Parameters
- **keypath**: Full registry path including hive.
- **value**: Name of the value to write.
- **data**: The data to write. Cast to the appropriate type (`int` for DWORD/QWORD, `str` for the others).
- **type** *(optional, str)*: Explicit type override — one of `sz`, `expand_sz`, `dword`, `multi_sz`, `qword` (or their `reg_*` long forms). Note: `REG_BINARY` writes are not currently supported.
- **to_print** *(optional, bool, default `True`)*: Whether to print a confirmation message.

#### regdelete
Deletes a registry value (when `value` is given) or an entire registry key (when only `keypath` is given). Key deletion is non-recursive and will fail if the key has subkeys.

##### Parameters
- **keypath**: Full registry path including hive.
- **value** *(optional, str)*: Specific value name to delete. Omit to delete the entire key.
- **to_print** *(optional, bool, default `True`)*: Whether to print a confirmation message.

---

## Limitations

- **No anonymous / null-session access.** WMI requires authenticated access; both the `NTLM` and `KERBEROS` `atype` options need a real credential.
- **Requires TCP/135 + RPC dynamic ports.** If only SMB (445) is reachable, use the SMB client instead. If only WinRM (5985 / 5986) is reachable, use the WinRM client.
- **`cmdexec` is blind.** No exit code, no stdout, no completion signal — only the new PID and the `Win32_Process.Create` return value. Use `cmdexecwithoutput` or `pscmdexecwithoutput` if you need to see the result.
- **`*exec*withoutput` write to disk and the registry on the target.** Both temp files in `C:\Windows\Temp\` and a registry key under `HKLM\Software\Classes\` are created and (if the operation completes) cleaned up. Operations interrupted mid-flight (AV, timeout, network drop) leave residue.
- **`pscmdexecwithoutput` chunks at 16 KiB per registry value** and stores an explicit chunk count. Very large outputs (hundreds of chunks) increase the chance that `exec_timeout` is too short and a chunk read fails.
- **`enumav` is client-OS only.** The `SecurityCenter2` namespace does not exist on Windows Server editions; the command returns an explanatory empty result rather than failing.
- **`enumdns` is DC-only.** The `microsoftdns` namespace requires the AD DNS Server role; the command returns an explanatory empty result on non-DC targets.
- **`enumsoftware` is slow and triggers Windows Installer side-effects.** See the warning under [Enumeration](#enumeration). Prefer `regread HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall` for a faster, side-effect-free inventory.
- **`regwrite` does not support `REG_BINARY`.** Write that type via the underlying `StdRegProv.SetBinaryValue` directly with `query`-style WMI calls if needed.
- **`regdelete` of a key is non-recursive.** Delete child values / subkeys first, then the key.
- **Registry exfil leaves a forensic trail.** `cmdexecwithoutput` and `pscmdexecwithoutput` both create randomly-named keys under `HKLM\Software\Classes\` plus `cmd.exe` / `powershell.exe` / `certutil.exe` / `reg.exe` / `Out-File` invocations — all standard EDR-detected patterns. Do not assume these commands are stealthy.
