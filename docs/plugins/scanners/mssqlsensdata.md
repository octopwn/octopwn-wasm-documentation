# MSSQL Sensitive Data Scanner (mssqlsensdata)

The **MSSQL Sensitive Data Scanner** automates the search for high-impact data exposure across SQL Server estates. It walks every accessible database, schema, table and column, then matches the table and column names against a built-in keyword dictionary covering six priority-ordered categories:

- **P1 PAYROLL** — salary, wages, compensation, bonuses, commissions, …
- **P2 FINANCIAL** — credit cards, bank accounts, IBANs, account numbers, …
- **P3 PII** — SSNs, passports, driver licenses, dates of birth, addresses, …
- **P4 HEALTH** — medical records, diagnoses, prescriptions (HIPAA-relevant).
- **P5 CONTACT** — addresses, phone numbers, email addresses.
- **P6 AUTH** — passwords, API keys, tokens, secrets.

When a match is found the scanner samples a configurable number of rows and (optionally) verifies the data format — for example, a Luhn check on credit card numbers or a regex on SSNs. Results are returned in priority order so the most alarming findings (payroll, financials, secrets) appear first.

Each result row carries the target IP, database, schema, table, column, the matched **CATEGORY** + **PRIORITY**, what the match was on (table or column name), the matched **KEYWORD**, the table's row count, a `VERIFIED` flag, and the optional sample data.

!!! tip "Tailor with custom keywords"
    Use the `customkeywords` parameter to inject organisation-specific terms (project codenames, HR system names, internal terminology). Custom keywords are always treated as **priority 1** so they bubble to the top of the report.

!!! warning "Sample data leaves the database"
    When `storesamples` is enabled (default) the sampled cell values are written into the project results — useful for proof, but treat the project file as sensitive afterwards. Set `storesamples` to `False` to flag candidate columns without actually retaining the sampled data.

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

#### samplesize
Number of rows to sample per matched column. Defaults to `5`. Set to `0` to disable sampling and only report column matches.

#### verifysample
When `True` (default), sampled values are checked against per-category validators (Luhn for credit cards, SSN regex, IBAN checksum, …). The `VERIFIED` flag in the result indicates whether the sample passed validation.

#### storesamples
When `True` (default), the sampled values are stored in the result `SAMPLE_DATA` column for evidence. Disable when you want to know **where** sensitive data lives without copying any of it back.

#### customkeywords
Extra keywords to look for during column / table name matching. Always treated as priority 1.

#### skipdatabases
Comma-separated list of databases to skip.

#### skipschemas
Comma-separated list of schemas to skip. `sys`, `INFORMATION_SCHEMA` and similar housekeeping schemas are usually safe to exclude.

#### skiptables
Comma-separated list of tables to skip.

#### skipcolumns
Comma-separated list of columns to skip.

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
Ports which trigger an automated `mssqlsensdata` scan when discovered by other scanners. Pre-populated with `1433/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
