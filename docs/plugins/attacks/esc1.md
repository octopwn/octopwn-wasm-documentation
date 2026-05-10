# ESC1 Attack

The **ESC1** attack module exploits a misconfigured AD CS certificate template to
**enroll a certificate with an attacker-chosen Subject Alternative Name (SAN)**,
then uses that certificate to authenticate to the domain as the impersonated user.
It is the most common AD CS escalation primitive — when it works, it goes
straight from "domain user" to "domain admin" in a few seconds, with the
resulting credential landing in the
[Credentials Hub](../../user-guide/credentials.md) as an immediately-usable PFX.

This module assumes you already know **which template is vulnerable**. To find
vulnerable templates first, run the LDAP client's
[`certtemplates`](../clients/ldap.md#certtemplates) (or the
[`certify` family of commands](../clients/ldap.md)) and look for templates with
the `ENROLLEE_SUPPLIES_SUBJECT` (`CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT`) flag set
**and** that allow client authentication and that the operator's user / group
can enroll. Those are your ESC1 targets.

For the case where you have *write access to the template* but the template is
**not** currently set up for ESC1, use [`ESC4`](esc4.md) — it temporarily flips
the right flags, runs ESC1, and reverts.

---

## How it works

1. **LDAP session** is opened against `dctarget` using `credential` (NTLM, hidden
   session). The session is used solely to:
    - Resolve the operator's domain (used to build the issuer `cn`).
    - Optionally enumerate Domain Admins (`dadms`) when no `targetusers` are
      supplied.
