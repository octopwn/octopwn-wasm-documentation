<!--
AUTO-GENERATED — DO NOT EDIT BY HAND.
Regenerate via:
    python scripts/generate_flowgraph_reference.py
Source of truth: octopwn/enterprise/flowgraph/registry.py.
-->

# CredMux

`CREDMUX` is the single most important routing block: it fans a single `credential` stream out onto protocol-typed output ports so that each downstream scanner / session / attack block receives only credentials it can actually use. Wiring `SOURCE_CREDENTIALS → CREDMUX → SCANNER_SMBLOGIN.credential` is idiomatic. See the [typing & wiring guide](../typing-and-wiring.md) for the full list of `credential_*` wire types.

---

**1 block type(s) in this category.**

---

### `CREDMUX`

*Category: `CREDMUX`*

Routes credentials to protocol-compatible output ports. Credentials are matched against the allowed secret types for each protocol (from connectionhelpers). Passwords are emitted on all matching ports. Incompatible types are silently dropped on that port.

**Ports**

| Port | Direction | Type | Optional | Description |
|------|-----------|------|----------|-------------|
| `credential_in` | input | `credential` | no | Any credential |
| `smb` | output | `credential_smb` | no | SMB-compatible credential (password, nt, rc4, aes, kerberos types) |
| `ldap` | output | `credential_ldap` | no | LDAP-compatible credential |
| `kerberos` | output | `credential_krb` | no | Kerberos-compatible credential |
| `ssh` | output | `credential_ssh` | no | SSH-compatible credential (password, sshprivkey) |
| `rdp` | output | `credential_rdp` | no | RDP-compatible credential (NTLM/Kerberos/password) |
| `winrm` | output | `credential_winrm` | no | WinRM-compatible credential (NTLM/Kerberos including CredSSP/SPNEGO variants) |
| `mssql` | output | `credential_mssql` | no | MSSQL-compatible credential (NTLM/Kerberos/password) |
| `wmi` | output | `credential_wmi` | no | WMI-compatible credential (NTLM/Kerberos) |
| `ftp` | output | `credential_ftp` | no | FTP-compatible credential (password) |
| `vnc` | output | `credential_vnc` | no | VNC-compatible credential (password) |
| `dcedrsuapi` | output | `credential_dcedrsuapi` | no | DCEDRSUAPI-compatible credential (NTLM/Kerberos) — used for DCSync via RPC |
| `snmp` | output | `credential_snmp` | no | SNMP community string credential (password) |
| `any` | output | `credential` | no | All credentials, unfiltered |
| `hashcat` | output | `credential` | no | Hash credentials crackable by hashcat: nt, dcc, dcc2, kerberos stypes |

**Parameters**

*No parameters.*

---
