<!--
AUTO-GENERATED — DO NOT EDIT BY HAND.
Regenerate via:
    python scripts/generate_flowgraph_reference.py
Source of truth: octopwn/enterprise/flowgraph/registry.py.
-->

# Session commands

A `CMD_<CLIENT>` block runs any command supported by a live `<CLIENT>` session — the command list comes straight from the same command map that drives the interactive console for that client. One block is generated per entry in `OCTOPWN_CLIENT_TABLE`. Wire the optional `data` input to feed dynamic per-invocation arguments (e.g. one share name per item) from an upstream scanner.

---

**15 block type(s) in this category.**

---

### `CMD_KERBEROS`

*Category: `COMMAND`*

Runs any Kerberos (KRB5) client command on an open session. Command list is sourced live from the server commandMap. Wire the optional data port to feed upstream results as dynamic command arguments (cross-product: each session × each data item).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_kerberos` | no | KERBEROS session reference |
| `data` | input | `scan_result` | yes | Optional dynamic params — items merged into command kwargs per invocation |
| `result` | output | `scan_result` | no | Command result items |
| `session_out` | output | `session_kerberos` | no | Pass-through: same session references from input |
| `error` | output | `error` | no | Error dict if command fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `command` | `str` |  | yes | KERBEROS command to run |
| `skip_done` | `bool` | false | no | Skip sessions already processed in a previous runloop iteration |

---

### `CMD_LDAP`

*Category: `COMMAND`*

Runs any LDAP client command on an open session. Command list is sourced live from the server commandMap. Wire the optional data port to feed upstream results as dynamic command arguments (cross-product: each session × each data item).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_ldap` | no | LDAP session reference |
| `data` | input | `scan_result` | yes | Optional dynamic params — items merged into command kwargs per invocation |
| `result` | output | `scan_result` | no | Command result items |
| `session_out` | output | `session_ldap` | no | Pass-through: same session references from input |
| `error` | output | `error` | no | Error dict if command fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `command` | `str` |  | yes | LDAP command to run |
| `skip_done` | `bool` | false | no | Skip sessions already processed in a previous runloop iteration |

---

### `CMD_SMB`

*Category: `COMMAND`*

Runs any SMB client command on an open session. Command list is sourced live from the server commandMap. Wire the optional data port to feed upstream results as dynamic command arguments (cross-product: each session × each data item).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_smb` | no | SMB session reference |
| `data` | input | `scan_result` | yes | Optional dynamic params — items merged into command kwargs per invocation |
| `result` | output | `scan_result` | no | Command result items |
| `session_out` | output | `session_smb` | no | Pass-through: same session references from input |
| `error` | output | `error` | no | Error dict if command fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `command` | `str` |  | yes | SMB command to run |
| `skip_done` | `bool` | false | no | Skip sessions already processed in a previous runloop iteration |

---

### `CMD_SSH`

*Category: `COMMAND`*

Runs any SSH client command on an open session. Command list is sourced live from the server commandMap. Wire the optional data port to feed upstream results as dynamic command arguments (cross-product: each session × each data item).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_ssh` | no | SSH session reference |
| `data` | input | `scan_result` | yes | Optional dynamic params — items merged into command kwargs per invocation |
| `result` | output | `scan_result` | no | Command result items |
| `session_out` | output | `session_ssh` | no | Pass-through: same session references from input |
| `error` | output | `error` | no | Error dict if command fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `command` | `str` |  | yes | SSH command to run |
| `skip_done` | `bool` | false | no | Skip sessions already processed in a previous runloop iteration |

---

### `CMD_NETCAT`

*Category: `COMMAND`*

