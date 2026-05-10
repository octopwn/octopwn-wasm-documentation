# ESC4 Attack

The **ESC4** attack module exploits **write access to a certificate template's
LDAP object** to temporarily make that template vulnerable to
[ESC1](esc1.md), enrol an arbitrary-SAN certificate, and then **automatically
restore the template's original flags** so the change is invisible by the time
the attack ends.

The high-level chain is:

1. **Modify** the template's `msPKI-Certificate-Name-Flag` to include
   `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT` — the bit that makes a template ESC1-vulnerable.
2. **Run [ESC1](esc1.md)** against that now-vulnerable template.
3. **Restore** the original flag value, even on error (the restore lives in the
   `finally` block).

End result: a PFX credential for an arbitrary user (typically Domain Admin)
appears in the [Credentials Hub](../../user-guide/credentials.md), and the
template looks unchanged in any future audit.

---

## How it works

1. **LDAP session** is opened against `dctarget` using `credential` (NTLM,
   hidden). The LDAP credential must have **`Write` permission on the
   target certificate template's LDAP object** — that's the entire ACL
   weakness ESC4 abuses. Effective ACEs to check for include
   `WriteProperty`, `GenericWrite`, `GenericAll` and
   `WriteOwner` / `WriteDACL` on the template object under
   `CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,...`.
