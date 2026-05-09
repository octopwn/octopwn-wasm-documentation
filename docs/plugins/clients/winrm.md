# WinRM Client

The **WinRM Client** speaks Windows Remote Management (WS-Management over HTTP/HTTPS) and gives you remote command execution, PowerShell execution, and PowerShell-driven file transfer against Windows targets — i.e. the protocol behind `Enter-PSSession` and `Invoke-Command`. It wraps [`awinrm`](https://github.com/skelsec/awinrm) and is most often used as a lateral-movement primitive against hosts where SMB is locked down but WinRM (5985 / 5986) is exposed.

| Variant   | Protocol | Default port |
| --------- | -------- | ------------ |
| `WINRM`   | HTTP     | 5985         |
| `WINRMS`  | HTTPS    | 5986         |

---

## Authentication

The WinRM client supports six authentication modes — three NTLM-flavoured and three Kerberos-flavoured — covering the wrappers Windows itself negotiates (`Negotiate`/SPNEGO and `CredSSP`).

| `atype`             | Underlying creds | Notes                                                                 |
| ------------------- | ---------------- | --------------------------------------------------------------------- |
| `NTLM`              | NTLM             | Defaults to the `SPNEGO` (Negotiate) wrapper.                         |
| `KERBEROS`          | Kerberos         | Defaults to the `SPNEGO` (Negotiate) wrapper.                         |
| `SPNEGO_NTLM`       | NTLM             | Explicit SPNEGO wrap; identical to `NTLM` above.                      |
| `SPNEGO_KERBEROS`   | Kerberos         | Explicit SPNEGO wrap; identical to `KERBEROS` above.                  |
| `CREDSSP_NTLM`      | NTLM             | CredSSP wrap (delegates credentials — useful for double-hop).         |
| `CREDSSP_KERBEROS`  | Kerberos         | CredSSP wrap (delegates credentials — useful for double-hop).         |

### NTLM credentials

| Secret type   | Description                                                          | Example              |
| ------------- | -------------------------------------------------------------------- | -------------------- |
| `password`    | Cleartext password.                                                  | `username:Pa55w0rd!` |
| `pwhex`       | Hex-encoded UTF-16LE password (for non-ASCII passwords).             | `username:70617373…` |
| `nt`          | NT hash (pass-the-hash).                                             | `username:aad3b…`    |
| `rc4`         | RC4 (synonym for NT for the NTLM exchange).                          | `username:aad3b…`    |
| `agentproxy`  | Use a remote NTLM signer over the wsnet agent proxy.                 | n/a                  |
| `sspiproxy`   | Use the OS's SSPI session via the wsnet agent proxy (Windows agent). | n/a                  |

### Kerberos credentials

| Secret type     | Description                                                                                | Example                              |
| --------------- | ------------------------------------------------------------------------------------------ | ------------------------------------ |
| `password`      | Cleartext password.                                                                        | `username:Pa55w0rd!`                 |
| `pwhex`         | Hex-encoded UTF-16LE password.                                                             | `username:70617373…`                 |
| `nt` / `rc4`    | NT/RC4 hash.                                                                               | `username:aad3b…`                    |
| `aes128`        | AES128 long-term key.                                                                      | `username:<32-hex>`                  |
| `aes256`        | AES256 long-term key.                                                                      | `username:<64-hex>`                  |
| `keytab`        | Kerberos keytab file in OctoPwn volatile storage.                                          | `/browserfs/volatile/admin.keytab`   |
| `keytabb64`     | Base64-encoded keytab inline.                                                              | `username:<b64>`                     |
| `ccache`        | MIT ccache file in OctoPwn volatile storage.                                               | `/browserfs/volatile/krb5cc.ccache`  |
| `ccacheb64`     | Base64-encoded ccache inline.                                                              | `username:<b64>`                     |
| `kirbi`         | `.kirbi` ticket file (Rubeus-style).                                                       | `/browserfs/volatile/admin.kirbi`    |
| `kirbib64`      | Base64-encoded `.kirbi` inline.                                                            | `username:<b64>`                     |
| `pfxb64`        | Base64-encoded PFX (PKINIT certificate auth).                                              | `username:<b64>`                     |
| `agentproxy`    | Remote KDC over the wsnet agent proxy.                                                     | n/a                                  |
| `sspiproxy`     | OS SSPI session via wsnet agent proxy (Windows agent).                                     | n/a                                  |

!!! tip "Pick `CREDSSP_*` when you need double-hop"
    Standard SPNEGO/Negotiate WinRM auth doesn't delegate credentials, so any further network hop from the remote shell (e.g. accessing a file share or another server) will fail with `Access is denied`. CredSSP delegates the credential to the target so the remote process can re-authenticate outwards on your behalf — at the cost of dropping a usable secret on the target, which is why it's disabled by default in many environments.

!!! warning "Host certificate validation on `WINRMS`"
    HTTPS connections rely on the underlying HTTP transport's TLS layer; expect the same forgiving stance other OctoPwn clients take towards self-signed enterprise WinRM certificates. Validate fingerprints out-of-band if integrity matters.

---

## Commands

### CONNECTION

#### login
Establishes a WinRM session against the target. There's no long-lived shell or socket held open between commands — under the hood every subsequent command opens its own `awinrm` session via the bound factory. `login` itself runs a single `whoami` round-trip to confirm credentials work end-to-end and flips the session into the connected state.

#### logout
Marks the session as logged out. Because every command opens its own short-lived session, no persistent connection needs to be torn down.

---

### CMD

#### cmdexec
Executes a single command via `cmd.exe` on the remote host and prints `stdout`, `stderr`, and the return code. Each invocation spins up a fresh `cmd.exe` process — there is **no shared state** between calls (no working directory, no environment variables, no command history).

##### Parameters
- **command**: The cmd.exe command to execute (e.g. `whoami /all`, `ipconfig /all`, `dir C:\`).

#### psexec
Executes a PowerShell command or script on the remote host and prints `stdout`, `stderr`, and the return code. Each invocation spawns a fresh PowerShell engine — again, **no shared state** between calls.

##### Parameters
- **script**: The PowerShell command or one-liner script (e.g. `Get-Process`, `Get-LocalUser`, `Get-WmiObject Win32_OperatingSystem | Select-Object Caption,Version`).

!!! tip "PowerShell beats cmd for almost everything"
    `psexec` is the more capable surface — richer object output, structured pipelines, and far more enumeration cmdlets. Reach for `cmdexec` only when you specifically need a `cmd.exe` builtin or a legacy console-mode binary that misbehaves under PowerShell.

---

### FILE

PowerShell-driven file transfer. There is no SMB share, no CIFS dependency — everything rides over the same WinRM channel as the command-execution APIs, base64-encoded inside short PowerShell scripts.

#### getfile
Downloads a remote file to OctoPwn's working directory. The remote file is read in 3 MiB chunks via `[IO.File]::OpenRead` + `[Convert]::ToBase64String`; each chunk is base64-decoded and appended locally. Progress is printed for files larger than one chunk.

##### Parameters
- **remotepath**: Absolute path to the file on the target (e.g. `C:\Windows\System32\config\SAM`, `C:\Users\Administrator\Desktop\loot.zip`).
- **localpath** *(optional)*: Destination path inside OctoPwn's working directory. **If omitted**, the file is saved under the same basename as the remote path. Both supplied and derived paths are jailed to the working directory — attempts to escape (`..`, absolute paths outside workdir) are rejected.

#### putfile
Uploads a local file to the remote host in 128 KiB chunks (the upper bound is dictated by the WinRM SOAP envelope size — uploads are fundamentally chunkier than downloads). The first chunk uses `[IO.File]::WriteAllBytes` (creates / overwrites); subsequent chunks use `[IO.File]::Open(... 'Append')`. Remote file size is verified after the final chunk.

##### Parameters
- **localpath**: Source file inside OctoPwn's working directory (jailed — paths outside workdir are rejected).
- **remotepath**: Absolute destination path on the target (e.g. `C:\Windows\Temp\loader.exe`).

!!! warning "PowerShell file transfer isn't fast"
    Both transfers serialize chunks through PowerShell scripts, so they're round-trip-bound. Expect noticeably slower throughput than SMB-based transfers. For small payloads (binaries, scripts, captured registry hives) it's fine; for multi-hundred-MB transfers you'll want a different vector.

!!! warning "Remote paths are interpolated into PowerShell"
    Both `getfile` and `putfile` interpolate `remotepath` directly into the PowerShell script that's sent to the target. **Don't** point them at attacker-controlled or untrusted path strings — single quotes inside the path will break the script (and could be used for PS-injection if the path is operator-supplied from elsewhere).

---

### HUNT

#### awscreds
Searches the remote host for AWS credential files (`credentials` files containing `aws_*` keys) using a single PowerShell `Get-ChildItem -Recurse | Select-String` pipeline.

##### Parameters
- **searchpath** *(optional)*: PowerShell-style array of paths to search. Defaults to ``'C:\Users\', 'C:\ProgramData\AWSCLI\', 'C:\Temp\'``. Provide your own as a comma-separated list of single-quoted strings, e.g. `'C:\Users\', 'D:\Backups\'`.

---

## Limitations & gotchas

- **No interactive shell / PTY.** WinRM is fundamentally a request/response protocol (WS-Management over SOAP) — it doesn't natively expose a PTY the way SSH does. An SSH-style terminal experience is on the to-do list (a corresponding TODO comment lives in `octopwn/clients/winrm/console.py` next to `help_groups`); attempts so far have struggled with line buffering, ANSI handling, and the `awinrm` shell-lifecycle plumbing. Until that's done, every `cmdexec` / `psexec` is a one-shot with **no shared state** (cwd, env vars, variables, loaded modules — all gone after each call).
- **Each command = a new session.** Because every `do_*` command wraps itself in `async with self.factory.get_session()`, there's a small per-command setup cost (auth handshake on first call is cached by the underlying HTTP layer, but a new shell is spawned each time). Batch logic into a single `psexec` invocation if you care about latency.
- **No double-hop without CredSSP.** Selecting `NTLM` / `KERBEROS` / `SPNEGO_*` won't let the remote shell re-authenticate to a third host. Use `CREDSSP_*` if you need that — at the usual cost.
- **PowerShell-only file transfer.** `getfile` and `putfile` go through the same SOAP channel as `psexec`; they're significantly slower than SMB and don't preserve metadata (timestamps, ACLs).
- **No certificate auth.** The factory doesn't currently expose WinRM's certificate-based authentication mechanism — only NTLM / Kerberos via SPNEGO or CredSSP.
- **`HUNT` is intentionally minimal.** Unlike the SSH client, the WinRM client doesn't ship a broad post-exploitation enumeration toolkit. For now, drive enumeration through `psexec` directly (e.g. `Get-LocalUser`, `Get-LocalGroupMember`, `Get-Process`, `Get-Service`, `Get-NetTCPConnection`, `(Get-WmiObject Win32_OperatingSystem)`, …).
