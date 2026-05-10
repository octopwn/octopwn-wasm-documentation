<!--
AUTO-GENERATED — DO NOT EDIT BY HAND.
Regenerate via:
    python scripts/generate_flowgraph_reference.py
Source of truth: octopwn/enterprise/flowgraph/registry.py.
-->

# Sources & prompts

Source blocks inject data into a flowgraph. Most pipelines start with one or more `SOURCE_*` blocks that emit credentials, targets, or live sessions from the OctoPwn project store. `*_NEW` variants only emit items not yet processed in the current runloop iteration and are the building blocks of feedback loops — pair them with the matching `*_QUEUE` sink in [queues & sinks](queues-sinks.md). `PROMPT_SOURCE_*` blocks ask the operator for a value via a UI dialog at run time and are intended for tutorial / demo graphs.

---

**42 block type(s) in this category.**

---

### `SOURCE_CREDENTIALS`

*Category: `SOURCE`*

Emits ALL credentials currently in the OctoPwn credential store (full snapshot). Use in single-shot runs or when you want every credential every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `credential` | output | `credential` | no | Credential object from the store |

**Parameters**

*No parameters.*

---

### `SOURCE_CREDENTIALS_NEW`

*Category: `SOURCE`*

Emits only credentials not seen in a previous runloop iteration, plus any credentials pushed into a CREDENTIAL_QUEUE. In a single-shot run behaves like SOURCE_CREDENTIALS.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `credential` | output | `credential` | no | Credential not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `SOURCE_TARGETS`

*Category: `SOURCE`*

Emits ALL targets currently in the OctoPwn target store (full snapshot). Use in single-shot runs or when you want every target every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | output | `scan_result` | no | Target object from the store |

**Parameters**

*No parameters.*

---

### `SOURCE_TARGETS_NEW`

*Category: `SOURCE`*

Emits only targets not seen in a previous runloop iteration, plus any targets pushed into a TARGET_QUEUE. In a single-shot run behaves like SOURCE_TARGETS.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | output | `scan_result` | no | Target not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `TARGET_QUEUE_NAMED_OUT`

*Category: `SOURCE`*

Emits stored targets from a named queue filled by TARGET_QUEUE_NAMED_IN (same name and persist flag). repeat=True re-emits the same list on every engine pass; repeat=False clears the queue after emitting. Use persist=True to share the bucket across RERUN passes; persist=False uses a per-pass bucket cleared at each pass start.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | output | `scan_result` | no | Target dict with __tid from the named queue |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `name` | `str` |  | yes | Queue name — must match TARGET_QUEUE_NAMED_IN |
| `persist` | `bool` | true | no | True: persistent bucket across passes (match IN). False: ephemeral bucket cleared each pass start. |
| `repeat` | `bool` | true | no | True: keep queue after emit. False: drain queue after this emit. |

---

### `SOURCE_RAW_TARGETS`

*Category: `SOURCE`*

Emits user-supplied raw target strings (IPs, hostnames, CIDR ranges) exactly once per run. Output type is raw_target — connects to scanners, attacks, and utils only. Use STORE_TARGETS to convert to stored targets for OPEN_SESSION_* blocks.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | output | `raw_target` | no | Raw target string as {value: str} — feeds scanners/attacks/utils |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `targets` | `list` |  | yes | Targets — IPs, hostnames, CIDRs, comma-separated |

---

### `SOURCE_STATIC_TARGETS`

*Category: `SOURCE`*

Emits targets from the OctoPwn store by ID, exactly once per run. Specify one or more integer target IDs (as shown in the targets panel). Output connects to OPEN_SESSION_* blocks and scanners.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | output | `scan_result` | no | Stored target dict with __tid set |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `target_ids` | `list` |  | yes | Integer target IDs to emit — comma-separated or one per line |

---

### `STORE_TARGETS`

*Category: `SOURCE`*

Adds raw target strings to the OctoPwn target store and emits stored target dicts. CIDR ranges are skipped with a warning — use SCANNER_PORTSCAN for bulk discovery. Intended for pinning a small number of specific hosts.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `raw_target` | input | `raw_target` | no | Raw target from SOURCE_RAW_TARGETS |
| `target` | output | `scan_result` | no | Stored target dict with __tid set |

**Parameters**

*No parameters.*

---

### `SOURCE_STATIC_CREDENTIALS`

*Category: `SOURCE`*

Emits credentials from the OctoPwn store by ID, exactly once per run. Specify one or more integer credential IDs (as shown in the credentials panel).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `credential` | output | `credential` | no | Credential dict with __cid set |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `credential_ids` | `list` |  | yes | Integer credential IDs to emit — comma-separated or one per line |

---

### `SOURCE_SESSIONS_KERBEROS`

*Category: `SOURCE`*

Emits ALL live Kerberos (KRB5) client sessions currently open in OctoPwn (full snapshot). Use when you want every existing KERBEROS session every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_kerberos` | no | KERBEROS session reference: {session_id, target_id, credential_id} |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NEW_KERBEROS`

*Category: `SOURCE`*

