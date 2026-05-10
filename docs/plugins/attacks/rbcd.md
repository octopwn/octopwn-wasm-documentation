# RBCD Attack

The **RBCD** (Resource-Based Constrained Delegation) attack abuses the
`msDS-AllowedToActOnBehalfOfOtherIdentity` attribute on a target machine
account to **make any user authenticate to that machine as any other user**,
including Domain Admins. The classic Elad Shamir
[Wagging the Dog](https://shenaniganslabs.io/2019/01/28/Wagging-the-Dog.html)
chain, fully automated.

In a single run, OctoPwn:

1. Creates a fresh machine account (`MachineAccountQuota` lets any domain user
   create up to 10 by default).
2. Sets `msDS-AllowedToActOnBehalfOfOtherIdentity` on the target machine,
   listing the new machine account's SID as allowed to delegate.
3. Performs S4U2Self + S4U2Proxy as the new machine to obtain a service ticket
   for the target machine **as `targetuser`** (e.g. `Administrator`).
4. Restores the target machine's original security descriptor and **deletes the
   newly created machine account**.

End result: a service ticket usable to access the target machine as any
delegate-able domain user, with the cleanup handled.

---

## How it works

1. **LDAP session.** Open a hidden LDAP session against `dctarget` using
   `credential` (NTLM). Login.
2. **Create a controlled machine account.**
   [`computeradd`](../clients/ldap.md#computeradd) is called with a randomly
   named machine (`TEST-<8 hex chars>$`). The new account is automatically
   added to the [Credentials Hub](../../user-guide/credentials.md) with its
   freshly minted password. The result includes:
    - `cid` — credential ID of the new machine account.
    - `sAMAccountName` — `TEST-...$`.
    - `distinguishedName` — full DN, kept for cleanup.
    - `objectSid` — the new machine's SID, used in step 4.
3. **Resolve the target machine's DN.**
   [`sam2dn`](../clients/ldap.md#sam2dn) is tried with both `<targetmachine>`
   and `<targetmachine>$` so you don't have to remember whether your input
   includes the trailing `$`.
4. **Write `msDS-AllowedToActOnBehalfOfOtherIdentity`** on the target machine
   via [`addallowedtoactonbehalfofotheridentity`](../clients/ldap.md#addallowedtoactonbehalfofotheridentity).
   The original security descriptor is captured so it can be restored in the
   `finally`.
5. **Open Kerberos session** as the new machine account (using `cid` from
   step 2). This session is also hidden.
6. **S4U2Proxy.** [`s4uproxy`](../clients/kerberos.md#s4uproxy) is called with
   `(targetspn, targetuser)`. Internally this performs the
   S4U2Self → S4U2Proxy chain — the new machine account asks the KDC to
   issue itself a TGS for `targetuser` to `targetuser` (S4U2Self), then
   exchanges that for a TGS to `targetspn` on behalf of `targetuser`
   (S4U2Proxy). The resulting service ticket is stored in the project as
   a Kerberos credential.
7. **Cleanup (always runs in `finally`).**
    - Restore the original `msDS-AllowedToActOnBehalfOfOtherIdentity` value
      on the target machine via
      [`restoreallowedtoactonbehalfofotheridentity`](../clients/ldap.md).
    - [`deluser`](../clients/ldap.md#deluser) on the new machine account's
      DN — the controlled computer object is removed from AD.
    - LDAP session logout.

The service ticket from step 6 is what you actually use post-attack: it grants
the holder access to `targetspn` on `targetmachine` as `targetuser`. Common
follow-ups:

- `targetspn = CIFS/<targetmachine>` → SMB session as
  `<targetuser>` against `<targetmachine>` (default if you leave `targetspn`
  empty).
- `targetspn = HOST/<targetmachine>` → general SPN for SMB / RPC / WinRM.
- `targetspn = HTTP/<targetmachine>` → WinRM / HTTP-based services.
- `targetspn = LDAP/<dc>` → LDAP as `<targetuser>` against the DC.

---

## Prerequisites

- A **valid domain credential** that can:
    - Create new machine accounts (i.e. `MachineAccountQuota > 0` for that
      account, default `10`). If `MachineAccountQuota = 0`, RBCD via this
      module fails at step 2; you must instead obtain or generate a
      pre-existing machine account credential via another path.
    - **Write `msDS-AllowedToActOnBehalfOfOtherIdentity` on the target
      machine.** This is the actual primitive RBCD abuses. Common ways to
      have this:
        - The credential is `Domain Admins` (trivial).
        - The credential / one of its groups has `WriteProperty` on the
          machine object via a misconfigured ACL (the standard RBCD scenario
          — typically delivered via a successful
          [`RELAYLDAP`](../servers/relayldap.md) into the target machine
          object's ACL).
        - The credential **is** the machine — i.e. you have NTDS / a captured
          machine secret.
- **`targetuser` must be delegate-able.** Members of `Protected Users`,
  accounts with `Account is sensitive and cannot be delegated` set, and
  accounts in the AdminSDHolder-protected groups under modern hardening will
  cause S4U2Proxy to return `KDC_ERR_BADOPTION` /
  `KRB_AP_ERR_BAD_INTEGRITY` / `KDC_ERR_POLICY`. Many production environments
  have *some* protected accounts but lots of unprotected ones; pick a
  delegate-able target user.
- **Outbound `389/636/TCP`** to `dctarget` (LDAP) and **`88/UDP+TCP`** for the
  Kerberos exchange.
- **The target machine must be reachable** at the protocol implied by
  `targetspn`. RBCD only gets you a valid ticket; you still need network
  access to use it.

---

## Parameters

### Normal parameters

#### `dctarget`
Target ID of the Domain Controller (LDAP). Required.

#### `credential`
Credential ID for the LDAP bind and as the creator of the new machine
account.

#### `targetmachine`
The `sAMAccountName` of the **machine you want to take over**, with or
without the trailing `$`. Required.

#### `targetuser`
The `sAMAccountName` of the **user to impersonate** (typically
`Administrator` or another delegate-able privileged account). Can be a UPN
(`user@domain`); if not, OctoPwn appends `@<dctarget's domain>`. Required.

#### `targetspn`
The SPN to request the service ticket for. If empty, defaults to
`CIFS/<targetmachine>` (i.e. SMB on the target machine). Set explicitly to
go after a non-SMB service:

```
CIFS/winterfell      # SMB on winterfell — default
HOST/winterfell      # generic host services
HTTP/winterfell      # WinRM / HTTP
LDAP/dc01            # LDAP — useful for cross-machine pivots
```

### Advanced parameters

The standard `ScannerBaseParameters` set: `maxruntime`, `resultsfile`,
`showerrors`, `timeout`, `workercount`, `wsnetreuse`, plus `proxy` from
`CredentialedScanParameters`.

---

## Output

```
targetuser           targetmachine    targetspn               computersam        success
Administrator        kingslanding     CIFS/kingslanding       TEST-a1b2c3d4$     True
```

Plus a stored Kerberos credential (the service ticket itself), and the
session-window log of every step (machine creation, DN resolution, ACL write,
Kerberos exchange, cleanup).

---

## Limitations and caveats

- **Cleanup matters.** The new machine account *and* the original SD on the
  target machine are restored / deleted in the `finally`, but if the LDAP
  session dies between the modify and the cleanup (rare), you'll leave a
  rogue machine account in AD and a writable
  `msDS-AllowedToActOnBehalfOfOtherIdentity` on the target. Always check the
  session window's tail for `Machine account removed successfully` and
  `Original SD restored`. If absent, clean up manually with the LDAP
  client.
- **`MachineAccountQuota` matters.** Many environments now set this to `0` to
  prevent exactly this attack. If creation fails with
  `LDAP_INSUFFICIENT_RIGHTS` / `STATUS_DS_USER_TOO_MANY_OBJECTS_IN_GROUP`,
  you'll need an existing machine account credential — at which point you
  can drive the underlying primitives manually via the
  [LDAP client](../clients/ldap.md) and
  [Kerberos client](../clients/kerberos.md).
- **Protected Users / sensitive accounts.** Pick a delegate-able target
  user. The error is informative but not always obvious — if S4U2Proxy
  fails with `KDC_ERR_POLICY`, the target user is protected.
- **Audit signature.** Two distinct events are likely to be logged:
  - `4741` (computer account created), then `4743` (computer account
    deleted) — within seconds of each other.
  - `4738` / `5136` on the target machine object (security-descriptor
    change), again with the inverse change shortly after.
  Mature SOCs catch this RBCD signature easily; this attack is fast,
  not subtle.
- **Multi-DC race.** AD replication can mean the LDAP write hits one DC and
  the S4U exchange hits another that hasn't replicated yet. If the attack
  fails immediately after the SD write with `KDC_ERR_BAD_INTEGRITY`, give
  it a minute and re-run, or pin both LDAP and Kerberos to the same DC.

---

## See also

- [LDAP client](../clients/ldap.md) — for manual RBCD work (the
  [`addallowedtoactonbehalfofotheridentity`](../clients/ldap.md#addallowedtoactonbehalfofotheridentity)
  /
  [`computeradd`](../clients/ldap.md#computeradd) /
  [`s4u2proxy`](../clients/ldap.md#s4u2proxy) commands).
- [Kerberos client → `s4uproxy`](../clients/kerberos.md#s4uproxy) — the
  underlying S4U primitive.
- [`SHADOWCREDS`](shadowcreds.md) — alternative way to take over a target
  user account when you have write rights on the user's object instead of
  on a machine.
- [`RELAYLDAP`](../servers/relayldap.md) — the most common way to *acquire*
  the necessary write access on a machine object before running RBCD.
- [Wagging the Dog (Elad Shamir)](https://shenaniganslabs.io/2019/01/28/Wagging-the-Dog.html)
  — the canonical RBCD reference.
