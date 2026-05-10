# Constrained Delegation Attack

The **CONSTRAINEDDELEG** attack is OctoPwn's helper for the
**S4U2Self → S4U2Proxy** Kerberos chain. Given a credential whose account
already has Kerberos *Constrained Delegation* configured (i.e.
`msDS-AllowedToDelegateTo` is populated for the account), it requests a
service ticket to one of the configured SPNs **as any chosen user** — no
machine creation, no LDAP writes, no cleanup.

This is the **post-discovery** module: use it once you have the credential of
a service account that has been granted constrained-delegation rights to
something interesting (typically discovered via the [LDAP
client](../clients/ldap.md)'s constrained-delegation enumeration). For the
flip side — abusing *write* access on a delegation attribute — that's the
[`RBCD`](rbcd.md) attack (resource-based) or manual S4U via the LDAP /
Kerberos clients (classic constrained delegation).

---

## How it works

1. **LDAP session** is opened against `dctarget` using `credential` (NTLM,
   hidden) and logged in. The LDAP session is used only to resolve the
   credential's domain (so OctoPwn can build canonical
   `<user>@<domain>` and `<spn>@<domain>` strings).
2. **Domain consistency.** If the supplied credential lacks an explicit
   `domain` field, OctoPwn clones the credential, sets the domain from the
   LDAP context, stores the clone in the
   [Credentials Hub](../../user-guide/credentials.md), and uses that for the
   subsequent Kerberos step. The original credential is left untouched.
3. **Open Kerberos session** as the (clean) credential.
4. **`s4uproxy(targetspn, targetuser)`** is called on the Kerberos session.
   This performs the full chain in one go:
    - **S4U2Self**: the source account asks the KDC for a TGS to *itself*
      *as `targetuser`*. Returns a forwardable service ticket whose client
      identity is `targetuser`.
    - **S4U2Proxy**: the source account presents that ticket back to the
      KDC and asks for a TGS to `targetspn` *on behalf of* `targetuser`.
      The KDC checks `msDS-AllowedToDelegateTo` on the source account. If
      it includes `targetspn`, the KDC issues the requested TGS.
   The resulting service ticket is stored as a Kerberos credential in the
   project (a `.kirbi` blob, immediately usable).
5. **Cleanup** is just an LDAP logout — no AD writes happened, so there's
   nothing to restore.

---

## Prerequisites

- A **valid credential for the source account** — i.e. the account that has
  `msDS-AllowedToDelegateTo` configured. Typically a service account
  whose password / NT hash you obtained via Kerberoast / DCSync / coercion
  / phishing / *etc.*
- The source account must have:
    - `TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION` (TrustedToAuthForDelegation,
      `userAccountControl` bit `0x1000000`) set, **and**
    - `msDS-AllowedToDelegateTo` containing the SPN you want to abuse,
    or — for "Constrained Delegation **without** protocol transition" —
    `TRUSTED_TO_DELEGATE` (`0x80000`) **and** an existing forwardable TGS
    you obtained some other way (rare in practice; the protocol-transition
    flag is the common case).
- **`targetuser` must be delegate-able.** Same constraint as
  [`RBCD`](rbcd.md): members of `Protected Users`, accounts with
  `Account is sensitive and cannot be delegated` set, and AdminSDHolder
  accounts will return `KDC_ERR_POLICY` from S4U2Self.
- **Network access**: `389/636/TCP` to `dctarget`, `88/UDP+TCP` for
  Kerberos.

---

## Discovering candidate accounts

Before running this attack, find accounts in the domain that have constrained
delegation configured:

```
# In the LDAP client, enumerate accounts with non-empty msDS-AllowedToDelegateTo.
ldap> deluser  <-- (no — that's "delete user")
ldap> getalldelegations
```

Look for accounts where the SPNs in `msDS-AllowedToDelegateTo` include
something high-value (`CIFS/<DC>` is the classic jackpot — gives you SMB on
the DC as any user). Service accounts for legacy products (SCCM, MSSQL,
Exchange, custom IIS app pools) are the typical hits.

