<!--
AUTO-GENERATED — DO NOT EDIT BY HAND.
Regenerate via:
    python scripts/generate_flowgraph_reference.py
Source of truth: octopwn/enterprise/flowgraph/registry.py.
-->

# Enumeration

LDAP enumeration blocks consume an open `session_ldap` and stream individual user / computer / template / trust dicts to downstream blocks. The engine uses `StorageRef` so the memory footprint stays flat even on 100 000-user domains — items are pulled lazily from the on-disk SQLite store the LDAP client already maintains for audit trails. A typical chain is `ENUM_LDAP_COMPUTERS → TARGET_QUEUE` to feed discovered hostnames into the next runloop pass.

---

**4 block type(s) in this category.**

---

### `ENUM_LDAP_USERS`

*Category: `ENUMERATION`*

Enumerate all domain users from an open LDAP session. Calls do_users() — audit trail preserved, results written to SQLite. The engine streams individual user dicts to downstream blocks via StorageRef so memory stays flat even for 100k+ user domains. Wire dataset to TARGET_QUEUE to add user DCs as scan targets, or to FILTER to scope by UAC / adminCount.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_ldap` | no | Open LDAP session reference |
| `dataset` | output | `dataset_users` | no | Domain user dicts (streamed from SQLite) |
| `error` | output | `error` | no | Error dict |

**Parameters**

*No parameters.*

**Output schema — `dataset`**

| Field | Type | Description |
|-------|------|-------------|
| `sAMAccountName` | `str` | User login name |
| `objectSid` | `str` | User SID |
| `userAccountControl` | `int` | UAC flags bitmask |
| `adminCount` | `int` | adminCount attribute (1 = privileged) |
| `servicePrincipalName` | `str` | SPN — non-null means kerberoastable |
| `distinguishedName` | `str` | Full LDAP DN |
| `__tid` | `int` | Session target ID |
| `__cid` | `int` | Session credential ID |


**MITRE ATT&CK:** `T1087.002`

---

### `ENUM_LDAP_COMPUTERS`

*Category: `ENUMERATION`*

Enumerate all domain computers from an open LDAP session. Calls do_machines() — audit trail preserved, results written to SQLite. The engine streams individual computer dicts to downstream blocks via StorageRef so memory stays flat for large domains. Wire dataset to TARGET_QUEUE to add hostnames as new scan targets.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_ldap` | no | Open LDAP session reference |
| `dataset` | output | `dataset_computers` | no | Domain computer dicts (streamed from SQLite) |
| `error` | output | `error` | no | Error dict |

**Parameters**

*No parameters.*

**Output schema — `dataset`**

| Field | Type | Description |
|-------|------|-------------|
| `sAMAccountName` | `str` | Computer account name (with $ suffix) |
| `dNSHostName` | `str` | Fully qualified DNS name |
| `objectSid` | `str` | Computer SID |
| `operatingSystem` | `str` | Operating system string |
| `distinguishedName` | `str` | Full LDAP DN |
| `__tid` | `int` | Session target ID |
| `__cid` | `int` | Session credential ID |


**MITRE ATT&CK:** `T1018`

---

### `ENUM_LDAP_ADCS_TEMPLATES`

*Category: `ENUMERATION`*

Enumerate ADCS certificate templates from an open LDAP session. Resolves security descriptors and enrollment services. Use FILTER(key=name) to scope to a specific template, then wire to CMD_ADCS_ESC1 / CMD_ADCS_ESC4 params.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_ldap` | no | Open LDAP session reference |
| `dataset` | output | `dataset_templates` | no | Certificate template dicts |
| `error` | output | `error` | no | Error dict |

**Parameters**

*No parameters.*

**Output schema — `dataset`**

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Template name |
| `displayName` | `str` | Template display name |
| `enroll_services` | `str` | Enrollment service list (CA\\name) |
| `__tid` | `int` | Session target ID |
| `__cid` | `int` | Session credential ID |


**MITRE ATT&CK:** `T1649`

---

### `ENUM_LDAP_TRUSTS`

*Category: `ENUMERATION`*

Enumerate domain trusts from an open LDAP session. Each trust domain is also added as a new Target in the OctoPwn target store so it can be used in subsequent blocks. Wire dataset to TARGET_QUEUE to scan trusted domains.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_ldap` | no | Open LDAP session reference |
| `dataset` | output | `dataset_trusts` | no | Domain trust dicts |
| `error` | output | `error` | no | Error dict |

**Parameters**

*No parameters.*

**Output schema — `dataset`**

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Trusted domain DNS name |
| `trustType` | `int` | Trust type (1=downlevel, 2=uplevel, 3=MIT) |
| `trustDirection` | `int` | Direction (1=inbound, 2=outbound, 3=bidirectional) |
| `trustAttributes` | `int` | Trust attributes bitmask |
| `tid` | `int` | OctoPwn target ID for the trusted domain |
| `__tid` | `int` | Session target ID |
| `__cid` | `int` | Session credential ID |


**MITRE ATT&CK:** `T1482`

---
