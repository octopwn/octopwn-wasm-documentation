# WMI Admin Privilege Scanner (wmiadmin)

The **WMI Admin Privilege Scanner** verifies whether the configured credential has administrative access to the WMI service on each target host. It connects via DCOM/RPC (port 135 for the endpoint mapper, then a dynamic high port; SMB on 445 is also used for authentication transport) and attempts a WMI operation that requires admin privileges. The result is a simple boolean `ADMIN` flag per target.

Administrative WMI access enables a powerful set of post-exploitation capabilities, all without dropping files to disk:

- **Remote command execution** via `Win32_Process.Create`.
- **Software inventory and patch level** via `Win32_Product`, `Win32_QuickFixEngineering`.
- **Service and scheduled task enumeration** via `Win32_Service`, `Win32_ScheduledJob`.
- **Event log access** via `Win32_NTLogEvent`.
- **Network and system configuration** via dozens of `Win32_*` classes.

Use this scanner to map which hosts in scope accept your current credentials for WMI-based lateral movement and remote execution.

!!! tip "Workflow"
    1. **wmiadmin** — find the hosts where the credential is admin.
    2. Use the [WMI client](../clients/wmi.md) for interactive enumeration / execution against the discovered hosts — the client doc covers the full DCOM transport (TCP/135 + dynamic high port), command groups, and the `NTLM` / `KERBEROS` authentication matrix.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication.

Enter the ID of the credential stored in the Credentials Window.

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
- **Port Group**: `p:<port>` (e.g., `p:135`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:135/tcp`).

---

### Advanced Parameters

#### authtype
Specifies the authentication protocol.

Available protocols:

- `NTLM`
- `Kerberos`

#### krbetypes
Specifies the Kerberos encryption types to use during the scan.

Provide a comma-separated list of encryption types (e.g., `23,17,18`).

#### krbrealm
Specifies the Kerberos realm to use.

#### maxruntime
Specifies the maximum runtime per host (in seconds). Set to `-1` to disable.

#### protocol
Specifies the protocol. Fixed to `WMI` for this scanner.

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
Ports which trigger an automated `wmiadmin` scan when discovered by other scanners. Pre-populated with `135/TCP, 445/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
