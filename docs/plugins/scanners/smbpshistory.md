# SMB PowerShell History Scanner (smbpshistory)

The **SMB PowerShell History Scanner** retrieves the **PSReadline** command history files from every user profile on each target host via SMB (port 445). Windows stores every command typed in a PowerShell console in a plaintext file:

```
%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

The scanner walks the user profile directories on each target and downloads these files for each user it can read. Each result row contains the target IP, the username whose history was retrieved, the full file path on the remote host and the file contents.

These history files are a goldmine during post-exploitation: they frequently contain plaintext passwords passed as command-line arguments (`-Password Pa$$w0rd`), internal URLs, database connection strings, service account names, helpful one-liner scripts that reveal what the host is used for, and AD group / server names that map out further pivoting opportunities. Always review them carefully for credential material and operational intelligence.

!!! tip "Combine with other secret-mining scanners"
    - [event6secrets](event6secrets.md) — credentials embedded in Windows Event Log entries.
    - [smbregsession](smbregsession.md) — local user SIDs from the registry.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication. Local-admin or backup-operator privileges are typically required to read other users' profile directories.

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
Ports which trigger an automated `smbpshistory` scan when discovered by other scanners. Pre-populated with `445/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
