# DCEDRSUAPI Client

The **DCEDRSUAPI Client** performs **DCSync** — extracting an account's secrets (NT hash, LM hash, Kerberos keys, password history, supplemental credentials) from a Domain Controller — by speaking the Directory Replication Service Remote Protocol (`MS-DRSR`, "DRSUAPI") directly to the DC. It targets one specific account at a time and is intentionally narrow in scope.

The same DCSync capability also exists on the [SMB client](./smb.md) and is the more common entry point for broader workflows (whole-realm dumps, automated user enumeration, etc.). The DCEDRSUAPI client is the focused alternative for cases where a single account's credentials are all that's needed and a full SMB session is undesirable.

---

## Transport — what's actually on the wire

This is the most important fact about this client and the one that's easiest to get wrong.

The DCEDRSUAPI client **does not use SMB**. Despite the underlying `aiosmb`-based plumbing (and the historical `from_smbconnection` naming inside the library), no SMB session is established and **port 445 is not touched**. The transport is pure DCERPC over TCP/IP:

| Step | Destination                                                  | Purpose                                                                   |
| ---- | ------------------------------------------------------------ | ------------------------------------------------------------------------- |
| 1    | DC, **TCP/135** (Endpoint Mapper, `epmapper`)                | Look up the dynamic port allocated to the DRSUAPI RPC interface on this DC. |
| 2    | DC, **TCP/&lt;dynamic port&gt;** (typically in the 49xxx range) | DCERPC bind, authentication, and the `IDL_DRSGetNCChanges` calls that perform the actual replication. |

Authentication is performed inside the DCERPC bind on the second connection, not via SMB.

!!! info "Plan firewall scope accordingly"
    For this client to work, you need TCP reachability to the DC on **port 135** *and* on the DC's RPC dynamic port range (49152–65535 by default on modern Windows; legacy DCs may use 1024–5000). If only port 445 is reachable, this client will not work and the SMB-based DCSync path on the [SMB client](./smb.md) is the appropriate alternative.

---

## When to use this client vs. the SMB client's DCSync

