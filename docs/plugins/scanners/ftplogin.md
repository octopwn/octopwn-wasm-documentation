# FTP Login Scanner (ftplogin)

The **FTP Login Scanner** validates a credential against one or more FTP servers (port 21 by default). For every target it performs a full FTP login and reports a simple `LOGIN_OK` boolean, allowing you to quickly map which credentials work where.

A successful login confirms the credential is valid for FTP access on that host. From there, the same credential typically grants read or write access to file systems, which can be leveraged for data exfiltration, payload deployment, or harvesting additional credentials embedded in hosted files.

!!! tip "Related scanners"
    - [ftpanon](ftpanon.md) — checks for **anonymous** FTP login (no credentials needed).

!!! tip "See also"
    Once a credential validates, drop into the [FTP client](../clients/ftp.md) for
    interactive directory listing, upload, download and command work. Note from the
    [client doc](../clients/ftp.md#authentication): only `PLAIN` (USER/PASS) authentication
    is implemented and only **passive** mode is supported for the data channel — pure-active
    networks will not work.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication.

Enter the ID of the credential stored in the Credentials Window.

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
- **Port Group**: `p:<port>` (e.g., `p:21`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:21/tcp`).

#### ports
Comma-separated list of FTP ports to try. Defaults to `21`.

---

### Advanced Parameters

#### authtype
Specifies the authentication protocol.

Available protocols:

- `NTLM`
- `Kerberos`

For most public FTP servers this is irrelevant — the credential's stored secret type controls the actual authentication.

#### krbetypes
Specifies the Kerberos encryption types to use during the scan.

Provide a comma-separated list of encryption types (e.g., `23,17,18`).

#### krbrealm
Specifies the Kerberos realm to use.

#### maxruntime
Specifies the maximum runtime per host (in seconds). Set to `-1` to disable.

#### protocol
Specifies the protocol. Fixed to `FTP` for this scanner.

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
Ports which trigger an automated `ftplogin` scan when discovered by other scanners. Pre-populated with `21/TCP, 2121/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
