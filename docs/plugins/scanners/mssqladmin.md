# MSSQL Admin Privilege Scanner (mssqladmin)

The **MSSQL Admin Privilege Scanner** logs into each target MSSQL server (default port 1433) with the supplied credential and asks SQL Server itself the question "am I sysadmin?". Concretely it executes `SELECT IS_SRVROLEMEMBER('sysadmin')` and reports the boolean result as `IS_ADMIN`.

A `True` result means the account is a member of the `sysadmin` fixed server role. That role can:

- Execute `xp_cmdshell` for code execution as the SQL service account.
- Read and write any database in the instance.
- Modify server configuration, including security and audit settings.
- Impersonate other logins via `EXECUTE AS LOGIN`.

In short: full control over the SQL Server instance and, very often, the host operating system. Use this scanner to quickly identify which SQL servers in scope can be leveraged for code execution or data exfiltration with the credentials you currently hold.

!!! tip "Workflow"
    1. [mssqllogin](mssqllogin.md) — confirm the credential is valid.
    2. **mssqladmin** — find the servers where you are sysadmin.
    3. [mssqlquery](mssqlquery.md) — run targeted queries (e.g. `xp_cmdshell` on sysadmin instances).

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
Optional SMB pipe name to tunnel the MSSQL connection through. Leave empty to use a direct TDS connection over TCP.

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
Ports which trigger an automated `mssqladmin` scan when discovered by other scanners. Pre-populated with `1433/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
