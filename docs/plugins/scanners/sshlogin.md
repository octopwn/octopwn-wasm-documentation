# SSH Login Scanner (sshlogin)

The **SSH Login Scanner** validates a credential against one or more SSH servers (default port 22). For every target it performs a full SSH login — using either password or public-key authentication, depending on what the credential carries — and reports a `LOGIN_OK` boolean.

A successful login almost always means shell-level access to the host, which typically grants full command execution as the authenticated user. Use `sshlogin` to validate stolen or discovered credentials across many SSH endpoints in one pass, or to verify that service-account keys work on the expected set of servers.

!!! info "Supported authentication methods"
    Only **password** and **public-key** authentication are supported. Other SSH mechanisms (GSSAPI/Kerberos, host-based, certificate, keyboard-interactive, …) are **not** implemented by the OctoPwn SSH client and will be skipped even if the server advertises them via [sshauth](sshauth.md).

!!! tip "Authentication"
    This scanner uses the same authentication surface as the [SSH client](../clients/ssh.md#authentication):
    only `password` and `publickey` are implemented end-to-end. The `authtype` field below is
    inherited generic plumbing and has no effect — supply a credential whose secret type is
    a password or a private key and the right mechanism is selected automatically.

!!! tip "Pair with the related SSH scanners"
    - [sshbanner](sshbanner.md) — software name and version (no auth).
    - [sshinfo](sshinfo.md) — supported KEX algorithms, ciphers, MACs (no auth).
    - [sshauth](sshauth.md) — accepted authentication methods (no auth) — useful to know in advance whether your credential type is even supported.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication.

Enter the ID of the credential stored in the Credentials Window. Use a credential whose secret type is either a password or an SSH private key — these are the only two SSH authentication mechanisms supported.

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
- **Port Group**: `p:<port>` (e.g., `p:22`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:22/tcp`).

---

### Advanced Parameters

#### authtype
Inherited generic authentication-protocol selector (`NTLM` / `Kerberos`). It has no effect for `sshlogin` — the SSH transport only supports password and public-key authentication, and the actual mechanism is chosen from the credential's stored secret type. Leave at the default.

#### krbetypes
Inherited Kerberos parameter. Has no effect for `sshlogin` because Kerberos/GSSAPI is not a supported SSH authentication method.

#### krbrealm
Inherited Kerberos parameter. Has no effect for `sshlogin` because Kerberos/GSSAPI is not a supported SSH authentication method.

#### maxruntime
Specifies the maximum runtime per host (in seconds). Set to `-1` to disable.

#### protocol
Specifies the protocol. Fixed to `SSH` for this scanner.

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
Ports which trigger an automated `sshlogin` scan when discovered by other scanners. Pre-populated with `22/TCP, 2222/TCP, 22222/TCP`.

#### verifyhost
When enabled, the SSH client verifies the server host key. Disabled by default — for credential validation against many unknown servers you usually want to skip host-key checks.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
