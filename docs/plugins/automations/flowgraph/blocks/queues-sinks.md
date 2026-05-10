<!--
AUTO-GENERATED — DO NOT EDIT BY HAND.
Regenerate via:
    python scripts/generate_flowgraph_reference.py
Source of truth: octopwn/enterprise/flowgraph/registry.py.
-->

# Queues, sinks, taps and console

`QUEUE` blocks are feedback sinks: items wired into a queue are held for the *next* runloop iteration, where the matching `SOURCE_*_NEW` block re-emits them with their "seen" flag cleared. This is how a flowgraph discovers new credentials, queues them, and tries them again on the next pass without manual intervention.

`SINK` blocks are terminators — `TERMINATOR_SINK` silently discards items, `FILE_SINK` writes them as JSONL, and the `RERUN_TRIGGER` family schedules another engine pass.

`TAP_SINK` is a pass-through probe used to inspect what is flowing through a wire from the results panel. `CONSOLE` does the same plus a formatted log line per item.

---

**24 block type(s) in this category.**

---

### `CREDENTIAL_QUEUE`

*Category: `QUEUE`*

Sink: receives credentials and holds them for the next runloop iteration. SOURCE_CREDENTIALS_NEW will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `credential` | input | `credential` | no | Credential to queue for next iteration |

**Parameters**

*No parameters.*

---

### `TARGET_QUEUE`

*Category: `QUEUE`*

Sink: receives targets and holds them for the next runloop iteration. SOURCE_TARGETS_NEW will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `scan_result` | no | Target to queue for next iteration |

**Parameters**

*No parameters.*

---

### `TARGET_QUEUE_NAMED_IN`

*Category: `QUEUE`*

Sink: extracts __tid / target_id from incoming targets and appends to a named queue for TARGET_QUEUE_NAMED_OUT. Dedupes by target ID. persist=True stores across RERUN passes until resetstate; persist=False uses an ephemeral bucket cleared at each pass start.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `target` | input | `scan_result` | no | Target item with __tid or target_id |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `name` | `str` |  | yes | Queue name — must match TARGET_QUEUE_NAMED_OUT |
| `persist` | `bool` | true | no | True: persistent across passes. False: ephemeral (cleared each engine pass start). |

---

### `SESSION_QUEUE_KERBEROS`

*Category: `QUEUE`*

Sink: receives Kerberos (KRB5) client session references and holds them for the next runloop iteration. SOURCE_SESSIONS_NEW_KERBEROS will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_kerberos` | no | KERBEROS session reference to queue for next iteration |

**Parameters**

*No parameters.*

---

### `SESSION_QUEUE_LDAP`

*Category: `QUEUE`*

Sink: receives LDAP client session references and holds them for the next runloop iteration. SOURCE_SESSIONS_NEW_LDAP will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_ldap` | no | LDAP session reference to queue for next iteration |

**Parameters**

*No parameters.*

---

### `SESSION_QUEUE_SMB`

*Category: `QUEUE`*

Sink: receives SMB client session references and holds them for the next runloop iteration. SOURCE_SESSIONS_NEW_SMB will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_smb` | no | SMB session reference to queue for next iteration |

**Parameters**

*No parameters.*

---

### `SESSION_QUEUE_SSH`

*Category: `QUEUE`*

Sink: receives SSH client session references and holds them for the next runloop iteration. SOURCE_SESSIONS_NEW_SSH will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_ssh` | no | SSH session reference to queue for next iteration |

**Parameters**

*No parameters.*

---

### `SESSION_QUEUE_NETCAT`

*Category: `QUEUE`*

Sink: receives Netcat client session references and holds them for the next runloop iteration. SOURCE_SESSIONS_NEW_NETCAT will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_netcat` | no | NETCAT session reference to queue for next iteration |

**Parameters**

*No parameters.*

---

### `SESSION_QUEUE_RDP`

*Category: `QUEUE`*

Sink: receives RDP client session references and holds them for the next runloop iteration. SOURCE_SESSIONS_NEW_RDP will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_rdp` | no | RDP session reference to queue for next iteration |

**Parameters**

*No parameters.*

---

### `SESSION_QUEUE_DNS`

*Category: `QUEUE`*

Sink: receives DNS client session references and holds them for the next runloop iteration. SOURCE_SESSIONS_NEW_DNS will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_dns` | no | DNS session reference to queue for next iteration |

**Parameters**

*No parameters.*

---

### `SESSION_QUEUE_DCEDRSUAPI`

*Category: `QUEUE`*

Sink: receives DCE-DRSUAPI client session references and holds them for the next runloop iteration. SOURCE_SESSIONS_NEW_DCEDRSUAPI will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_dcedrsuapi` | no | DCEDRSUAPI session reference to queue for next iteration |

**Parameters**

*No parameters.*

---

### `SESSION_QUEUE_WINRM`

*Category: `QUEUE`*

