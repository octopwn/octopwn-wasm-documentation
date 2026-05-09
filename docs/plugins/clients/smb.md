# SMB Client

The **SMB Client** is OctoPwn's full-fat SMB / DCERPC-over-SMB swiss-army knife — built on top of [`aiosmb`](https://github.com/skelsec/aiosmb) and exposing virtually every interactive primitive the library implements: file operations, user / group / session enumeration, the full SCM (services), Task Scheduler, Remote Registry, Print Spooler (incl. PrinterBug + PrintNightmare), AD CS certificate enrollment (ESC1 / ESC3 in this client), NTLM-relay coercion, six different DCERPC-based command-execution methods, three independent secrets-dumping engines, DPAPI harvesting, GPP `cpassword` decryption, BloodHound-equivalent VHDX offline secretsdump, snaffler-style file scanning, WMI queries, shadow-copy management, and an "agent over SMB named pipe" tunnel.

This is the largest client in OctoPwn — almost 100 callable commands. The page is organised so the [Transport](#transport), [Authentication](#authentication) and [GUI](#gui-experience) sections come first, then every command grouped by its `help` category, then a short [Additional commands](#additional-commands) section for utilities that are callable but not listed in `help`.

---

## Transport

Three module names map to the same underlying client — they only differ in the dialect string OctoPwn uses to seed `aiosmb`:

| Module name | Dialect family       | Default port |
| ----------- | -------------------- | ------------ |
| `SMB`       | SMB2 / SMB3 (auto)   | `445`        |
| `SMB2`      | SMB2 / SMB3 (auto)   | `445`        |
| `SMB3`      | SMB2 / SMB3 (auto)   | `445`        |

!!! note "There is no SMB1"
    In the GUI the protocol picker offers `SMB`, `SMB2` and `SMB3`. Despite the name, **`SMB` is not SMB1** — SMB1 is not implemented. All three are functionally identical and end up using `aiosmb`'s SMB2 / SMB3 auto-negotiation (the server picks the highest mutually-supported dialect during the negotiate exchange). The three module entries exist for backwards compatibility with older session blobs and for parameter symmetry with other transports.

---

## Authentication

Two `atype`s are supported — both Microsoft-Windows authentication mechanisms. There is no PLAIN, no SIMPLE, no anonymous bind here (anonymous SMB *can* be done with `none` / no creds, but it is selected at the credential level, not via `atype`).

### `NTLM` — NTLM SSP

Standard NTLM SSP — the workhorse for everything from local-machine accounts to AD users.

| Secret type     | Description                                                     |
| --------------- | --------------------------------------------------------------- |
| `password`      | Cleartext password.                                             |
| `pwhex`         | Hex-encoded UTF-16LE password.                                  |
| `nt` / `rc4`    | NT hash (pass-the-hash).                                        |
| `agentproxy`    | Remote NTLM signer over the wsnet agent proxy.                  |
| `sspiproxy`     | OS SSPI session via the wsnet agent proxy (Windows agent only). |

### `KERBEROS` — Kerberos via SASL GSSAPI

Standard Kerberos / SPNEGO. Requires reachability to a KDC (set on the credential / target) and the SMB SPN `cifs/<host>@<REALM>` (auto-built for you).

| Secret type     | Description                                                     |
| --------------- | --------------------------------------------------------------- |
| `password`      | Cleartext password.                                             |
| `pwhex`         | Hex-encoded UTF-16LE password.                                  |
| `nt` / `rc4`    | NT/RC4 hash.                                                    |
| `aes128`        | AES128 long-term key.                                           |
| `aes256`        | AES256 long-term key.                                           |
| `keytab`        | Keytab file in OctoPwn volatile storage.                        |
| `keytabb64`     | Base64-encoded keytab inline.                                   |
| `ccache`        | MIT ccache file in OctoPwn volatile storage.                    |
| `ccacheb64`     | Base64-encoded ccache inline.                                   |
| `kirbi`         | `.kirbi` ticket file (Rubeus-style).                            |
| `kirbib64`      | Base64-encoded `.kirbi` inline.                                 |
| `pfxb64`        | Base64-encoded PFX (PKINIT certificate auth via Kerberos).      |
| `agentproxy`    | Remote KDC over the wsnet agent proxy.                          |
| `sspiproxy`     | OS SSPI session via the wsnet agent proxy (Windows agent only). |

---

## GUI experience

SMB does **not** ship a custom React component — it uses OctoPwn's generic client session window. The header carries the standard tabs plus a single SMB-specific addition (**Services**):

- **Commands** — clickable buttons for every CLI command, grouped exactly like the [Commands](#commands) section below.
- **Files** — a full SMB file browser. Tree-style sidebar with shares as the root, expandable directories, and a right-hand pane that shows the contents of the selected directory with sortable name / size / date columns and a list / grid view toggle. Right-click context menu offers download, upload (drag-and-drop is also supported), delete, rename, mkdir. View-in-place works for text files. The browser does **not** use the regular `cd` / `ls` / `get` / `put` console commands — instead, it talks to the backend over a dedicated streamed-RPC channel (`remoteShares`, `remoteListDirectory`, `remoteDownloadFile`, `remoteOpenFile`, `remoteReadFile`, `remoteCreateFile`, `remoteCloseFile`, `remotedeleteFile`, `remotedeleteDirectory`, `remotecreateDirectory`) so that browser navigation does not interfere with the console state.
- **Services** — SMB-only tab. Renders the catalogue produced by [`services`](#services) with searchable name / display-name / status columns and a Refresh button (re-runs `services` on demand).
- **Jobs** — long-running background commands and a stop button.
- **History** — full command history for the session.
- **Debug** / **Settings** — protocol-level debug output and connection parameters.
- **AI** — appears when an LLM provider is configured globally. Uses the SMB-specific system prompt baked into the backend (`OCTOPWN_SMB_LLM_PROMPT`) so the assistant only proposes SMB commands.

Tab-completion in the console is share / directory / file aware — typing `use <Tab>` cycles through known shares, `cd <Tab>` cycles through subdirectories of the current directory, `get <Tab>` / `del <Tab>` cycle through files.

---

## Commands

Every command below is callable from the session console (and most from the **Commands** GUI tab as a button). The grouping mirrors the `help` output of the running session.

All commands return `(result, error)` on the backend. Many also accept `to_print=False` to suppress the human-readable output while still returning the structured result.

---

### CONNECTION

#### login
Opens the SMB connection, performs the chosen authentication exchange, fetches the share list (unless [`nodce`](#nodce) was issued first), and starts a connection-monitor task that auto-fires `logout` if the server drops the link.

#### logout
Closes every open file handle, cancels the connection monitor, terminates the underlying `SMBConnection`, and resets the connection-status pill.

#### nodce
Disables automatic share listing on login. Useful when authenticating as a user that has access to a single share but not to `IPC$` — without this flag the auto-`shares` call inside `login` fails and the session is torn down. Must be issued before `login`.

---

### FILE OPERATIONS

#### shares
Lists every accessible SMB share (`srvsvc.NetrShareEnumAll`) and caches the result for tab-completion.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print the share list.

#### use
Mounts a share by name (case-insensitive). Connects the share, switches into its root directory, refreshes the directory listing, and changes the prompt to `[\\<host>\<share>] $`.

##### Parameters
- **share_name**: Name of the share (e.g. `C$`, `ADMIN$`, `Users`).

#### cd
Change directory inside the currently-mounted share. Accepts `..` to go up one level. Refreshes the new directory's contents on entry.

##### Parameters
- **directory_name**: Name of the subdirectory (relative to the current directory).

#### ls
List the current directory's contents (cached from the last refresh; use [`refreshcurdir`](#refreshcurdir) to force a re-list).

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### dir
Alias for [`ls`](#ls).

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### refreshcurdir
Re-lists the current directory from the server (flushes the local cache).

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print "Directory refreshed!" on success.

#### get
Downloads a file from the current directory to the OctoPwn working directory. Supports `fnmatch`-style globs (`*.txt`, `secret*.bak`) — every match is downloaded sequentially. The optional volume-shadow timestamp suffix `@@<vstimestamp>` (parsed by `aiosmb.commons.utils.tschecker.tssplit`) downloads from a specific snapshot revision (see [`snapshots`](#snapshots)). Prints throughput every 2 seconds during transfer.

##### Parameters
- **file_name**: File name in the current directory. May be a glob, optionally suffixed with `@@<vstimestamp>` for snapshot reads.

#### put
Uploads a local file (resolved against the OctoPwn working directory) into the current SMB directory under the same basename. Reads in 65 MiB chunks; prints throughput every 2 seconds.

##### Parameters
- **file_name**: Local file path (relative to OctoPwn working directory).

#### del
Deletes a file from the current directory. Refreshes the directory afterwards.

##### Parameters
- **file_name**: File name in the current directory.

#### mkdir
Creates a subdirectory under the current directory.

##### Parameters
- **directory_name**: Name of the new directory.

#### getfilesd
Fetches the security descriptor of a file in the current directory and prints it as SDDL.

##### Parameters
- **file_name**: File name in the current directory.

#### getdirsd
Fetches the security descriptor of the current directory and prints it as SDDL.

#### enumall
Recursively walks every share and every directory, printing each entry's full UNC path with a `[F]` / `[D]` marker. Use sparingly on production hosts — every directory triggers an SMB round-trip.

##### Parameters
- **depth** *(optional, int, default `3`)*: Recursion depth (per share).

#### snapshots
Lists every Volume Shadow Copy that backs the current share or directory. Each entry is a timestamp string that can be appended to a [`get`](#get) target as `<filename>@@<timestamp>` to download the snapshotted version of a file.

##### Parameters
- **path** *(optional, str, default `\`)*: Optional path inside the share (defaults to the share root).

---

### USER / GROUP MANAGEMENT

All listing commands here use SAMR / LSARPC over `\PIPE\samr` and `\PIPE\lsarpc` — they require a fully-functional DCE/RPC channel.

#### users
Lists every user account in the named domain (or the host's primary domain when omitted). Prints `<sAMAccountName> <SID>` per row.

##### Parameters
- **domain** *(optional, str)*: Domain name. Default: enumerate the primary domain.
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### domains
Lists every domain known to the host (the primary domain plus `Builtin`).

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### domaingroups
Lists every group inside a named domain.

##### Parameters
- **domain_name**: Domain name (e.g. `CONTOSO`, `Builtin`).
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### groupmembers
Lists members of an arbitrary group.

##### Parameters
- **domain_name**: Domain name.
- **group_name**: Group name.
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### localgroups
Lists every local group (members of the `Builtin` domain).

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### localgroupmembers
Lists members of a single local group (resolves under the `Builtin` domain).

##### Parameters
- **group_name**: Local group name (e.g. `Administrators`, `Backup Operators`).
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### sessions
Lists every active SMB session against the target (`srvsvc.NetrSessionEnum`). Useful for finding which users are currently logged on and from which IPs.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### whoami
Calls the LSARPC `LsarGetUserName` extended op plus a token-info lookup — returns the bound principal's username, domain, SID, and resolved group memberships. Caches the result on the session for later use.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### addsidtolocalgroup
Adds a SID to a local (`Builtin`) group via SAMR (`SamrAddMemberToAlias`). Requires Administrators / `SeTakeOwnershipPrivilege`-equivalent rights.

##### Parameters
- **group_name**: Local group name.
- **sid**: SID to add.

---

### SERVICE OPERATIONS

All service commands use the SCM (`\PIPE\svcctl`).

#### services
Lists every service on the target with name / display name / current status. Optionally also returns the full per-service config (exec path, start type, etc.) at the cost of an extra round-trip per service. Streams the result to the GUI **Services** tab in 100-row batches.

##### Parameters
- **with_config** *(optional, bool, default `False`)*: Also fetch each service's configuration block.
- **to_print** *(optional, bool, default `True`)*: Whether to print the result table.

#### servicegetstatus
Fetches a single service's full configuration block.

##### Parameters
- **service_name**: Service short name (e.g. `RemoteRegistry`).
- **to_print** *(optional, bool, default `True`)*: Whether to print the config.

#### servicestart
Starts a stopped service.

##### Parameters
- **service_name**: Service short name.
- **to_print** *(optional, bool, default `True`)*: Whether to print "Service started".

#### serviceen
Enables a disabled service (changes the start type to `SERVICE_DEMAND_START`). Pair with [`servicestart`](#servicestart) to actually start it after enabling.

##### Parameters
- **service_name**: Service short name.
- **to_print** *(optional, bool, default `True`)*: Whether to print "Service enabled".

#### servicecreate
Creates a new service with the given binary path. The service is created with `SERVICE_DEMAND_START`; use [`servicestart`](#servicestart) to actually run it.

##### Parameters
- **service_name**: Service short name.
- **command**: Command line / binary path the service will execute.
- **display_name** *(optional, str)*: Display name. Defaults to the short name.
- **to_print** *(optional, bool, default `True`)*: Whether to print "Service created!".

#### servicedeploy
Uploads a local binary into the current SMB directory and creates a service that points to it (in one shot). The service still needs to be started via [`servicestart`](#servicestart).

##### Parameters
- **path_to_exec**: Local path to the binary (relative to OctoPwn working directory).
- **remote_path**: Remote filename — used as the binary basename inside the current directory.
- **to_print** *(optional, bool, default `True`)*: Whether to print "Service deployed!".

#### servicedel
Stops (if running) and deletes a service.

##### Parameters
- **service_name**: Service short name.
- **to_print** *(optional, bool, default `True`)*: Whether to print "Service deleted!".

---

### COMMAND EXECUTION

OctoPwn ships **seven** different remote-command-execution primitives over the SMB session — pick the one your target lets you use and your detection budget allows. All of them upload their stdout via SMB and stream it back to the console.

#### servicecmdexec
Classic PSExec-style execution: creates a temporary service whose binary is `cmd.exe /c <command> > <tempfile>`, starts it, reads `<tempfile>` from the share, deletes the file and the service. Loud (creates EID 7045 service-installed events).

##### Parameters
- **command**: Shell command to execute.
- **timeout** *(optional, int, default `1`)*: Read timeout in seconds.
- **to_print** *(optional, bool, default `True`)*: Whether to print stdout.

#### taskcmdexec
Same primitive but uses the Task Scheduler instead of the SCM (registers a one-shot task, runs it, deletes it). Quieter than `servicecmdexec` for some EDRs.

##### Parameters
- **command**: Shell command to execute.
- **timeout** *(optional, int, default `2`)*: Read timeout in seconds.
- **to_print** *(optional, bool, default `True`)*: Whether to print stdout.

#### taskcmdexecas
Like `taskcmdexec`, but registers the task to run **as a different user** (by SID). Used to escalate from `SYSTEM` to a logged-on user (or vice-versa) without needing that user's password.

##### Parameters
- **run_as_sid**: SID of the principal to run the task as.
- **command**: Command to execute.
- **arguments** *(optional, str)*: Arguments to the command.
- **cleanup** *(optional, bool, default `True`)*: Delete the task afterwards.
- **to_print** *(optional, bool, default `True`)*: Whether to print the result.

#### wmicmdexec
Runs the command via WMI's `Win32_Process.Create` over DCOM (i.e. the classic `wmic process call create` primitive). Returns the spawned PID and the WMI return value. **Does not** capture stdout — pair with `> \\?\C:\…\out.txt` redirection and a follow-up [`get`](#get) if you need the output.

##### Parameters
- **command**: Command to execute.
- **to_print** *(optional, bool, default `True`)*: Whether to print the result.

#### mmc20cmdexec
DCOM lateral-movement classic — uses the `MMC20.Application` COM object's `ExecuteShellCommand` method. Same caveat as `wmicmdexec`: no stdout capture.

##### Parameters
- **command**: Command to execute.
- **to_print** *(optional, bool, default `True`)*: Whether to print the result.

#### shellwindowscmdexec
DCOM lateral-movement via the `Shell.Application` -> `ShellWindows` -> `Document.Application.ShellExecute` chain. No stdout capture.

##### Parameters
- **command**: Command to execute.
- **to_print** *(optional, bool, default `True`)*: Whether to print the result.

#### shellbrowserwindowscmdexec
DCOM lateral-movement via `ShellBrowserWindow` -> `Document.Application.ShellExecute`. No stdout capture.

##### Parameters
- **command**: Command to execute.
- **to_print** *(optional, bool, default `True`)*: Whether to print the result.

---

### REGISTRY OPERATIONS

These commands talk to the Remote Registry service via `\PIPE\winreg`. The `RemoteRegistry` service must be running on the target — [`regdump`](#regdump) starts it for you, the others assume it is already up.

#### reglistusers
Enumerates `HKEY_USERS` and lists every user-hive SID, plus resolves each SID back to a sAMAccountName when possible. Effectively "who has ever logged on to this machine".

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### regsave
Saves a registry hive to a file on the remote host (uses `RegSaveKey`). Output path must be writable by the calling user.

##### Parameters
- **hive_name**: Hive to save (e.g. `HKLM\SAM`, `HKLM\SYSTEM`, `HKLM\SECURITY`).
- **file_path**: Remote output path (e.g. `C:\Windows\Temp\sam.bin`).

#### regquery
Enumerates the subkeys of a registry path.

##### Parameters
- **path**: Full registry path (e.g. `HKLM\SOFTWARE\Microsoft`).
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### regenumvalues
Enumerates every value of a registry key. Long values are truncated in the console (use [`reggetvalue`](#reggetvalue) to get the full payload).

##### Parameters
- **path**: Full registry path.
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### reggetvalue
Reads a single registry value.

##### Parameters
- **path**: Full registry path.
- **value_name**: Value name.
- **to_print** *(optional, bool, default `True`)*: Whether to print result.

#### regsetvalue
Writes to an existing registry value (preserves the existing value type — for `BINARY` values, supply the new payload as a hex string).

##### Parameters
- **path**: Full registry path.
- **value_name**: Value name.
- **value_data**: New value (hex-encoded for `BINARY` types).
- **to_print** *(optional, bool, default `True`)*: Whether to print "Value set!".

#### regdeletevalue
Deletes a registry value.

##### Parameters
- **path**: Full registry path.
- **value_name**: Value name.
- **to_print** *(optional, bool, default `True`)*: Whether to print "Value deleted!".

#### regdeletekey
Deletes a subkey of the named registry path. The key must be empty.

##### Parameters
- **path**: Parent registry path.
- **key_name**: Subkey to delete.
- **to_print** *(optional, bool, default `True`)*: Whether to print "Key deleted!".

#### regcreatekey
Creates a new subkey under the named registry path.

##### Parameters
- **basepath**: Parent registry path.
- **key_name**: Name of the new subkey.
- **to_print** *(optional, bool, default `True`)*: Whether to print "Key created!".

#### regcreatevalue
Creates a new value under a registry key. Supports the standard registry value types: `SZ`, `BINARY`, `DWORD`, `DWORD_LITTLE_ENDIAN`, `DWORD_BIG_ENDIAN`, `EXPAND_SZ`, `LINK`, `MULTI_SZ`, `NONE`, `QWORD`, `QWORD_LITTLE_ENDIAN`. For `BINARY` values, supply the data as a hex string.

##### Parameters
- **path**: Full registry path.
- **value_name**: Value name.
- **value_type**: One of the supported types above (case-insensitive).
- **value_data**: Value payload.
- **to_print** *(optional, bool, default `True`)*: Whether to print "Value created!".

---

### TASK OPERATIONS

#### tasks
Lists every scheduled task on the target.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### taskregister
Registers a new scheduled task from an XML template file (loaded from the OctoPwn working directory).

##### Parameters
- **template_file**: Local path to the task XML.
- **task_name** *(optional, str)*: Task name. If omitted, derived from the template.

#### taskdel
Deletes a scheduled task.

##### Parameters
- **task_name**: Task name.

---

### PRINTER OPERATIONS

#### printerenumdrivers
Enumerates printer drivers via the `RPRN` interface (`\PIPE\spoolss`). A successful enumeration confirms the spooler is reachable and is the precondition for the [`printnightmare`](#printnightmare) check.

---

### NTLM COERCION

#### printerbug
Triggers the **PrinterBug** (RPRN `RpcRemoteFindFirstPrinterChangeNotification` / `RpcRemoteFindFirstPrinterChangeNotificationEx`) authentication coercion — forces the target to authenticate to `attacker_ip` over SMB. The classic NTLM-relay primitive.

##### Parameters
- **attacker_ip**: IP / hostname the target should authenticate to.
- **to_print** *(optional, bool, default `True`)*: Whether to print "Printerbug triggered OK!".

#### coersion
Runs the full **multi-protocol coercion** suite from `aiosmb`'s `examples.coersion` module — fires PetitPotam (`MS-EFSR`), DFSCoerce (`MS-DFSNM`), PrinterBug (`MS-RPRN`), ShadowCoerce (`MS-FSRVP`) and every other implemented coercion at the listener IP, with optional pacing between attempts. Use this when you want to spray every coercion vector at once.

##### Parameters
- **listenip**: IP / hostname the target should authenticate to.
- **delay** *(optional, int, default `1`)*: Delay between attempts (in milliseconds).
- **to_print** *(optional, bool, default `True`)*: Whether to print progress.

---

### CERTIFICATE OPERATIONS

These commands talk to AD CS over MS-ICPR (the same RPC interface used by Certify). The connection runs piggy-backed on the existing SMB authentication context — so they only work if the bound user can reach an Enterprise CA.

#### certreq
Requests a certificate from an Enterprise CA. When `altname` or `altsid` is supplied, this becomes the **ESC1** abuse path: enrol against a template that has `ENROLLEE_SUPPLIES_SUBJECT_ALT_NAME` and ask for a cert that authenticates as someone else. The resulting PFX (password `admin`) is auto-stored as a credential in the OctoPwn store; on a successful ESC1 hit, the result is also fed into the vulnerability scanner as an `ESC1Result`.

##### Parameters
- **service**: ADCS enrollment service name (no domain part — e.g. `WIN-CA01-CA`).
- **template**: Certificate template name.
- **cn**: CN for the certificate (in `username@fqdn` format, e.g. `victim@test.corp`).
- **altname**: Alternative SAN UPN for impersonation (in `username@fqdn` format). Use empty string to skip.
- **altsid** *(optional, str)*: Alternative NTDS object SID to embed for the **strong-mapping** ESC9 / ESC10 / ESC16 abuse path.

#### certreqonbehalf
**ESC3** abuse: enrols on behalf of another principal using a previously-obtained "Enrollment Agent" certificate. The result is fed into the vulnerability scanner as an `ESC3Result` and the resulting PFX is auto-stored.

##### Parameters
- **service**: ADCS enrollment service name.
- **template**: Certificate template name (the one that allows enrol-on-behalf-of).
- **cn**: CN for the certificate.
- **altname**: SAN UPN of the principal to impersonate.
- **onbehalf**: Principal to enrol on behalf of (typically the same as `altname`).
- **enroll_cert**: Local path to the Enrollment Agent PFX bundle (in OctoPwn working directory).
- **enroll_password** *(optional, str)*: Password for the PFX.

---

### SECRETS DUMPING

Three independent dumping engines + DPAPI domain-backup-keys + DCSync over the SMB-tunnelled DRSUAPI.

#### regdump
Classical "dump the SAM/SYSTEM/SECURITY hives" attack. Enables and starts the `RemoteRegistry` service (if not running), `RegSaveKey`s the three hives to `C:\Windows\Temp\<random>`, downloads them, parses them with `pypykatz`, deletes the remote files, and stores the discovered secrets (machine account hash, local accounts, cached domain logons, LSA secrets, DCC2, etc.) into the OctoPwn credential store. Caches the result on the session so subsequent calls (or [`dpapisecretsremoteregdump`](#dpapisecretsremoteregdump)) return instantly.

##### Parameters
- **waittime** *(optional, int, default `5`)*: Seconds to wait between starting `RemoteRegistry` / saving / reading the hive (writes are async on the server).
- **to_print** *(optional, bool, default `True`)*: Whether to print progress.

#### regdump2
Same outcome as [`regdump`](#regdump) but uses `pypykatz`'s `RemoteRegistry` driver — reads the hive **on the wire** without ever writing it to disk on the target. Stealthier (no file artefacts) but slower for huge SECURITY hives. Cached on the session like `regdump`.

##### Parameters
- **waittime** *(optional, int, default `5`)*: Reserved (currently unused — kept for parameter symmetry).
- **to_print** *(optional, bool, default `True`)*: Whether to print progress.

#### lsassdump
Dumps `LSASS` remotely and parses the minidump on the wire (no local download). Two execution methods are supported:

- `service` (default) — creates a one-shot service that runs `comsvcs.dll`'s `MiniDump` / similar primitive.
- `task` — same, via the Task Scheduler.

The remote dump file is parsed with `apypykatz` (every package: msv1_0, kerberos, wdigest, tspkg, livessp, ssp, dpapi, cloudap, …) and **deleted** afterwards. Output is in pypykatz "grep" format.

##### Parameters
- **method** *(optional, str, default `service`)*: `service` or `task`.

#### dcsync
Performs a DCSync (DRSUAPI `GetNCChanges`). When `username` is supplied, only that account is dumped; otherwise the entire NTDS is replicated and written to a `dcsync_<random>.txt` file in the OctoPwn working directory (in the WASM build, the file lives in `/volatile/`). When `storesecrets=True`, every recovered secret is also pushed into the OctoPwn credential store.

The underlying transport here is **SMB-tunnelled DRSUAPI** — the DCERPC connection is opened over the existing SMB session against `\PIPE\drsuapi`, **not** as a separate TCP connection on a dynamic port (which is what the dedicated [DCEDRSUAPI client](./dcedrsuapi.md) does). Same end result, different transport.

##### Parameters
- **username** *(optional, str)*: sAMAccountName to dump. Default: dump everything.
- **domain** *(optional, str)*: Domain to dump from. Default: target's primary domain.
- **storesecrets** *(optional, bool, default `False`)*: Push every discovered secret into the credential store.
- **to_print** *(optional, bool, default `True`)*: Whether to print progress.

#### backupkeys
Retrieves the **DPAPI domain backup keys** from a Domain Controller via LSARPC (`LsaRetrievePrivateData("G$BCKUPKEY_PREFERRED")` + the per-GUID lookups). Writes every recovered key to disk in three formats: `<guid>_legacykey.key` (the legacy machine key), `<guid>.pvk` (the PVK private key file), `<guid>.der` (the matching certificate). With these keys you can decrypt **every user's DPAPI blobs in the entire domain** offline.

---

### SECRETS HUNTING

#### cpasswd
Searches `SYSVOL` for GPP `cpassword` XML files (`Groups.xml`, `Services.xml`, `ScheduledTasks.xml`, `DataSources.xml`, `Drives.xml`, `Printers.xml`) up to depth 5. For every hit, decrypts the AES-encrypted password using the well-known Microsoft key (CVE-2014-1812) and stores the resulting credential in the OctoPwn credential store.

#### snaffler
Runs a [Snaffler](https://github.com/SnaffCon/Snaffler) implementation (via [`pysnaffler`](https://github.com/skelsec/pysnaffler)) starting from the **current SMB directory**. Navigate to where you want to scan (`use SYSVOL` then `cd policies` for example), then run `snaffler`. By default uses pysnaffler's bundled ruleset; pass `rulesdir` to use your own. Files matching a "grab" rule are downloaded to `snaffler_downloads/`, scanned for sensitive content, then either kept (on a content match) or deleted.

##### Parameters
- **rulesdir** *(optional, str)*: Path to a directory of `.toml` rules. Default: bundled ruleset.
- **gen_filelist** *(optional, bool, default `False`)*: Also write a flat list of every file scanned to `<dirname>.txt`.

#### dpapifiles
Walks the remote filesystem and downloads every DPAPI artefact it can find:

- Per-user masterkey files from `AppData\Roaming\Microsoft\Protect` and `AppData\Local\Microsoft\Protect`.
- Per-user credential files from `AppData\Roaming\Microsoft\Credentials` and `AppData\Local\Microsoft\Credentials`.
- Chrome `Local State`, `Login Data` and `Cookies` for every user.
- The `SYSTEM` account's masterkey + credential files from `Windows\System32\config\systemprofile\…` and `Windows\System32\Microsoft\Protect\S-1-5-18\User`.
- The `OBJECTS.DATA` WMI database file (containing CCM / SCCM `NAA Credentials`, `Task Sequences`, `Collection Variables` and other secrets).

Every artefact is downloaded, hex-encoded into a JSON blob (`dpapi_secrets_encrypted_<host>.json`) and the local files are deleted. **No decryption is performed** — pass the result to [`dpapisecretshives`](#dpapisecretshives) or [`dpapisecretsremoteregdump`](#dpapisecretsremoteregdump) for that.

##### Parameters
- **skipusers** *(optional, bool, default `False`)*: Skip the per-user walk and only collect SYSTEM-level + WMI artefacts.

#### dpapisecretshives
End-to-end DPAPI offline decryption: combines [`dpapifiles`](#dpapifiles) with **locally-supplied registry hives** (SYSTEM / SAM / SECURITY) to derive the DPAPI prekeys, then decrypts every masterkey, credential file, and the WMI / SCCM blobs (NAA creds, Task Sequence secrets, Collection Variables, Other Secrets) found on the host. Decrypted masterkeys and credential files are persisted to the session DB (`DPAPI_MASTERKEY`, `DPAPI_MASTERKEYFILE`, `DPAPI_CREDENTIALFILE`, `DPAPI_WMIFILEDATA`).

##### Parameters
- **systemhive**: Local path to a SYSTEM hive (in OctoPwn working directory).
- **samhive**: Local path to a SAM hive.
- **securityhive**: Local path to a SECURITY hive.
- **password** *(optional, str)*: Optional cleartext user password — when supplied, also derives per-user DPAPI prekeys (so user masterkeys can be decrypted in addition to system ones).
- **skipusers** *(optional, bool, default `False`)*: Skip the per-user file walk.

#### dpapisecretsremoteregdump
Same as [`dpapisecretshives`](#dpapisecretshives) but instead of taking local hives, it runs [`regdump2`](#regdump2) under the hood — does the entire end-to-end DPAPI dump in a single shot, no local files needed.

##### Parameters
- **password** *(optional, str)*: Optional cleartext user password for per-user prekey derivation.
- **skipusers** *(optional, bool, default `False`)*: Skip the per-user file walk.

#### vhdxsecretsdump
Opens a remote `.vhdx` (or `.vhd` / `.vmdk` — anything `adiskreader` understands) file via SMB, mounts every NTFS partition **without writing anything**, walks the in-image registry hives, runs the registry-secrets module, then opens `\Windows\NTDS\ntds.dit` from the same image and dumps every NTDS secret. Every recovered credential is stored in the OctoPwn credential store. The classic "Hyper-V backup share has DC backups in it" abuse, fully offline.

##### Parameters
- **filepath**: Remote SMB path to the VHDX file.

---

### VULNERABILITIES

#### printnightmare
Triggers **CVE-2021-34527 (PrintNightmare)** via the RPRN protocol's `RpcAddPrinterDriverEx` — uploads a malicious driver from a UNC share and asks the spooler to load it. Requires the Print Spooler to be running on the target.

##### Parameters
- **share**: UNC path to the share holding the malicious driver.
- **driverpath** *(optional, str)*: Optional explicit driver path within the share.

#### parprintnightmare
Same exploit, but goes through the **PAR** protocol (`MS-PAR`) instead of `MS-RPRN`. Some hardening configurations disable RPRN but leave PAR open — try this when `printnightmare` errors out.

##### Parameters
- **share**: UNC path to the share holding the malicious driver.
- **driverpath** *(optional, str)*: Optional explicit driver path within the share.

---

### AGENT

#### agentpipe
Connects to a wsnet **agent listening on a remote SMB named pipe**. The pipe is opened against `\\<host>\IPC$\<pipename>`, then wrapped in an OctoPwn agent transport so the remote agent appears as a brand-new session in the Sessions panel. Used to chain pivots: an agent on a host with no inbound network access exposes its control channel as an SMB pipe; you reach that host over SMB and "promote" the pipe into a full agent.

##### Parameters
- **pipename**: Pipe name (the part after `IPC$\`).

---

### WMI OPERATIONS

These commands are tunnelled over the **same** SMB session — no separate DCOM TCP connection on a dynamic port. Same backend as the [WMI client](./wmi.md), exposed here as a convenience so you don't have to spawn a second session against the same host.

#### wmiquery
Runs an arbitrary WQL query and prints every row.

##### Parameters
- **query**: WQL query (e.g. `SELECT Name, ProcessId FROM Win32_Process`).

#### wmiquery_json
Same as [`wmiquery`](#wmiquery) but returns the result as a JSON-encoded list of dicts.

##### Parameters
- **query**: WQL query.
- **to_print** *(optional, bool, default `False`)*: Whether to print the JSON.

#### wmishadowcopylist
Lists every existing **Volume Shadow Copy** on the target (queries `Win32_ShadowCopy`). Returns ID, device object, volume name, install date, GMT label and state for each.

##### Parameters
- **to_print** *(optional, bool, default `False`)*: Whether to print results.

#### wmishadowcopycreate
Creates a new Volume Shadow Copy of the named volume (`Win32_ShadowCopy.Create`). Returns the new shadow ID and device object — the latter can be combined with [`get`](#get) (using a UNC path like `\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy<n>\…`) or with [`getfullpath`](#additional-commands) to pull files out of the snapshot.

##### Parameters
- **volume**: Volume to snapshot (e.g. `C:\`).
- **to_print** *(optional, bool, default `True`)*: Whether to print the result.

#### wmishadowcopydelete
Deletes a Volume Shadow Copy by ID.

##### Parameters
- **shadow_id**: Shadow copy ID (as printed by `wmishadowcopylist`).
- **to_print** *(optional, bool, default `True`)*: Whether to print the result.

---

### UTILS

#### resolveusertosid
Resolves a username (with or without domain prefix) to a SID via LSARPC.

##### Parameters
- **username**: User to resolve.
- **to_print** *(optional, bool, default `True`)*: Whether to print the SID.

#### resolveusersidtoname
Resolves a SID back to `<username>@<domain>` via LSARPC.

##### Parameters
- **usersid**: SID to resolve.
- **to_print** *(optional, bool, default `True`)*: Whether to print the result.

---

## Additional commands

These are callable from the console but do not appear in the `help` output.

#### ll
Alias for [`ls`](#ls).

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### createvsssnapshot
Convenience wrapper that creates a one-shot service that calls `wmic shadowcopy call create volume=<drive>:\` and starts it. Used as a fallback when the WMI-based [`wmishadowcopycreate`](#wmishadowcopycreate) is unavailable. The service is auto-deleted after the call.

##### Parameters
- **service_name** *(optional, str, default `vssnapshot12`)*: Name of the temporary service.
- **drive** *(optional, str, default `C`)*: Drive letter (without colon).

#### getfullpath
Downloads a file given its **full UNC path** (e.g. `\\192.168.56.11\NETLOGON\secret.ps1`) into the OctoPwn working directory under the same basename. Useful when you need to grab a file that lives outside the currently-mounted share without re-mounting.

##### Parameters
- **filepath**: Full UNC path (must start with `\\`).

#### interfaces
Lists every network interface of the remote machine via the SRVSVC `NetrServerTransportEnum` interface — useful for spotting dual-homed hosts and pivoting candidates.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.
- **h_token** *(optional, int)*: GUI streaming token — leave as `None` from the console.

---

## Limitations

- **No SMB1.** The `SMB`, `SMB2` and `SMB3` modules are all SMB2/SMB3 auto-negotiate. SMB1-only hosts cannot be talked to.
- **No anonymous bind via `atype`.** Anonymous SMB sessions (e.g. for `IPC$` enumeration on hardened DCs) are configured at the **credential** level (use a credential with `secret_type=none` / no creds), not via a separate `atype`.
- **`get` glob expansion is client-side.** `get *.bak` works because the SMB client expands the glob against the **cached local directory listing** (the one populated by the last [`refreshcurdir`](#refreshcurdir)). If the directory has changed on the server since you last `cd`-ed into it, refresh first.
- **`servicedeploy` does not start the service.** Call [`servicestart`](#servicestart) afterwards.
- **`wmicmdexec`, `mmc20cmdexec`, `shellwindowscmdexec` and `shellbrowserwindowscmdexec` do not capture stdout.** They spawn a process and that's it. Use shell redirection (`> \\?\C:\…\out.txt`) plus a follow-up [`get`](#get) if you need the output.
- **`regdump` enables `RemoteRegistry` if it's not running.** It does not roll the start type back to whatever it was before — if the service was Disabled, you've changed that.
- **`lsassdump` deletes the remote dump file but is loud.** Both methods (`service` and `task`) leave EID 7045 (service installed) / EID 4698 (task created) in the Windows Event Log.
- **`coersion` fires every implemented coercion at the listener.** That's the point — every miss leaves a 4625 / 5145 in the target's logs.
- **`certreq` writes the resulting PFX to `cert_<random>.pfx` with password `admin`.** The PFX is also stored in the credential store. If you never want the file on disk, delete it after the run.
- **`dpapifiles` writes a JSON blob to disk.** `dpapi_secrets_encrypted_<host>.json` is a hex-dump of every artefact found — handle accordingly.
- **`vhdxsecretsdump` is read-only.** It does not write to the VHDX, but it does require enough memory to hold the parsed registry + NTDS in RAM. Very large NTDS files on small WASM heaps will OOM.
- **`agentpipe` requires a remote agent listening on the named pipe.** OctoPwn does not deploy the agent for you — that's done with one of the agent-builder utilities and is out of scope here.
- **`dcsync` over SMB requires `\PIPE\drsuapi`.** If the DC is hardened to refuse named-pipe DRSUAPI connections, use the dedicated [DCEDRSUAPI client](./dcedrsuapi.md) instead (which goes EPM → dynamic TCP port → DRSUAPI).
