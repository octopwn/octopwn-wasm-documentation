# MSSQL Query Scanner (mssqlquery)

The **MSSQL Query Scanner** runs an arbitrary SQL statement against every target MSSQL server (default port 1433) and streams every result row back. It connects with the supplied credential, executes the configured query (defaults to `SELECT @@VERSION`) and emits each returned row as a separate result entry. All columns returned by the query are preserved in the output as key/value pairs.

This is your bulk-SQL Swiss army knife: query linked servers, check server configurations, extract specific tables, run `xp_cmdshell` on instances where you have sysadmin, or run anything else SQL Server understands — across many servers in one scan.

!!! tip "Workflow"
    1. [mssqllogin](mssqllogin.md) — confirm credentials.
    2. [mssqldbinfo](mssqldbinfo.md) — understand what schema you're shooting at.
    3. **mssqlquery** — extract exactly what you need.

!!! example "Useful queries"
    - `SELECT name FROM sys.databases` — list databases.
    - `SELECT name, type_desc FROM sys.server_principals` — list logins.
    - `SELECT @@VERSION` — version banner.
    - `SELECT name, srvname, srvproduct FROM sys.sysservers` — linked servers (great for further pivoting).
    - `EXEC xp_cmdshell 'whoami'` — command execution (sysadmin only).

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

Enter the ID of the credential stored in the Credentials Window.

#### pipename
Optional SMB pipe name to tunnel the MSSQL connection through. Leave empty for direct TDS over TCP.

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

#### query
The SQL statement to execute. Defaults to `SELECT @@VERSION`. Marked as advanced because the parameter slot is internally tagged that way, but in practice you almost always want to set it.

#### resultsfile
Specifies a file for saving the scan results.

The file will be saved in OctoPwn’s `/browserefs/volatile` directory.

#### showerrors
Determines whether errors encountered during the scan should be displayed.

#### timeout
Sets the timeout (in seconds) for each connection attempt.

#### triggerports
Ports which trigger an automated `mssqlquery` scan when discovered by other scanners. Pre-populated with `1433/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
