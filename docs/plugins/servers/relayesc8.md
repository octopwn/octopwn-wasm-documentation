# RelayESC8 Server

The **RelayESC8** server is the NTLM relay variant aimed at **AD CS Web Enrollment**
endpoints (the `certsrv` IIS application that ships with Active Directory Certificate
Services Web Enrollment Role). It is OctoPwn's implementation of the **ESC8** attack
([SpecterOps' "Certified Pre-Owned" #8](https://posts.specterops.io/certified-pre-owned-d95910965cd2)).

Inbound NTLM authentications are forwarded into a fresh HTTP session against the target
CA's Web Enrollment URL. Once the relayed session reaches the enrollment page, the
relay drives the **full certificate-request workflow** — generates a CSR with the
attacker's chosen template and Subject Alternative Names, posts it to `certfnsh.asp`,
downloads the issued certificate, packs it into a PFX, and **stores the PFX as a usable
credential** in the project's Credentials Hub.

| Inbound listener (front)                     | Outbound back-end                          |
| -------------------------------------------- | ------------------------------------------ |
| `smb`, `http`, `https`, `httpproxy`, `mssql` | AD CS Web Enrollment on `target` (HTTP/HTTPS) |

The listener side is **shared** with the rest of the relay family — see the
**"Listener-side parameters (shared)"** section in [`RELAYSMB`](relaysmb.md#listener-side-parameters-shared)
for the full reference. This page documents only the ESC8-specific parameters and
behaviour.

---

## How it works

1. A victim authenticates to one of the front-end listeners — typically a domain
   computer or user that was *coerced* (PrinterBug, MS-EFSRPC, WebDAV …) toward the
   agent's IP.
2. The captured NTLM exchange is shuttled into an `httpx.AsyncClient` configured with
   `HttpxNtlmRelayAuth` — a custom auth handler that drives the in-flight NTLM
   challenge / response into the outbound HTTP request stream.
3. The first request is `GET /certsrv/certrqxt.asp` against `target` — this both
   completes the NTLM handshake and dumps the list of templates the CA exposes.
4. The relayed user's username and domain are pulled from the captured NTLM info.
   If `template = Unknown` (default), OctoPwn auto-selects:
   - `Machine` if the username ends with `$` (computer account).
   - `User` otherwise.
5. A CSR is generated locally with the requested key size (default `2048`), the
   relayed username as the subject, and any SAN values you supplied
   (`altdns`, `altupn`, `altsid`, `subject`, `applicationpolicies`, `smime`).
6. The CSR is `POST`ed to `/certsrv/certfnsh.asp` along with `Mode=newreq` and the
   chosen template.
7. The CA replies with a certificate ID; the relay then `GET`s
   `/certsrv/certnew.cer?ReqID=<id>` to download the issued certificate.
8. Certificate + private key are packed into a PFX (password `admin`) and stored in
   the **Credentials Hub** via `store_pfx_creds`. The new credential ID is printed in
   the server console — that is the ID to feed to subsequent
   [LDAP `certify`](../clients/ldap.md#certify) /
   [Kerberos PKINIT](../clients/kerberos.md) flows.

Unlike the other relay variants, **no interactive client session is spawned**. The
*output* of `RELAYESC8` is a PFX credential, not a connected session.

!!! info "ESC8 in one sentence"
    "If the AD CS Web Enrollment role is exposed over HTTP and the target CA does not
    enforce **EPA** (Extended Protection for Authentication / channel binding), any NTLM
    authentication you can coerce into the agent can be turned into a certificate for the
    relayed account."

---

## Operational requirements

The same requirements as the rest of the relay family apply — see
[`RELAYSMB` Operational requirements](relaysmb.md#operational-requirements). ESC8-specific
considerations:

- **Discover the CA first.** Use the LDAP client's [`certify`](../clients/ldap.md#certify)
  / [`certify2`](../clients/ldap.md#certify2) flows to enumerate certificate authorities
  and the templates each one exposes. The CA's `dnsHostname` (or IP) is what you put
  in `target`.
- **Web Enrollment must actually be installed.** The ESC8 attack targets the IIS-based
  `certsrv` web app. Plain AD CS without the **Web Enrollment Role** has no
  `/certsrv/` endpoint. If the first GET returns 404, the role is not deployed.
- **EPA / channel binding** on the CA defeats HTTPS relays. If `enrollmentproto=https`
  and the auth handshake is silently rejected, the CA enforces EPA — try `http` if it
  is exposed, or accept that this CA is not vulnerable.
- **Template enumeration is informational.** The relay tries to *parse* the template
  list out of `certrqxt.asp` and prints what it finds, but it still uses whatever
  `template` you specified. Use the LDAP `certify` enumeration to know which template
  to actually request.

---

## Relay-specific parameters

These are the parameters unique to **`RELAYESC8`**. See
[`RELAYSMB`](relaysmb.md#listener-side-parameters-shared) for the listener-side parameters
shared by every relay variant.

### Normal parameters

#### `target`
Single AD CS Web Enrollment server — FQDN or IP. **Required.** Note: this is **not** a
list. ESC8 is a one-target-at-a-time attack because the CA-side enrollment workflow
needs to complete fully for each authentication.

#### `template`
Default: `Unknown`. The certificate template to request. When set to `Unknown` (or
empty), the relay auto-selects `Machine` if the relayed username ends with `$` and
`User` otherwise. Override this with whatever template the LDAP `certify` enumeration
flagged as ESC1/ESC3/ESC15-vulnerable (e.g. a custom template that allows
`SubjectAltName` of any UPN).

#### `altdns`
Optional. Adds a `dNSName` SAN to the CSR. Used in ESC1-style abuse where the template
allows the requester to specify the SAN, and you want the resulting cert to authenticate
as a different host name.

#### `altupn`
Optional. Adds a `userPrincipalName` SAN to the CSR. The classic ESC1 payload — set
this to the UPN of a privileged user (e.g. `Administrator@domain.local`) and the
resulting certificate authenticates to that user via PKINIT.

#### `altsid`
Optional. Adds an `objectSID` extension (Microsoft-specific OID
`1.3.6.1.4.1.311.25.2`) to the CSR. Required on patched CAs (post May-2022 update)
for SAN-spoofing attacks to actually map to the requested account — without it, the
KDC ignores the SAN and authenticates as the *requesting* (relayed) account.

#### `subject`
Optional. Override the CSR Subject DN. Default is whatever the CA assigns based on the
relayed account.

#### `applicationpolicies`
Optional. List of application-policy OIDs (or friendly names — `OID_TO_STR_NAME_MAP`
maps `clientAuthentication`, `smartcardLogon`, etc. to their OIDs). Used in **ESC15**
abuse against schema-version-1 templates: by adding a `Client Authentication`
application policy to a request for a non-clientauth template, you can sneak EKU
abuse past the issuance policy check.

#### `smime`
Optional. S/MIME capabilities to embed in the request. Niche, mostly for completeness.

### Advanced parameters

#### `keysize`
Default: `2048`. RSA key size for the generated CSR. Bigger is slower; the default is
fine.

#### `enrollmentproto`
Default: `http`. One of `http` / `https`. The protocol used to talk to the CA's Web
Enrollment endpoint. Try `http` first — it is the historically vulnerable path; many
CAs only enforce EPA on `https`.

#### `connectproxy`
Proxy ID for the **outbound** HTTP/HTTPS connection to the CA. Independent from
`serverproxy`. On WASM this is auto-set to `0` if unset.

---

## Commands

The standard `ScannerConsoleBase` command set applies (`setparam`, `getparam`, `params`,
`info`, `serve`, `stop`, `historylist`, …):

#### `serve`
Bring up the configured listeners and the relay-handler task. Each captured
authentication is shuttled into `handle_esc8_relay`, which performs the full
HTTP enrollment workflow against `target`.

#### `stop`
Stop all listener tasks and the relay-handler task. PFX credentials produced by
previous successful relays remain in the Credentials Hub.

---

## Typical workflow

1. **Discover certificate authorities.** From an [LDAP client](../clients/ldap.md)
   session, run [`certify`](../clients/ldap.md#certify) to enumerate CAs and
   templates. Note any CA that has Web Enrollment enabled and any template flagged
   as ESC1-vulnerable.
2. **Pick the attack shape:**
   - **Plain ESC8** — you don't need a vulnerable template, you just want a certificate
     for the relayed account itself. Leave `template=Unknown` and most SAN fields
     unset.
   - **ESC8 + ESC1** — you want a certificate for *another* account. Set `template`
     to the ESC1-vulnerable template, set `altupn` (and `altsid`) to the target
     UPN/SID.
3. **Start `RELAYESC8`** with `target=<CA hostname>`, the chosen `template`, and
   `enrollmentproto=http` first. Disable the SMB listener
   (`servertypes=http,https,httpproxy`) to avoid pulling in coerced auth that won't
   help here.
4. **Coerce a domain account** toward the agent. PrinterBug / MS-EFSRPC against a
   domain controller is the canonical path — coerced `DC$` authentications relayed to
   AD CS produce a domain-controller certificate, which is golden.
5. **Watch the server console.** A successful relay prints `[+] PFX creds stored
   successfully with ID: <id>`. That credential is now in the project's Credentials
   Hub and ready to use.
6. **Use the certificate** for follow-on attacks: PKINIT via the
   [Kerberos client](../clients/kerberos.md), LDAPS-with-client-certificate auth via
   the [LDAP client](../clients/ldap.md), pass-the-cert against any SChannel-enabled
   service, etc.

---

## Limitations & gotchas

- **No interactive session.** The deliverable is a PFX credential, not a connected
  client. If you want a connected session, use the resulting credential to start a
  new session manually.
- **Single target only.** Unlike `RELAYSMB` / `RELAYLDAP`, `target` is a single host.
  To hit multiple CAs you need separate `RELAYESC8` sessions.
- **The PFX password is hardcoded as `admin`.** This is set inside the relay; the
  Credentials Hub records the PFX as such. When using the credential in OctoPwn this
  is transparent, but if you export the PFX to disk for an external tool, the
  password is `admin`.
- **EPA-enforced HTTPS rejects the relay.** If `https` doesn't work, fall back to
  `http`. If the CA only exposes `https` *and* enforces EPA, this CA is not
  vulnerable to ESC8 over the OctoPwn relay path.
- **Template auto-detection is naive.** It only inspects the `$` suffix on the
  username. Service accounts that *don't* end in `$` will be treated as users — set
  `template` explicitly if that matters.
- **`altsid` is mandatory after the May-2022 patch.** Without it, the issued
  certificate will not map to the SAN-specified account on patched DCs — PKINIT will
  fall back to the relayed account.
- **No retry / queuing.** Each captured authentication runs the enrollment workflow
  once. If the CA hiccups, the auth is consumed and you have to coerce again.
