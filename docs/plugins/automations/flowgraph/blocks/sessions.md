<!--
AUTO-GENERATED — DO NOT EDIT BY HAND.
Regenerate via:
    python scripts/generate_flowgraph_reference.py
Source of truth: octopwn/enterprise/flowgraph/registry.py.
-->

# Sessions and ID splitters

`OPEN_SESSION_<CLIENT>` blocks consume a `target` (and a protocol-typed `credential` where required) and emit a `session_<client>` reference on success or an `error` dict on failure. One block is generated per entry in `octopwn.clients.OCTOPWN_CLIENT_TABLE`. The `result` input port accepts a combined scan-result with both `__tid` and `__cid` set (typically straight out of an authenticated scanner like `SCANNER_SMBADMIN`) and opens exactly one session per item.

`ID_SPLITTER` and `ID_SPLITTER_PAIR` unpack a session or error item back into target / credential identifiers so downstream attack blocks can be wired without losing provenance. Prefer `ID_SPLITTER_PAIR` whenever each (target, credential) pair should run an attack exactly once.

---

**17 block type(s) in this category.**

---

### `OPEN_SESSION_KERBEROS`

*Category: `SESSION`*

Opens an authenticated Kerberos (KRB5) client session to a host using the provided credential.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `result` | input | `scan_result` | no | Combined scan result with __tid+__cid from an authenticated scanner — opens exactly one session per item |
| `host` | input | `scan_result` | no | Host dict with __tid (cross-product with credential port) |
| `credential` | input | `credential_krb` | no | KERBEROS-compatible credential (cross-product with host port) |
| `session` | output | `session_kerberos` | no | KERBEROS session reference: {session_id, target_id, credential_id} |
| `error` | output | `error` | no | Error dict if session could not be opened |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `atype` | `str` | `TGT` | no | Auth type (default: TGT) |
| `timeout` | `int` | `10` | no | Connection timeout in seconds |

---

### `OPEN_SESSION_LDAP`

*Category: `SESSION`*

Opens an authenticated LDAP client session to a host using the provided credential.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `result` | input | `scan_result` | no | Combined scan result with __tid+__cid from an authenticated scanner — opens exactly one session per item |
| `host` | input | `scan_result` | no | Host dict with __tid (cross-product with credential port) |
| `credential` | input | `credential_ldap` | no | LDAP-compatible credential (cross-product with host port) |
| `session` | output | `session_ldap` | no | LDAP session reference: {session_id, target_id, credential_id} |
| `error` | output | `error` | no | Error dict if session could not be opened |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `atype` | `str` | `NTLM` | no | Auth type (default: NTLM) |
| `timeout` | `int` | `10` | no | Connection timeout in seconds |

---

### `OPEN_SESSION_SMB`

*Category: `SESSION`*

Opens an authenticated SMB client session to a host using the provided credential.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `result` | input | `scan_result` | no | Combined scan result with __tid+__cid from an authenticated scanner — opens exactly one session per item |
| `host` | input | `scan_result` | no | Host dict with __tid (cross-product with credential port) |
| `credential` | input | `credential_smb` | no | SMB-compatible credential (cross-product with host port) |
| `session` | output | `session_smb` | no | SMB session reference: {session_id, target_id, credential_id} |
| `error` | output | `error` | no | Error dict if session could not be opened |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `atype` | `str` | `NTLM` | no | Auth type (default: NTLM) |
| `timeout` | `int` | `10` | no | Connection timeout in seconds |

**MITRE ATT&CK:** `T1021.002`

---

### `OPEN_SESSION_SSH`

*Category: `SESSION`*

Opens an authenticated SSH client session to a host using the provided credential.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `result` | input | `scan_result` | no | Combined scan result with __tid+__cid from an authenticated scanner — opens exactly one session per item |
| `host` | input | `scan_result` | no | Host dict with __tid (cross-product with credential port) |
| `credential` | input | `credential_ssh` | no | SSH-compatible credential (cross-product with host port) |
| `session` | output | `session_ssh` | no | SSH session reference: {session_id, target_id, credential_id} |
| `error` | output | `error` | no | Error dict if session could not be opened |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `atype` | `str` | `PASSWORD` | no | Auth type (default: PASSWORD) |
| `timeout` | `int` | `10` | no | Connection timeout in seconds |

**MITRE ATT&CK:** `T1021.004`

---

### `OPEN_SESSION_NETCAT`

*Category: `SESSION`*

Opens an authenticated Netcat client session to a host using the provided credential.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `result` | input | `scan_result` | no | Combined scan result with __tid+__cid from an authenticated scanner — opens exactly one session per item |
| `host` | input | `scan_result` | no | Host dict with __tid (cross-product with credential port) |
| `credential` | input | `credential` | no | NETCAT-compatible credential (cross-product with host port) |
| `session` | output | `session_netcat` | no | NETCAT session reference: {session_id, target_id, credential_id} |
| `error` | output | `error` | no | Error dict if session could not be opened |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `atype` | `str` | `NONE` | no | Auth type (default: NONE) |
| `timeout` | `int` | `10` | no | Connection timeout in seconds |

