# HTTP Fingerprint Scanner (httpfinger)

The **HTTP Fingerprint Scanner** identifies web applications and technologies running on HTTP/HTTPS services across your target hosts by matching responses against a built-in library of service signatures. It connects to each target on the configured ports over both HTTP and HTTPS, then fingerprints the service by analysing response patterns. Web servers, application frameworks, CMS platforms, API gateways, management consoles and more are all in scope.

Each result row contains the target IP, the URL, the detected service name, its category, a CPE identifier, the page title and the `Server` header. This makes the scanner an essential first step for web-attack surface mapping: it tells you exactly what is running on each port so you can prioritise manual testing or feed the confirmed endpoints into a targeted vulnerability scan with the [nuclei](nuclei.md) scanner. It is also the fastest way to discover forgotten admin panels, development servers and APIs that hide behind unexpected ports.

!!! tip "Workflow"
    Run [portscan](portscan.md) first to discover open TCP ports across your subnet, then point `httpfinger` at the discovered web ports. The detected services can then be passed to [httpheader](httpheader.md) for header analysis or to [nuclei](nuclei.md) for template-based vulnerability detection.

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
- **Port Group**: `p:<port>` (e.g., `p:445`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:445/tcp`).

#### ports
Comma-separated list of TCP ports to probe. Defaults cover the most common web ports: `80, 443, 8080, 8443, 4443, 2381`.

#### protocols
Which web schemes to try against each port. Defaults to `http,https`. The scanner tries both unless you pin it to one.

#### services
Restricts the fingerprinting to a subset of the built-in service catalogue. The default value `all` matches every known signature.

#### continue_on_success
When `False` (default), the scanner stops probing additional services on a target/port once it has produced a positive match. Set to `True` to keep matching every signature even after a hit — useful when multiple frameworks may be stacked on the same endpoint.

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
Sets the timeout (in seconds) for each connection attempt.

#### triggerports
Ports which trigger an automated `httpfinger` scan when discovered by other scanners. Pre-populated with the same default web port set.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
