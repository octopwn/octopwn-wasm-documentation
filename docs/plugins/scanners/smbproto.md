# SMB Protocol Scanner (smbproto)

The **SMB Protocol Scanner** enumerates **all** SMB dialect versions supported by each target and reports the signing configuration **per dialect** (port 445). For every dialect the scanner negotiates a separate connection and records:

- **PROTO** — the SMB dialect (e.g. `SMB2.02`, `SMB2.10`, `SMB3.00`, `SMB3.11`).
- **SIGN_ENABLED** — whether the server advertises support for SMB signing.
- **SIGN_ENFORCED** — whether the server **requires** SMB signing.

This is a thorough scan: it opens five to six connections per host. If you only need a single yes/no on signing, use the [smbsig](smbsig.md) scanner instead — it negotiates SMB 2.02 once and is significantly faster.

No credentials are required.

Servers that support signing but do not enforce it are vulnerable to SMB relay attacks: an attacker who can coerce another machine to authenticate to such a host can relay the credentials and perform actions as the coerced identity. The per-dialect breakdown also helps identify hosts still offering legacy SMB1 / early SMB2 dialects, which may have additional weaknesses (notably SMB1 entirely).

!!! tip "When to use which"
    - [smbsig](smbsig.md) — fast, single yes/no on SMB signing. Use it for bulk discovery of relay targets.
    - **smbproto** — full per-dialect breakdown. Use when you also care about which dialects a host supports.

!!! tip "Mapping to client transport"
    The dialects reported here are negotiated directly. When you connect from the
    [SMB client](../clients/smb.md#transport), the `SMB` / `SMB2` / `SMB3` selectors all
    auto-negotiate within the SMB2/SMB3 family — there is no SMB1 path in OctoPwn even when
    a target advertises it.

---

## Parameters

### Normal Parameters

#### targets
Specifies the targets to scan.

A list of targets can be specified in the following formats:

- **ID**: ID of the target server from the targets window.
- **IP**: Single IP address (e.g., `192.168.1.1`).
- **CIDR**: IP range in CIDR notation (e.g., `192.168.1.0/24`).
- **Hostname**: Resolvable hostname.
- **File**: Path to a file containing targets (must be in OctoPwn’s `/browserefs/volatile` directory). File lists need to be uploaded into OctoPwn and separated by newlines.
- **Control word**: Use `all` to scan all stored targets.
- **Single Group**: `g:<groupname>` (e.g., `g:test1`).
- **Multiple Groups**: `g:<groupname1>,g:<groupname2>` (e.g., `g:test1,g:test2`).
- **Port Group**: `p:<port>` (e.g., `p:445`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:445/tcp`).

---

### Advanced Parameters

#### dialect
Specifies the SMB connection dialect. Fixed to `SMB2` for this scanner — the dialect actually negotiated rotates through the supported set internally.

#### maxruntime
Specifies the maximum runtime per host (in seconds). Set to `-1` to disable.

#### proxy
Specifies the proxy ID to use for the scan.

Enter the ID of the proxy to route the scan through. Proxies must be configured in the Proxy Window.

#### resultsfile
Specifies a file for saving the scan results.

The file will be saved in OctoPwn’s `/browserefs/volatile` directory.

#### showerrors
Determines whether errors encountered during the scan should be displayed.

#### timeout
Sets the timeout (in seconds) for each connection attempt.

#### triggerports
Ports which trigger an automated `smbproto` scan when discovered by other scanners. Pre-populated with `445/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
