# HTTP Header Scanner (httpheader)

The **HTTP Header Scanner** is a lightweight first-pass tool for web reconnaissance. It sends a single `GET` request over both HTTP and HTTPS to every target/port combination, captures the full response headers, the HTTP status code and the page `<title>` tag. No authentication is performed.

Each result row contains the target IP, the URL, the status code, the page title, the `Server` string and the complete header set as a dictionary. That is enough to identify the web technology stack from `Server` / `X-Powered-By`, spot administration panels and default installations from the page title, and flag missing security headers (`Strict-Transport-Security`, `Content-Security-Policy`, `X-Frame-Options`, …) for the report. Each successfully probed target/port also gets registered as a `<port>/TCP` target-port entry, so follow-up scanners can pick it up automatically.

!!! tip "When to use which web scanner"
    - **httpheader** — fastest, returns every header and the page title. Good for triage and reporting.
    - [httpfinger](httpfinger.md) — heavier, performs signature-based service identification.
    - [webscreenshot](webscreenshot.md) — visual triage, captures full-page screenshots.
    - [nuclei](nuclei.md) — full template-based vulnerability scan.

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
Comma-separated list of TCP ports to probe. Defaults to `80, 443, 8080, 8443, 4443, 2381`.

#### protocols
Which web schemes to try. Defaults to `HTTP,HTTPS`; the scanner tries both unless you restrict the list.

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
Ports which trigger an automated `httpheader` scan when discovered by other scanners.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
