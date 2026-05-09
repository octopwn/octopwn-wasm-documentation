# Baseline Assessment Scanner (baseline)

The **Baseline Assessment Scanner** is the recommended starting point for any internal-network engagement. It runs **twelve** complementary checks against each target host in a single pass, merges every finding into one stream and stores everything in the project — giving you a comprehensive first-pass view of every host's attack surface in one scan session.

The following modules run in parallel per target:

- **SMB shares & write test** — enumerates shares and tests for write access ([smbshare](smbshare.md)).
- **PrintNightmare** — tests for CVE-2021-1675 / CVE-2021-34527 ([smbprintnightmare](smbprintnightmare.md)).
- **WebDAV detection** — checks if the WebClient service is active ([smbwebdav](smbwebdav.md)).
- **NTLM reflection** — tests for relay-to-self vulnerability ([ntlmreflection](ntlmreflection.md)).
- **Local user SID enumeration** — lists local accounts via remote registry ([smbregsession](smbregsession.md)).
- **MSSQL named pipes** — discovers SQL instances behind SMB pipes ([mssqlpipe](mssqlpipe.md)).
- **MSSQL database info** — enumerates database schemas via the discovered pipe ([mssqldbinfo](mssqldbinfo.md)).
- **LDAP enumeration** — runs core LDAP queries against the configured DC.
- **LDAP signing check** — tests LDAP signing / channel-binding enforcement ([ldapsig](ldapsig.md)).
- **Print Spooler detection** — checks if the Spooler RPC is reachable ([smbspooler](smbspooler.md)).
- **SMB fingerprinting** — extracts OS/domain info from NTLM handshake ([smbfinger](smbfinger.md)).
- **FTP anonymous login** — tests for anonymous FTP access ([ftpanon](ftpanon.md)).

!!! tip "When (not) to use baseline"
    `baseline` is the easy mode for scoping a network in a single command and seeing what stands out. For deeper investigation of a specific finding (e.g. "every workstation has WebDAV", "every SQL server has weak schema isolation") run the corresponding focused scanner afterwards — they expose more parameters and produce more targeted results.

!!! info "Enterprise tier"
    `baseline` orchestrates a substantial number of components and is part of the **enterprise** tier.

!!! tip "Per-protocol authentication"
    `baseline` reuses one credential across four very different protocols. Each one has its
    own authentication semantics — refer to the corresponding client doc when something
    rejects:

    - **SMB / DCERPC checks** — see [SMB client authentication](../clients/smb.md#authentication) (`NTLM` / `KERBEROS`, no SMB1).
    - **MSSQL pipe + dbinfo** — see [MSSQL client authentication](../clients/mssql.md#authentication). The `sqlcredential` parameter overrides the SMB credential for the TDS-over-pipe login and follows the same `PLAIN` / `NTLM` / `KERBEROS` rules as the [`MSSQLPIPE` transport row](../clients/mssql.md#transport).
    - **LDAP enumeration + signing** — see [LDAP client authentication](../clients/ldap.md#authentication) (`NTLM` / `KERBEROS` / `SIMPLE` / `SSL`, plus StartTLS and client-cert binds).
    - **FTP anonymous** — see [FTP client authentication](../clients/ftp.md#authentication) (only `PLAIN`; the embedded check uses the `anonymous` credential anyway).

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for SMB / LDAP / SQL authentication.

Enter the ID of the credential stored in the Credentials Window. A standard domain user gives you the bulk of the value; local-admin unlocks the registry-based checks (NTLM reflection, local user SIDs).

#### dcip
Optional explicit Domain Controller IP for the embedded LDAP queries. Leave empty to let OctoPwn auto-discover via DNS / DC locator.

#### sqlcredential
Optional separate credential ID for the SQL connection through any discovered MSSQL named pipes. Leave empty to reuse the SMB credential.

#### sqlpiperegex
Regex used to identify SQL named pipes (forwarded to the embedded `mssqlpipe` check). Default:

```
^(?:MSSQL\$[A-Za-z0-9_-]+\\)?sql\\query$
```

#### writetest
When `True` (default), the SMB share check actively tests for write access by attempting to create a file on each readable share.

#### skipdatabases
Comma-separated list of databases to skip in the embedded `mssqldbinfo` enumeration.

#### skipschemas
Comma-separated list of schemas to skip.

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
- **Port Group**: `p:<port>` (e.g., `p:445`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:445/tcp`).

---

### Advanced Parameters

#### authtype
Specifies the authentication protocol.

Available protocols:

- `NTLM`
- `Kerberos`

#### dialect
Specifies the SMB connection dialect. Fixed to `SMB2` for this scanner.

#### krbetypes
Specifies the Kerberos encryption types to use during the scan.

Provide a comma-separated list of encryption types (e.g., `23,17,18`).

#### krbrealm
Specifies the Kerberos realm to use.

#### maxruntime
Specifies the maximum runtime per host (in seconds). Set to `-1` to disable. Because `baseline` orchestrates many sub-scanners, give this a generous value on slow networks.

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
Ports which trigger an automated `baseline` scan when discovered by other scanners. Pre-populated with `445/TCP, 1433/TCP, 389/TCP, 636/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