Emits only Kerberos (KRB5) client sessions not seen in a previous runloop iteration, plus any sessions pushed into a SESSION_QUEUE_KERBEROS. In a single-shot run behaves like SOURCE_SESSIONS_KERBEROS.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_kerberos` | no | KERBEROS session not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_LDAP`

*Category: `SOURCE`*

Emits ALL live LDAP client sessions currently open in OctoPwn (full snapshot). Use when you want every existing LDAP session every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_ldap` | no | LDAP session reference: {session_id, target_id, credential_id} |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NEW_LDAP`

*Category: `SOURCE`*

Emits only LDAP client sessions not seen in a previous runloop iteration, plus any sessions pushed into a SESSION_QUEUE_LDAP. In a single-shot run behaves like SOURCE_SESSIONS_LDAP.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_ldap` | no | LDAP session not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_SMB`

*Category: `SOURCE`*

Emits ALL live SMB client sessions currently open in OctoPwn (full snapshot). Use when you want every existing SMB session every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_smb` | no | SMB session reference: {session_id, target_id, credential_id} |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NEW_SMB`

*Category: `SOURCE`*

Emits only SMB client sessions not seen in a previous runloop iteration, plus any sessions pushed into a SESSION_QUEUE_SMB. In a single-shot run behaves like SOURCE_SESSIONS_SMB.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_smb` | no | SMB session not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_SSH`

*Category: `SOURCE`*

Emits ALL live SSH client sessions currently open in OctoPwn (full snapshot). Use when you want every existing SSH session every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_ssh` | no | SSH session reference: {session_id, target_id, credential_id} |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NEW_SSH`

*Category: `SOURCE`*

Emits only SSH client sessions not seen in a previous runloop iteration, plus any sessions pushed into a SESSION_QUEUE_SSH. In a single-shot run behaves like SOURCE_SESSIONS_SSH.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_ssh` | no | SSH session not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NETCAT`

*Category: `SOURCE`*

Emits ALL live Netcat client sessions currently open in OctoPwn (full snapshot). Use when you want every existing NETCAT session every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_netcat` | no | NETCAT session reference: {session_id, target_id, credential_id} |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NEW_NETCAT`

*Category: `SOURCE`*

Emits only Netcat client sessions not seen in a previous runloop iteration, plus any sessions pushed into a SESSION_QUEUE_NETCAT. In a single-shot run behaves like SOURCE_SESSIONS_NETCAT.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_netcat` | no | NETCAT session not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_RDP`

*Category: `SOURCE`*

Emits ALL live RDP client sessions currently open in OctoPwn (full snapshot). Use when you want every existing RDP session every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_rdp` | no | RDP session reference: {session_id, target_id, credential_id} |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NEW_RDP`

*Category: `SOURCE`*

Emits only RDP client sessions not seen in a previous runloop iteration, plus any sessions pushed into a SESSION_QUEUE_RDP. In a single-shot run behaves like SOURCE_SESSIONS_RDP.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_rdp` | no | RDP session not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_DNS`

*Category: `SOURCE`*

Emits ALL live DNS client sessions currently open in OctoPwn (full snapshot). Use when you want every existing DNS session every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_dns` | no | DNS session reference: {session_id, target_id, credential_id} |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NEW_DNS`

*Category: `SOURCE`*

Emits only DNS client sessions not seen in a previous runloop iteration, plus any sessions pushed into a SESSION_QUEUE_DNS. In a single-shot run behaves like SOURCE_SESSIONS_DNS.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_dns` | no | DNS session not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_DCEDRSUAPI`

*Category: `SOURCE`*

Emits ALL live DCE-DRSUAPI client sessions currently open in OctoPwn (full snapshot). Use when you want every existing DCEDRSUAPI session every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_dcedrsuapi` | no | DCEDRSUAPI session reference: {session_id, target_id, credential_id} |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NEW_DCEDRSUAPI`

*Category: `SOURCE`*

Emits only DCE-DRSUAPI client sessions not seen in a previous runloop iteration, plus any sessions pushed into a SESSION_QUEUE_DCEDRSUAPI. In a single-shot run behaves like SOURCE_SESSIONS_DCEDRSUAPI.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_dcedrsuapi` | no | DCEDRSUAPI session not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_WINRM`

*Category: `SOURCE`*

Emits ALL live WinRM client sessions currently open in OctoPwn (full snapshot). Use when you want every existing WINRM session every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_winrm` | no | WINRM session reference: {session_id, target_id, credential_id} |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NEW_WINRM`

*Category: `SOURCE`*

Emits only WinRM client sessions not seen in a previous runloop iteration, plus any sessions pushed into a SESSION_QUEUE_WINRM. In a single-shot run behaves like SOURCE_SESSIONS_WINRM.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_winrm` | no | WINRM session not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NFS3`

*Category: `SOURCE`*

Emits ALL live NFS client sessions currently open in OctoPwn (full snapshot). Use when you want every existing NFS3 session every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_nfs3` | no | NFS3 session reference: {session_id, target_id, credential_id} |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NEW_NFS3`

*Category: `SOURCE`*

