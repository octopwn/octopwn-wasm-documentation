# FTP Anonymous Login Scanner (ftpanon)

The **FTP Anonymous Login Scanner** tests every target FTP server (typically port 21) for anonymous login access. It logs in with the username `anonymous` and a dummy email address as the password — no real credential is required.

A successful login means the FTP server allows unauthenticated access. Anonymous FTP is a recurrent finding in internal assessments: writable anonymous shares can be used to plant malicious files, while readable ones frequently contain configuration files, database dumps or software packages with embedded credentials.

!!! info "No credentials required"
    The scanner injects a temporary `anonymous / anonftp@octopwn.com` credential into the project automatically, so you do not need to provide one. The injected credential is reused by every probe.

!!! tip "Related scanners"
    - [ftplogin](ftplogin.md) — validates a credential of your choice (instead of `anonymous`).

!!! tip "See also"
    For interactive browsing of the discovered anonymous shares, drop into the
    [FTP client](../clients/ftp.md) — note from its
    [authentication](../clients/ftp.md#authentication) section that only `PLAIN` is
    implemented and only **passive** mode is supported for the data channel.

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
- **Port Group**: `p:<port>` (e.g., `p:21`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:21/tcp`).

#### ports
Comma-separated list of FTP ports to try. Defaults to `21`.

---

### Advanced Parameters

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
Ports which trigger an automated `ftpanon` scan when discovered by other scanners. Pre-populated with `21/TCP, 2121/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
