# MSSQL Login Scanner (mssqllogin)

The **MSSQL Login Scanner** validates a credential against one or more Microsoft SQL Server instances (default port 1433). It runs a full TDS login on every target and reports a simple `LOGIN_OK` boolean. Both SQL authentication and Windows authentication (NTLM / Kerberos) are supported — the actual mechanism is determined by the credential type stored in OctoPwn.

A successful login is the prerequisite for every other authenticated MSSQL scanner. Once `mssqllogin` confirms a credential is valid for a given server you can immediately follow up with [mssqladmin](mssqladmin.md), [mssqldbinfo](mssqldbinfo.md), [mssqlquery](mssqlquery.md) or [mssqlsensdata](mssqlsensdata.md).

!!! tip "Reach SQL servers through SMB pipes"
    If TDS is firewalled but SMB is open, set the `pipename` parameter (or run [mssqlpipe](mssqlpipe.md) first) to route the SQL connection through an SMB named pipe.

!!! tip "Authentication"
    This scanner uses the same authentication surface as the [MSSQL client](../clients/mssql.md#authentication).
    Use `PLAIN` for SQL Server logins (`sa`, `dbadmin`, application accounts), and `NTLM` /
    `KERBEROS` for domain accounts (`CONTOSO\jdoe`). The client doc has the full secret-type
    tables and a "Picking the right `atype` at a glance" cheat sheet.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication.

Enter the ID of the credential stored in the Credentials Window. Both SQL logins (`PASSWORD`) and Windows logins (`PASSWORD`, `NT`, `AES`, certificates, …) work.

#### pipename
Optional SMB pipe name to tunnel the MSSQL connection through. Leave empty to use a direct TDS connection over TCP. When set, the scanner connects to `\\<target>\IPC$\<pipename>` and speaks TDS over the named pipe. Use this when port 1433 is blocked but SMB is reachable.

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
- **Port Group**: `p:<port>` (e.g., `p:1433`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:1433/tcp`).

---

### Advanced Parameters

#### authtype
Specifies the authentication protocol. See the [MSSQL client authentication](../clients/mssql.md#authentication) section for the full breakdown of which secret types each `authtype` accepts.

Available protocols:

- `PLAIN` — SQL Server logins (`sa`, `dbadmin`, application accounts).
- `NTLM` — Windows / domain accounts.
- `KERBEROS` — Windows / domain accounts.

#### krbetypes
Specifies the Kerberos encryption types to use during the scan.

Provide a comma-separated list of encryption types (e.g., `23,17,18`).

#### krbrealm
Specifies the Kerberos realm to use.

#### maxruntime
Specifies the maximum runtime per host (in seconds). Set to `-1` to disable.

#### protocol
Specifies the protocol. Fixed to `MSSQL` for this scanner.

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
Ports which trigger an automated `mssqllogin` scan when discovered by other scanners. Pre-populated with `1433/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
