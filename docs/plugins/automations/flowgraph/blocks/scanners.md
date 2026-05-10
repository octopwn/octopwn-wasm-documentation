<!--
AUTO-GENERATED — DO NOT EDIT BY HAND.
Regenerate via:
    python scripts/generate_flowgraph_reference.py
Source of truth: octopwn/enterprise/flowgraph/registry.py.
-->

# Scanners

Every entry in `octopwn.scanners.OCTOPWN_SCANNER_TABLE` is auto-registered as a `SCANNER_<NAME>` block. Scanner blocks have a `target` input port, an optional `credential` port (for authenticated scanners), an optional `pair` input that bypasses the cross-product, and a `result` output that emits scan-result items. Family-specific params (dialect, protocol, port lists, …) are derived dynamically from `octopwn.common.scanparams` so they always reflect what the scanner itself accepts. For the full scanner catalogue (WASM compat, tier, etc.) see the [scanner overview](../../../scanners/index.md).

---

**49 block type(s) in this category.**

---

### `SCANNER_PORTSCAN`

*Category: `SCANNER`*

TCP connect scanner to discover open ports across target hosts

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `ports` | `list` | `['445', '22', '88', '3389']` | no | Ports to scan |
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `target` | `str` | Target IP or hostname |
| `port` | `int` | Port number |
| `protocol` | `str` | Protocol (TCP or UDP) |
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1046`

---

### `SCANNER_SMBSESSION`

*Category: `SCANNER`*

Lists active user sessions on SMB targets to map who is logged in where

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


---

### `SCANNER_SMBPROTO`

*Category: `SCANNER`*

Enumerates supported SMB dialects and signing settings per protocol version

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1046`

---

### `SCANNER_SMBPRINTNIGHTMARE`

*Category: `SCANNER`*

Tests for PrintNightmare (CVE-2021-1675 / CVE-2021-34527) vulnerability via SMB

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1210`

---

### `SCANNER_SMBFINGER`

*Category: `SCANNER`*

Fingerprints OS version and domain info from unauthenticated SMB NTLM handshakes

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `domainname` | `str` | NetBIOS domain name |
| `computername` | `str` | NetBIOS computer name |
| `dnscomputername` | `str` | DNS computer name (FQDN) |
| `dnsdomainname` | `str` | DNS domain name |
| `dnsforestname` | `str` | DNS forest name |
| `local_time` | `str` | Server local time |
| `os_build` | `str` | OS build number |
| `os_guess` | `str` | OS guess string (e.g. Windows Server 2019) |
| `os_major_version` | `str` | OS major version name |
| `os_minor_version` | `str` | OS minor version name |
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1046`

---

### `SCANNER_SMBIFACE`

*Category: `SCANNER`*

Enumerates network interfaces and IP addresses on targets via SMB

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


---

### `SCANNER_SMBADMIN`

*Category: `SCANNER`*

Tests admin-level access on targets by probing C$, Service Manager and Remote Registry

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `SHARE` | `bool` | Access to C$ (admin share) |
| `SERVICE` | `bool` | Access to Remote Service Manager |
| `REGISTRY` | `bool` | Access to Remote Registry |
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1135`

---

### `SCANNER_SMBFILE`

*Category: `SCANNER`*

Recursively enumerates shares, directories and files on SMB targets

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1083`

---

### `SCANNER_RDPSCREEN`

*Category: `SCANNER`*

Captures screenshots from RDP sessions for visual reconnaissance

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


---

### `SCANNER_RDPLOGIN`

*Category: `SCANNER`*

Tests credential validity against RDP servers for remote desktop access

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `data` | `str` | Login result string: always 'TRUE' (only successes stored) |
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1021.001`

---

### `SCANNER_RDPCAP`

*Category: `SCANNER`*

Enumerates RDP security capabilities including Restricted Admin and auth modes

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


---

### `SCANNER_KRB5USER`

*Category: `SCANNER`*

Enumerates valid AD usernames via Kerberos without credentials

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_krb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1087.002`

---

### `SCANNER_SNAFFLER`

*Category: `SCANNER`*

