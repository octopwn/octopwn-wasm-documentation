# Web Screenshot Scanner (webscreenshot)

The **Web Screenshot Scanner** captures screenshots of web services using a headless Chrome instance and returns the image data as base64-encoded PNGs. The scanner iterates over each target/port combination (both HTTP and HTTPS), navigates to the URL, and renders a screenshot at a configurable resolution (default `1024x768`). When a page loads successfully on one protocol, the other is skipped for that target/port to save time.

Each result row contains the URL and the base64-encoded screenshot. This is visual reconnaissance at scale — perfect for triaging hundreds of web services to spot admin panels, login pages, default installations, internal dashboards and other high-value targets without manually opening each URL.

!!! warning "Browser version not supported"
    `webscreenshot` shells out to a local Chrome installation and is therefore **not compatible with the browser (WASM) version of OctoPwn**. Run it from the desktop / server build of OctoPwn. The scanner is part of the **enterprise** tier.

!!! tip "Workflow"
    1. Use [portscan](portscan.md) to discover open TCP ports.
    2. Run [httpheader](httpheader.md) or [httpfinger](httpfinger.md) to confirm web services.
    3. Point `webscreenshot` at the confirmed endpoints to triage them visually.
    4. Feed the interesting URLs to [nuclei](nuclei.md) for template-based vulnerability checks.

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
- **Port Group**: `p:<port>` (e.g., `p:443`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:443/tcp`).

#### portdef
Comma-separated list of TCP ports to capture. Defaults to `80, 443, 8443, 8444, 8080`.

#### width
Width (in pixels) of the rendered screenshot. Defaults to `1024`.

#### height
Height (in pixels) of the rendered screenshot. Defaults to `768`.

#### batchsize
Number of URLs Chrome processes in a single batch. Defaults to `10`. Lower values reduce memory pressure; higher values speed up large scans.

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
Sets the timeout (in seconds) for each Chrome navigation.

#### triggerports
Ports which trigger an automated `webscreenshot` scan when discovered by other scanners.

#### workercount
Specifies the number of parallel workers for the scan. Note that Chrome itself batches per `batchsize` — most parallelism is controlled by that parameter.

#### wsnetreuse
Internal parameter. Do not modify.
