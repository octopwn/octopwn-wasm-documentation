# SMB Spooler Scanner (smbspooler)

The **SMB Spooler Scanner** detects whether the Windows **Print Spooler** service (`spoolsv`) is reachable on each target via RPC. It binds to the Spooler RPC interface (typically over port 135 endpoint mapper and 445 SMB) and reports a simple `AVAILABLE` boolean per host. No credentials are required.

An exposed Print Spooler unlocks two well-known attack families:

- **PrinterBug / SpoolSample** — abuse the `RpcRemoteFindFirstPrinterChangeNotification` (`MS-RPRN`) interface to coerce the target machine to authenticate back to an attacker-controlled host. Combined with [smbwebdav](smbwebdav.md) targets and an NTLM relay, this is a reliable path to RBCD abuse and lateral movement.
- **PrintNightmare** (CVE-2021-1675 / CVE-2021-34527) — remote code execution via the Spooler. Use the **smbprintnightmare** scanner to confirm whether a given host is still exploitable after patching.

Even on fully patched hosts where PrintNightmare RCE is fixed, a reachable Spooler is still a coercion sink — so this finding remains relevant for any engagement that touches NTLM relay paths.

!!! tip "Coercion + relay workflow"
    1. **smbspooler** — find Spooler-enabled hosts.
    2. [smbwebdav](smbwebdav.md) — find WebDAV-enabled relay sinks (or just any non-signing-enforced service).
    3. Start the relay server (Servers → relay).
    4. Use the printerbug attack to coerce the discovered Spooler hosts.

!!! tip "Drive coercion + RCE from the SMB client"
    When you have a credential to act from, the [SMB client](../clients/smb.md) exposes
    the matching coercion and RCE primitives directly:
    [`printerbug` and other NTLM-coercion commands](../clients/smb.md#ntlm-coercion), and the
    [`printnightmare` family in the vulnerabilities group](../clients/smb.md#vulnerabilities).

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
Ports which trigger an automated `smbspooler` scan when discovered by other scanners. Pre-populated with `135/TCP, 445/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