Once you have a service account credential, use its `cid` here and use the
discovered `targetspn` value verbatim.

---

## Parameters

### Normal parameters

#### `dctarget`
Target ID of the Domain Controller (LDAP, Kerberos KDC). Required.

#### `credential`
Credential ID of the **source account** — i.e. the account whose
constrained-delegation rights you are exercising. This is *not* the target;
it's the principal that's allowed to delegate.

#### `targetuser`
The `sAMAccountName` (or UPN) of the user to impersonate. If a UPN, used
as-is; if a bare name, OctoPwn appends `@<dctarget's domain>`. Required.

#### `targetspn`
The SPN to request the service ticket for. Must be **one of the SPNs
configured in `msDS-AllowedToDelegateTo` on the source account**.
Standard SPN syntax (`<service>/<host>` or
`<service>/<host>@<domain>`). Required.

### Advanced parameters

The standard `ScannerBaseParameters` set: `maxruntime`, `resultsfile`,
`showerrors`, `timeout`, `workercount`, `wsnetreuse`, plus `proxy` from
`CredentialedScanParameters`.

---

## Output

```
targetuser           targetspn               success
Administrator        CIFS/winterfell         True
```

Plus a stored Kerberos credential — the actual service ticket. Use it via
the [SMB / LDAP / WinRM / MSSQL clients](../clients/smb.md) by selecting the
new Kerberos cred from the Hub.

---

## When this differs from RBCD

- **CONSTRAINEDDELEG** uses **classic constrained delegation** — the source
  account has been *pre-configured* by an administrator (or by the operator
  via a previous LDAP write) to delegate to specific SPNs. No AD writes
  happen during the attack itself.
- **[RBCD](rbcd.md)** uses **resource-based constrained delegation** —
  the operator *creates* the delegation right by writing to the *target's*
  `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute on the fly, then
  tears it down. Requires write rights on the target machine object.

If you have:

- A **service account credential with constrained delegation already
  configured** → use this attack.
- A **write on a target machine object's ACL** (typically via successful
  RELAYLDAP) → use [`RBCD`](rbcd.md).

---

## Limitations and caveats

- **Protected Users / sensitive accounts.** Same as RBCD — pick a
  delegate-able target. `KDC_ERR_POLICY` from S4U2Self means the target
  user is protected.
- **Wrong SPN.** S4U2Proxy will return `KDC_ERR_BADOPTION` if the
  `targetspn` you're requesting isn't in the source account's
  `msDS-AllowedToDelegateTo`. Double-check via LDAP enumeration.
- **No `_self` workflows here.** This module exposes only the chained
  S4U2Self+S4U2Proxy flow. If you want raw S4U2Self (impersonation against
  the source account itself, useful for the "S4U2Self only" abuse path
  on accounts with `TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION`), call
  [`s4uself`](../clients/kerberos.md#s4uself) directly on the
  Kerberos client.
- **No cross-realm.** This module assumes single-domain operation. For
  cross-realm constrained-delegation abuse, drive the
  [Kerberos client](../clients/kerberos.md) manually with the appropriate
  realm flags.
- **Audit signature.** S4U2Self is logged on the KDC as event `4769` with
  the `msDS-AllowedToDelegateTo` audit context; large numbers of S4U2Self
  events from a single source against many users / SPNs are a known IoC.

---

## See also

- [LDAP client](../clients/ldap.md) — for enumerating accounts with
  constrained delegation configured.
- [Kerberos client → `s4uproxy`](../clients/kerberos.md#s4uproxy) /
  [`s4uself`](../clients/kerberos.md#s4uself) — the underlying Kerberos
  primitives, useful when you need full control over flags / realms.
- [`RBCD`](rbcd.md) — *resource-based* constrained delegation (creates the
  delegation right on demand).
- [`KERBEROAST`](kerberoast.md) — most common way to *obtain* the
  source-account credential needed for this attack.
- [The Hacker Recipes: Unconstrained / Constrained / RBCD](https://www.thehacker.recipes/a-d/movement/kerberos/delegations)
  — canonical Kerberos delegation reference.
