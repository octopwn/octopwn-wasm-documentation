# MSSQL Named-Pipe Scanner (mssqlpipe)

The **MSSQL Named-Pipe Scanner** discovers MSSQL instances that are reachable through SMB named pipes (port 445), even when TCP 1433 is firewalled. It connects to `IPC$` on each target, lists every named pipe, and matches the pipe names against a configurable regex (defaults to the standard MSSQL pipe pattern: `sql\query` or `MSSQL$<INSTANCE>\sql\query`). For every matching pipe the scanner can also attempt a TDS connection through the pipe to confirm the SQL instance is reachable and accepts the supplied credential.

Each result row contains the target IP, the pipe name, the full UNC path and a `LOGINOK` boolean.

This is particularly useful when MSSQL is hidden behind firewall rules that allow SMB but block direct TDS — a surprisingly common setup for legacy applications. Finding SQL instances behind named pipes expands your attack surface for data access and potential command execution via `xp_cmdshell`.

!!! tip "Workflow"
    1. **mssqlpipe** — discover SQL instances reachable through SMB pipes.
    2. [mssqllogin](mssqllogin.md) (with `pipename` set) — confirm credentials work over the pipe.
    3. [mssqladmin](mssqladmin.md), [mssqldbinfo](mssqldbinfo.md), [mssqlquery](mssqlquery.md) — continue the SQL workflow over the pipe by setting their `pipename` parameter.

!!! tip "Authentication"
    This scanner uses **two** credential slots that map to the same authentication
    surface as the [MSSQL client](../clients/mssql.md#authentication) — specifically the
    `MSSQLPIPE` transport row in the [transport table](../clients/mssql.md#transport).

    - `credential` (`authtype`) authenticates the **SMB** connection that hosts the named pipe.
      Only `NTLM` / `KERBEROS` are valid here — there is no anonymous SMB pipe access.
    - `sqlcredential` (optional) authenticates the **TDS-over-pipe** SQL login.
      It supports the same `PLAIN` / `NTLM` / `KERBEROS` mix as the MSSQL client, so use
      `PLAIN` for SQL Server logins (`sa`, `dbadmin`, application accounts) and `NTLM` /
      `KERBEROS` for domain accounts (`CONTOSO\jdoe`). When omitted, the SMB credential
      is reused for SQL.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for the SMB connection.

Enter the ID of the credential stored in the Credentials Window.

#### sqlcredential
Optional separate credential ID to use for the **SQL** login through the discovered pipe. Leave empty to reuse the SMB credential. Useful when the SMB-side identity is a Windows account but you want to test a different SQL login over the pipe.

#### sqlpiperegex
Regex used to identify which named pipes look like SQL listeners. Default:

```
^(?:MSSQL\$[A-Za-z0-9_-]+\\)?sql\\query$
```

This matches both the default-instance pipe (`sql\query`) and named-instance pipes (`MSSQL$INSTANCE\sql\query`). Loosen it if you have non-standard naming.

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

#### authtype
Specifies the authentication protocol used for the SMB connection that hosts the named pipe.
The optional `sqlcredential` (above) covers the TDS-over-pipe SQL login independently — see the
[MSSQL client authentication](../clients/mssql.md#authentication) section for the full breakdown.

Available protocols:

- `NTLM`
- `KERBEROS`

#### dialect
Specifies the SMB connection dialect. Fixed to `SMB2` for this scanner.

#### krbetypes
Specifies the Kerberos encryption types to use during the scan.

Provide a comma-separated list of encryption types (e.g., `23,17,18`).

#### krbrealm
Specifies the Kerberos realm to use.

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
Ports which trigger an automated `mssqlpipe` scan when discovered by other scanners. Pre-populated with `445/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
