# SMB Fingerprint Scanner (smbfinger)

The **SMB Fingerprint Scanner** enumerates NTLM-handshake information from SMB servers (port 445) **without requiring credentials**. It is one of the fastest ways to gather Active Directory and OS-level metadata from a Windows estate during initial reconnaissance.

The following details are gathered during the scan:

- **domainname** — NetBIOS domain name of the target.
- **computername** — NetBIOS computer name.
- **dnsforestname** — DNS forest name of the domain.
- **dnsdomainname** — DNS domain name of the target.
- **dnscomputername** — Fully-qualified DNS computer name.
- **local_time** — Current local time on the target system (handy for Kerberos clock-skew diagnostics).
- **os_major_version** — Major OS version reported in the NTLM target info.
- **os_minor_version** — Minor OS version.
- **os_build** — OS build number.
- **os_guess** — Best-effort OS string derived from the version triplet.

!!! info "No credentials required"
    The scanner uses an unauthenticated SMB negotiate / NTLM challenge handshake. You do **not** need to set the `credential` parameter for this scan.

!!! tip "Related scanners"
    - [mssqlfinger](mssqlfinger.md) — same idea, but extracts the data from an unauthenticated MSSQL TDS pre-login.
    - [smbproto](smbproto.md) — enumerates supported SMB dialects and signing settings.
    - [smbsig](smbsig.md) — fast SMB-signing yes/no check.

!!! tip "Authenticated follow-up"
    Once you have a credential, the [SMB client](../clients/smb.md) is the natural next stop —
    use the fingerprinted DNS / NetBIOS / domain values directly when configuring targets and
    Kerberos realms.

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
- **Port Group**: `p:<port>` (e.g., `p:445`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:445/tcp`).

---

### Advanced Parameters

#### dialect
Specifies the SMB connection dialect. Fixed to `SMB2` for this scanner.

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
Ports which trigger an automated `smbfinger` scan when discovered by other scanners. Pre-populated with `445/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