---

### `OPEN_SESSION_RDP`

*Category: `SESSION`*

Opens an authenticated RDP client session to a host using the provided credential.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `result` | input | `scan_result` | no | Combined scan result with __tid+__cid from an authenticated scanner — opens exactly one session per item |
| `host` | input | `scan_result` | no | Host dict with __tid (cross-product with credential port) |
| `credential` | input | `credential` | no | RDP-compatible credential (cross-product with host port) |
| `session` | output | `session_rdp` | no | RDP session reference: {session_id, target_id, credential_id} |
| `error` | output | `error` | no | Error dict if session could not be opened |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `atype` | `str` | `NTLM` | no | Auth type (default: NTLM) |
| `timeout` | `int` | `10` | no | Connection timeout in seconds |

**MITRE ATT&CK:** `T1021.001`

---

### `OPEN_SESSION_DNS`

*Category: `SESSION`*

Opens an authenticated DNS client session to a host using the provided credential.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `result` | input | `scan_result` | no | Combined scan result with __tid+__cid from an authenticated scanner — opens exactly one session per item |
| `host` | input | `scan_result` | no | Host dict with __tid (cross-product with credential port) |
| `credential` | input | `credential` | no | DNS-compatible credential (cross-product with host port) |
| `session` | output | `session_dns` | no | DNS session reference: {session_id, target_id, credential_id} |
| `error` | output | `error` | no | Error dict if session could not be opened |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `atype` | `str` | `NONE` | no | Auth type (default: NONE) |
| `timeout` | `int` | `10` | no | Connection timeout in seconds |

---

### `OPEN_SESSION_DCEDRSUAPI`

*Category: `SESSION`*

Opens an authenticated DCE-DRSUAPI client session to a host using the provided credential.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `result` | input | `scan_result` | no | Combined scan result with __tid+__cid from an authenticated scanner — opens exactly one session per item |
| `host` | input | `scan_result` | no | Host dict with __tid (cross-product with credential port) |
| `credential` | input | `credential` | no | DCEDRSUAPI-compatible credential (cross-product with host port) |
| `session` | output | `session_dcedrsuapi` | no | DCEDRSUAPI session reference: {session_id, target_id, credential_id} |
| `error` | output | `error` | no | Error dict if session could not be opened |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `atype` | `str` | `NTLM` | no | Auth type (default: NTLM) |
| `timeout` | `int` | `10` | no | Connection timeout in seconds |

**MITRE ATT&CK:** `T1021`

---

### `OPEN_SESSION_WINRM`

*Category: `SESSION`*

Opens an authenticated WinRM client session to a host using the provided credential.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `result` | input | `scan_result` | no | Combined scan result with __tid+__cid from an authenticated scanner — opens exactly one session per item |
| `host` | input | `scan_result` | no | Host dict with __tid (cross-product with credential port) |
| `credential` | input | `credential` | no | WINRM-compatible credential (cross-product with host port) |
| `session` | output | `session_winrm` | no | WINRM session reference: {session_id, target_id, credential_id} |
| `error` | output | `error` | no | Error dict if session could not be opened |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `atype` | `str` | `NTLM` | no | Auth type (default: NTLM) |
| `timeout` | `int` | `10` | no | Connection timeout in seconds |

**MITRE ATT&CK:** `T1021.006`

---

### `OPEN_SESSION_NFS3`

*Category: `SESSION`*

Opens an authenticated NFS client session to a host using the provided credential.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `result` | input | `scan_result` | no | Combined scan result with __tid+__cid from an authenticated scanner — opens exactly one session per item |
| `host` | input | `scan_result` | no | Host dict with __tid (cross-product with credential port) |
| `credential` | input | `credential` | no | NFS3-compatible credential (cross-product with host port) |
| `session` | output | `session_nfs3` | no | NFS3 session reference: {session_id, target_id, credential_id} |
| `error` | output | `error` | no | Error dict if session could not be opened |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `atype` | `str` | `NONE` | no | Auth type (default: NONE) |
| `timeout` | `int` | `10` | no | Connection timeout in seconds |

---

### `OPEN_SESSION_SNMP`

*Category: `SESSION`*

Opens an authenticated SNMP client session to a host using the provided credential.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `result` | input | `scan_result` | no | Combined scan result with __tid+__cid from an authenticated scanner — opens exactly one session per item |
| `host` | input | `scan_result` | no | Host dict with __tid (cross-product with credential port) |
| `credential` | input | `credential` | no | SNMP-compatible credential (cross-product with host port) |
| `session` | output | `session_snmp` | no | SNMP session reference: {session_id, target_id, credential_id} |
| `error` | output | `error` | no | Error dict if session could not be opened |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `atype` | `str` | `v2c` | no | Auth type (default: v2c) |
| `timeout` | `int` | `10` | no | Connection timeout in seconds |

---

### `OPEN_SESSION_NTP`

