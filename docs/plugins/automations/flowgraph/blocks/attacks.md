<!--
AUTO-GENERATED — DO NOT EDIT BY HAND.
Regenerate via:
    python scripts/generate_flowgraph_reference.py
Source of truth: octopwn/enterprise/flowgraph/registry.py.
-->

# Attacks

Curated, opinionated wrappers around the most common post-auth attacks in `OCTOPWN_ATTACK_TABLE`. Most attack blocks accept either a `pair` input (paired target + credential dict from `ID_SPLITTER_PAIR`) or independent `target` and `credential` inputs that are cross-producted internally. Successful runs emit `scan_result` items and auto-store any discovered credentials in the OctoPwn credential store, where they become available to downstream `SOURCE_CREDENTIALS_NEW` blocks.

---

**8 block type(s) in this category.**

---

### `CMD_KERBEROAST`

*Category: `ATTACK`*

Kerberoast and AS-REP Roast all service accounts reachable via Kerberos. Outputs hash items (ttype, user, domain, hashcatres) for each roastable account. Wire to HASHCAT_WORDLIST or HASHCAT_BRUTEFORCE to crack, or FILE_SINK to save. Filter by ttype to separate kerberoast_* from asreproast_* results.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `pair` | input | `scan_result` | yes | Paired {__tid, __cid} from ID_SPLITTER_PAIR — takes priority over target+credential ports |
| `target` | input | `raw_target` | yes | Target host (DC or machine) — raw_target or scan_result |
| `credential` | input | `credential` | yes | Compatible credential with __cid |
| `result` | output | `scan_result` | no | Attack result items |
| `error` | output | `error` | no | Error dict if attack fails |

**Parameters**

*No parameters.*

**MITRE ATT&CK:** `T1558.003`

---

### `CMD_ASREPROAST`

*Category: `ATTACK`*

AS-REP Roast accounts that do not require pre-authentication. Runs the same attack as CMD_KERBEROAST — wire a FILTER(ttype contains asrep) downstream to extract only AS-REP hashes.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `pair` | input | `scan_result` | yes | Paired {__tid, __cid} from ID_SPLITTER_PAIR — takes priority over target+credential ports |
| `target` | input | `raw_target` | yes | Target host (DC or machine) — raw_target or scan_result |
| `credential` | input | `credential` | yes | Compatible credential with __cid |
| `result` | output | `scan_result` | no | Attack result items |
| `error` | output | `error` | no | Error dict if attack fails |

**Parameters**

*No parameters.*

**MITRE ATT&CK:** `T1558.004`

---

### `CMD_DCSYNC`

*Category: `ATTACK`*

DCSync: replicate secrets from a domain controller via DRSUAPI. Requires Domain Admin, Replication, or DCSync delegation rights. Set storecreds=true to automatically add extracted NT hashes to the credential store.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `pair` | input | `scan_result` | yes | Paired {__tid, __cid} from ID_SPLITTER_PAIR — takes priority over target+credential ports |
| `target` | input | `raw_target` | yes | Target host (DC or machine) — raw_target or scan_result |
| `credential` | input | `credential` | yes | Compatible credential with __cid |
| `result` | output | `scan_result` | no | Attack result items |
| `error` | output | `error` | no | Error dict if attack fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `storecreds` | `bool` | true | no | Store extracted NT hashes as credentials |
| `username` | `str` | "" | no | Target a specific user (empty = all users) |
| `domain` | `str` | "" | no | Target a specific domain (empty = current) |

**MITRE ATT&CK:** `T1003.006`

---

### `CMD_DPAPI`

*Category: `ATTACK`*

