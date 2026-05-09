# Nmap Scanner (nmap)

The **Nmap Scanner** wraps the `nmap` binary so that you can launch full Nmap scans from inside OctoPwn and have the results imported into the project automatically. The scanner builds an Nmap command line from your parameters (targets, ports, scan flags), runs `nmap` as a subprocess and streams its output into the console as the scan progresses. Once Nmap finishes, the XML output is parsed and every discovered host, port and service is stored in the project; the open ports are also registered as `<port>/TCP` target-port entries so the protocol-specific scanners can pick them up later.

Each result row contains the Nmap command that was executed and the raw XML output (base64-encoded) for archival.

!!! warning "Browser version not supported"
    `nmap` shells out to a local `nmap` binary and is **not compatible with the browser (WASM) version of OctoPwn**. Run it from the desktop / server build. The scanner is part of the **enterprise** tier.

!!! info "Prerequisites"
    - The `nmap` binary must be available in `PATH` (or set `nmappath` to its absolute location).
    - Some scan types — SYN scan (`-sS`), OS detection (`-O`) and many NSE scripts — require **root / sudo** privileges. Running OctoPwn unprivileged will silently degrade these scans to the next-best alternative (typically TCP connect).

!!! tip "When to use which"
    - [portscan](portscan.md) — built-in TCP-connect scanner. Works in the browser, no external binary, fine for quick port discovery.
    - **nmap** — when you need SYN scan, version detection, OS fingerprinting, NSE scripts or any other Nmap-specific feature.

---

## Parameters

### Normal Parameters

#### targets
Specifies the targets to scan. Targets are passed verbatim to Nmap, so any expression Nmap accepts also works here.

A list of targets can be specified in the following formats:

- **ID**: ID of the target server from the targets window.
- **IP**: Single IP address (e.g., `192.168.1.1`).
- **CIDR**: IP range in CIDR notation (e.g., `192.168.1.0/24`).
- **Hostname**: Resolvable hostname.
- **File**: Path to a file containing targets (must be in OctoPwn’s `/browserefs/volatile` directory).
- **Control word**: Use `all` to scan all stored targets.
- **Single Group**: `g:<groupname>` (e.g., `g:test1`).
- **Multiple Groups**: `g:<groupname1>,g:<groupname2>` (e.g., `g:test1,g:test2`).
- **Port Group**: `p:<port>` (e.g., `p:445`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:445/tcp`).

#### portdef
Comma-separated port specification passed straight to Nmap's `-p` flag. Defaults to `22,88,443,445,389,636,3389`. Accepts ranges (`1-1024`), `T:` / `U:` prefixes, etc.

#### flags
Extra Nmap flags. Defaults to `-sT -sV` (TCP connect + version detection). Use this to switch scan type, enable NSE scripts (`--script vuln`), tune timing (`-T4`), enable OS detection (`-O`), etc.

#### nmappath
Path to the `nmap` executable. Defaults to `nmap` (resolved via `PATH`). Set this when the binary lives in a non-standard location.

#### batchsize
Maximum number of targets passed to a single Nmap invocation. Defaults to `255`. Larger sets are split into multiple sequential Nmap runs.

---

### Advanced Parameters

#### maxruntime
Specifies the maximum runtime per host (in seconds). Set to `-1` to disable.

#### proxy
Specifies the proxy ID to use for the scan. Note that Nmap itself talks directly to targets — the proxy is only used by the OctoPwn-side wrapper.

#### resultsfile
Specifies a file for saving the scan results.

The file will be saved in OctoPwn’s `/browserefs/volatile` directory.

#### showerrors
Determines whether errors encountered during the scan should be displayed.

#### timeout
Sets the timeout (in seconds) for the OctoPwn-side wrapper. Nmap's own timing is controlled through the `flags` parameter (`-T<n>`, `--host-timeout`, `--max-rtt-timeout`, …).

#### triggerports
Ports which trigger an automated `nmap` scan when discovered by other scanners.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
