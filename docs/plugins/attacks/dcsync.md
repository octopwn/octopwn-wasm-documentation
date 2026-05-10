# DCSync Attack

The **DCSync** attack module performs the canonical DCSync technique — replicating
secrets out of Active Directory by impersonating a Domain Controller at the
`MS-DRSR` (Directory Replication Service) RPC level. It is the cleanest path from
"replicating-rights credential" to **every NT hash, AES key, Kerberos key,
supplemental credential, and DPAPI domain backup key in the directory**.

This is the same primitive Mimikatz exposes as `lsadump::dcsync` and Impacket as
`secretsdump.py -just-dc`; in OctoPwn it is wrapped as a multi-target scanner-style
executor with optional LDAP-driven user filtering.

| Source                   | Output stored where                                         |
| ------------------------ | ----------------------------------------------------------- |
| Per-user RC4 / AES / DES | [Credentials Hub](../../user-guide/credentials.md), `stype = nt` / `aes_256` / `aes_128` / `des_cbc_md5` |
| `krbtgt`                 | Same — required for Golden Ticket forging                   |
| Domain DPAPI backup keys | Stored on the project; subsequent [`DPAPI`](dpapi.md) runs use them automatically for "God Mode" decryption |
| Cleartext (UF\_USE\_DES, reversibly-encrypted, *etc.*) | Hub as `password` when present                |

---

## How it works

1. **SMB connect + login** with the supplied `credential` against the next target
   (typically a Domain Controller). The credential needs **DCSync rights** —
   either built-in (`Domain Admins`, `Enterprise Admins`, `Administrators` on the DC,
   `Domain Controllers`) or via an explicit ACE granting `DS-Replication-Get-Changes`
   + `DS-Replication-Get-Changes-All` on the domain object. If you're not sure
   whether your account has it, the LDAP client's
   [`acl`](../clients/ldap.md) commands can tell you.
2. **`SMBMachine.dcsync(target_users=...)`** is invoked, which under the hood:
    - Opens a DCERPC bind to the `\PIPE\lsarpc` named pipe.
    - Issues `DRSBind` to register us as a fake DC.
    - For each user in `target_users` (or every user when none specified),
      issues `DRSGetNCChanges` requesting the user's secret attributes.
    - Decrypts the returned blob using session-key wrapping → emits a `pypykatz`
      `OffineRegistry` (yes, the typo is in the upstream class name) entry per user.
3. **LDAP-driven user filter (optional).** When `ldapfilter` is set:
    - OctoPwn opens a separate LDAP / LDAPS connection (using `ldaptarget` /
      `ldapcredential` / `ldapauthtype` / `ldapproxy` / `ldapprotocol` if provided,
      otherwise reusing the SMB target / credential).
    - Runs the supplied LDAP filter, paged-search, attribute `sAMAccountName` only.
    - The resulting list of usernames is passed as `target_users` to the DCSync
      run, instead of "all users".
   This is the recommended path for big environments where you don't want to
   replicate the entire directory — example filters below.
4. **Result handling.**
    - When `storecreds=True`, every recovered secret is added to the
      [Credentials Hub](../../user-guide/credentials.md) via `store_ntds_secrets`.
    - When `outfile` is set, the human-readable Mimikatz-style line for each user
      is appended to the file in `/browserfs/volatile`.
    - When `outfilehash` is set, a flat list of NT hashes (one per line) is
      appended to that file — convenient for piping into Hashcat / John.
    - If neither file is set and `storecreds=False`, the result is just printed to
      the session window.

---

## Useful LDAP filters

`ldapfilter` accepts any standard LDAP filter — `sAMAccountName` is the only
attribute fetched, so the filter just needs to *select* the right objects. A few
recipes:

```
# Every enabled user account (skip computers & disabled accounts)
(&(samAccountType=805306368)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))

# Only members of Domain Admins
(&(samAccountType=805306368)(memberOf=CN=Domain Admins,CN=Users,DC=corp,DC=local))

# Only the krbtgt account (for forging Golden Tickets)
(sAMAccountName=krbtgt)

# Only computer accounts (machine NT hashes)
(samAccountType=805306369)

# Specific OU
(&(samAccountType=805306368)(distinguishedName=*OU=Servers,DC=corp,DC=local))
```

If you want a single user without any filter overhead, set `username` instead.

---

## Prerequisites

- **DCSync rights** for the supplied `credential`. Without them, the
  `DRSGetNCChanges` call returns `ERROR_DS_DRA_ACCESS_DENIED` and the attack
  errors out per-user.
