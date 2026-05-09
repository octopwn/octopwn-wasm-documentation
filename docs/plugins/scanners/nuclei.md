# Nuclei Scanner (nuclei)

The **Nuclei Scanner** wraps the upstream [Nuclei](https://github.com/projectdiscovery/nuclei) vulnerability scanner from ProjectDiscovery. It builds URLs from your target list and port configuration, launches the local `nuclei` binary as a subprocess, and streams findings back into the project in real time.

Nuclei runs a large library of YAML templates against web applications to detect vulnerabilities, misconfigurations, exposed admin panels, default credentials, CVE PoCs and more. Each finding pulled from Nuclei's JSONL output is normalised into a row containing `severity`, `template_id`, `matched_at`, `host`, `port`, `matcher`, `cve_id`, plus the raw Nuclei record (template name, description, references, CVE/CWE metadata, curl reproduction command, …) so the data integrates smoothly with the OctoPwn vulnerability tracking engine.

!!! warning "Browser version not supported"
    `nuclei` shells out to the `nuclei` binary on the host running OctoPwn. It is **not compatible with the browser (WASM) version**. Run it from the desktop / server build. The scanner is part of the **enterprise** tier.

!!! info "Prerequisites"
    The Nuclei binary must be available on the host and reachable via `PATH`:

    - macOS: `brew install nuclei`
    - Linux: `apt install nuclei` (or download a release from the [GitHub releases page](https://github.com/projectdiscovery/nuclei/releases)).
    - After installation, fetch the templates: `nuclei -update-templates`.

    If the binary is not found at `nucleipath`, the scan aborts with a clear error message.

!!! tip "Workflow"
    1. [portscan](portscan.md) → discover open TCP ports.
    2. [httpheader](httpheader.md) / [httpfinger](httpfinger.md) → confirm web services.
    3. **nuclei** → throw templated checks at the confirmed endpoints.

---

## Parameters

### Normal Parameters

#### targets
Specifies the targets to scan. URLs (`http://...` / `https://...`) are accepted as-is; bare IPs / hostnames are expanded into URLs using `ports` and `protocols`.

A list of targets can be specified in the following formats:

- **ID**: ID of the target server from the targets window.
- **IP**: Single IP address (e.g., `192.168.1.1`).
- **CIDR**: IP range in CIDR notation (e.g., `192.168.1.0/24`).
- **Hostname**: Resolvable hostname.
- **URL**: Full URL (e.g., `https://example.com/admin`) — used directly.
- **File**: Path to a file containing targets (must be in OctoPwn’s `/browserefs/volatile` directory).
- **Control word**: Use `all` to scan all stored targets.
- **Single Group**: `g:<groupname>` (e.g., `g:test1`).
- **Multiple Groups**: `g:<groupname1>,g:<groupname2>` (e.g., `g:test1,g:test2`).
- **Port Group**: `p:<port>` (e.g., `p:443`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:443/tcp`).

#### ports
Comma-separated list of TCP ports to test. Defaults to `80, 443, 8080, 8443, 4443, 2381`.

#### protocols
Which web schemes to try against each port. Defaults to `HTTP,HTTPS`.

#### templates
Restrict Nuclei to a template path or tag (`-t` flag). Examples: `cves/`, `exposures/`, `cves/2024/`. Leave empty to use Nuclei's default template selection.

#### severity
Restrict Nuclei to one or more severity levels (`-severity`). Comma-separated, valid values: `critical,high,medium,low,info`. Empty means "no filter".

---

### Advanced Parameters

#### nucleipath
Path to the `nuclei` executable. Defaults to `nuclei` (resolved via `PATH`). Set this when the binary lives in a non-standard location.

#### ratelimit
Maximum requests per second sent by Nuclei (`-rate-limit`). Defaults to `150`.

#### bulksize
Number of hosts processed per template (`-bulk-size`). Defaults to `25`.

#### concurrency
Number of templates run concurrently (`-concurrency`). Defaults to `25`.

#### timeout
Per-request timeout in seconds (`-timeout`). Defaults to `10`.

#### retries
Number of retries per failed request (`-retries`). Defaults to `1`.

#### nointeractsh
When `True` (default), the scanner passes `-no-interactsh` to disable Nuclei's out-of-band testing server. Set to `False` if your engagement permits OOB callbacks and you want to catch SSRF / blind-RCE templates.

#### maxruntime
Specifies the maximum runtime per host (in seconds). Set to `-1` to disable.

#### proxy
Specifies the proxy ID to use for the scan.

Enter the ID of the proxy to route the scan through. Proxies must be configured in the Proxy Window. Note that the Nuclei subprocess itself talks directly to targets — only the OctoPwn-side URL generation participates in proxy logic.

#### resultsfile
Specifies a file for saving the scan results.

The file will be saved in OctoPwn’s `/browserefs/volatile` directory.

#### showerrors
Determines whether errors encountered during the scan should be displayed.

#### triggerports
Ports which trigger an automated `nuclei` scan when discovered by other scanners.

#### workercount
Specifies the number of parallel workers for the OctoPwn-side scanner shell. Nuclei manages its own internal concurrency through `bulksize` / `concurrency`.

#### wsnetreuse
Internal parameter. Do not modify.