Emits only NFS client sessions not seen in a previous runloop iteration, plus any sessions pushed into a SESSION_QUEUE_NFS3. In a single-shot run behaves like SOURCE_SESSIONS_NFS3.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_nfs3` | no | NFS3 session not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_SNMP`

*Category: `SOURCE`*

Emits ALL live SNMP client sessions currently open in OctoPwn (full snapshot). Use when you want every existing SNMP session every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_snmp` | no | SNMP session reference: {session_id, target_id, credential_id} |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NEW_SNMP`

*Category: `SOURCE`*

Emits only SNMP client sessions not seen in a previous runloop iteration, plus any sessions pushed into a SESSION_QUEUE_SNMP. In a single-shot run behaves like SOURCE_SESSIONS_SNMP.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_snmp` | no | SNMP session not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NTP`

*Category: `SOURCE`*

Emits ALL live NTP client sessions currently open in OctoPwn (full snapshot). Use when you want every existing NTP session every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_ntp` | no | NTP session reference: {session_id, target_id, credential_id} |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NEW_NTP`

*Category: `SOURCE`*

Emits only NTP client sessions not seen in a previous runloop iteration, plus any sessions pushed into a SESSION_QUEUE_NTP. In a single-shot run behaves like SOURCE_SESSIONS_NTP.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_ntp` | no | NTP session not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_MSSQL`

*Category: `SOURCE`*

Emits ALL live MSSQL client sessions currently open in OctoPwn (full snapshot). Use when you want every existing MSSQL session every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_mssql` | no | MSSQL session reference: {session_id, target_id, credential_id} |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NEW_MSSQL`

*Category: `SOURCE`*

Emits only MSSQL client sessions not seen in a previous runloop iteration, plus any sessions pushed into a SESSION_QUEUE_MSSQL. In a single-shot run behaves like SOURCE_SESSIONS_MSSQL.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_mssql` | no | MSSQL session not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_FTP`

*Category: `SOURCE`*

Emits ALL live FTP client sessions currently open in OctoPwn (full snapshot). Use when you want every existing FTP session every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_ftp` | no | FTP session reference: {session_id, target_id, credential_id} |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NEW_FTP`

*Category: `SOURCE`*

Emits only FTP client sessions not seen in a previous runloop iteration, plus any sessions pushed into a SESSION_QUEUE_FTP. In a single-shot run behaves like SOURCE_SESSIONS_FTP.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_ftp` | no | FTP session not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_WMI`

*Category: `SOURCE`*

Emits ALL live WMI client sessions currently open in OctoPwn (full snapshot). Use when you want every existing WMI session every iteration.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_wmi` | no | WMI session reference: {session_id, target_id, credential_id} |

**Parameters**

*No parameters.*

---

### `SOURCE_SESSIONS_NEW_WMI`

*Category: `SOURCE`*

Emits only WMI client sessions not seen in a previous runloop iteration, plus any sessions pushed into a SESSION_QUEUE_WMI. In a single-shot run behaves like SOURCE_SESSIONS_WMI.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | output | `session_wmi` | no | WMI session not yet processed in this runloop |

**Parameters**

*No parameters.*

---

### `PROMPT_SOURCE_CREDENTIAL`

*Category: `PROMPT_SOURCE`*

Prompts the user for a single credential ID before running. When this block has no credential_id set and the user clicks Run, the frontend shows an input dialog asking for the credential to use. Emits a single credential from the OctoPwn store by ID. Designed for tutorial and example flowgraphs.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `credential` | output | `credential` | no | Credential dict with __cid set |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `credential_id` | `str` |  | yes | Credential ID to emit (integer from the credentials panel) |
| `continuous` | `bool` | false | no | Re-emit on every engine iteration (default: emit only once) |

---

### `PROMPT_SOURCE_TARGET`

*Category: `PROMPT_SOURCE`*

Prompts the user for a single target ID before running. When this block has no target_id set and the user clicks Run, the frontend shows an input dialog asking for the target to use. Emits a single stored target from the OctoPwn store by ID. Output connects to OPEN_SESSION_* blocks and scanners. Designed for tutorial and example flowgraphs.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | output | `scan_result` | no | Stored target dict with __tid set |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `target_id` | `str` |  | yes | Target ID to emit (integer from the targets panel) |
| `continuous` | `bool` | false | no | Re-emit on every engine iteration (default: emit only once) |

---

### `PROMPT_SOURCE_TARGETS`

*Category: `PROMPT_SOURCE`*

Prompts the user for target strings before running. When this block has no targets set and the user clicks Run, the frontend shows an input dialog asking for target IPs/hostnames. Emits user-supplied raw target strings (IPs, hostnames, CIDR ranges). Output type is raw_target — connects to scanners, attacks, and utils. Use STORE_TARGETS to convert to stored targets for OPEN_SESSION_* blocks. Designed for tutorial and example flowgraphs.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | output | `raw_target` | no | Raw target string as {value: str} — feeds scanners/attacks/utils |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `targets` | `list` |  | yes | Targets — IPs, hostnames, CIDRs, comma-separated or one per line |
| `continuous` | `bool` | false | no | Re-emit on every engine iteration (default: emit only once) |

---
