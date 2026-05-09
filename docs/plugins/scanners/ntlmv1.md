# NTLMv1 Scanner (ntlmv1)

The **NTLMv1 Scanner** checks whether a target host still permits the legacy **NTLMv1** authentication protocol. It connects over SMB (port 445), authenticates with the supplied credential, then opens the Remote Registry and reads:

```
HKLM\SYSTEM\CurrentControlSet\Control\Lsa\LmCompatibilityLevel
```

A value of `0` or `1` means the host will accept (and respond with) NTLMv1 challenges, which are dramatically weaker than NTLMv2:

- NTLMv1 captured hashes can often be cracked to **plaintext** on commodity GPU hardware in a matter of hours.
- In relay scenarios NTLMv1 lacks the server-challenge binding that protects NTLMv2, broadening the attack surface.
- Many compliance frameworks (CIS, STIG, PCI-DSS) explicitly prohibit anything below `LmCompatibilityLevel = 3`.

Each result row contains the target IP, the OS version (`OS_MAJOR`, `OS_MINOR`, `BUILD`), the raw `LMCOMPATIBILITYLEVEL` value and a `VULNERABLE` boolean (`True` when the value is `0` or `1`).

!!! warning "Administrator access required"
    Reading the `LSA` registry key requires administrative access on the target. The credential supplied to this scanner must hold local-admin privileges, otherwise the registry open will fail and the result will be reported as an error.

!!! warning "Remote Registry must be running"
    The check goes through the **Remote Registry** service. If the service is disabled, the scanner cannot read the value.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication. Must hold local-admin privileges on the target.

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
Ports which trigger an automated `ntlmv1` scan when discovered by other scanners. Pre-populated with `445/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