Dump DPAPI secrets (Chrome cookies, WiFi passwords, credential files) from a Windows host over SMB. Requires admin SMB access.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `pair` | input | `scan_result` | yes | Paired {__tid, __cid} from ID_SPLITTER_PAIR — takes priority over target+credential ports |
| `target` | input | `raw_target` | yes | Target host (DC or machine) — raw_target or scan_result |
| `credential` | input | `credential` | yes | Compatible credential with __cid |
| `result` | output | `scan_result` | no | Attack result items |
| `error` | output | `error` | no | Error dict if attack fails |

**Parameters**

*No parameters.*

**MITRE ATT&CK:** `T1555.004`

---

### `CMD_REGDUMP`

*Category: `ATTACK`*

Dump SAM, SYSTEM, and SECURITY registry hives from a Windows host over SMB and extract local account NT hashes. Requires admin SMB access.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `pair` | input | `scan_result` | yes | Paired {__tid, __cid} from ID_SPLITTER_PAIR — takes priority over target+credential ports |
| `target` | input | `raw_target` | yes | Target host (DC or machine) — raw_target or scan_result |
| `credential` | input | `credential` | yes | Compatible credential with __cid |
| `result` | output | `scan_result` | no | Attack result items |
| `error` | output | `error` | no | Error dict if attack fails |

**Parameters**

*No parameters.*

**MITRE ATT&CK:** `T1003.002`

---

### `CMD_ADCS_ESC1`

*Category: `ATTACK`*

Exploit ADCS ESC1: request a certificate as any domain user by supplying an alternative subject name (requires enrollee-supplies-subject template flag). Outputs a PFX credential that can be converted to an NT hash via CONVERT_PFX_TO_NT.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `pair` | input | `scan_result` | yes | Paired {__tid, __cid} from ID_SPLITTER_PAIR — takes priority over target+credential ports |
| `target` | input | `raw_target` | yes | Target host (DC or machine) — raw_target or scan_result |
| `credential` | input | `credential` | yes | Compatible credential with __cid |
| `result` | output | `scan_result` | no | Attack result items |
| `error` | output | `error` | no | Error dict if attack fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `dctarget` | `int` |  | yes | Target ID of the domain controller |
| `service` | `str` |  | yes | ADCS service name (CA name) |
| `template` | `str` |  | yes | Certificate template name to exploit |
| `targetusers` | `str` | "" | no | User(s) to impersonate (empty = domain admins) |

**MITRE ATT&CK:** `T1649`

---

### `CMD_ADCS_ESC4`

*Category: `ATTACK`*

Exploit ADCS ESC4: modify a certificate template to enable ESC1, then exploit it. Requires write access to the template object in LDAP. Outputs a PFX credential convertible to NT hash via CONVERT_PFX_TO_NT.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `pair` | input | `scan_result` | yes | Paired {__tid, __cid} from ID_SPLITTER_PAIR — takes priority over target+credential ports |
| `target` | input | `raw_target` | yes | Target host (DC or machine) — raw_target or scan_result |
| `credential` | input | `credential` | yes | Compatible credential with __cid |
| `result` | output | `scan_result` | no | Attack result items |
| `error` | output | `error` | no | Error dict if attack fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `dctarget` | `int` |  | yes | Target ID of the domain controller |
| `service` | `str` |  | yes | ADCS service name (CA name) |
| `template` | `str` |  | yes | Certificate template name to exploit |
| `targetusers` | `str` | "" | no | User(s) to impersonate (empty = domain admins) |

**MITRE ATT&CK:** `T1649`

---

### `CMD_BLOODHOUND`

*Category: `ATTACK`*

Run BloodHound data collection on an open LDAP session. Enumerates users, groups, computers, ACLs, sessions, and trusts, then writes a BloodHound-compatible ZIP to the workdir. Connect to an OPEN_SESSION_LDAP output.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_ldap` | no | Open LDAP session reference |
| `result` | output | `scan_result` | no | Result dict with zipfile path |
| `error` | output | `error` | no | Error dict if collection fails |

**Parameters**

*No parameters.*

**MITRE ATT&CK:** `T1087.002` `T1069.002` `T1482`

---
