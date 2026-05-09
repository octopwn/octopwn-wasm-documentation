# NTLM Reflection Scanner (ntlmreflection)

The **NTLM Reflection Scanner** identifies hosts that are vulnerable to NTLM reflection (a.k.a. NTLM **relay-back-to-self**). It authenticates with the supplied credential, opens the Remote Registry over SMB (port 445), reads the OS build / UBR fields and the SMB-signing configuration, then evaluates whether the patch level is below the mitigation threshold and whether SMB signing is enforced.

Each result row contains the target IP, the OS version (`OS_MAJOR`, `OS_MINOR`, `BUILD`, `UBR`), a `VULNERABLE` flag and `SIGNING_REQUIRED`. A host is flagged as vulnerable when its OS build is below the patch level that mitigates NTLM reflection **and** SMB signing is not enforced.

When a host is vulnerable, an attacker who can coerce that machine to authenticate to itself (via Spooler / [smbspooler](smbspooler.md), PetitPotam, …) can relay the authentication back to its own services, frequently achieving SYSTEM-level access — even from an unprivileged starting point.

!!! warning "Remote Registry must be running"
    The check reads OS build and signing settings from `HKLM\SYSTEM` over the **Remote Registry** service. If the service is disabled on the target, the scanner cannot determine the build and the result will not be accurate. Verify the service status before trusting a clean result.

!!! tip "Combine with coercion checks"
    - [smbspooler](smbspooler.md) — Print Spooler reachable? Coercion path open.
    - [smbwebdav](smbwebdav.md) — WebClient (WebDAV) reachable? Another reliable coercion vector.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication.

Enter the ID of the credential stored in the Credentials Window. A standard domain user usually has enough access to read the registry value used by this check.

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
Ports which trigger an automated `ntlmreflection` scan when discovered by other scanners. Pre-populated with `445/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