2. **Flip the template flag.** OctoPwn calls
   [`addcerttemplatenameflagaltname`](../clients/ldap.md#addcerttemplatenameflagaltname)
   with no `flags` argument — that path **records the current value of the
   template's `msPKI-Certificate-Name-Flag` attribute, then OR-merges in
   `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT`**, and writes the result back. The
   original numeric value is captured in `orig_flags` and held in the
   attack-session state.
3. **Confirm and emit a result row** so the operator sees the change happened.

    ```
    [+][ADCS][12][corp\jdoe][ESC4] Successfully modified certificate template to be vulnerable to ESC1
    [+][ADCS][12][corp\jdoe][ESC4] Original flags: 8
    ```
4. **Run ESC1** by handing the same LDAP session over to
   [`exploit_esc1`](esc1.md) with the now-vulnerable template. Because the
   LDAP session is reused, no second LDAP login happens. ESC1 then:
    - Resolves `targetusers` (or fetches Domain Admins via
      [`dadms`](../clients/ldap.md#dadms)).
    - Opens a hidden SMB session to the ADCS server (`target`).
    - Issues a [`certreq`](../clients/smb.md#certreq) per impersonated user
      with `altname = <user>@<domain>`.
    - Stores each resulting PFX in the Credentials Hub.
5. **Always restore the original flag value.** The `finally` block calls
   `addcerttemplatenameflagaltname(template, orig_flags)` to put the flag
   back. This runs even on cancellation / error, so you do not leave the
   template ESC1-vulnerable after the attack.

   !!! warning "Restore can fail silently"
       The restore happens *as the same LDAP session*. If the LDAP session
       was lost between the modify and the finally (e.g. network blip), the
       restore will not happen. Always check the session window's tail —
       look for `[+] Successfully restored original flags`. If you don't see
       it, manually clear the flag with the LDAP client's
       [`addcerttemplatenameflagaltname`](../clients/ldap.md#addcerttemplatenameflagaltname)
       command, or use [`certtemplates`](../clients/ldap.md#certtemplates)
       to inspect.

---

## When to choose ESC4 vs ESC1

| Situation                                                             | Use                |
| --------------------------------------------------------------------- | ------------------ |
| Template already has `ENROLLEE_SUPPLIES_SUBJECT` set, you can enroll  | [`ESC1`](esc1.md)  |
| Template doesn't have that flag, you have `WriteProperty` / `GenericWrite` on the template object | **`ESC4`** |
| Template already vulnerable but **you can also write to it**          | Either; `ESC1` is one fewer LDAP round-trip |
| You want to abuse template ACLs for *anything other than ESC1* (replace `pKIExtendedKeyUsage`, change issuance requirements, …) | Drive [LDAP client](../clients/ldap.md) directly — OctoPwn currently only automates the ESC1-via-name-flag path |

To find ESC4-vulnerable templates, look at template object ACLs with the
[LDAP client](../clients/ldap.md). Anything the operator's user / group can
write to is a candidate; the most common practical hit is
`Authenticated Users` having `WriteProperty` on a template that wasn't
hardened during deployment.

---

## Prerequisites

- A **valid domain credential** with **write access on the target template's
  LDAP object**. Not "the operator's user is in some group that's a Cert
  Publisher" — *write* on the template itself.
- **Knowledge of the template name and the CA service name** — same inputs as
  ESC1.
- **Outbound `389/636/TCP`** to `dctarget` (LDAP), and **`445/TCP`** to
  `target` (the ADCS server, for the certreq RPC).
- **The ADCS server runs the Cert Service** and accepts ICPR requests on its
  named pipe. (Standard AD CS deployment.)

---

## Parameters

Identical to [ESC1](esc1.md):

#### `dctarget`
Target ID of a Domain Controller (LDAP). Required.

#### `target`
Target ID of the **ADCS server** (where the certreq is delivered). Required.

#### `credential`
Credential ID for both LDAP and SMB. Must have `WriteProperty` /
`GenericWrite` (or stronger) on the target template object.

#### `service`
CA service name (e.g. `ESSOS-CA`). Required.

#### `template`
Template name to abuse. Must be writeable by `credential`. Required.

#### `targetusers`
Comma-separated list of `sAMAccountName`s to impersonate. Optional. When
empty, every Domain Admin is impersonated.

### Advanced parameters

The standard set: `maxruntime`, `resultsfile`, `showerrors`, `timeout`,
`workercount`, `wsnetreuse`, plus `proxy`. See
[scanner parameters reference](../scanners/baseline.md).

---

## Output

Two result row types:

```
template          orig_flags    modified
User-Custom       8             True

targetuser        credentialid  template      service
Administrator     47            User-Custom   ESSOS-CA
```

Plus the standard ESC1 PFX credentials in the Hub. Use them via the
[Kerberos client](../clients/kerberos.md) to PKINIT into a TGT for the
impersonated user.

---

## Limitations and caveats

- **`altsid` is currently `None`.** Inherited from ESC1 — see the
  [ESC1 page's "Limitations" section](esc1.md#limitations-and-caveats) for
  the SID-extension / strong-cert-mapping caveat.
- **Restore window.** Between step 2 (modify) and step 5 (restore), the
  template *is* ESC1-vulnerable. If anyone else happens to enrol against it
  during that window (typically seconds), they get a SAN-supplying
  certificate too. In practice this is a non-issue, but on heavily monitored
  CAs you'll see your own enrolment + the restore + the original flag in the
  CA event log within seconds of each other — a clear ESC4 signature.
- **Only the "name flag" path is automated.** Other ESC4-class abuses
  (replacing `pKIExtendedKeyUsage` with `Smart Card Logon` / `Client
  Authentication`, lowering `msPKI-RA-Signature` to 0, removing `MANAGER
  APPROVAL` issuance requirements, …) require driving the LDAP client
  manually.
- **Atomicity.** The flag-flip and the certreq are not transactional. If the
  network drops between them, you may end up with the flag still set and no
  PFX issued. Re-running the attack is safe — it'll restore the original
  value either way (because the captured `orig_flags` is what was already
  modified, but in practice the `finally` runs before any external
  observer noticing).

---

## See also

- [`ESC1`](esc1.md) — the underlying primitive ESC4 wraps.
- [LDAP client → `addcerttemplatenameflagaltname`](../clients/ldap.md#addcerttemplatenameflagaltname)
  — the same template-flag flip available as a single-shot LDAP command.
- [LDAP client → `certtemplates`](../clients/ldap.md#certtemplates) — list /
  inspect templates and their ACLs to identify ESC4-writeable ones.
- [SMB client → `certreq`](../clients/smb.md#certreq) — single-user certreq
  with full parameter control.
- [SpecterOps: Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf)
  — canonical AD CS abuse paper (ESC4 is template ACL abuse, technique 4).
