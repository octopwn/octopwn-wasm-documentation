# SSH Banner Scanner (sshbanner)

The **SSH Banner Scanner** retrieves the protocol banner string that every SSH server sends immediately upon TCP connection (typically port 22). The banner usually carries the SSH software name and version, for example `SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6`. No authentication is performed, no credentials are required.

Each result row contains the target IP and the raw banner string. Banners are useful for fingerprinting the operating system and SSH implementation, identifying outdated or vulnerable SSH versions, and spotting non-standard or embedded SSH stacks. On many Linux distributions the banner also reveals the distribution and patch level — invaluable when prioritising targets for known exploits.

!!! tip "Pair with the related SSH scanners"
    - [sshinfo](sshinfo.md) — supported KEX algorithms, ciphers, MACs (algorithm hardening audit).
    - [sshauth](sshauth.md) — accepted authentication methods (password vs publickey vs gssapi).
    - [sshlogin](sshlogin.md) — actually validates a credential against the server.

!!! tip "Authentication"
    Banner grabbing is unauthenticated, but once you move on to [sshlogin](sshlogin.md) or
    open an interactive session, the OctoPwn [SSH client](../clients/ssh.md#authentication)
    only implements `password` and `publickey` — GSSAPI / keyboard-interactive / certificates
    are out of scope even when the server advertises them.

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
- **Port Group**: `p:<port>` (e.g., `p:22`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:22/tcp`).

---

### Advanced Parameters

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
Ports which trigger an automated `sshbanner` scan when discovered by other scanners. Pre-populated with `22/TCP, 2222/TCP, 22222/TCP`.

#### verifyhost
When enabled, the SSH client verifies the server host key. Disabled by default — banner grabbing is purely informational and does not need host-key trust.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
