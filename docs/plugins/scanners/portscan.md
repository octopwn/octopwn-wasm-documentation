# Port Scanner (portscan)

The **Port Scanner** in OctoPwn performs basic TCP port scanning on specified targets. While functional, this scanner is less feature-rich compared to dedicated tools like **Nmap**, **Masscan**, or **Unicornscan**. It is recommended to use this scanner only when those tools are unavailable.

---

## Parameters

### Normal Parameters

#### ports
Specifies the ports to scan.

A comma-separated list of ports to include in the scan. Example: `22,88,443,445,3389`. 

A more comprehensive list may include: `25,80,88,443,445,8080,8443,5985,5986,3389,139,22,21,69,389,161,1433,135,152`
#### protocol
Specifies the protocol for the scan.

Currently, only `TCP` is supported for port scanning.
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

#### maxruntime
Specifies the maximum runtime for the scanner.

#### proxy
Specifies the proxy ID to use for the scan.

Enter the ID of the proxy to route the scan through. Proxies must be configured in the Proxy Window.

#### resultsfile
Specifies a file for saving the scan results.

The file will be saved in OctoPwn’s `/browserefs/volatile` directory.
#### showerrors
Determines whether errors encountered during the scan should be displayed.

#### timeout
Sets the timeout (in seconds) for each target.

#### workercount
Specifies the number of parallel workers for the scan.
#### wsnetreuse
Internal parameter. Do not modify.
