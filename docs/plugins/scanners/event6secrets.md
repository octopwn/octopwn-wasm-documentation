# Event Log Secrets Scanner (event6secrets)

The **Event Log Secrets Scanner** mines Windows Event Logs on each target host for entries that contain embedded secrets — credentials, tokens, keys — by reading the logs remotely via SMB (port 445). Internally it relies on the `Event6` library to parse event-log records and extract secret material that Windows occasionally logs in plaintext, including:

- Scheduled task definitions where the credential was passed inline.
- `4688` process-creation events with the password on the command line (`-Password`, `/p`, `psexec -p`, …).
- `4624` / `4625` logon events that captured cleartext passwords when WDigest or specific GPO settings were active.
- Generic application logs that contain hard-coded credentials in error or audit messages.

Each result row contains the target IP, the raw event-log entry that matched and the extracted secret.

This is a **post-exploitation** reconnaissance technique: once you have authenticated access (typically local admin) to a host, mining its event logs frequently reveals additional credentials that enable lateral movement to other systems.

!!! tip "Combine with other secret-mining scanners"
    - [smbpshistory](smbpshistory.md) — PSReadline command history files.
    - [smbregsession](smbregsession.md) — local user SIDs from registry.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication. Local-admin privileges are typically required to read security event logs.

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
Specifies the maximum runtime per host (in seconds). Set to `-1` to disable. Note: parsing every record on a busy server can be slow — bump this if scans get cancelled prematurely.

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
Ports which trigger an automated `event6secrets` scan when discovered by other scanners. Pre-populated with `445/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