2. **Resolve target users.** If `targetusers` is set, those names are used
   verbatim. If empty, OctoPwn calls
   [`dadms`](../clients/ldap.md#dadms) on the LDAP session to list every
   member of `Domain Admins` in the realm and uses that as the impersonation
   set.
3. **SMB session** is opened against `target` (the **ADCS server's** TID, not
   the DC) using the same credential. The session is used to deliver the
   certificate request via DCERPC over the `\PIPE\cert` named pipe (the ICPR
   protocol — `RAW` and `WSTEP`-style request). HTTP/Web-Enrollment is **not**
   the path here; for that, use [`RELAYESC8`](../servers/relayesc8.md).
4. **For each target user**, OctoPwn calls
   [`certreq`](../clients/smb.md#certreq) with:
    - `service = <CA name>` — e.g. `ESSOS-CA`.
    - `template = <vulnerable template name>` — e.g. `ESC1` /
      `User-Custom`.
    - `cn = <operator>@<domain>` — the requesting identity put on the cert.
    - `altname = <targetuser>@<domain>` — the SAN UPN that AD will treat as
      the authenticated identity when the cert is later used for PKINIT.
    - `altsid = None` — *currently a TODO in the implementation.* See the
      "Limitations" section below.
5. **Result handling.** Each successful `certreq` produces a PFX credential
   stored in the project. Its credential ID is logged in the session
   window:

    ```
    [+][ADCS][12][corp\jdoe][ESC1] Successfully performed certreq for user Administrator
    [+][ADCS][12][corp\jdoe][ESC1] CIDs: 47, 48, 49
    ```

   Use the resulting CID with [Kerberos client](../clients/kerberos.md)
   `tgt --etype 0` (PKINIT) to obtain a TGT for the impersonated user, or with
   [SMB / LDAP / WinRM clients](../clients/smb.md) directly (they all accept
   PFX credentials and do PKINIT internally).

---

## Prerequisites

- A **valid domain credential** — used as the requestor identity. This account
  must have **enroll** permissions on the target template (defaults are usually
  `Authenticated Users` for legacy templates; in environments that follow
  Microsoft hardening, this is restricted to specific groups).
- **Knowledge of the vulnerable template's name and the CA's service name.**
  Run the LDAP client's [`certtemplates`](../clients/ldap.md#certtemplates) to
  enumerate; pair with [`adcssrv`](../clients/ldap.md) for the CA service name.
- **Outbound `445/TCP`** from the agent to the ADCS server (for the certreq
  RPC). `dctarget` is only accessed over LDAP (`389/636`).
- **The ADCS server runs the Cert Service** and accepts ICPR requests over its
  named pipe. Almost all default AD CS deployments do.

---

## Parameters

### Normal parameters

#### `dctarget`
Target ID of a Domain Controller, used for LDAP. Required.

#### `target`
Target ID of the **ADCS / Enterprise CA server**. This is *not* the DC unless
the CA happens to live on the DC (uncommon outside small labs). Required.

#### `credential`
Credential ID for both the LDAP and SMB authentications. Must have enroll
rights on the target template.

#### `service`
Name of the **Certificate Authority service** (e.g. `ESSOS-CA`). Required.

#### `template`
Name of the **certificate template** to abuse. Must be ESC1-vulnerable
(`ENROLLEE_SUPPLIES_SUBJECT` + client auth + the operator can enroll). Required.

#### `targetusers`
Comma-separated list of `sAMAccountName`s to impersonate. Optional. When
empty, OctoPwn enumerates Domain Admins via LDAP and impersonates each one in
turn (intentionally noisy — narrow this down for real ops).

### Advanced parameters

The standard `ScannerBaseParameters` set: `maxruntime`, `resultsfile`,
`showerrors`, `timeout`, `workercount`, `wsnetreuse`, plus `proxy` from
`CredentialedScanParameters`. See the
[scanner parameters reference](../scanners/baseline.md). Defaults are fine.

---

## Output

For each successful enrollment:

```
targetuser     credentialid    template         service
Administrator  47              ESC1             ESSOS-CA
```

The `credentialid` is the project credential ID of the newly stored PFX. From
there:

- **Get a TGT for the impersonated user**:
  use that PFX cred with the [Kerberos client](../clients/kerberos.md) to
  request a TGT (PKINIT auto-engages when a PFX is supplied as the credential).
- **Run any other module as the impersonated user** by selecting the new PFX
  cred — every PFX-aware client (LDAP, SMB, WinRM, MSSQL, …) does PKINIT
  transparently.

---

## Limitations and caveats

- **`altsid` is currently `None`.** OctoPwn does not yet inject the target
  user's SID into the certificate's `szOID_NTDS_CA_SECURITY_EXT` extension.
  After Microsoft's May 2022 patch (KB5014754), DCs that fully enforce
  strong certificate mapping reject UPN-only mappings and require the SID
  extension. Practical impact:
    - In **compatibility mode** (the default until Feb 2025; many environments
      still run it as of this writing) — ESC1 works as documented.
    - In **enforcement mode** — the issued PFX is valid, but the PKINIT
      authentication will fail with `KDC_ERR_CLIENT_NAME_MISMATCH`. There is
      a code TODO to add the SID, which will resolve this.
    - If you must operate against an enforced environment, request the
      certificate manually using the [SMB client's](../clients/smb.md)
      [`certreq`](../clients/smb.md#certreq) command, supplying the
      `altsid` parameter explicitly.
- **`targetusers = empty` enumerates all DAs.** That can mean *dozens* of
  certreq calls on a single run — each visible in CA event logs. Always
  narrow this down for stealth.
- **No template-feasibility pre-check.** OctoPwn does not verify that the
  named template is actually ESC1-vulnerable; it just attempts the request.
  If you point it at a non-vulnerable template, every certreq comes back
  with a CA-policy denial. Run [`certtemplates`](../clients/ldap.md#certtemplates)
  first.
- **Web-Enrollment (HTTP) ESC1** is not exposed by this module. For
  HTTP-based ESC1 (often combined with NTLM relay), use
  [`RELAYESC8`](../servers/relayesc8.md).

---

## See also

- [`ESC4`](esc4.md) — when *you have write rights on the template* but ESC1 is
  not currently configured. Briefly enables ESC1 on the template, runs ESC1,
  reverts.
- [LDAP client → `certtemplates`](../clients/ldap.md#certtemplates) — list
  templates and inspect their flags / ACLs to identify ESC1-vulnerable ones.
- [LDAP client → `dadms`](../clients/ldap.md#dadms) — enumerate Domain Admins
  manually.
- [SMB client → `certreq`](../clients/smb.md#certreq) — single-user certreq
  with full parameter control (including `altsid`).
- [`RELAYESC8`](../servers/relayesc8.md) — the HTTP / Web-Enrollment ESC8
  variant; pairs with NTLM relay.
- [Kerberos client](../clients/kerberos.md) — for using the resulting PFX to
  obtain a TGT.
- [SpecterOps: Certified Pre-Owned](https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf)
  — canonical AD CS abuse paper (ESC1 is technique 1).
