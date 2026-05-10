# Shadow Credentials Attack

The **Shadow Credentials** attack (Elad Shamir's
["Shadow Credentials"](https://posts.specterops.io/shadow-credentials-abusing-key-trust-account-mapping-for-takeover-8ee1a53566ec))
abuses **write access on a target user / computer object's
`msDS-KeyCredentialLink` attribute** to plant a forged WHfB-style key
credential, then uses **PKINIT** to obtain a TGT for the target — and finally
[**UnPAC the Hash**](https://www.thehacker.recipes/a-d/movement/kerberos/unpac-the-hash)
to recover the target's NT hash.

In a single OctoPwn run, this:

1. Generates a fresh self-signed certificate + RSA key.
2. Embeds the public key in a `KeyCredential` blob and **appends it to**
   (not replaces) the target object's `msDS-KeyCredentialLink` — capturing
   the original value first.
3. Uses the PFX (cert + private key) to do **PKINIT** as the target.
4. Calls `nt` on the resulting Kerberos session to UnPAC the target's
   **NT hash** out of the TGT's `PAC_CREDENTIAL_INFO`.
5. Restores the original `msDS-KeyCredentialLink` value, no matter what.

The recovered NT hash is stored in the
[Credentials Hub](../../user-guide/credentials.md) and is immediately usable
for pass-the-hash, Kerberoast, *etc.* — and the target's normal authentication
keeps working because their existing keys / WHfB devices were preserved.

---

## How it works

1. **LDAP session** is opened against `dctarget` using `credential` (NTLM,
   hidden) and logged in.
2. **`shadowcred(targetuser)`** is called on the LDAP session, which under
   the hood:
    - Generates a fresh RSA key + self-signed X.509 cert in OctoPwn.
    - Builds a `KeyCredential` (Microsoft KEYCREDENTIALLINK_BLOB) wrapping
      that public key, with a fresh `DeviceID` GUID.
    - Reads the target user's current `msDS-KeyCredentialLink` value and
      stashes it in `original_certs`.
    - Writes back the original list **plus the new entry**.
    - Stores the matching PFX (cert + private key) as a project credential
      and returns its `cid` along with `original_certs` and the `target_dn`.
   The new PFX cred shows up in the Credentials Hub immediately.
3. **Open Kerberos session** as the target user, using the new PFX. Because
   the credential is a PFX, the Kerberos session does **PKINIT** to get a
   TGT — the KDC validates the certificate against the published key
   credential we just planted and hands over a TGT for the target.
4. **`nt` on the Kerberos session** (`do_nt`). This issues an additional
   AS-REQ / TGS-REQ flow that requests the
   `KERB-PA-PAC-OPTIONS` containing `PAC_CREDENTIAL_INFO` — the recovered
   NT hash is decrypted out of the response and stored as a
   project credential. This is the **UnPAC the Hash** primitive.
5. **Cleanup** runs in `finally`:
    [`setkeycredentiallink`](../clients/ldap.md#setkeycredentiallink) is
    called on `target_dn` with `original_certs` — restoring the attribute to
    its pre-attack value (preserving any legitimate WHfB devices the target
    had).

End result: a new NT-hash credential in the Hub, no permanent change on the
target object.

---

## Prerequisites

- A **valid domain credential** with **write access on the target object's
  `msDS-KeyCredentialLink` attribute**. Standard ways to have this:
    - The credential is `Domain Admins` (trivial).
    - The credential / one of its groups has `WriteProperty` on the
      target object via a misconfigured ACL — typical scenario after a
      successful [`RELAYLDAP`](../servers/relayldap.md) into the
      target's ACL.
    - The credential **is** the target's owner (`WriteOwner` is enough to
      grant yourself the write).
- **The forest functional level must be ≥ 2016** for `msDS-KeyCredentialLink`
  to exist as an attribute. On forests stuck at 2012-R2 / older, the
  attribute is absent and the LDAP write fails with
  `NO_SUCH_ATTRIBUTE`. There is no workaround in that case.
- **At least one DC must support PKINIT** (every DC since 2008 does, by
  default, unless the operator explicitly disabled it).
- **The target must not be in `Protected Users`** for the PKINIT TGT to be
  usable for UnPAC (Protected Users disables PAC_CREDENTIAL_INFO). If you
  see the TGT come back fine but `nt` fails with "no PAC_CREDENTIAL_INFO" —
  that's the cause.
- **Outbound `389/636/TCP`** to `dctarget` (LDAP) and **`88/UDP+TCP`** for
  PKINIT.

---

## Parameters

### Normal parameters

#### `dctarget`
Target ID of the Domain Controller (LDAP). Required.

#### `credential`
Credential ID for the LDAP bind. Must hold write rights on the target's
`msDS-KeyCredentialLink`.

#### `targetuser`
The `sAMAccountName` of the **user (or computer) to take over**. Required.
You can target either user or computer accounts — the attack works the same
way; computer takeovers are useful for getting a machine's NT hash without
touching the local SAM.

### Advanced parameters

The standard `ScannerBaseParameters` set: `maxruntime`, `resultsfile`,
`showerrors`, `timeout`, `workercount`, `wsnetreuse`, plus `proxy` from
`CredentialedScanParameters`. Defaults are fine.

---

## Output

```
targetuser           cids        success
stannis.baratheon    [47, 48]    True
```

Where `cids` is the list of newly-stored credential IDs:

- One PFX credential (the cert + key OctoPwn generated for PKINIT).
- One **NT-hash** credential for the target user (the actual loot — used
  for everything you'd normally do with NT-hash material: pass-the-hash,
  Kerberoast, RBCD, *etc.*).

---

## Why prefer ShadowCreds over RBCD or DCSync?

| Attack             | Required write target                      | Output                       | Cleanup automatic? | Detection profile                           |
| ------------------ | ------------------------------------------ | ---------------------------- | ------------------ | ------------------------------------------- |
| **ShadowCreds**    | `msDS-KeyCredentialLink` on **target user** | NT hash of target            | Yes (restore)      | LDAP write event + PKINIT login event       |
| [`RBCD`](rbcd.md)  | `msDS-AllowedToActOnBehalfOfOtherIdentity` on **target machine** | TGS for target user against target machine | Yes (restore + delete machine) | Computer creation/deletion + LDAP write     |
| [`DCSYNC`](dcsync.md) | DCSync rights on the **domain**         | NT / AES / DPAPI keys for **every** account | N/A (read-only)  | Distinctive 4662 + replication RPC pattern |

ShadowCreds is the cleanest "I have a write on this specific user/computer
object" primitive — no machine creation, no SD juggling, just one attribute
write that's restored at the end.

---

## Limitations and caveats

- **The 1-minute LDAP-replication race.** If the LDAP write hits DC-A but
  the PKINIT exchange hits DC-B that hasn't replicated yet, PKINIT fails
  with `KDC_ERR_CLIENT_NAME_MISMATCH` or `KDC_ERR_PADATA_TYPE_NOSUPP`.
  Pin both to the same DC, or wait a minute and retry.
- **Restore can fail silently.** Same caveat as
  [`ESC4`](esc4.md#how-it-works): if the LDAP session dies between the
  modify and the finally, the restore won't run and you'll leave a planted
  `msDS-KeyCredentialLink` entry on the target. Always check the session
  log for `Original certificates restored successfully`. If absent, manually
  call [`setkeycredentiallink`](../clients/ldap.md#setkeycredentiallink) to
  restore.
- **Some forests reject PKINIT for service accounts** with `userAccountControl`
  flag `DONT_REQUIRE_PREAUTH` set. Edge case, easy to spot from the error
  message.
- **Audit signature.** A `5136` event on the target object will record the
  `msDS-KeyCredentialLink` change, then a second `5136` records the
  restore — within seconds of each other. Mature SOCs treat this as a
  ShadowCreds signature.
- **Cannot defeat Protected Users.** If the target is in `Protected Users`,
  the `nt` (UnPAC) step fails — but the PKINIT login itself still works
  (the PFX credential is left in the Hub for downstream use).

---

## See also

- [LDAP client → `shadowcred`](../clients/ldap.md#shadowcred) — the
  attribute-write primitive, callable directly for manual workflows.
- [LDAP client → `setkeycredentiallink`](../clients/ldap.md#setkeycredentiallink)
  — manual restore / fully custom KeyCredentialLink management.
- [Kerberos client → `nt`](../clients/kerberos.md#nt) — the UnPAC-the-Hash
  primitive used internally.
- [`RBCD`](rbcd.md) — alternative takeover when you have write rights on a
  *machine* object.
- [`RELAYLDAP`](../servers/relayldap.md) — the most common way to *acquire*
  the necessary write rights on a target object.
- [SpecterOps: Shadow Credentials](https://posts.specterops.io/shadow-credentials-abusing-key-trust-account-mapping-for-takeover-8ee1a53566ec)
  — original technique writeup.
- [The Hacker Recipes: UnPAC the Hash](https://www.thehacker.recipes/a-d/movement/kerberos/unpac-the-hash)
  — the recovery primitive.
