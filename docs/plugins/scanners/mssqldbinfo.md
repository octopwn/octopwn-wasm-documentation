# MSSQL Database Info Scanner (mssqldbinfo)

The **MSSQL Database Info Scanner** maps the full schema of every accessible database on each target SQL Server: databases → schemas → tables → columns, plus an approximate row count per table. System databases (`master`, `model`, `msdb`, `tempdb`) are excluded by default. You can additionally skip specific databases, schemas, tables or columns through the `skip*` parameters.

Each result row contains the target IP, database name, schema, table name, column name and the row count of that table. The output gives you a complete map of where data lives across the SQL estate — the natural prerequisite for targeted data extraction.

!!! tip "MSSQL hunting workflow"
    1. [mssqllogin](mssqllogin.md) — confirm credentials work.
    2. **mssqldbinfo** — discover the schema landscape across all accessible servers.
    3. [mssqlsensdata](mssqlsensdata.md) — automatically flag columns whose names suggest sensitive data (PII, financials, secrets) and sample them.
    4. [mssqlquery](mssqlquery.md) — extract the exact rows you want with custom SQL.

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

#### skipdatabases
Comma-separated list of database names to skip during enumeration. Useful for excluding application databases that you have already mapped, or for narrowing scope to one or two specific databases.

#### skipschemas
Comma-separated list of schema names to skip. Most workloads can safely skip `sys`, `INFORMATION_SCHEMA`, `db_*` and similar.

#### skiptables
Comma-separated list of table names to skip.

#### skipcolumns
Comma-separated list of column names to skip.

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
Ports which trigger an automated `mssqldbinfo` scan when discovered by other scanners. Pre-populated with `1433/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
