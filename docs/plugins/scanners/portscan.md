# TCP Port Scanner (portscan)

The **TCP Port Scanner** discovers open TCP ports on each target by performing a full TCP connect against every target/port combination. The scanner takes a list of targets (IPs, CIDR ranges, hostnames, files, target IDs, target groups) and a list of ports, then tries to establish a TCP connection on every combination. A successful connection means the port is open; a timeout or refusal means it is closed or filtered. SOCKS proxy chaining is supported through the `proxy` parameter.

Each result row contains the target IP, the open port number and the protocol (`TCP`). Discovered open ports are **automatically registered as target-port entries in the project**, which makes them available to every protocol-specific scanner — so SMB-related checks light up as soon as 445 is found, RDP scanners see 3389, etc. This auto-registration is what makes `portscan` the natural first scanner to run on a fresh project.

!!! tip "Workflow"
    1. **portscan** — sweep the target subnet to populate the project with open ports.
    2. Other scanners with matching `triggerports` (`smbfinger` on 445, `sshbanner` on 22, `httpfinger` on 80/443, …) can then be launched on `targets=all` and they will only run against hosts where the relevant port is known to be open.

!!! info "Browser-friendly"
    Unlike [nmap](nmap.md), `portscan` is implemented in pure Python, runs inside the browser-based OctoPwn build, and does not need any external binary. It is less feature-rich than dedicated scanners (no SYN scan, no version detection, no NSE) — for those, prefer [nmap](nmap.md).

---

## Parameters

### Normal Parameters

#### ports
Comma-separated list of TCP ports to probe. Default: `22, 88, 443, 445, 3389`.

A more comprehensive set might include:
`21, 22, 25, 69, 80, 88, 135, 139, 152, 161, 389, 443, 445, 1433, 3389, 5985, 5986, 8080, 8443`.

#### protocol
Currently only `TCP` is supported.

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

---

### Advanced Parameters

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
Sets the timeout (in seconds) for each TCP connect attempt.

#### triggerports
Ports which trigger an automated `portscan` when discovered by other scanners.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