Rule-based file triage scanner that finds sensitive data in SMB shares

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `use_llm` | `bool` | false | no | Use LLM to extract credentials from matched files |
| `llm_model` | `str` | "" | no | LLM model name (empty = use global model) |
| `maxfilesize` | `int` | `10485760` | no | Maximum file size in bytes to download for inspection |
| `maxdownloads` | `int` | `4` | no | Max concurrent file downloads per target |
| `maxdownloadstotal` | `int` | `20` | no | Max concurrent file downloads across all targets |
| `keepfiles` | `bool` | false | no | Keep downloaded files instead of deleting after analysis |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `otype` | `str` | Object type: file, dir, or share |
| `rule` | `str` | Triage level (Black, Red, Yellow, Green) |
| `rule_name` | `str` | Name of the matching snaffler rule |
| `unc_path` | `str` | Full UNC path to the matched file/dir/share |
| `size` | `int` | File size in bytes |
| `size_human` | `str` | Human-readable file size |
| `last_write_time` | `str` | Last write time (ISO 8601) |
| `data` | `str` | Matched content snippet |
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1083` `T1552.001`

---

### `SCANNER_LDAPSIG`

*Category: `SCANNER`*

Checks LDAP signing and channel binding enforcement on domain controllers

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_ldap` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


---

### `SCANNER_SMBLAPS`

*Category: `SCANNER`*

Validates LAPS passwords against target hosts via SMB authentication

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1552.004`

---

### `SCANNER_NFS3FILE`

*Category: `SCANNER`*

Enumerates files and directories on NFS v3 shares

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


---

### `SCANNER_SMBSIG`

*Category: `SCANNER`*

Fast check of SMB signing status -- finds relay-attack targets

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `PROTO` | `str` | SMB dialect negotiated |
| `SIGN_ENABLED` | `bool` | Signing advertised by server |
| `SIGN_ENFORCED` | `bool` | Signing required by server |
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1046`

---

### `SCANNER_SMBSHARE`

*Category: `SCANNER`*

Enumerates SMB shares and tests for read/write access on each target

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `path` | `str` | UNC share path (e.g. \\host\share) |
| `writable` | `str` | Write access test result |
| `description` | `str` | Share description/remark |
| `access` | `str` | Access mask |
| `sddl` | `str` | Security descriptor (SDDL) |
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1135`

---

### `SCANNER_IPMICAPS`

*Category: `SCANNER`*

Discovers IPMI BMCs and enumerates their authentication capabilities

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1046`

---

### `SCANNER_IPMICIPHERZERO`

*Category: `SCANNER`*

Tests IPMI BMCs for unauthenticated cipher-zero access

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1552`

---

### `SCANNER_SNMPHOST`

*Category: `SCANNER`*

Queries SNMP agents for system description to identify devices

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1046`

---

### `SCANNER_HTTPHEADER`

*Category: `SCANNER`*

Fetches HTTP headers, status codes and page titles from web services

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `target` | `str` | Target IP or hostname |
| `url` | `str` | Full URL fetched |
| `port` | `int` | Port number |
| `status` | `int` | HTTP status code |
| `title` | `str` | Page title |
| `headers` | `str` | Response headers dict |
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1046`

---

### `SCANNER_CVE_2017_12542`

*Category: `SCANNER`*

Tests HP iLO 4 for CVE-2017-12542 authentication bypass

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1190`

---

### `SCANNER_MSSQLFINGER`

*Category: `SCANNER`*

Fingerprints OS and domain info from unauthenticated MSSQL NTLM handshakes

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `domainname` | `str` | NetBIOS domain name |
| `computername` | `str` | NetBIOS computer name |
| `dnscomputername` | `str` | DNS computer name (FQDN) |
| `dnsdomainname` | `str` | DNS domain name |
| `dnsforestname` | `str` | DNS forest name |
| `local_time` | `str` | Server local time |
| `os_build` | `str` | OS build number |
| `os_guess` | `str` | OS guess string |
| `os_major_version` | `str` | OS major version name |
| `os_minor_version` | `str` | OS minor version name |
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1046`

---

### `SCANNER_MSSQLQUERY`

*Category: `SCANNER`*

Runs a custom SQL query across multiple MSSQL servers and collects results

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


---

### `SCANNER_MSSQLLOGIN`

*Category: `SCANNER`*

Tests credential validity against MSSQL servers

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | MSSQL login succeeded |
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1021`

---

### `SCANNER_MSSQLADMIN`

*Category: `SCANNER`*

Checks sysadmin privileges on MSSQL servers with current credentials

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


---

### `SCANNER_MSSQLPIPE`

*Category: `SCANNER`*

Discovers MSSQL instances via SMB named pipes and tests SQL connectivity

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


---

### `SCANNER_SSHLOGIN`

*Category: `SCANNER`*

Tests credential validity against SSH servers for shell access

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_ssh` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | SSH login succeeded |
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1021.004`

---

### `SCANNER_SSHINFO`

