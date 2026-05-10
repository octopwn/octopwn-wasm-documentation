<!--
AUTO-GENERATED — DO NOT EDIT BY HAND.
Regenerate via:
    python scripts/generate_flowgraph_reference.py
Source of truth: octopwn/enterprise/flowgraph/registry.py.
-->

# Transforms

Transform blocks take credentials of one kind and turn them into credentials of another kind. `CONVERT_PFX_TO_NT` walks a PKINIT U2U exchange on an already-opened Kerberos session to extract an NT hash. The `HASHCAT_*` blocks spawn a visible HASHCAT utility session, auto-detect the hash type from the incoming credential, and emit plaintext-password credentials on success.

---

**3 block type(s) in this category.**

---

### `CONVERT_PFX_TO_NT`

*Category: `TRANSFORM`*

Convert a PFXB64 certificate credential to an NT hash via PKINIT U2U. The Kerberos session must have been opened with OPEN_SESSION_KERBEROS using a PFXB64 credential (e.g. output of CMD_ADCS_ESC1). The extracted NT hash is added to the credential store and emitted as a credential dict that can flow to CREDENTIAL_QUEUE or attack blocks.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `session` | input | `session_kerberos` | no | Kerberos session opened with PFXB64 credential |
| `result` | output | `credential` | no | New NT hash credential dict {__cid, username, ...} |
| `error` | output | `error` | no | Error dict if extraction fails |

**Parameters**

*No parameters.*

**MITRE ATT&CK:** `T1649`

---

### `HASHCAT_WORDLIST`

*Category: `TRANSFORM`*

Crack hash credentials using hashcat dictionary (wordlist) attack. Spawns a visible HASHCAT utility session, auto-detects hash type from the secret prefix or stype field, and emits cracked plaintext-password credential dicts. Requires hashcat installed on the host.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `credential` | input | `credential` | no | Hash credential dict (KERBEROAST, NTLM, etc.) |
| `result` | output | `credential` | no | Cracked credential dicts with stype=password |
| `error` | output | `error` | no | Error dict if cracking fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `hashcat` | `str` | `hashcat` | yes | Path to hashcat binary |
| `wordlist` | `str` | `rockyou.txt` | yes | Path to wordlist file |
| `rules` | `str` | "" | no | Path to rules file (optional) |
| `maxruntime` | `int` | `5` | no | Max runtime in minutes per mode |

**MITRE ATT&CK:** `T1110.002`

---

### `HASHCAT_BRUTEFORCE`

*Category: `TRANSFORM`*

Crack hash credentials using hashcat mask (bruteforce) attack. Spawns a visible HASHCAT utility session, auto-detects hash type from the secret prefix or stype field, and emits cracked plaintext-password credential dicts. Requires hashcat installed on the host.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `credential` | input | `credential` | no | Hash credential dict (KERBEROAST, NTLM, etc.) |
| `result` | output | `credential` | no | Cracked credential dicts with stype=password |
| `error` | output | `error` | no | Error dict if cracking fails |

**Parameters**

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `hashcat` | `str` | `hashcat` | yes | Path to hashcat binary |
| `brutemask` | `str` | `?a?a?a?a?a?a?a` | yes | Hashcat mask pattern |
| `brutemin` | `int` | `1` | no | Minimum password length |
| `brutemax` | `int` | `7` | no | Maximum password length |
| `maxruntime` | `int` | `5` | no | Max runtime in minutes per mode |

**MITRE ATT&CK:** `T1110.001`

---
