# MSSQL Fingerprint Scanner (mssqlfinger)

The **MSSQL Fingerprint Scanner** is the SQL-server equivalent of [smbfinger](smbfinger.md). It connects to each MSSQL listener (default port 1433), starts a TDS pre-login and triggers an NTLM challenge — all without authenticating. The challenge response leaks a useful chunk of Active Directory metadata that the SQL service exposes for free.

The following details are gathered during the scan:

- **domainname** — NetBIOS domain name of the host.
- **computername** — NetBIOS computer name.
- **dnsforestname** — Active Directory DNS forest name.
- **dnsdomainname** — AD DNS domain name.
- **dnscomputername** — Fully-qualified DNS computer name.
- **local_time** — Server clock as reported by NTLM (handy for Kerberos / clock-skew diagnostics).
- **os_major_version**, **os_minor_version**, **os_build** — OS version triplet.
- **os_guess** — Best-effort OS string derived from the version triplet.

Use it to discover Active Directory information and OS versions on SQL servers without needing any credentials — ideal for early-stage network reconnaissance, especially when SMB is firewalled but TDS is not.

!!! info "No credentials required"
    The scanner uses an **unauthenticated** TDS pre-login. You do not need to set the `credential` parameter for this scan.

!!! tip "Authenticated follow-up"
    Once you have a SQL Server credential, the [MSSQL client](../clients/mssql.md) is the
    natural next stop — the [authentication section](../clients/mssql.md#authentication)
    explains when to use `PLAIN` (`sa`-style logins) vs. `NTLM` / `KERBEROS` (domain accounts),
    and the [transport section](../clients/mssql.md#transport) covers TCP/1433 (`MSSQL`) vs.
    SMB-named-pipe (`MSSQLPIPE`) when 1433 is firewalled.

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
- **Port Group**: `p:<port>` (e.g., `p:1433`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:1433/tcp`).

---

### Advanced Parameters

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
Ports which trigger an automated `mssqlfinger` scan when discovered by other scanners. Pre-populated with `1433/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
