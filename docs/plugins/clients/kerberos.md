# Kerberos Client

The **Kerberos Client** is OctoPwn's interactive console for talking directly to a Domain Controller's KDC (port 88) using [`minikerberos`](https://github.com/skelsec/minikerberos). It bundles the day-to-day ticket-acquisition primitives (`tgt`, `tgs`) together with the offensive Kerberos toolkit you need on an Active Directory engagement: roasting (`kerberoast`, `asreproast`), constrained-delegation abuse (`s4uself`, `s4uproxy`), PKINIT-to-NT recovery (`nt`), the Badsuccessor / dMSA attack (`dmsa`), the CVE-2022-33679 keystream-guessing exploit, and a vanilla KPASSWD password change (`changepassword`).

Unlike most other clients, "logging in" here is essentially a no-op — the session just holds the credential and target you bound to it. The real network round-trip happens the first time you invoke a command. Most commands need a credential bound to the session; `asreproast` and `cve202233679` are the two notable exceptions (and even there, the latter still needs a session for *some* user, just one whose password is unknown).

!!! info "Every command persists its result to the Credentials Window"
    Successfully executed commands write a new credential into the Credentials Window so you can pivot directly into other modules. The `source` field is set to the producing command name, which makes the output trivial to filter and audit later.

    | Command           | Stored as              | Source tag       |
    | ----------------- | ---------------------- | ---------------- |
    | `tgt`             | `kirbib64`             | `tgt`            |
    | `tgs`             | `kirbib64` *(see [Limitations](#limitations-gotchas))* | `tgs`            |
    | `s4uself`         | `kirbib64`             | `s4uself`        |
    | `s4uproxy`        | `kirbib64`             | `s4uproxy`       |
    | `dmsa`            | `kirbib64` (+ `NT` / `AES128` / `AES256` for previous keys) | `dmsa`           |
    | `kerberoast`      | `KERBEROAST` ($krb5tgs hashcat string) | `kerberoast`     |
    | `asreproast`      | `ASREPROAST` ($krb5asrep hashcat string) | `asreproast`     |
    | `nt`              | `NT`                   | `nt`             |
    | `cve202233679`    | `kirbib64`             | `cve202233679`   |
    | `changepassword`  | `password`             | `changepassword` |

    `kirbib64` credentials produced by `tgt`, `s4uself`, `s4uproxy`, `dmsa` and `cve202233679` are immediately usable to authenticate other client sessions (SMB, LDAP, …) — pick auth protocol **Kerberos** and the kirbi credential. `tgs` is the exception, see below.

---

## Prerequisites

Kerberos is unforgiving about misconfiguration — getting the basics right up front saves a lot of head-scratching:

1. **Realm** — set the global realm on the main console (`realm <FQDN>`, e.g. `realm sevenkingdoms.local`). Used as the default domain for SPN parsing.
2. **DC IP** — the session's target must be the KDC. If you only have a hostname, set up a DNS resolver first.
3. **DNS resolver** — name resolution must reach the domain's DNS or you'll see `KDC_ERR_S_PRINCIPAL_UNKNOWN` on perfectly valid SPNs. See the [DNS Client](dns.md#wiring-it-up-as-the-global-resolver) page for how to wire one up as the global resolver.
4. **Time skew** — Kerberos rejects requests when client clock skew exceeds 5 minutes. If `tgt` fails with `KRB_AP_ERR_SKEW`, check the DC's time first — the [NTP Client](ntp.md) is the fastest way.
5. **Credential** — a credential bound to the session is required for everything except `asreproast` (target user(s) only) and `cve202233679` (any session, the credential's *user* needs `DONT_REQUIRE_PREAUTH`).

---

## Commands

The console groups its commands into five categories that map onto how you'll actually use them: ticket plumbing and the lone admin action (`BASIC`), offline-crackable hash extraction (`ROAST`), certificate-based recovery (`PKI`), named CVEs / exploits (`ATTACKS`), and the standalone Badsuccessor primitive (`DMSA`).

### BASIC

#### tgt
Requests a TGT for the credential bound to this session and prints it as a base64-encoded kirbi. The ticket is also persisted as a `kirbib64` credential, so you can immediately use it as the credential for an SMB / LDAP / WinRM / … session.

The encryption type is negotiated automatically — by default the client offers `23,17,18` (RC4-HMAC, AES128, AES256) and the KDC picks the strongest mutually supported one. Override with `etype` if you need to coerce a specific encryption type, e.g. when probing for `KDC_ERR_ETYPE_NOTSUPP`.

##### Parameters
- **etype** *(optional)*: A single Kerberos encryption type number to force. Common values: `23` (RC4-HMAC), `17` (AES128-CTS-HMAC-SHA1-96), `18` (AES256-CTS-HMAC-SHA1-96). When omitted, the client offers all three.

!!! tip "Using the kirbi outside OctoPwn"
    If you want to feed the ticket to an Impacket-flavoured tool, convert it with the [`minikerberos-kirbi2ccache`](https://github.com/skelsec/minikerberos) helper — feed it the base64 kirbi printed to the console.

#### tgs
Requests a service ticket (TGS) for a given SPN. Prints the kirbi to the console and stores it as a `kirbib64` credential.

##### Parameters
- **spn**: The target SPN. Two forms are accepted:
    - SPN form: `service/host@domain`, e.g. `cifs/dc01.sevenkingdoms.local@sevenkingdoms.local` or `mssql/srv-sql01@sevenkingdoms.local`. Use the LDAP client's [`machine`](ldap.md) command and inspect the `servicePrincipalName` attribute to find valid SPNs.
    - User form: `user@domain` — useful when you want to roast a specific service account by name without first looking up its SPN.

!!! warning "TGS credentials are not yet usable for authentication"
    Unlike a `tgt`, the kirbi produced by `tgs` is stored in the Credentials Window for inspection / export but **OctoPwn cannot currently consume it as the credential of another session** — that wiring is on the to-do list. For now, export the kirbi and feed it to an external tool. Use `tgt` if you need a Kerberos credential to authenticate further sessions inside OctoPwn.

#### s4uself
S4U2self lets a service request a Kerberos service ticket *to itself, on behalf of any user*, without that user ever being involved. Combined with constrained delegation it's the canonical primitive for impersonating a high-value user; on its own it's also enough to turn a captured **machine-account TGT** into a usable shell on that machine.

The classic operator scenario: you obtained a TGT for a machine account `WKSTN-2$` (e.g. via unconstrained delegation coercion). A machine account can't remote-admin itself directly, but it *can* ask the KDC for a forwardable ticket "to itself, as Domain Admin" via S4U2self — and the resulting ticket lets you authenticate to that machine as Domain Admin. Same trick works against any host whose machine TGT you can lay hands on.

##### Parameters
- **targetuser**: The user to impersonate, in `user@domain` form, e.g. `Administrator@sevenkingdoms.local`. The session credential is the *service* asking; this parameter is the *user* it's pretending to act for.

#### s4uproxy
S4U2proxy is the second half of constrained-delegation abuse: given a forwardable service ticket obtained via S4U2self, request access to a *different* service on behalf of the same user. The session credential must own a service account that's been configured with constrained delegation (the SPNs it can delegate to live in `msDS-AllowedToDelegateTo` — the LDAP client's `unconstrained` / `constrained` / `s4u2proxy` analysis commands will surface them).

Typical chain: `s4uself <targetuser>` to grab the forwardable ticket → `s4uproxy <downstream-spn> <targetuser>` to pivot onto the downstream service as that user. The result is a usable kirbi credential for the downstream SPN.

##### Parameters
- **spn**: The downstream service SPN you want to access, in `service/host@domain` form (e.g. `cifs/file01.sevenkingdoms.local@sevenkingdoms.local`).
- **targetuser**: The user being impersonated, in `user@domain` form (e.g. `Administrator@sevenkingdoms.local`).

!!! warning "SPN format matters"
    A `not enough values to unpack` exception almost always means the SPN was passed in the wrong form. The downstream SPN must be `service/host@domain`; passing a bare `user@domain` here will fail.

#### changepassword
Performs a Kerberos **KPASSWD** password change for the current session's user. On success, the new password is persisted as a fresh `password` credential (so you don't lose access to the account if you needed the old credential for something else first).

##### Parameters
- **newpassword**: The new password to set.
- **hostname** *(optional)*: Override the KPASSWD server hostname. Leave empty to let `minikerberos` pick the KDC of the session target — usually correct.

---

### ROAST

#### kerberoast
Performs the **Kerberoasting** attack — request TGS tickets for one or more service accounts and print them as `$krb5tgs$…` hashcat strings ready for offline cracking. Every result is also added to the Credentials Window with type `KERBEROAST`.

The command accepts three input modes that each unlock a different workflow:

- **Single user** (`spn` is a `samAccountName@domain` string, e.g. `mssqlsvc@sevenkingdoms.local`) — roast exactly that account using the credential bound to the session.
- **LDAP session ID** (`spn` is an integer matching an active LDAP/LDAPS client session) — the LDAP client is queried for *every* service account (via `get_all_service_users`) and they're all roasted in one pass. This is the usual way to run a domain-wide kerberoast.
- **No credential bound to the session** — the request is delegated to the local Kerberos stack: SSPI on a Windows native build, or wsnet's auth bridge in the browser. Useful when you have an interactive Windows session but no separately stored credential.

Vulnengine integration is automatic: every roastable account is also fed through `check_vulnerability` so the run shows up in the Vulnerabilities view.

##### Parameters
- **spn**: Either `samAccountName@domain`, or the session ID (integer) of an active LDAP client.
- **crossdomain** *(optional)*: Set to `True` if the target service account lives in a different domain than your session credential — the client will fetch a referral ticket first. Default `False`.
- **etype_tgt** *(optional)*: Encryption types to offer when requesting the TGT. Default `23,17,18`.
- **etype_tgs** *(optional)*: Encryption type to request for the resulting TGS. Default **`23`** (RC4-HMAC) — the form most service accounts will issue and the easiest to crack offline. Set to `17` or `18` if RC4 is disabled in the domain.

#### asreproast
Performs the **AS-REP Roasting** attack — for any user with `DONT_REQUIRE_PREAUTH` set on their `userAccountControl`, the KDC will hand out an AS-REP message encrypted with a key derived from the user's password, with no pre-auth challenge first. Crackable offline as `$krb5asrep$…`.

No credential is required to run this attack — the session just needs a target (the KDC). The same two input modes as `kerberoast` apply:

- **Single user**: pass `samAccountName@domain`.
- **LDAP session ID**: pass an integer; the LDAP client enumerates every user with `DONT_REQUIRE_PREAUTH` set (via `get_all_knoreq_users`) and all are roasted in one pass.

##### Parameters
- **user**: Either `samAccountName@domain`, or the session ID (integer) of an active LDAP client for a domain-wide sweep.

---

### PKI

#### nt
Recovers the NT hash of the current session's user from the PAC of a PKINIT-issued TGT — the standard "UnPAC-the-Hash" trick. Only works when the session was created with a **certificate-based credential** (auth protocol `P12`); for any other credential type you'll get `'AIOKerberosClient' object has no attribute 'get_NT_from_PAC'`.

This is the obvious follow-up to AD CS abuse (ESC1 / ESC8 / Certifried / …) — once you've forged or coerced a certificate for a user, `nt` turns it into the user's actual NT hash, which is far more flexible (Kerberos pre-auth, NTLM, pass-the-hash to non-AD services, …).

##### Parameters
None — operates on the session's bound credential.

---

### ATTACKS

#### cve202233679
Performs the **CVE-2022-33679** Kerberos exploit — abuses RC4-MD4 keystream reuse against an account with `DONT_REQUIRE_PREAUTH` to recover a *usable* TGT for that account, no password required.

This command takes **no arguments**. It runs against the credential bound to the current session — that credential must reference a user with `DONT_REQUIRE_PREAUTH` set, but you don't need to know their password. Create the Kerberos client session using just the username (any AS-REP-roastable user will do), then run `cve202233679`. The resulting TGT is printed as a kirbi and persisted as a credential, ready to use for further authentication.

The implementation guesses one byte of the RC4-MD4 keystream at a time by replaying crafted AS-REQs and checking which guess avoids the `KDC_ERR_PREAUTH_FAILED` response. It chats a lot — the console prints each step (`FETCHING TGT`, `PARTIAL KEYSTREAM`, `VERIFYING KEYSTREAM`, byte-by-byte progress) so you can follow along.

##### Parameters
None — uses the session's bound credential.

---

### DMSA

#### dmsa
Performs the **Badsuccessor** attack against a delegated Managed Service Account (dMSA). The session credential is used to request a service ticket via the dMSA migration path, which yields a valid kirbi for `targetuser`. When `linkeduser` is supplied, the previous-key material embedded in the response (RC4 / AES128 / AES256) is also unpacked and persisted as separate `NT` / `AES128` / `AES256` credentials for that user — typically the high-value account whose keys you're after.

This command is the **Kerberos-side step** of the attack. The discovery and weaponisation happen in the LDAP client first — `badsuccessor_check` to find an exploitable dMSA in the domain, `dmsas` to list them, `create_broken_dmsa_user` / `dmsaaddmanagedaccountprecededbylink` / `dmsasetdelegatedmsastate` to set one up. Run those first, then come back here with the resulting target / linked user.

##### Parameters
- **targetuser**: The dMSA principal to ticket, in `user@domain` form.
- **linkeduser**: The user whose previous-key material should be unpacked, in `user@domain` form. Optional but practically required — without it you only get a TGS, not the hashes you came for.

---

## Limitations & gotchas

- **TGS credentials cannot yet be used for authentication inside OctoPwn.** `tgs` produces and persists a kirbi, but other client sessions can't currently consume it as their credential. Use `tgt` for in-framework re-authentication; export the `tgs` kirbi (and convert with `minikerberos-kirbi2ccache` if needed) for use with external tooling. This is a known to-do.
- **Some commands have no SSPI / WSNET fallback.** `tgt`, `tgs`, `s4uself`, `s4uproxy`, `nt`, `dmsa`, `changepassword` all require a credential explicitly bound to the session — they won't fall back to the operating system's Kerberos stack.
- **Cross-domain roasting needs a TGT-capable credential.** `kerberoast crossdomain=True` requests a referral ticket via your session's TGT, so the SSPI / WSNET (no-credential) path doesn't support it.
- **`nt` requires a P12 (certificate) credential.** Other credential types will throw `'AIOKerberosClient' object has no attribute 'get_NT_from_PAC'`.
- **`cve202233679` is loud and slow.** It issues hundreds of AS-REQs to recover keystream bytes; expect noticeable noise in DC logs. Not a stealth tool.