| Need                                                                                                | Use                                |
| --------------------------------------------------------------------------------------------------- | ---------------------------------- |
| Pull secrets for the entire domain, or a whole class of users (all admins, all service accounts).   | [SMB client's DCSync](./smb.md)    |
| Pull secrets for **one specific account** with no other enumeration.                                | DCEDRSUAPI client (this page)      |
| Port 445 is firewalled but TCP/135 + RPC dynamic ports are reachable.                               | DCEDRSUAPI client                  |
| Port 445 is reachable but TCP/135 / RPC dynamic ports are not.                                      | SMB client's DCSync                |
| Need other DC operations alongside DCSync (SAMR enumeration, LSAT, registry hive dumping, etc.).    | SMB client                         |

---

## Authentication

The client supports the standard NTLM and Kerberos credential families, identical to the SMB and WMI clients. Authentication is negotiated as part of the DCERPC bind (`RPC_C_AUTHN_LEVEL_PKT_PRIVACY` is required by DRSUAPI and is set automatically).

| `atype`    | Underlying creds | Notes                                                                              |
| ---------- | ---------------- | ---------------------------------------------------------------------------------- |
| `NTLM`     | NTLM             | Requires the targeted account to allow NTLM.                                       |
| `KERBEROS` | Kerberos         | Standard Kerberos auth against the DC's `ldap/<dchost>` or `host/<dchost>` SPN.    |

### NTLM credentials

| Secret type   | Description                                                          | Example                |
| ------------- | -------------------------------------------------------------------- | ---------------------- |
| `password`    | Cleartext password.                                                  | `username:Pa55w0rd!`   |
| `pwhex`       | Hex-encoded UTF-16LE password (for non-ASCII passwords).             | `username:70617373…`   |
| `nt`          | NT hash (pass-the-hash).                                             | `username:aad3b…`      |
| `rc4`         | RC4 (synonym for NT for the NTLM exchange).                          | `username:aad3b…`      |
| `agentproxy`  | Use a remote NTLM signer over the wsnet agent proxy.                 | n/a                    |
| `sspiproxy`   | Use the OS's SSPI session via the wsnet agent proxy (Windows agent). | n/a                    |

### Kerberos credentials

| Secret type     | Description                                                  | Example                              |
| --------------- | ------------------------------------------------------------ | ------------------------------------ |
| `password`      | Cleartext password.                                          | `username:Pa55w0rd!`                 |
| `pwhex`         | Hex-encoded UTF-16LE password.                               | `username:70617373…`                 |
| `nt` / `rc4`    | NT/RC4 hash.                                                 | `username:aad3b…`                    |
| `aes128`        | AES128 long-term key.                                        | `username:<32-hex>`                  |
| `aes256`        | AES256 long-term key.                                        | `username:<64-hex>`                  |
| `keytab`        | Kerberos keytab file in OctoPwn volatile storage.            | `/browserfs/volatile/admin.keytab`   |
| `keytabb64`     | Base64-encoded keytab inline.                                | `username:<b64>`                     |
| `ccache`        | MIT ccache file in OctoPwn volatile storage.                 | `/browserfs/volatile/krb5cc.ccache`  |
| `ccacheb64`     | Base64-encoded ccache inline.                                | `username:<b64>`                     |
| `kirbi`         | `.kirbi` ticket file (Rubeus-style).                         | `/browserfs/volatile/admin.kirbi`    |
| `kirbib64`      | Base64-encoded `.kirbi` inline.                              | `username:<b64>`                     |
| `pfxb64`        | Base64-encoded PFX (PKINIT certificate auth).                | `username:<b64>`                     |
| `agentproxy`    | Remote KDC over the wsnet agent proxy.                       | n/a                                  |
| `sspiproxy`     | OS SSPI session via wsnet agent proxy (Windows agent).       | n/a                                  |

!!! note "Required privileges on the DC"
    DCSync requires the calling account to have the `DS-Replication-Get-Changes` and `DS-Replication-Get-Changes-All` extended rights on the domain naming context. By default this is granted to Domain Admins, Enterprise Admins, and the Administrators group. Any non-privileged account with these rights explicitly granted via an ACL (a common misconfiguration / persistence technique) also works.

---

## Commands

### CONNECTION

#### login
Performs the connection sequence in full:

1. Builds the un-connected `SMBConnection` container that carries the credential and target metadata.
2. Opens the EPM connection on TCP/135 to the DC.
3. Asks EPM for the DRSUAPI service binding (returns a `ncacn_ip_tcp:<dc>[<port>]` string).
4. Opens a fresh DCERPC connection to the dynamic RPC port and performs the bind with `RPC_C_AUTHN_LEVEL_PKT_PRIVACY` (mandatory for DRSUAPI).
5. Issues `DRSBind` to register a session with the DC.

A successful `login` leaves the DCERPC connection open and ready for `dcsync` calls.

#### logout
Closes the DCERPC connection and resets session state. Safe to call when no connection is active.

---

### OPERATIONS

#### dcsync
Pulls the secrets for a single account from the DC and stores them as new credentials in OctoPwn's credential store. Internally this issues `DRSCrackNames` (to resolve the supplied identifier into a GUID) followed by `IDL_DRSGetNCChanges` to retrieve the account's replication attributes (`unicodePwd`, `dBCSPwd`, `ntPwdHistory`, `lmPwdHistory`, `supplementalCredentials`, `objectSid`, `pwdLastSet`, `userAccountControl`).

##### Parameters
- **username**: Identifier for the target account. Several formats are accepted and auto-detected:
    - **sAMAccountName** (e.g. `Administrator`) — resolved against the DC's default domain.
    - **User Principal Name** (e.g. `administrator@corp.local`) — preferred when targeting a specific domain in a multi-domain forest.
    - **Distinguished Name** (e.g. `CN=Administrator,CN=Users,DC=corp,DC=local`) — recognised by the leading `CN=`.
    - **SID** (e.g. `S-1-5-21-...-500`) — recognised by the `S-1-5-` prefix.
- **to_print** *(optional, bool, default `True`)*: Whether to print the recovered secrets to the console. When `False`, secrets are still added to the credential store and indexed under the session's `DCSYNC` results, but no console output is produced.

##### Output

When `to_print` is `True` (the default), `dcsync` prints the formatted secret object to the console — including username, domain, SID, NT hash, LM hash (if present), and all Kerberos long-term keys (RC4, AES128, AES256). The same data is also:

- **Stored as new credentials in the Credentials Window**, one credential per recovered key (NT hash, RC4 key, AES128 key, AES256 key), each tagged with `description='DCSYNC'`, `source='SMB-DCSYNC-<session>'`, and the original `objectSid`.
- **Indexed under the session's `DCSYNC` results** as the full secret JSON, so the data remains queryable from the Sessions tab even after the console is cleared.

The empty-NT-hash sentinel (`31d6cfe0d16ae931b73c59d7e0c089c0`) is filtered out — accounts without a password set will produce Kerberos-key credentials only.

---

## Limitations

- **Single-account only.** There is no built-in iteration. To pull multiple accounts, call `dcsync` once per identifier — or use the SMB client's DCSync for whole-realm or filtered-set workflows.
- **Requires DC reachability on TCP/135 and the RPC dynamic port range.** If only port 445 is reachable, use the SMB client's DCSync instead.
- **Requires `DS-Replication-Get-Changes(-All)` rights.** A non-privileged account without these rights will fail at the `IDL_DRSGetNCChanges` call regardless of how the rest of the auth went.
- **Domain detection requires either a target realm or a domain on the credential.** If neither is set, `login` will fail with `Domain is not set neither on target nor on credential`.
- **No incremental / range queries.** Each `dcsync` call pulls the full attribute set for the named account; there is no way to ask for "just the NT hash" or "just the AES256 key".