- **Outbound `445/TCP`** from the agent to the target DC (DCERPC over SMB named
  pipes is what's used).
- **The target must be a Domain Controller**. DCSync against a member server is
  not a thing — the relevant RPC interface only exists on DCs.
- **Defender / Advanced Threat Analytics** can detect DCSync via the
  `4662` event ("Object Operation") combined with the
  `89e95b76-444d-4c62-991a-0facbeda640c` GUID in the access-mask. On
  monitored environments, expect alerts.

---

## Parameters

### Normal parameters

#### `credential`
ID of the credential to authenticate over SMB. Must hold DCSync rights.

#### `targets`
List of targets — typically a single DC, but standard list / CIDR / file / `all`
syntax works.

#### `domain`
Optional. Override the domain DCSync targets. Default: detected from the SMB
context.

#### `storecreds`
Default: `False`. When `True`, every recovered secret is added to the
Credentials Hub. **Set this to `True` for almost every real run** — without it,
the secrets only land in the result stream and `outfile`.

#### `username`
Optional. Limit DCSync to a single named account (e.g. `krbtgt`). Mutually
useful with `ldapfilter` for the simple case.

#### `outfile`
Optional. Filename in `/browserfs/volatile` to append human-readable results to
(one line per user, Mimikatz-style).

#### `outfilehash`
Optional. Filename in `/browserfs/volatile` to append flat NT hashes to (one per
line). Convenient for piping into a cracker.

#### `ldapfilter`
Optional. LDAP filter string. When set, OctoPwn first runs an LDAP search and
passes the resulting `sAMAccountName` list as the DCSync target list.

### Advanced parameters

These only matter when `ldapfilter` is set and the LDAP context differs from the
SMB context:

#### `ldaptarget`
Target ID of the DC to use for the LDAP filter step. Defaults to `targets[0]`.

#### `ldapcredential`
Credential ID for the LDAP bind. Defaults to `credential`.

#### `ldapauthtype`
LDAP auth protocol. Default: `NTLM`. Set to `KERBEROS` if your credential is
Kerberos-only.

#### `ldapproxy`
Proxy ID for the LDAP connection.

#### `ldapprotocol`
Default: `LDAP`. Use `LDAPS` for TLS; `STARTTLS` for plain-port-with-StartTLS.

Plus the standard credentialled-SMB scanner parameter set: `authtype`, `dialect`,
`krbetypes`, `krbrealm`, `maxruntime`, `proxy`, `resultsfile`, `showerrors`,
`timeout`, `workercount`, `wsnetreuse`. See
[SMB client → authentication](../clients/smb.md#authentication) for the
auth-related ones.

---

## Typical workflow

1. **Confirm DCSync rights** before running. Either you know your account is in
   `Domain Admins` (trivial) or you've explicitly granted DCSync via
   [`addaceuser`](../clients/ldap.md) / `addacegroup` (e.g. after a successful
   [`RELAYLDAP`](../servers/relayldap.md) ACL write).
2. **Decide your scope.**
    - "Whole domain" — leave `username` and `ldapfilter` empty, set
      `storecreds=True`, set `outfile=ntds.dump`.
    - "Just `krbtgt`" — set `username=krbtgt`. Use this on quick smash-and-grab
      runs where you only want to forge a Golden Ticket.
    - "Just enabled users" — set the LDAP filter shown above.
3. **Run it.** With `storecreds=True`, the Credentials Hub fills up with the
   directory's NT hashes / AES keys / DPAPI backup keys.
4. **Use the loot.**
    - NT / AES keys → pass-the-hash, pass-the-key, [Kerberos](../clients/kerberos.md)
      ticket forging.
    - `krbtgt` → Golden / Sapphire / Diamond tickets.
    - Domain DPAPI backup keys → "God Mode" for the [`DPAPI`](dpapi.md) attack
      against any host in the domain.

---

## See also

- [LDAP client](../clients/ldap.md) — to *grant* DCSync rights with
  `addaceuser` / `addacegroup` after a successful
  [`RELAYLDAP`](../servers/relayldap.md) bind.
- [`DPAPI`](dpapi.md) — biggest direct beneficiary of DCSync output (domain
  backup keys).
- [Kerberos client](../clients/kerberos.md) — for using `krbtgt` and
  service-account keys to forge tickets.
- [SMB client](../clients/smb.md) — for the single-host `dcsync` command (same
  primitive without the multi-target / LDAP-filter harness).