Runs any Netcat client command on an open session. Command list is sourced live from the server commandMap. Wire the optional data port to feed upstream results as dynamic command arguments (cross-product: each session × each data item).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_netcat` | no | NETCAT session reference |
| `data` | input | `scan_result` | yes | Optional dynamic params — items merged into command kwargs per invocation |
| `result` | output | `scan_result` | no | Command result items |
| `session_out` | output | `session_netcat` | no | Pass-through: same session references from input |
| `error` | output | `error` | no | Error dict if command fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `command` | `str` |  | yes | NETCAT command to run |
| `skip_done` | `bool` | false | no | Skip sessions already processed in a previous runloop iteration |

---

### `CMD_RDP`

*Category: `COMMAND`*

Runs any RDP client command on an open session. Command list is sourced live from the server commandMap. Wire the optional data port to feed upstream results as dynamic command arguments (cross-product: each session × each data item).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_rdp` | no | RDP session reference |
| `data` | input | `scan_result` | yes | Optional dynamic params — items merged into command kwargs per invocation |
| `result` | output | `scan_result` | no | Command result items |
| `session_out` | output | `session_rdp` | no | Pass-through: same session references from input |
| `error` | output | `error` | no | Error dict if command fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `command` | `str` |  | yes | RDP command to run |
| `skip_done` | `bool` | false | no | Skip sessions already processed in a previous runloop iteration |

---

### `CMD_DNS`

*Category: `COMMAND`*

Runs any DNS client command on an open session. Command list is sourced live from the server commandMap. Wire the optional data port to feed upstream results as dynamic command arguments (cross-product: each session × each data item).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_dns` | no | DNS session reference |
| `data` | input | `scan_result` | yes | Optional dynamic params — items merged into command kwargs per invocation |
| `result` | output | `scan_result` | no | Command result items |
| `session_out` | output | `session_dns` | no | Pass-through: same session references from input |
| `error` | output | `error` | no | Error dict if command fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `command` | `str` |  | yes | DNS command to run |
| `skip_done` | `bool` | false | no | Skip sessions already processed in a previous runloop iteration |

---

### `CMD_DCEDRSUAPI`

*Category: `COMMAND`*

Runs any DCE-DRSUAPI client command on an open session. Command list is sourced live from the server commandMap. Wire the optional data port to feed upstream results as dynamic command arguments (cross-product: each session × each data item).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_dcedrsuapi` | no | DCEDRSUAPI session reference |
| `data` | input | `scan_result` | yes | Optional dynamic params — items merged into command kwargs per invocation |
| `result` | output | `scan_result` | no | Command result items |
| `session_out` | output | `session_dcedrsuapi` | no | Pass-through: same session references from input |
| `error` | output | `error` | no | Error dict if command fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `command` | `str` |  | yes | DCEDRSUAPI command to run |
| `skip_done` | `bool` | false | no | Skip sessions already processed in a previous runloop iteration |

---

### `CMD_WINRM`

*Category: `COMMAND`*

Runs any WinRM client command on an open session. Command list is sourced live from the server commandMap. Wire the optional data port to feed upstream results as dynamic command arguments (cross-product: each session × each data item).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_winrm` | no | WINRM session reference |
| `data` | input | `scan_result` | yes | Optional dynamic params — items merged into command kwargs per invocation |
| `result` | output | `scan_result` | no | Command result items |
| `session_out` | output | `session_winrm` | no | Pass-through: same session references from input |
| `error` | output | `error` | no | Error dict if command fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `command` | `str` |  | yes | WINRM command to run |
| `skip_done` | `bool` | false | no | Skip sessions already processed in a previous runloop iteration |

---

### `CMD_NFS3`

*Category: `COMMAND`*

Runs any NFS client command on an open session. Command list is sourced live from the server commandMap. Wire the optional data port to feed upstream results as dynamic command arguments (cross-product: each session × each data item).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_nfs3` | no | NFS3 session reference |
| `data` | input | `scan_result` | yes | Optional dynamic params — items merged into command kwargs per invocation |
| `result` | output | `scan_result` | no | Command result items |
| `session_out` | output | `session_nfs3` | no | Pass-through: same session references from input |
| `error` | output | `error` | no | Error dict if command fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `command` | `str` |  | yes | NFS3 command to run |
| `skip_done` | `bool` | false | no | Skip sessions already processed in a previous runloop iteration |

