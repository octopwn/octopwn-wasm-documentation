# Kerberoast Attack

The **Kerberoast** attack module performs both classic **SPN-roasting**
(MITRE ATT&CK [T1558.003](https://attack.mitre.org/techniques/T1558/003/)) **and**
**AS-REP roasting** (T1558.004) against Active Directory in a single run, against every
etype the KDC will issue (RC4, AES128, AES256). Hashes are stored in the
[Credentials Hub](../../user-guide/credentials.md) under credential type `KERBEROAST`,
ready to copy into Hashcat / John for offline cracking.

Both techniques exploit the same underlying property: any authenticated principal in a
realm can request a Kerberos ticket whose encrypted portion is sealed with the *target
account's* password-derived key. Crack the encrypted blob offline → recover the target
account's password.

| Sub-attack       | Targets                                          | Hashcat prefix    | Etypes generated                   |
| ---------------- | ------------------------------------------------ | ----------------- | ---------------------------------- |
| **SPN-roast**    | All users with a `servicePrincipalName` set      | `$krb5tgs$`       | RC4 (23), AES128 (17), AES256 (18) |
| **AS-REP roast** | All users with `DONT_REQ_PREAUTH` (UF) flag set  | `$krb5asrep$`     | RC4 (23), AES128 (17), AES256 (18) |

OctoPwn enumerates both candidate sets automatically from LDAP and runs the appropriate
roast against each user — you don't need to feed in lists of accounts.

---

## How it works

1. **LDAP enumeration.** OctoPwn opens an LDAP/LDAPS connection to `ldaptarget` (or
   `target` if `ldaptarget` is unset) using the supplied `credential`. Both NTLM and
   Kerberos binds are tried over both LDAP and LDAPS — whichever succeeds first wins.
2. **Two filters are applied:**
    - `(&(samAccountType=805306368)(servicePrincipalName=*))` — service users (SPN-roast
      candidates). The `krbtgt` account is explicitly excluded.
    - `(userAccountControl:1.2.840.113556.1.4.803:=4194304)` — `DONT_REQ_PREAUTH` users
      (AS-REP-roast candidates).
3. **For each candidate, OctoPwn issues a TGS-REQ (SPN-roast) or AS-REQ (AS-REP-roast)
   to the KDC** in `target`. For SPN-roast, the request is repeated with each of
   `etype=23,17,18` so you get the RC4 *and* the AES variants — useful when one is
   considered weak by your cracker, or when the KDC supports only a subset.
4. **Cross-domain support.** When `target` and `ldaptarget` are different (i.e. you
   enumerate from one DC but request tickets from another DC's KDC), the SPN-roast loop
   sets `cross_domain=True` so the TGS-REQ goes through the correct cross-realm path.
5. **WSNET browser path.** When the supplied `credential` has secret type `WSNET` (i.e.
   the credential is the wsnet-bridged identity of the user's *browser session*),
   OctoPwn switches to a different code path that asks the wsnet agent to acquire the
   tickets directly via the platform Kerberos API. This is the only way to roast from
   a logged-in domain user without exposing their password / NT hash to the framework.
6. **Hash storage.** Each captured hash is saved in the project's Credentials Hub with:
    - `secret = <full hashcat-format string>` (the `$krb5tgs$...` or `$krb5asrep$...`
      blob).
    - `stype = 'KERBEROAST'`.
    - `source = 'KERBEROAST-<session-id>'`, `description = 'KERBEROAST'`.
    - `username` / `domain` populated from the AD object.
   The exact ticket type (`kerberoast_rc4` / `kerberoast_aes128` / `kerberoast_aes256` /
   `asreproast_rc4` / …) is recorded as the result `ttype` so the
   [vulnerability engine](../../user-guide/credentials.md) can fire the right rules.

---

## Prerequisites

- A **valid domain credential** (any user — including a low-priv account or a
  WSNET-bridged interactive logon). No special privileges are required to issue
  TGS-REQs or AS-REQs.
- LDAP and Kerberos network access from the OctoPwn agent to the DC. If you need to
  proxy through wsnet, set `proxy`.
- For **AS-REP roast** to find anything, at least one user must have
  `DONT_REQ_PREAUTH` set on their account. This is uncommon by default but creeps in
  through legacy app onboarding mistakes — the scan is essentially free, so always run it.
- For **SPN-roast** to find anything, at least one user (not computer) account in the
  domain must have a `servicePrincipalName` set. Service accounts for legacy products
  (SQL Server with non-default service accounts, Exchange, custom IIS app pools, …) are
  the usual hits.

!!! tip "Pair with the krb5user scanner"
    The [`krb5user`](../scanners/krb5user.md) scanner discovers valid usernames against
    a KDC without needing credentials. If you have a username list but no password,
    feed those usernames into `krb5user`, and any user that comes back as
    `KDC_ERR_PREAUTH_REQUIRED` (i.e. they exist but require pre-auth) is **not** an
    AS-REP-roast candidate; the ones that come back with a ticket *are* — that hash is
    immediately roastable.

---

## Parameters

### Normal parameters

#### `target`
Target ID of the **KDC** that will be asked to issue tickets — typically a Domain
Controller in the realm you want to roast. Required.

#### `ldaptarget`
Target ID of the **DC used for LDAP enumeration**. Optional; defaults to `target` when
unset. Set this only for cross-realm operations where you want to enumerate
roastable accounts on one domain and request their tickets via another domain's
trust path.

#### `credential`
Credential ID of any **authenticated domain user**. Used for both the LDAP bind
(NTLM/Kerberos auto-detected) and as the requesting principal for the TGS-REQ /
AS-REQ Kerberos exchanges. A low-priv user is sufficient.

#### `proxy`
Proxy ID for the LDAP and Kerberos traffic. Required only when the OctoPwn agent
cannot reach the DC directly.

### Advanced parameters

The standard `ScannerBaseParameters` set: `maxruntime`, `resultsfile`, `showerrors`,
`timeout`, `workercount`, `wsnetreuse`. See the
[scanner parameters reference](../scanners/baseline.md) for descriptions; defaults are
fine for almost every Kerberoast run.

---

## Output

Each roastable user produces one result row per etype that the KDC actually issued:

```
ttype                user            domain          hashcatres
kerberoast_rc4       svc-sql         CORP.LOCAL      $krb5tgs$23$*svc-sql$CORP.LOCAL$...
kerberoast_aes128    svc-sql         CORP.LOCAL      $krb5tgs$17$*svc-sql$CORP.LOCAL$...
kerberoast_aes256    svc-sql         CORP.LOCAL      $krb5tgs$18$*svc-sql$CORP.LOCAL$...
asreproast_rc4       legacy-svc      CORP.LOCAL      $krb5asrep$23$legacy-svc@CORP.LOCAL:...
```

The full Hashcat-formatted blob is what gets stored in the Credentials Hub — copy it
straight into Hashcat:

```
hashcat -m 13100 spn.hashes wordlist.txt        # $krb5tgs$23 (RC4)
hashcat -m 19700 spn.hashes wordlist.txt        # $krb5tgs$17 (AES128)
hashcat -m 19600 spn.hashes wordlist.txt        # $krb5tgs$18 (AES256)
hashcat -m 18200 asrep.hashes wordlist.txt      # $krb5asrep$23 (RC4)
hashcat -m 31300 asrep.hashes wordlist.txt      # $krb5asrep$17 (AES128)
hashcat -m 33200 asrep.hashes wordlist.txt      # $krb5asrep$18 (AES256)
```

---

## See also

- [Kerberos client → kerberoast / asreproast](../clients/kerberos.md) — the same
  primitives one-account-at-a-time, useful when you want full control over the
  Kerberos exchange (custom etypes, specific SPNs, etc.).
- [`krb5user` scanner](../scanners/krb5user.md) — unauthenticated AS-REP-roastable
  user discovery.
- [LDAP client](../clients/ldap.md) — to manually enumerate `servicePrincipalName`
  users ([`spns`](../clients/ldap.md#spns)) or `DONT_REQ_PREAUTH` users
  ([`asrep`](../clients/ldap.md#asrep)) without triggering a roast yet.