*Category: `SESSION`*

Opens an authenticated NTP client session to a host using the provided credential.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `result` | input | `scan_result` | no | Combined scan result with __tid+__cid from an authenticated scanner — opens exactly one session per item |
| `host` | input | `scan_result` | no | Host dict with __tid (cross-product with credential port) |
| `credential` | input | `credential` | no | NTP-compatible credential (cross-product with host port) |
| `session` | output | `session_ntp` | no | NTP session reference: {session_id, target_id, credential_id} |
| `error` | output | `error` | no | Error dict if session could not be opened |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `atype` | `str` | `NONE` | no | Auth type (default: NONE) |
| `timeout` | `int` | `10` | no | Connection timeout in seconds |

---

### `OPEN_SESSION_MSSQL`

*Category: `SESSION`*

Opens an authenticated MSSQL client session to a host using the provided credential.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `result` | input | `scan_result` | no | Combined scan result with __tid+__cid from an authenticated scanner — opens exactly one session per item |
| `host` | input | `scan_result` | no | Host dict with __tid (cross-product with credential port) |
| `credential` | input | `credential` | no | MSSQL-compatible credential (cross-product with host port) |
| `session` | output | `session_mssql` | no | MSSQL session reference: {session_id, target_id, credential_id} |
| `error` | output | `error` | no | Error dict if session could not be opened |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `atype` | `str` | `NTLM` | no | Auth type (default: NTLM) |
| `timeout` | `int` | `10` | no | Connection timeout in seconds |

**MITRE ATT&CK:** `T1021`

---

### `OPEN_SESSION_FTP`

*Category: `SESSION`*

Opens an authenticated FTP client session to a host using the provided credential.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `result` | input | `scan_result` | no | Combined scan result with __tid+__cid from an authenticated scanner — opens exactly one session per item |
| `host` | input | `scan_result` | no | Host dict with __tid (cross-product with credential port) |
| `credential` | input | `credential` | no | FTP-compatible credential (cross-product with host port) |
| `session` | output | `session_ftp` | no | FTP session reference: {session_id, target_id, credential_id} |
| `error` | output | `error` | no | Error dict if session could not be opened |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `atype` | `str` | `PASSWORD` | no | Auth type (default: PASSWORD) |
| `timeout` | `int` | `10` | no | Connection timeout in seconds |

**MITRE ATT&CK:** `T1021`

---

### `OPEN_SESSION_WMI`

*Category: `SESSION`*

Opens an authenticated WMI client session to a host using the provided credential.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `result` | input | `scan_result` | no | Combined scan result with __tid+__cid from an authenticated scanner — opens exactly one session per item |
| `host` | input | `scan_result` | no | Host dict with __tid (cross-product with credential port) |
| `credential` | input | `credential` | no | WMI-compatible credential (cross-product with host port) |
| `session` | output | `session_wmi` | no | WMI session reference: {session_id, target_id, credential_id} |
| `error` | output | `error` | no | Error dict if session could not be opened |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `atype` | `str` | `NTLM` | no | Auth type (default: NTLM) |
| `timeout` | `int` | `10` | no | Connection timeout in seconds |

**MITRE ATT&CK:** `T1047`

---

### `ID_SPLITTER`

*Category: `SESSION`*

Unpacks session references and/or error dicts into separate target and credential flows. Accepts items from both the session port (OPEN_SESSION_* success output) and the error port (OPEN_SESSION_* or CMD_* error output). Emits a __tid dict on the target port and a __cid dict on the credential port for each item that carries the respective ID. Items that yield neither are silently dropped. Wire target → attack block target port, credential → attack block credential port. NOTE: emits target and credential on separate ports — downstream will cross-product them. Use ID_SPLITTER_PAIR instead if you want each (target, credential) pair to run exactly once.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `any` | yes | Session reference from OPEN_SESSION_* success output |
| `error` | input | `any` | yes | Error dict from OPEN_SESSION_* or CMD_* error output |
| `target` | output | `scan_result` | no | Target dict {__tid} for each resolvable item |
| `credential` | output | `credential` | no | Credential dict {__cid} for each resolvable item |

**Parameters**

*No parameters.*

---

### `ID_SPLITTER_PAIR`

*Category: `SESSION`*

Unpacks session references and/or error dicts into paired {__tid, __cid} dicts. Unlike ID_SPLITTER (which emits on separate ports causing cross-product fan-out), this block keeps each (target_id, credential_id) pair together on a single "pair" port. Wire pair → attack block pair port so each session runs exactly once with its own credential. Items missing either ID are silently dropped. Set skip_done=true in runloop graphs to suppress pairs already emitted in a previous iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `any` | yes | Session reference from OPEN_SESSION_* success output |
| `error` | input | `any` | yes | Error dict from OPEN_SESSION_* or CMD_* error output |
| `pair` | output | `scan_result` | no | Paired {__tid, __cid} dict — one per session |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `skip_done` | `bool` | false | no | Skip (tid, cid) pairs already emitted in a previous runloop iteration |

---