---

### `CMD_SNMP`

*Category: `COMMAND`*

Runs any SNMP client command on an open session. Command list is sourced live from the server commandMap. Wire the optional data port to feed upstream results as dynamic command arguments (cross-product: each session × each data item).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_snmp` | no | SNMP session reference |
| `data` | input | `scan_result` | yes | Optional dynamic params — items merged into command kwargs per invocation |
| `result` | output | `scan_result` | no | Command result items |
| `session_out` | output | `session_snmp` | no | Pass-through: same session references from input |
| `error` | output | `error` | no | Error dict if command fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `command` | `str` |  | yes | SNMP command to run |
| `skip_done` | `bool` | false | no | Skip sessions already processed in a previous runloop iteration |

---

### `CMD_NTP`

*Category: `COMMAND`*

Runs any NTP client command on an open session. Command list is sourced live from the server commandMap. Wire the optional data port to feed upstream results as dynamic command arguments (cross-product: each session × each data item).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_ntp` | no | NTP session reference |
| `data` | input | `scan_result` | yes | Optional dynamic params — items merged into command kwargs per invocation |
| `result` | output | `scan_result` | no | Command result items |
| `session_out` | output | `session_ntp` | no | Pass-through: same session references from input |
| `error` | output | `error` | no | Error dict if command fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `command` | `str` |  | yes | NTP command to run |
| `skip_done` | `bool` | false | no | Skip sessions already processed in a previous runloop iteration |

---

### `CMD_MSSQL`

*Category: `COMMAND`*

Runs any MSSQL client command on an open session. Command list is sourced live from the server commandMap. Wire the optional data port to feed upstream results as dynamic command arguments (cross-product: each session × each data item).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_mssql` | no | MSSQL session reference |
| `data` | input | `scan_result` | yes | Optional dynamic params — items merged into command kwargs per invocation |
| `result` | output | `scan_result` | no | Command result items |
| `session_out` | output | `session_mssql` | no | Pass-through: same session references from input |
| `error` | output | `error` | no | Error dict if command fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `command` | `str` |  | yes | MSSQL command to run |
| `skip_done` | `bool` | false | no | Skip sessions already processed in a previous runloop iteration |

---

### `CMD_FTP`

*Category: `COMMAND`*

Runs any FTP client command on an open session. Command list is sourced live from the server commandMap. Wire the optional data port to feed upstream results as dynamic command arguments (cross-product: each session × each data item).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_ftp` | no | FTP session reference |
| `data` | input | `scan_result` | yes | Optional dynamic params — items merged into command kwargs per invocation |
| `result` | output | `scan_result` | no | Command result items |
| `session_out` | output | `session_ftp` | no | Pass-through: same session references from input |
| `error` | output | `error` | no | Error dict if command fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `command` | `str` |  | yes | FTP command to run |
| `skip_done` | `bool` | false | no | Skip sessions already processed in a previous runloop iteration |

---

### `CMD_WMI`

*Category: `COMMAND`*

Runs any WMI client command on an open session. Command list is sourced live from the server commandMap. Wire the optional data port to feed upstream results as dynamic command arguments (cross-product: each session × each data item).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_wmi` | no | WMI session reference |
| `data` | input | `scan_result` | yes | Optional dynamic params — items merged into command kwargs per invocation |
| `result` | output | `scan_result` | no | Command result items |
| `session_out` | output | `session_wmi` | no | Pass-through: same session references from input |
| `error` | output | `error` | no | Error dict if command fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `command` | `str` |  | yes | WMI command to run |
| `skip_done` | `bool` | false | no | Skip sessions already processed in a previous runloop iteration |

---
