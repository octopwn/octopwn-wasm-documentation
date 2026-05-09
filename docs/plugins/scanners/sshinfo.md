# SSH Algorithm Scanner (sshinfo)

The **SSH Algorithm Scanner** enumerates the full set of cryptographic algorithms each target SSH server supports — without authenticating. It completes the key-exchange init phase (`SSH_MSG_KEXINIT`) and extracts every advertised algorithm category in one round trip.

The following algorithm categories are gathered:

- **kex_algorithms** — Key exchange methods (e.g. `curve25519-sha256`, `diffie-hellman-group14-sha256`).
- **host_key_algorithms** — Server host-key types (e.g. `ssh-ed25519`, `rsa-sha2-512`).
- **encryption_algorithms** — Symmetric ciphers (e.g. `aes256-gcm@openssh.com`, `chacha20-poly1305@openssh.com`).
- **mac_algorithms** — Message authentication codes (e.g. `hmac-sha2-256-etm@openssh.com`).
- **compression_algorithms** — Supported compression (e.g. `none`, `zlib@openssh.com`).
- **languages** — Rarely used, reported when present.

Each row is a single target with comma-separated algorithm lists. This data is essential for SSH security auditing: identifying servers that still offer weak algorithms (`diffie-hellman-group1-sha1`, `arcfour`, `hmac-md5`) or that lack modern AEAD ciphers helps prioritise hardening efforts and may reveal attack surface for downgrade attacks.

!!! tip "Pair with the related SSH scanners"
    - [sshbanner](sshbanner.md) — software name and version.
    - [sshauth](sshauth.md) — accepted authentication methods.
    - [sshlogin](sshlogin.md) — credential validation.

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
Ports which trigger an automated `sshinfo` scan when discovered by other scanners. Pre-populated with `22/TCP, 2222/TCP, 22222/TCP`.

#### verifyhost
When enabled, the SSH client verifies the server host key. Disabled by default — `sshinfo` only inspects the server's KEXINIT and never moves on to authentication.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
