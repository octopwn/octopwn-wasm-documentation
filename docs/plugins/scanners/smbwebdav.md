# SMB WebDAV Detection Scanner (smbwebdav)

The **SMB WebDAV Detection Scanner** detects whether the **WebClient** (WebDAV) service is running on each target host by probing over SMB (port 445). It returns a single boolean `AVAILABLE` per host.

A machine with the WebClient service active is a high-value target for **NTLM relay** attacks. When WebDAV is enabled the host will follow UNC paths over **HTTP**, which means an attacker on the same network can coerce NTLM authentication without requiring SMB signing on the relay path. This pairs naturally with authentication-coercion techniques (PetitPotam, PrinterBug, …) to relay credentials to LDAP, AD CS or other services where signing is not enforced — frequently leading to domain compromise.

Finding WebDAV-enabled hosts is a standard step in any internal assessment that focuses on NTLM relay paths.

!!! tip "Combine with the other relay-path scanners"
    - [smbspooler](smbspooler.md) — Print Spooler reachable? Solid coercion vector.
    - [ntlmreflection](ntlmreflection.md) — vulnerable to relay-back-to-self?
    - The relay server (under Servers → relay) — the actual relay target / sink.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication.

Enter the ID of the credential stored in the Credentials Window. A standard domain user is sufficient.

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
Ports which trigger an automated `smbwebdav` scan when discovered by other scanners. Pre-populated with `445/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