Sink: receives WinRM client session references and holds them for the next runloop iteration. SOURCE_SESSIONS_NEW_WINRM will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_winrm` | no | WINRM session reference to queue for next iteration |

**Parameters**

*No parameters.*

---

### `SESSION_QUEUE_NFS3`

*Category: `QUEUE`*

Sink: receives NFS client session references and holds them for the next runloop iteration. SOURCE_SESSIONS_NEW_NFS3 will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_nfs3` | no | NFS3 session reference to queue for next iteration |

**Parameters**

*No parameters.*

---

### `SESSION_QUEUE_SNMP`

*Category: `QUEUE`*

Sink: receives SNMP client session references and holds them for the next runloop iteration. SOURCE_SESSIONS_NEW_SNMP will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_snmp` | no | SNMP session reference to queue for next iteration |

**Parameters**

*No parameters.*

---

### `SESSION_QUEUE_NTP`

*Category: `QUEUE`*

Sink: receives NTP client session references and holds them for the next runloop iteration. SOURCE_SESSIONS_NEW_NTP will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_ntp` | no | NTP session reference to queue for next iteration |

**Parameters**

*No parameters.*

---

### `SESSION_QUEUE_MSSQL`

*Category: `QUEUE`*

Sink: receives MSSQL client session references and holds them for the next runloop iteration. SOURCE_SESSIONS_NEW_MSSQL will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_mssql` | no | MSSQL session reference to queue for next iteration |

**Parameters**

*No parameters.*

---

### `SESSION_QUEUE_FTP`

*Category: `QUEUE`*

Sink: receives FTP client session references and holds them for the next runloop iteration. SOURCE_SESSIONS_NEW_FTP will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_ftp` | no | FTP session reference to queue for next iteration |

**Parameters**

*No parameters.*

---

### `SESSION_QUEUE_WMI`

*Category: `QUEUE`*

Sink: receives WMI client session references and holds them for the next runloop iteration. SOURCE_SESSIONS_NEW_WMI will re-emit them as "new" on the next pass, bypassing the seen-ID filter.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_wmi` | no | WMI session reference to queue for next iteration |

**Parameters**

*No parameters.*

---

### `TERMINATOR_SINK`

*Category: `SINK`*

Zero sink — accepts any input and silently discards it. Wire error output ports here to prevent unconnected-port warnings.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `data` | input | `any` | no | Any item — discarded |

**Parameters**

*No parameters.*

---

### `RERUN_TRIGGER`

*Category: `SINK`*

Local re-run trigger — if any items arrive, schedules a re-run of the current workflow scope. At the top level this re-runs the entire flowgraph after the global delay (setdelay). Inside a composite block this re-runs only the composite's inner graph. Wire any result port here whose non-empty output should trigger another pass — e.g. new credentials discovered by DCSync, new targets found by LDAP machines enumeration. Acts as a silent sink: items are discarded, only presence matters. Has no effect outside a run() call with persistent state (use the Run button, not runloop).

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `data` | input | `any` | no | Any items — their presence triggers a re-run |

**Parameters**

*No parameters.*

---

### `RERUN_TRIGGER_GLOBAL`

*Category: `SINK`*

Global re-run trigger — if any items arrive, schedules a re-run of the outermost (root) flowgraph after the global delay, regardless of nesting depth. Use inside composite blocks when inner-graph discoveries (e.g. new credentials) should cause the entire parent pipeline to run again. At the top level (no composites) this behaves identically to RERUN_TRIGGER. Acts as a silent sink: items are discarded, only presence matters.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `data` | input | `any` | no | Any items — their presence triggers a global re-run |

**Parameters**

*No parameters.*

---

### `FILE_SINK`

*Category: `SINK`*

Writes each incoming item as a JSON line (JSONL) to a file in the OctoPwn workdir. Append mode by default so multiple runs accumulate.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `data` | input | `any` | no | Any item — serialised to JSON and written to file |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `filename` | `str` |  | yes | Output filename (no path — always written to workdir) |
| `mode` | `str` | `append` | no | append (default) or overwrite |

---

### `TAP_SINK`

*Category: `TAP`*

Pass-through probe — forwards all items unchanged while making the wire inspectable in the results panel. Insert inline on any edge to observe what is flowing through.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `data` | input | `any` | no | Any item flowing through the wire |
| `data` | output | `any` | no | Same items, passed through unchanged |

**Parameters**

*No parameters.*

---

### `CONSOLE`

*Category: `CONSOLE`*

Pass-through logging probe. Formats each incoming item using the message template and prints it to the runtime console via self.print(). Data flows through unchanged. Use {field_name} placeholders to interpolate item fields.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `data` | input | `any` | no | Any item — logged then forwarded |
| `data` | output | `any` | no | Same items, passed through unchanged |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `message` | `str` | "" | no | Message template. Use {field_name} to interpolate. Empty = raw JSON. |

---
