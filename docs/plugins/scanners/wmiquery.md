# WMI Query Scanner (wmiquery)

The **WMI Query Scanner** executes a custom **WQL** (WMI Query Language) statement against each target host via DCOM/RPC and streams the result rows back. It connects with the supplied credential, runs the configured WQL query (defaults to `SELECT * FROM Win32_OperatingSystem`) and emits one result entry per returned row.

WQL can interrogate almost every aspect of a Windows system: processes, services, installed software, hotfixes, network configuration, user accounts, scheduled tasks, registry, file system, hardware inventory and many more. This makes `wmiquery` an extremely flexible bulk-enumeration tool — write a WQL query once and run it across hundreds of hosts.

!!! tip "Workflow"
    1. [wmiadmin](wmiadmin.md) — confirm admin access (most useful WQL queries require it).
    2. **wmiquery** — run your custom WQL across the confirmed hosts.
    3. For interactive WQL, command execution, registry manipulation and shadow-copy work, drop into the [WMI client](../clients/wmi.md) — same DCOM transport (TCP/135 + dynamic high port) and the same `NTLM` / `KERBEROS` authentication.

!!! example "Useful WQL queries"
    - `SELECT * FROM Win32_OperatingSystem` — OS details, install date, last boot.
    - `SELECT * FROM Win32_QuickFixEngineering` — installed hotfixes / patches.
    - `SELECT Name, ProcessId, CommandLine FROM Win32_Process` — running processes.
    - `SELECT * FROM Win32_Product` — installed software (slow on many systems).
    - `SELECT * FROM Win32_Service WHERE State='Running'` — running services.
    - `SELECT * FROM Win32_LoggedOnUser` — currently logged-on users.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication.

Enter the ID of the credential stored in the Credentials Window.

#### query
The WQL statement to execute. Defaults to `SELECT * FROM Win32_OperatingSystem`. Standard WQL syntax — note that WQL is a subset of SQL with some differences (no `JOIN`, `LIKE` uses `%` wildcards, etc.).

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
Ports which trigger an automated `wmiquery` scan when discovered by other scanners. Pre-populated with `135/TCP, 445/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