*Category: `SCANNER`*

Enumerates SSH crypto algorithms (KEX, ciphers, MACs) for security auditing

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1046`

---

### `SCANNER_SSHBANNER`

*Category: `SCANNER`*

Retrieves SSH server banners for version fingerprinting

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1046`

---

### `SCANNER_SSHAUTH`

*Category: `SCANNER`*

Enumerates accepted authentication methods on SSH servers

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_ssh` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1046`

---

### `SCANNER_FTPLOGIN`

*Category: `SCANNER`*

Tests credential validity against FTP servers

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | FTP login succeeded |
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1021`

---

### `SCANNER_NMAP`

*Category: `SCANNER`*

Nmap wrapper for advanced port scanning with XML result import

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1046`

---

### `SCANNER_NUCLEI`

*Category: `SCANNER`*

Template-based web vulnerability scanner powered by Nuclei

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1595.002`

---

### `SCANNER_SMBWEBDAV`

*Category: `SCANNER`*

Detects WebDAV (WebClient) service for NTLM relay attack paths

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `AVAILABLE` | `bool` | WebClient (WebDAV) service running |
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1021.002`

---

### `SCANNER_SMBSPOOLER`

*Category: `SCANNER`*

Detects reachable Print Spooler services for coercion and RCE attacks

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `AVAILABLE` | `bool` | Print Spooler service reachable via RPC |
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1547.012`

---

### `SCANNER_SMBPSHISTORY`

*Category: `SCANNER`*

Retrieves PowerShell command history (PSReadline) from user profiles via SMB

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1552.001`

---

### `SCANNER_FTPANON`

*Category: `SCANNER`*

Tests FTP servers for anonymous login access

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | FTP anonymous login allowed |
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


---

### `SCANNER_MSSQLDBINFO`

*Category: `SCANNER`*

Maps the full database schema (databases, tables, columns) on MSSQL servers

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1046`

---

### `SCANNER_MSSQLSENSDATA`

*Category: `SCANNER`*

Scans MSSQL databases for sensitive data (PII, financial, credentials) using keyword matching

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1005`

---

### `SCANNER_WEBSCREENSHOT`

*Category: `SCANNER`*

Captures screenshots of web services for visual reconnaissance at scale

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1592`

---

### `SCANNER_NTLMREFLECTION`

*Category: `SCANNER`*

Tests for NTLM reflection (relay-to-self) vulnerability via remote registry

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1187`

---

### `SCANNER_NTLMV1`

*Category: `SCANNER`*

Checks if NTLMv1 is permitted by reading LmCompatibilityLevel from registry

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1557`

---

### `SCANNER_BASELINE`

*Category: `SCANNER`*

All-in-one baseline assessment combining 12+ checks per target

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1046`

---

### `SCANNER_SMBREGSESSION`

*Category: `SCANNER`*

Enumerates local user SIDs from the remote registry via SMB

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1012`

---

### `SCANNER_HTTPFINGER`

*Category: `SCANNER`*

Identifies web applications and technologies on HTTP/HTTPS services

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1046`

---

### `SCANNER_EVENT6SECRETS`

*Category: `SCANNER`*

Extracts embedded secrets (credentials, keys) from Windows Event Logs via SMB

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1552`

---

### `SCANNER_WMIADMIN`

*Category: `SCANNER`*

Tests admin-level WMI access for remote execution capabilities

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `raw_target` | no | Scan target — raw_target or scan_result from any source block or upstream scanner |
| `credential` | input | `credential_smb` | no | Compatible credential |
| `pair` | input | `scan_result` | yes | Pre-paired (tid, cid) items — bypasses target x credential cross-product |
| `result` | output | `scan_result` | no | Scan result items |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `timeout` | `int` | `10` | no | Per-host timeout in seconds |
| `skip_done` | `bool` | false | no | Skip (target, credential) pairs already scanned in a previous runloop iteration |
| `skip_target` | `bool` | false | no | Skip targets that already produced results in a previous runloop iteration |
| `skip_credential` | `bool` | false | no | Skip credentials that already produced results in a previous runloop iteration |

**Output schema — `result`**

| Field | Type | Description |
|-------|------|-------------|
| `ADMIN` | `bool` | WMI admin access confirmed |
| `resid` | `str` | Result ID (usually target IP or hostname) |
| `restype` | `str` | Result type class name |
| `__tid` | `int` | Target store ID |
| `__cid` | `int` | Credential store ID (null for unauthenticated scans) |


**MITRE ATT&CK:** `T1047`

---
