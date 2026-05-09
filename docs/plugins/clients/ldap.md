# LDAP Client

The **LDAP Client** is OctoPwn's general-purpose interface for LDAP — primarily Active Directory, but with limited support for non-Microsoft LDAP servers as well. It wraps the [`msldap`](https://github.com/skelsec/msldap) library and exposes its full surface as both a **GUI session window** (with tree browser, object viewer, raw query builder, and an Enterprise-only vulnerability scanner) and a very large **CLI command set** covering enumeration, modification, AD CS / Certify-style certificate abuse, BloodHound dump, DCSync ACL writes, delegation analysis, AD-integrated DNS manipulation, dMSA / Bad Successor checks, GPO hunting, LAPS retrieval, password-policy dumping, and more.

This is one of the largest clients in OctoPwn — over 80 callable commands. The page is organised so the [Authentication](#authentication) and [GUI](#gui-experience) sections come first, then every command grouped by its `help` category, then a short [Additional commands](#additional-commands) section for utilities that are callable but not listed in `help`.

---

## Transport

There are two transport variants of the same underlying client:

| Module name | Transport       | Default port |
| ----------- | --------------- | ------------ |
| `LDAP`      | TCP             | `389`        |
| `LDAPS`     | TLS-from-start  | `636`        |

Functionally the two are **identical** — every command on this page works on both. The difference is at session-creation time. `LDAPS` wraps the entire connection in TLS from the very first byte. `LDAP` is plaintext by default — but see the [`SSL` authentication type](#ssl-client-certificate-via-tls-or-starttls) below for the StartTLS path that upgrades a plain `LDAP` session to TLS mid-bind.

There is **no** Global Catalog (`GC` / `GC_SSL`) variant exposed here yet — use the `query` command's `basedn` argument together with `LDAP` / `LDAPS` for cross-domain searches in the same forest.

---

## Authentication

LDAP authentication is unusually rich. OctoPwn exposes four `atype` choices, each backed by its own family of secret types and each with its own quirks. Picking the wrong one is the most common reason a session fails to bind.

### `NTLM` — domain accounts via NTLM SSP

Standard NTLM bind via the LDAP `SASL/GSS-SPNEGO` mechanism (with the optional `encrypt=true` flag enabling NTLM signing/sealing — note that NTLM signing is incompatible with `LDAPS` and is automatically skipped there). Use this for any Windows / Active Directory account when you do not specifically need or want Kerberos.

| Secret type     | Description                                                  |
| --------------- | ------------------------------------------------------------ |
| `password`      | Cleartext password.                                          |
| `pwhex`         | Hex-encoded UTF-16LE password.                               |
| `nt` / `rc4`    | NT hash (pass-the-hash).                                     |
| `agentproxy`    | Remote NTLM signer over the wsnet agent proxy.               |
| `sspiproxy`     | OS SSPI session via the wsnet agent proxy (Windows agent).   |

### `KERBEROS` — domain accounts via Kerberos / SASL GSSAPI

Standard Kerberos bind via SASL GSSAPI. Requires reachability to a KDC (set on the credential / target) and a service principal of the form `ldap/<dc-hostname>@<REALM>`.

| Secret type     | Description                                                  | Example                              |
| --------------- | ------------------------------------------------------------ | ------------------------------------ |
| `password`      | Cleartext password.                                          | `user:Pa55w0rd!`                     |
| `pwhex`         | Hex-encoded UTF-16LE password.                               | `user:70617373…`                     |
| `nt` / `rc4`    | NT/RC4 hash.                                                 | `user:aad3b…`                        |
| `aes128`        | AES128 long-term key.                                        | `user:<32-hex>`                      |
| `aes256`        | AES256 long-term key.                                        | `user:<64-hex>`                      |
| `keytab`        | Keytab file in OctoPwn volatile storage.                     | `/browserfs/volatile/svc.keytab`     |
| `keytabb64`     | Base64-encoded keytab inline.                                | `user:<b64>`                         |
| `ccache`        | MIT ccache file in OctoPwn volatile storage.                 | `/browserfs/volatile/krb5cc.ccache`  |
| `ccacheb64`     | Base64-encoded ccache inline.                                | `user:<b64>`                         |
| `kirbi`         | `.kirbi` ticket file (Rubeus-style).                         | `/browserfs/volatile/admin.kirbi`    |
| `kirbib64`      | Base64-encoded `.kirbi` inline.                              | `user:<b64>`                         |
| `pfxb64`        | Base64-encoded PFX (PKINIT certificate auth via Kerberos).   | `user:<b64>`                         |
| `agentproxy`    | Remote KDC over the wsnet agent proxy.                       | n/a                                  |
| `sspiproxy`     | OS SSPI session via wsnet agent proxy (Windows agent).       | n/a                                  |

### `SIMPLE` — non-Microsoft LDAP

LDAP **simple bind** as defined in RFC 4513 — the username (typically the full DN, e.g. `cn=admin,dc=example,dc=org`) and the password are sent verbatim inside the BindRequest. This is the only authentication mode supported by most non-Microsoft LDAP servers (OpenLDAP, 389 DS, ApacheDS, …) and does **not** work against Active Directory unless the DC has been explicitly configured to allow it (it normally does, but the username has to be the full DN, not `DOMAIN\user`).

| Secret type | Description                                |
| ----------- | ------------------------------------------ |
| `password`  | Cleartext password sent verbatim in the bind. |
| `none`      | Anonymous bind (no password).              |

!!! warning "Simple bind is cleartext"
    `SIMPLE` over the `LDAP` (389) transport sends the password in the clear. Pair it with `LDAPS` (636) — or with `SSL` over `LDAP` (StartTLS) — whenever you do not own the wire.

### `SSL` — client certificate via TLS or StartTLS

Authentication is performed by the TLS handshake itself (the bind's username/password fields are empty). The only secret type is `pfxb64` — a base64-encoded PFX bundle containing the client certificate plus its private key.

The behaviour depends on the transport:

| Transport               | What happens                                                                                                                 |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `LDAPS` (port 636)      | The client certificate is presented during the **initial** TLS handshake. No SASL bind is sent — once the handshake succeeds, the user is bound. |
| `LDAP` (port 389)       | The client sends the **StartTLS extended operation** (`1.3.6.1.4.1.1466.20037`), wraps the existing TCP connection in TLS, then performs a **SASL EXTERNAL** bind. The server reads the certificate from the TLS context to identify the user. |

So `SSL` over `LDAP` is the StartTLS path; `SSL` over `LDAPS` is the implicit-TLS / "LDAPS-with-client-cert" path. Both end up with a TLS-protected, certificate-authenticated session.

| Secret type | Description                                                       |
| ----------- | ----------------------------------------------------------------- |
| `pfxb64`    | Base64-encoded PFX (`.pfx` / `.p12`) bundle with cert + private key. |

!!! tip "Picking the right `atype` at a glance"
    | The username looks like…                                             | Pick this `atype`     |
    | -------------------------------------------------------------------- | --------------------- |
    | `CONTOSO\jdoe`, `jdoe@contoso.local` — AD account                    | `NTLM` or `KERBEROS`  |
    | `cn=admin,dc=example,dc=org` — non-MS LDAP                            | `SIMPLE`              |
    | None — you have a `.pfx` bundle (e.g. from `shadowcred` / `certify`) | `SSL`                 |
    | None — anonymous bind for `ldapinfo` / RootDSE recon                 | `SIMPLE` + `none`     |

---

## GUI experience

The LDAP session window opens on the **Commands** tab by default. The header carries seven (eight on Enterprise) tabs:

- **Commands** — clickable buttons for every CLI command, grouped exactly like the [Commands](#commands) section below.
- **Objects** — a tabular browser for cached AD objects (users, machines, groups, GPOs, certificate templates, certify2 results, GPO-hunt results, trusts). Each row carries a context menu with one-click actions: change password, unlock, enable / disable, add-to-group, remove-from-group, change SAM name, change owner, grant DCSync, grant AddMember, grant LAPS read, plus jump-to-DN. The data behind it is populated by running the bulk fetchers (`users`, `machines`, `groups`, `gpos`, `trusts`, `certtemplates`, `certify2`, `gpohunt`) and is persisted in the session DB so you do not have to refetch on every tab switch.
- **Browser** — a tree-style LDAP directory browser rooted at the domain DN. Lazy-loads each container's children via a `listDirectory` RPC; clicking an entry on the right-hand pane shows all its attributes (with `objectClass` icons, decoded GUIDs / SIDs, and SDDL for security descriptors).
- **Query** — a dedicated raw-query builder with explicit fields for **base DN**, **scope** (`base` / `one` / `sub`), **filter**, and **attribute list**. Has a preset library (LDAP_QUERY_PRESETS) for common recon filters (kerberoastable users, DCs, computers, GPOs, etc.), per-result detail view, in-result search, last-10 history, and execution-time display.
- **Vulns** — Enterprise-only. Renders the structured findings produced by [`vulncheck`](#vulncheck) with severity colours (CRITICAL / HIGH / MEDIUM / LOW / INFO), filtering, search, expandable per-finding object lists, and pagination. The Vulns tab only appears on builds where `licenseType === 'remote'` (i.e. the Enterprise / WASM-pro distribution).
- **Jobs** — long-running background commands and a stop button.
- **History** — full command history for the session.
- **Settings** / **Debug** — connection parameters and protocol-level debug output.

Every tab is fed by the same backend session — running a CLI command (e.g. [`users`](#additional-commands)) directly populates the **Objects** tab; running [`vulncheck`](#vulncheck) directly populates the **Vulns** tab; etc. There is no "fetch data for the GUI" button — interacting with the GUI sends the right CLI command for you, and the result is stored in the session DB so the next tab open is instant.

---

## Commands

Every command below is callable from the session console (and most from the **Commands** GUI tab as a button). The grouping mirrors the `help` output of the running session.

All commands return `(result, error)` on the backend. Many also accept `to_print=False` to suppress the human-readable output while still returning the structured result — useful when chaining commands from scripts. Where a command takes that flag, it is documented as such.

---

### CONNECTION

#### login
Opens the LDAP/LDAPS connection, performs the chosen authentication exchange, fetches the AD info (`adinfo`) for the prompt, refreshes the credential's SID from the server (`whoamifull`), and proactively builds the privileged-groups cache used later by [`privcheck`](#privcheck) and [`privcheckall`](#privcheckall). Spins up a connection-monitor task so the session auto-fires `logout` if the server drops the link.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print status messages.

#### logout
Cancels the connection-monitor task, disconnects the LDAP client, and resets the connection-status pill.

---

### INFO

#### ldapinfo
Prints the full DSA / RootDSE info as returned by the server (`get_server_info`). Includes naming contexts, supported controls, supported SASL mechanisms, vendor, version, and schema/configuration NCs. Cached on first call — re-call is free.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print the result.

#### adinfo
Fetches the domain object (`(objectClass=domainDNS)` at the root) and caches its key fields (`distinguishedName`, `objectSid`, `domain_name`). Required by most commands and called automatically by [`login`](#login). Also pushes the parsed info to the GUI as `ADINFO` / `DOMAINS` so the Browser tab knows where to root the tree.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print the result.

#### whoami
Calls the LDAP `Who Am I?` extended operation **plus** the additional `whoamifull` helper that resolves the bound principal's SID, sAMAccountName, domain, and `tokenGroups` (every group the user is a transitive member of, expanded by the server).

#### whoamisimple
Just the bare `Who Am I?` extended op — returns the server's view of the bound principal (typically `u:DOMAIN\user`).

---

### ROAST

#### spns
Lists kerberoastable user accounts — users with a non-empty `servicePrincipalName` attribute (`(&(objectClass=user)(servicePrincipalName=*))`). For each match prints the `sAMAccountName`. Pair with the [Kerberos client](./kerberos.md)'s `kerberoast` to actually request and crack the TGS tickets.

#### asrep
Lists ASREP-roastable user accounts — users with the `DONT_REQ_PREAUTH` (`0x400000`) bit set in `userAccountControl`. Pair with the [Kerberos client](./kerberos.md)'s `asreproast` to request and crack the unprotected AS-REP responses.

#### spninfo
Like [`spns`](#spns), but pretty-prints a table for every SPN with `sAMAccountName`, `servicePrincipalName`, `memberOf`, `pwdLastSet`, `lastLogon`, decoded delegation flags (unconstrained / constrained), and `description`. Useful for triaging which SPN to attack first (look for stale `pwdLastSet`, juicy `description`, low `pwdLastSet` age vs. policy).

---

### ENUMERATION

#### domainmanager
Registers the current LDAP session with OctoPwn's **Domain Manager** subsystem — auto-logs in if needed and adds the domain to the global domain registry. Used by other clients (and the Enterprise UI) to share the LDAP session as the project's authoritative domain context.

#### computeraddr
Lists every computer account in the domain by `dNSHostName`, falling back to `<sAMAccountName-without-trailing-$>.<domain>` when `dNSHostName` is empty. Returns the resolved hostname list — useful as input for downstream port-scanning / SMB recon.

#### targetenum
Enumerates every machine account and bulk-adds them to OctoPwn's **Targets** registry. For each computer it:

- derives the FQDN (or falls back to `<sam-without-$>.<domain>`);
- derives a default port set (`445/TCP` plus any port hints from each SPN, e.g. `MSSQL` → `1433`, `WSMAN` → `5985`, etc.);
- captures `userAccountControl`, the `objectSid`, the OS strings, and the `description`;
- marks it as a DC if `userAccountControl` carries `SERVER_TRUST_ACCOUNT`;
- optionally resolves the IP via AD-integrated DNS.

##### Parameters
- **ldapresolve** *(optional, bool, default `False`)*: Resolve every host to an IP via [`dnsquerya`](#additional-commands) before adding it. Slow on large domains.
- **resolve** *(optional, bool, default `False`)*: Pass `resolve=True` down to OctoPwn's Targets manager so it resolves the IPs again with the global resolver after the bulk insert.

#### dump
Streams every user and every computer account to two TSV files (`users_<ts>.tsv`, `computers_<ts>.tsv`) in the OctoPwn working directory using the canonical `MSADUser_TSV_ATTRS` column set. No filtering, no decoration — useful when you need a flat dump for offline tools (BloodHound CE community edition, custom analyzers, …).

#### fulldump
Heavy-duty offline dump: writes ten separate TSV / JSON files (`adinfo`, `schema`, `trusts`, `users`, `computers`, `groups`, `ous`, `containers`, `gpos`, `dns`) plus packs them all into a single LZMA-compressed `dump_<ts>.zip` in the OctoPwn working directory. Suitable for offline forensic analysis.

#### tree
Prints an ASCII tree starting from the given DN (default: the domain root) down to the given depth (default: 1).

##### Parameters
- **dn** *(optional, str)*: DN to root the tree at. If a number is passed here it is treated as a depth override and the DN defaults to the domain root.
- **level** *(optional, int, default `1`)*: Depth of the tree.

#### bloodhound
Runs the embedded `MSLDAPDump2Bloodhound` collector against the current connection and writes a BloodHound-compatible ZIP into the OctoPwn working directory (`work_dir`). Returns the ZIP path on success. This is the equivalent of running `SharpHound` / `bloodhound.py` against the domain — feed the resulting ZIP to BloodHound (CE or legacy) for graph-based analysis.

#### userdescription
Sweeps every user object and prints `sAMAccountName : description` for every user whose `description` attribute is non-empty. The classic "passwords-in-description" discovery.

---

### QUERY

#### query
The raw LDAP search escape hatch. Sends a server-side paged search and prints every entry's DN and attributes (decoding `bytes` to hex and `SECURITY_DESCRIPTOR` to SDDL).

##### Parameters
- **query**: The LDAP search filter (e.g. `(&(objectClass=user)(adminCount=1))`).
- **attributes** *(optional, str, default `*`)*: Comma-separated attribute list (e.g. `sAMAccountName,memberOf,description`). `*` returns every non-operational attribute.
- **basedn** *(optional, str)*: The base DN to search from. Defaults to the domain root.
- **scope** *(optional, str, default `sub`)*: Search scope. One of `sub` (whole subtree), `one` (one level below the base), `base` (just the base DN itself).
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### modify
Generic LDAP modify — replaces a single attribute with a single value on a target object. Only works for string-typed attributes; for binary attributes (security descriptors, `msDS-AllowedToActOnBehalfOfOtherIdentity`, etc.) use the dedicated commands ([`setsd`](#setsd), [`addallowedtoactonbehalfofotheridentity`](#addallowedtoactonbehalfofotheridentity), …).

##### Parameters
- **dn**: DN of the object to modify.
- **attribute**: Name of the attribute to replace.
- **value**: New value.

---

### USER

#### user
Fetches a single user object by `sAMAccountName` and pretty-prints all known fields.

##### Parameters
- **samaccountname**: The user's sAMAccountName (without `DOMAIN\` prefix).

#### adduser
Creates a new user object at the given DN with the given password.

##### Parameters
- **user_dn**: Full DN where the user object will be created (e.g. `CN=newuser,CN=Users,DC=test,DC=corp`).
- **password**: Initial password.

#### deluser
Deletes the user object at the given DN. **Irreversible** — domain admins can recover from tombstones, but everyone else cannot.

##### Parameters
- **user_dn**: Full DN of the user to delete.

#### changeuserpw
Changes a user's password. If `oldpass` is supplied the change is performed via the user-self path (works without admin); if omitted, the change is performed administratively (requires `Reset Password` extended right). On success a `password` credential is auto-stored in the OctoPwn credential store. On `constraintViolation` errors the command prints a friendly explanation of the typical causes (history, complexity, lockout, missing old password).

##### Parameters
- **user_dn**: Full DN of the target user.
- **newpass**: New password.
- **oldpass** *(optional, str)*: Old password — required for self-service change, omit for admin reset.

#### unlockuser
Unlocks an account by setting `lockoutTime` to `0`.

##### Parameters
- **user_dn**: Full DN of the locked user.

#### enableuser
Enables a disabled user by clearing the `ACCOUNTDISABLE` bit in `userAccountControl`.

##### Parameters
- **user_dn**: Full DN of the user.

#### disableuser
Disables a user by setting the `ACCOUNTDISABLE` bit in `userAccountControl`.

##### Parameters
- **user_dn**: Full DN of the user.

#### addspn
Appends an entry to the user's `servicePrincipalName` multi-value attribute. A common kerberoasting setup step (give yourself an SPN on a controlled account so it becomes kerberoastable, request the TGS, crack offline).

##### Parameters
- **user_dn**: Full DN of the user.
- **spn**: SPN to add (e.g. `MSSQLSvc/dummy.test.corp:1433`).

#### delspn
Removes an entry from the user's `servicePrincipalName` multi-value attribute.

##### Parameters
- **user_dn**: Full DN of the user.
- **spn**: SPN to remove.

#### addusertogroup
Adds a user to a group by appending the user's DN to the group's `member` attribute. Both arguments must be full DNs.

##### Parameters
- **user_dn**: User DN.
- **group_dn**: Group DN.

#### deluserfromgroup
Removes a user from a group.

##### Parameters
- **user_dn**: User DN.
- **group_dn**: Group DN.

---

### MACHINE

#### machine
Fetches a machine object by `sAMAccountName` (computer accounts end in `$`, but the trailing `$` is automatically appended by the underlying lookup if missing). Also decodes the `msDS-AllowedToActOnBehalfOfOtherIdentity` security descriptor to SDDL for resource-based-constrained-delegation analysis.

##### Parameters
- **samaccountname**: The machine's sAMAccountName.

#### computeradd
Creates a new computer account, respecting MachineAccountQuota (so unprivileged users can usually create one — see [`maq`](#maq)). Returns the auto-generated computer name and password (which is also stored as a `Credential` in the OctoPwn credential store, tagged `LDAP-COMPUTERADD-<sessionid>`).

##### Parameters
- **computername** *(optional, str)*: Desired sAMAccountName (without trailing `$`). If omitted, a random one is generated.
- **password** *(optional, str)*: Desired password. If omitted, a random one is generated.

#### addhostname
Appends an entry to the computer account's additional-hostnames list (`msDS-AdditionalDnsHostName` / `servicePrincipalName`). Used for SPN-spoofing tricks during Kerberos-relay setups.

##### Parameters
- **user_dn**: Full DN of the computer account.
- **hostname**: Additional hostname to register.

#### pre2000
Lists machine accounts that were created with the legacy "Assign this computer account as a pre-Windows 2000 computer" tickbox — `(&(userAccountControl=4128)(logonCount=0))`. These accounts famously have a known default password (the lower-cased machine name, no trailing `$`) and are a recurrent privilege-escalation primitive.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### computeraddr
*(Listed under [ENUMERATION](#enumeration) — included in the MACHINE help group as well.)*

#### changesamaccountname
Changes the `sAMAccountName` of an arbitrary object by DN — used during the original noPac / sAMAccountName-spoofing attack chain.

##### Parameters
- **dn**: DN of the object.
- **newname**: New `sAMAccountName` value.

#### domaincontrollers
Lists every domain controller in the current domain (using `(&(objectCategory=computer)(primaryGroupId=516))`).

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

---

### GPO

#### gpos
Lists all Group Policy Objects (GPOs) in the domain — `displayName`, GPO GUID, file-system path (`\\<domain>\SYSVOL\…`), and `versionNumber`.

#### gpohunt
For a given user (or SID) — or the current bound principal if no argument is given — evaluates every GPO's security descriptor with the user's expanded `tokenGroups` and reports the **effective access mask** plus any directly-granted permissions on each GPO. Use it to find GPOs your token can write to (`GENERIC_WRITE`, `WRITE_DACL`, `WRITE_OWNER`, …) — the classical GPO-takeover preconditions.

##### Parameters
- **username_or_sid** *(optional, str)*: A SID (`S-1-5-21-…`), a sAMAccountName, or a comma-separated `<sid>,<extra-sid-1>,<extra-sid-2>,…` blob to manually inject token groups. Defaults to the bound principal.

---

### LAPS

#### laps
Reads the legacy Microsoft LAPS attribute `ms-Mcs-AdmPwd` from every computer object visible to the bound principal (or a single machine if `machinesid` is given). Empty / no-permission entries are surfaced as `<MISSING>`.

##### Parameters
- **machinesid** *(optional, str)*: Limit to a single machine by SID. Default: enumerate all.

#### newlaps
Reads the modern Windows LAPS attributes `msLAPS-Password`, `msLAPS-EncryptedPassword`, `msLAPS-EncryptedPasswordHistory`, `msLAPS-EncryptedDSRMPassword`, `msLAPS-EncryptedDSRMPasswordHistory`. Encrypted blobs are printed in hex; decryption requires the appropriate DPAPI keys and is not yet handled by this command.

#### grantreadlapsrights
Grants the named user / SID **read** rights on the legacy LAPS attribute (`ms-Mcs-AdmPwd`) of a target computer object by appending an `ACCESS_ALLOWED_OBJECT_ACE` with `READ_PROP | WRITE_PROP | CONTROL_ACCESS` over that specific schema attribute's GUID.

##### Parameters
- **target_dn**: DN of the computer object.
- **user_dn_or_sid**: DN or SID of the principal to grant rights to.

---

### GROUP

#### groupmembership
Fetches every group SID that the named DN is a transitive member of (via `tokenGroups`) and resolves each one to a DN.

##### Parameters
- **dn**: DN of the user / computer.

#### groupmembers
Returns the members of a group (recursively by default).

##### Parameters
- **dn**: DN of the group.
- **recursive** *(optional, bool, default `True`)*: Whether to expand nested groups.
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### dadms
Lists every member of the **Domain Admins** group (recursive). Sugar around `groupmembers` for the `Domain Admins` SID (`<domain-sid>-512`).

#### privcheck
Checks whether a given principal is a member (directly or indirectly) of any privileged AD group. Looks up against a cached set of privileged SIDs (built once by the implicit call to [`buildprivgroups`](#additional-commands)): builtin Administrators / Account / Server / Print / Backup Operators / Replicator + Domain Admins / Cert Publishers / Schema Admins / Enterprise Admins / Key Admins / Enterprise Key Admins, plus DnsAdmins / Certificate Operators by name. The lookup tries the local DB first (USERS then MACHINES tables, populated by the bulk fetchers) and falls back to a live `tokenGroups` query.

##### Parameters
- **cid_dn_sid_sam**: A credential ID, SID, DN, or sAMAccountName.
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

---

### TRUSTS

#### trusts
Lists every domain trust (`trustedDomain` objects) and adds each trust target as a Target with `isdc=True` and the standard DC port set (389/88/445). Useful as the first step before pivoting across forests.

#### dclist
Heavy-weight DC enumeration that combines `(&(objectCategory=computer)(primaryGroupId=516))` for the local domain with a per-trust DNS-SRV lookup (`_ldap._tcp.dc._msdcs.<trust-domain>`) to enumerate DCs across every trust as well. Resolves IPs through AD-integrated DNS for everything found. Returns a `{current_domain: [...], trusted_domains: [...]}` structure and prints a per-trust breakdown including direction (Inbound / Outbound / Bidirectional / Disabled), trust type (NT / AD / Kerberos / Azure AD), and decoded trust attributes (Forest Transitive, Within Forest, Cross Organization, Quarantined, PAM Trust, …).

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

---

### POLICY

#### passpol
Dumps the **default domain password policy** by reading the `domainDNS` object's `minPwdLength`, `pwdHistoryLength`, `maxPwdAge`, `minPwdAge`, `lockoutThreshold`, `lockoutDuration`, `lockOutObservationWindow`, `forceLogoff`, and `pwdProperties`. Decodes the FILETIME durations and the `pwdProperties` complexity flags (`DOMAIN_PASSWORD_COMPLEX`, `DOMAIN_PASSWORD_NO_ANON_CHANGE`, `DOMAIN_PASSWORD_NO_CLEAR_CHANGE`, `DOMAIN_LOCKOUT_ADMINS`, `DOMAIN_PASSWORD_STORE_CLEARTEXT`, `DOMAIN_REFUSE_PASSWORD_CHANGE`).

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### pso
Lists Fine-Grained Password Policies (Password Settings Objects) by querying `(objectclass=msDS-PasswordSettings)` under `CN=Password Settings Container,CN=System,<domain-dn>`. For every PSO prints its name, all `msDS-*` policy fields with FILETIME durations decoded, and the list of objects the PSO applies to. Also prints a separate list of objects with `(msDS-PSOApplied=*)`.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

---

### RECON

#### entraid
Finds Entra ID (Azure AD Connect) sync infrastructure by:

1. Searching for `MSOL_*` accounts (one per AD Connect connector) — extracts the source server hostname from the account's `description` (`computer <host> configured`).
2. Searching for `ADSyncMSA*` accounts (group-managed service accounts used by AD Connect 2.x) — resolves their `msDS-HostServiceAccountBL` back to the actual host computer.
3. Resolving every discovered host to an IP via AD-integrated DNS and adding it as a Target.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### sccm
Discovers SCCM / MECM (System Center Configuration Manager) infrastructure (PKI-Recon-1 technique). Looks at:

- The `CN=System Management,CN=System,<domain-dn>` container's DACL — every principal with full control (`0xF01FF`) on this container is an SCCM site server. Group SIDs are recursively expanded to find member machine accounts.
- `(objectClass=mSSMSSite)` — actual SCCM site definitions with site code / assignment site code.
- `(objectClass=mSSMSManagementPoint)` — every Management Point with `dNSHostName`, default-MP flag, and site code. Sites with no MP are flagged as **CAS** (Central Administration Site).
- `(|(samaccountname=*sccm*)(samaccountname=*mecm*)(description=*sccm*)(description=*mecm*)…)` — named SCCM-related users / computers / groups (the "did the admins literally name something sccm" pass).

Every discovered server is added as a Target. Resolves hostnames via AD-integrated DNS.

##### Parameters
- **recursive** *(optional, bool, default `False`)*: When `True`, group memberships in the named-objects pass are expanded recursively (`memberOf:1.2.840.113556.1.4.1941:=…`).
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### credattrs
Sweeps every user for password-adjacent LDAP attributes — `info`, `userPassword`, `unixUserPassword`, `comment` — and prints every populated value. Optional grep filter applies to both the `sAMAccountName` and the value itself.

##### Parameters
- **filter_str** *(optional, str)*: Optional substring filter.
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### usercredsllm
LLM-driven password discovery. Pulls every user with at least one populated `description` / `info` / `userPassword` / `unixUserPassword` / `comment` attribute, hands them to the configured LLM (via the `instructor` library — model and provider come from the project-wide LLM client), parses the structured `LLMUserPasswordAnalysis` response for password candidates, then **validates each candidate by performing an actual LDAP NTLM bind** against the DC. Valid passwords are stored in the credential store. Honours the domain lockout policy: schedules safe batches (`lockoutThreshold - 1`) and waits the lockout observation window between batches.

##### Parameters
- **username** *(optional, str)*: Limit analysis to a single user. Default: scan everyone with populated attributes.
- **batch** *(optional, bool, default `False`)*: Send all users to the LLM in a single batched call. Faster but consumes more tokens per request.
- **login_timeout** *(optional, int, default `15`)*: Per-bind timeout in seconds.

#### maq
Prints the domain's `MachineAccountQuota` (read from `adinfo.machineAccountQuota` — no extra LDAP query). Anything > 0 means an unprivileged user can create that many machine accounts via [`computeradd`](#computeradd).

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### obsolete
Finds **enabled** machine accounts running end-of-life Windows versions (Server 2003 / 2008 / 2012, XP, Vista, 7, 8, 8.1) — `(&(objectCategory=computer)(!(userAccountControl:1.2.840.113556.1.4.803:=2))(operatingSystem=*<obsolete os>*))`. Output includes `pwdLastSet` and `lastLogonTimestamp` so you can spot dormant boxes.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

---

### SCHEMA

#### schemaentry
Fetches a single schema entry by DN (must start with `CN=` and live under the schema NC).

##### Parameters
- **cn**: DN of the schema object.

#### schemaentryname
Fetches a single schema entry by attribute / class name (e.g. `ms-Mcs-AdmPwd`).

##### Parameters
- **name**: The schema entry's `name` (or `lDAPDisplayName`).

#### allschemaentry
Iterates every schema entry — slow but useful for one-off offline analysis.

---

### SECURITY DESCRIPTOR

#### getsd
Fetches the security descriptor of a target object and prints it as SDDL.

##### Parameters
- **dn**: DN of the target.

#### setsd
Replaces the security descriptor of a target object with a new one parsed from SDDL.

##### Parameters
- **target_dn**: DN of the target.
- **sddl**: New security descriptor as an SDDL string.

#### changeowner
Changes the **owner** of an object's security descriptor (or of one of its attributes' SDs when `target_attribute` is specified). Useful for the WriteOwner abuse path: take ownership → `setsd` to grant yourself the rights you want.

##### Parameters
- **new_owner_sid**: SID of the new owner.
- **target_dn**: DN of the target.
- **target_attribute** *(optional, str)*: When set, change the owner of this attribute's SD instead of the object's main SD.

#### addprivdcsync
Modifies the **forest** security descriptor to add the two ACEs (`Replicating Directory Changes` + `Replicating Directory Changes All`) that grant DCSync rights to the named user. After this, the user can be used with the [DCEDRSUAPI client](./dcedrsuapi.md) to dump every secret in the domain.

##### Parameters
- **user_dn**: DN of the user to grant DCSync to.
- **forest** *(optional, str)*: Override the forest DN. Defaults to the current domain's distinguishedName.

#### addprivaddmember
Adds an `AddMember` extended-right ACE to a group's SD so the named user can append themselves (or anyone) to it without being `WRITE`-on-the-group.

##### Parameters
- **user_dn**: DN of the user being granted the right.
- **group_dn**: DN of the target group.

#### addallowedtoactonbehalfofotheridentity
Sets / appends to the target object's `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute — the **resource-based constrained delegation** primitive. Returns the original SD blob in hex (or `None` if there was no prior value), which you should keep around for [`restoreallowedtoactonbehalfofotheridentity`](#additional-commands) cleanup.

##### Parameters
- **target_dn**: DN of the target object (typically a computer account).
- **other_identity_sid**: SID of the identity being allowed to delegate to the target (typically a controlled computer account from [`computeradd`](#computeradd)).

#### add_genericwrite
Appends an `ACCESS_ALLOWED_ACE` with `GENERIC_WRITE` over the target object's DACL, giving the named user `GenericWrite` on the target. Used as a building block for many AD attack paths.

##### Parameters
- **targetdn**: DN of the object being modified.
- **userdn**: DN of the user being granted the right.

---

### SID

The five resolution helpers — every command takes a `to_print` flag.

#### sid2dn
Resolves a SID to a DN via `LDAP://<DC>/<SID=…>` syntactic search.

##### Parameters
- **sid**: The SID string.
- **to_print** *(optional, bool, default `True`)*: Whether to print the DN.

#### dn2sid
Reads `objectSid` from the named DN.

##### Parameters
- **dn**: The DN.
- **to_print** *(optional, bool, default `True`)*: Whether to print the SID.

#### sam2dn
Looks up the DN of the object with the given `sAMAccountName`.

##### Parameters
- **sAMAccountName**: The sAMAccountName.
- **to_print** *(optional, bool, default `True`)*: Whether to print the DN.

#### dn2sam
Reads `sAMAccountName` from the named DN.

##### Parameters
- **dn**: The DN.
- **to_print** *(optional, bool, default `True`)*: Whether to print the sAMAccountName.

#### sidresolv
Calls the `LsarLookupSids` equivalent through LDAP and prints `<DOMAIN>\<username>`.

##### Parameters
- **sid**: The SID.
- **to_print** *(optional, bool, default `True`)*: Whether to print the result.

---

### GMSA

#### gmsa
Lists every group-managed service account (`(objectClass=msDS-GroupManagedServiceAccount)`) and — for every gMSA the bound principal is allowed to read — fetches the `msDS-ManagedPassword` blob, decodes it to the gMSA's current password (cleartext) and NT hash, and stores the password as a `pwb64` credential in the OctoPwn credential store. Prints the list of allowed principals (the `PrincipalsAllowedToRetrieveManagedPassword` SDDL ACEs) for every gMSA so you know who can read what.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

---

### PKI

#### rootcas
Lists every certificate in the **AIA / Root CA** container (`Root CAs` published in the configuration NC).

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### ntcas
Lists every certificate in the **NTAuth** container — these are the CAs the DC trusts for **client smartcard / PKINIT** authentication.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### aiacas
Lists every certificate in the **AIA** container.

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### enrollmentservices
Lists every AD CS enrollment service (CA) registered in the configuration NC — name, DNS hostname, supported templates, and CA flags. Each CA is added to the OctoPwn Targets registry so it can be used by other clients (e.g. the certificate-enrollment HTTP/RPC tools).

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### certtemplates
Lists every certificate template, with its full security descriptor (resolved against a SID lookup table) and which enrollment service(s) publish it. Pushes the result to the GUI as `CERTTEMPLATES` so the Objects tab can render it.

##### Parameters
- **name** *(optional, str)*: Limit to a single template by name.
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### certify
Identifies vulnerable certificate templates using the original `is_vulnerable` heuristic. For every vulnerable template prints the reason. If `username` is supplied, the user's `tokenGroups` are used to filter matches to templates *that user* can interact with.

##### Parameters
- **username** *(optional, str)*: sAMAccountName of the user to check. Default: the bound principal.
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### certify2
Updated Certify-style vulnerability check that uses the more recent `is_vulnerable2` analysis (per-vulnerability findings with `Reason` strings, ESC1 / ESC2 / ESC3 / ESC4 / ESC6 / ESC7 / ESC9 / ESC10 / ESC11 / ESC13 / ESC15 mapping). Pushes the result to the GUI as `CERTIFY2` for the Objects tab to render. Adds every involved enrollment-service host to the Targets registry.

##### Parameters
- **username** *(optional, str)*: Override the principal whose `tokenGroups` are used. Default: the bound principal.
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### addcerttemplatenameflagaltname
Modifies `msPKI-Certificate-Name-Flag` on the named template to enable `ENROLLEE_SUPPLIES_SUBJECT_ALT_NAME` (the **ESC1** abuse primitive). Optionally sets the flag value to a caller-provided integer instead.

##### Parameters
- **certtemplatename**: Template name.
- **flags** *(optional, int)*: If provided, set `msPKI-Certificate-Name-Flag` to exactly this value. If omitted, the existing value is OR-ed with `ENROLLEE_SUPPLIES_SUBJECT_ALT_NAME`.

#### addenrollmentright
Grants enrollment rights (`READ_PROP | WRITE_PROP | CONTROL_ACCESS` over the `Certificate-Enrollment` extended-right GUID) on the named template to the user identified by DN.

##### Parameters
- **certtemplatename**: Template name.
- **user_dn**: DN of the principal being granted enrollment rights.

---

### DELEGATION

#### unconstrained
Lists machines and users with **unconstrained delegation** set (`TRUSTED_FOR_DELEGATION`).

#### constrained
Lists every object with **constrained delegation** set — for each one prints `<sAMAccountName> -> <SPN>` for every entry in `msDS-AllowedToDelegateTo`.

#### s4u2proxy
Lists every object set up for **S4U2Proxy** (the protocol-transition variant of constrained delegation — `TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION`).

---

### DNS

The DNS commands operate against **AD-integrated DNS** (the records stored in the `MicrosoftDNS` directory partition). Everything except `dnsdump` accepts the same `forest` / `legacy` flags that decide which copy of the zone to talk to.

#### dnszones
Lists every DNS zone known to AD-integrated DNS. For each zone prints the name plus its full property block (allow-update flag, secondary servers, etc.).

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### dnsunsecure
Detects zones that allow **non-secure dynamic updates** (`DnsZoneAllowUpdate = 1`) — a primitive for unauthenticated DNS-record injection. Also reports zones that are secure-only (`= 2`) and zones with updates disabled (`= 0`).

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### dnsdump
Enumerates every record in every zone (or in a single zone if `zone` is supplied) and writes them as TSV (`<zone-dn>\t<name>\t<rrtype>\t<formatted-data>`) to `dns_<ts>.tsv` in the OctoPwn working directory.

##### Parameters
- **zone** *(optional, str)*: Limit to a single zone. Default: dump all zones.

#### dnsquery
Queries the records of a single name in a single zone.

##### Parameters
- **target**: The record name to query.
- **zone** *(optional, str)*: Zone name. Default: derived from settings.
- **forest** *(optional, bool, default `False`)*: Use the forest-wide replica.
- **legacy** *(optional, bool, default `False`)*: Use the legacy `DC=DomainDnsZones,…` replica.

#### dnsqueryall
Same as `dnsquery` but enumerates every record in the zone.

##### Parameters
- **zone** *(optional, str)*: Zone name.
- **forest** *(optional, bool, default `False`)*: Use the forest-wide replica.
- **legacy** *(optional, bool, default `False`)*: Use the legacy replica.

#### dnsadd
Creates a new A record. The change can take minutes to take effect because it has to replicate.

##### Parameters
- **target**: Record name.
- **ip**: IPv4 address.
- **zone** *(optional, str)*: Zone name. Default: derived from settings.
- **forest** *(optional, bool, default `False`)*: Use the forest-wide replica.
- **legacy** *(optional, bool, default `False`)*: Use the legacy replica.

#### dnsremove
**Tombstones** an existing A record (sets the tombstone bit, the record disappears at next scavenging).

##### Parameters
- **target**: Record name.
- **ip**: IPv4 address being removed.
- **zone** *(optional, str)*: Zone name.
- **forest** *(optional, bool, default `False`)*: Use the forest-wide replica.
- **legacy** *(optional, bool, default `False`)*: Use the legacy replica.

#### dnsdelete
**Hard-deletes** the directory object backing the record (vs. tombstoning).

##### Parameters
- **target**: Record name.
- **zone** *(optional, str)*: Zone name.
- **forest** *(optional, bool, default `False`)*: Use the forest-wide replica.
- **legacy** *(optional, bool, default `False`)*: Use the legacy replica.

#### dnsmodify
Replaces the IP for an existing record.

##### Parameters
- **target**: Record name.
- **ip**: New IPv4 address.
- **zone** *(optional, str)*: Zone name.
- **forest** *(optional, bool, default `False`)*: Use the forest-wide replica.
- **legacy** *(optional, bool, default `False`)*: Use the legacy replica.

#### dnsrestore
Restores a previously-tombstoned record.

##### Parameters
- **target**: Record name.
- **zone** *(optional, str)*: Zone name.
- **forest** *(optional, bool, default `False`)*: Use the forest-wide replica.
- **legacy** *(optional, bool, default `False`)*: Use the legacy replica.

#### dnsgetserial
Returns the SOA serial number of a zone.

##### Parameters
- **zone** *(optional, str)*: Zone name.
- **forest** *(optional, bool, default `False`)*: Use the forest-wide replica.
- **legacy** *(optional, bool, default `False`)*: Use the legacy replica.

---

### DMSA

Delegated Managed Service Accounts (Server 2025) and the related "Bad Successor" abuse primitive.

#### dmsas
Lists every Delegated Managed Service Account (`(objectClass=msDS-DelegatedManagedServiceAccount)`).

#### badsuccessor_check
Checks for the **Bad Successor** primitive — a Server 2025 OU-level attack where any user with `GenericAll` / `GenericWrite` / `WriteOwner` / `WriteDacl` / `CreateChild` / `WriteProperty` / `ControlAccess` on an OU can create a dMSA and convince the KDC to issue tickets impersonating any user in the domain. Iterates every OU's DACL, filters out well-known privileged SIDs, and reports any non-privileged principal that can abuse the OU. Also lists every Server 2025 DC found in the domain (so you know whether the prerequisite is met).

#### dmsaaddmanagedaccountprecededbylink
Sets the `msDS-ManagedAccountPrecededByLink` attribute on a DMSA — a building block for the Bad Successor exploitation chain.

##### Parameters
- **dn**: DN of the DMSA.
- **managedaccountprecededbylink**: Replacement DN string.

#### dmsasetdelegatedmsastate
Sets the `msDS-DelegatedMSAState` attribute on a DMSA.

##### Parameters
- **dn**: DN of the DMSA.
- **delegatedmsastate**: Integer state value.

#### create_broken_dmsa_user
Creates a "broken" DMSA service user that, in conjunction with the Bad Successor primitive, can be used to escalate privileges. Do not use outside of an authorised engagement.

##### Parameters
- **user_dn**: DN where the DMSA object will be created.
- **computersid**: SID of the computer to associate the DMSA with.

---

### ANALYSIS

#### vulncheck
**Enterprise-only.** Runs the full registered LDAP-vulnerability check suite (`octopwn.enterprise.ldap_checks.base.CheckRegistry`) against the current connection. Each check produces zero or more `LDAPVulnerability` issues; results are pushed to the GUI as `LDAP_VULNERABILITY` so the **Vulns** tab can render them with severity, affected objects, and remediation hints. Returns the JSON-serialised list of issues. The check suite covers the standard AD-misconfig surface (PKI / ESC chains, LAPS, weak password policy, dangerous ACLs, signed-binding policy, unconstrained delegation, certificate templates, AD CS web enrollment, …).

##### Parameters
- **to_print** *(optional, bool, default `True`)*: Whether to also print every issue to the console.

---

## Additional commands

These are callable from the console but do not appear in the `help` output. Most are helpers that other commands call internally; a few are fully usable on their own.

#### users / machines / groups
Bulk fetchers that populate the session's local DB and stream results to the GUI's **Objects** tab. Each one streams in 1000-object chunks. If the DB already has data, the cached version is replayed unless `overwrite=True`.

##### Parameters (`users`, `machines`)
- **overwrite** *(optional, bool, default `False`)*: Re-fetch from the server even if the DB is populated.
- **fetch_token_groups** *(optional, bool, default `True`)*: Also fetch each object's `tokenGroups` (slower but lets [`privcheckall`](#privcheckall) work without further LDAP queries).

##### Parameters (`groups`)
- **overwrite** *(optional, bool, default `False`)*: Re-fetch even if the DB is populated.

#### privcheckall
Runs [`privcheck`](#privcheck) over every object of the named storage type in the local DB (default `USERS`, also `MACHINES`). Uses cached `tokenGroups` so it is much faster than a live-LDAP scan. Results are themselves cached as `PRIVCHECKALL_<key>` for future fast lookups.

##### Parameters
- **key** *(optional, str, default `USERS`)*: Storage type to scan.
- **force** *(optional, bool, default `False`)*: Re-run even if the cache is populated.
- **to_print** *(optional, bool, default `True`)*: Whether to print results.

#### buildprivgroups
Builds the cache of privileged-group SIDs used by `privcheck` / `privcheckall`. Combines well-known SIDs (`S-1-5-32-544/548/549/550/551/552`), domain-relative RIDs (`<domain-sid>-512/517/518/519/526/527`), and named groups (`DnsAdmins`, `Certificate Operators`). Persisted in the session DB as `PRIVGROUP`.

##### Parameters
- **force** *(optional, bool, default `False`)*: Re-build even if the cache is populated.
- **to_print** *(optional, bool, default `True`)*: Whether to print the table.

#### lookupobj
Looks up an object in the local DB by credential ID, SID, DN, or sAMAccountName. The storage type is the second positional argument.

##### Parameters
- **cid_dn_sid_sam**: Identifier.
- **key**: Storage type — `USERS`, `MACHINES`, `GROUPS`, etc.
- **to_print** *(optional, bool, default `True`)*: Whether to print the matched object.

#### resolvebasic
Returns a `{sAMAccountName, objectSid, distinguishedName}` triple for the given identifier (credential ID / SID / DN / sAMAccountName).

##### Parameters
- **cid_dn_sid_sam**: Identifier.
- **to_print** *(optional, bool, default `True`)*: Whether to print the result.

#### bindtree
Changes the tree (search base) used by `MSLDAPClient` for subsequent calls. **Dangerous** — switching to a tree outside the bound domain triggers a referral chase that can leak credentials to the wrong server.

##### Parameters
- **newtree**: New base DN (e.g. `DC=test,DC=corp`).

#### domains
Alias for `adinfo(False)` — kept for backwards compatibility.

#### sid2sam
Same data as [`sidresolv`](#sidresolv) but returns just the `sAMAccountName` (without the `<DOMAIN>\` prefix).

##### Parameters
- **sid**: SID.
- **to_print** *(optional, bool, default `True`)*: Whether to print the username.

#### addfullcontrolright
Grants **`GENERIC_ALL`** to the named user / SID on a target object's DACL (the brute-force version of [`add_genericwrite`](#add_genericwrite)).

##### Parameters
- **target_dn**: DN of the object being modified.
- **user_dn_or_sid**: DN or SID of the principal.

#### restoreallowedtoactonbehalfofotheridentity
Cleanup helper for [`addallowedtoactonbehalfofotheridentity`](#addallowedtoactonbehalfofotheridentity). Restores the original `msDS-AllowedToActOnBehalfOfOtherIdentity` blob (passed as a hex string), or removes the attribute entirely when `original_sd` is omitted / empty.

##### Parameters
- **target_dn**: DN of the target.
- **original_sd** *(optional, str)*: Hex-encoded original SD blob (as returned by the original add command). Omit to delete the attribute.

#### setkeycredentiallink
Replaces the `msDS-KeyCredentialLink` attribute on a target object — the lower-level building block behind [`shadowcred`](#shadowcred).

##### Parameters
- **targetdn**: DN of the target.
- **keycredentiallink** *(optional, list)*: List of credential link strings. Pass an empty list (or omit) to clear the attribute.

#### shadowcred
The full **Shadow Credentials** attack: generates a self-signed certificate, packages it into a Key Credential Link, appends it to the target user's `msDS-KeyCredentialLink`, exports the matching PFX (password: `admin`), and stores it in the OctoPwn credential store as a `pfxb64` credential — usable directly with the [Kerberos client](./kerberos.md)'s `pfxb64` PKINIT auth or with this client's [`SSL`](#ssl-client-certificate-via-tls-or-starttls) auth. Returns the original Key Credential list so you can restore it later via [`setkeycredentiallink`](#setkeycredentiallink).

##### Parameters
- **targetuser**: sAMAccountName of the target user.

#### dnsquerya
Resolves an FQDN to its A record(s) via AD-integrated DNS. Used internally by every command that needs to resolve a hostname (`targetenum --ldapresolve`, `dclist`, `entraid`, `sccm`, …).

##### Parameters
- **fqdn**: FQDN to resolve.
- **to_print** *(optional, bool, default `True`)*: Whether to print the addresses.

#### dnsprobe
Auto-detects the AD-integrated DNS layout (forest-wide vs. domain-wide, modern vs. legacy partition) by trying every combination against a known FQDN. Caches the result on the session — future DNS commands (`dnsquerya`, `dnsadd`, …) reuse the cache.

##### Parameters
- **hostname**: A known-good FQDN to probe with.

#### dnssoa
Prints the SOA record of a zone.

##### Parameters
- **zone** *(optional, str)*: Zone name.
- **forest** *(optional, bool, default `False`)*: Use the forest-wide replica.
- **legacy** *(optional, bool, default `False`)*: Use the legacy replica.

#### subnets
Fetches every machine account's IP via AD-integrated DNS, then groups the IPs into realistic CIDR ranges using a proximity heuristic (max gap and minimum prefix tunable). Useful as a quick "what subnets exist in this domain?" answer when there is no Sites & Services data.

##### Parameters
- **max_gap** *(optional, int, default `256`)*: Maximum gap between consecutive IPs to keep them in the same subnet (default `256` ⇒ effectively `/24`).
- **min_prefix** *(optional, int, default `16`)*: Minimum prefix length allowed (no `/8` results).

#### test_login
Helper used by [`usercredsllm`](#usercredsllm) — performs a one-shot LDAP NTLM bind with the given username/password (or NT hash) against the same target as the current session and returns success/failure. You probably want the [`sshlogin`](../scanners/sshlogin.md) / SMB equivalents in the **Scanners** category for actual credential-spraying.

##### Parameters
- **username**: sAMAccountName.
- **password**: Cleartext password — or a 32-character hex string (auto-detected as an NT hash).

---

## Limitations

- **Pick the right `atype`.** `SIMPLE` is for OpenLDAP / 389 DS / non-MS LDAP; `NTLM` / `KERBEROS` is for AD; `SSL` is the cert-based path. The most common reason for a failed bind is mixing them up — see the [tip table](#authentication) above.
- **No Global Catalog transport (yet).** Use `query` with `basedn` for cross-domain searches in the same forest, or open a separate session against `<dc-host>:3268`.
- **`SIMPLE` over `LDAP` (389) is cleartext.** Use `LDAPS` (636) or `SSL`-over-`LDAP` (StartTLS) when you do not own the wire.
- **`vulncheck` is Enterprise-only.** The `octopwn.enterprise.ldap_checks` module is not bundled with the community / WASM-pro distribution; the command will fail to import on those builds.
- **`bloodhound` writes a ZIP to `work_dir`.** Make sure your working directory has space (large domains can produce hundreds of MB).
- **DNS commands need the right `forest` / `legacy` setting.** Use [`dnsprobe`](#dnsprobe) once at the start of a session against a known FQDN — every subsequent DNS command will reuse the cached settings.
- **`changeuserpw` raises `constraintViolation` on policy violations.** The exception is caught and a friendly explanation is printed (history, complexity, missing old password, lockout). Read it.
- **`newlaps` does not decrypt encrypted blobs.** `msLAPS-EncryptedPassword` and friends are printed in hex; decryption requires DPAPI keys and is out of scope for this command.
- **`bindtree` to a foreign domain leaks credentials.** Switching the search base to a DN outside the bound domain triggers a referral chase. Only do this with a credential you do not mind leaking.
- **`fulldump` / `dump` write to disk in `work_dir`.** They do not stream — make sure the working directory has space.
- **`dnsadd` / `dnsmodify` / `dnsremove` take minutes to propagate.** AD replication, not OctoPwn — be patient before assuming the call failed.
- **Many commands take a DN and refuse anything else.** When in doubt, resolve with [`sam2dn`](#sam2dn) / [`sid2dn`](#sid2dn) first.
