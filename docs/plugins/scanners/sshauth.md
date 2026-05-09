# SSH Authentication Methods Scanner (sshauth)

The **SSH Authentication Methods Scanner** enumerates which authentication methods each target SSH server is willing to accept. The scanner connects, requests the list of allowed authentication methods, and emits one row per target/method pair.

Common results include `password`, `publickey`, `keyboard-interactive`, `gssapi-with-mic` and `hostbased`. This information is critical for planning your approach: servers that accept `password` can be targeted with credential spraying or brute force, servers that only accept `publickey` require a stolen private key, and the presence of `gssapi-with-mic` indicates Kerberos integration which opens up ticket-based attack paths.

!!! tip "Authentication"
    Even when this scanner reports `keyboard-interactive`, `gssapi-with-mic` or `hostbased`,
    the OctoPwn [SSH client](../clients/ssh.md#authentication) only implements `password`
    and `publickey`. Servers that don't advertise at least one of those two will not be
    usable from OctoPwn, regardless of what `sshauth` shows here.

!!! tip "Pair with the related SSH scanners"
    - [sshbanner](sshbanner.md) — software name and version.
    - [sshinfo](sshinfo.md) — supported KEX algorithms, ciphers, MACs.
    - [sshlogin](sshlogin.md) — actually validates a credential against the server.

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
Ports which trigger an automated `sshauth` scan when discovered by other scanners. Pre-populated with `22/TCP, 2222/TCP, 22222/TCP`.

#### verifyhost
When enabled, the SSH client verifies the server host key. Disabled by default.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
