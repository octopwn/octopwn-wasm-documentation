# ROADtools Utility

The **ROADtools** utility is OctoPwn's wrapper around
[Dirk-jan Mollema's ROADtools framework](https://github.com/dirkjanm/ROADtools)
for **Entra ID / Azure AD** reconnaissance. It exposes:

- **Token acquisition** — username/password (v1 and v2 endpoints), refresh-token
  flows, and tenant / user discovery.
- **ROADrecon `gather`** — the bulk Azure AD data dump that feeds every other
  ROADtools analysis tool.
- **Two ROADrecon plugins** — `xlsexport` (everything to an Excel workbook) and
  `policies` (Conditional Access Policy parser → standalone HTML report).

All acquired tokens are stored in the
[Credentials Hub](../../user-guide/credentials.md) with `stype = PRT`,
`source = store_token` — ready to be reused by subsequent ROADtools sessions or
by other Azure-aware modules. Output databases / reports are written to the
project's working directory (typically `/browserfs/volatile`).

---

## Parameters

All parameters are session-scoped and used as defaults for the auth / gather
commands. They map 1:1 onto ROADtools' `Authentication` config:

| Parameter | Default | Purpose |
| --- | --- | --- |
| `proxyid` | none | OctoPwn proxy ID for HTTP traffic to login.microsoftonline.com / graph |
| `tenant` | none | Tenant ID / domain (`contoso.onmicrosoft.com` or GUID) |
| `client` | `1b730954-1685-4b74-9bfd-dac224a7b894` | Application (client) ID — default is the well-known "Microsoft Azure AD PowerShell" client |
| `accesstoken` | none | Pre-existing access token to use directly |
| `refreshtoken` | none | Pre-existing refresh token (paired with `tenant` / `client`) |
| `samltoken` | none | Pre-existing SAML token |
| `tokenfile` | `.roadtools_auth` | Filename for ROADtools' on-disk token cache |
| `resource` | `https://graph.windows.net` | Resource URI (the API the token is for) |
| `scope` | none | OAuth2 scope (only required by the v2 endpoint) |
| `useragent` | none | Custom User-Agent string |
| `debug` | `False` | Pass-through to ROADtools' debug logger |

---

## Commands

### AUTH

#### userpass
`userpass(username, password)` — authenticate via the **v1** OAuth endpoint.
Works against any tenant and any user that allows password auth. Returned
token is stored in the Hub as a `PRT` credential.

#### userpassv2
`userpassv2(username, password, scope=None)` — same as above but against the
**v2** OAuth endpoint. Requires `scope` to be set (either as a parameter or
via the session `scope` parameter). Use this for modern app registrations.

#### userdiscovery
`userdiscovery(username)` — given a `user@domain`, look up tenant identity
(realm-discovery). Useful pre-auth to figure out what tenant a user lives in
and whether the tenant uses federated / managed authentication.

#### authrefreshtoken
`authrefreshtoken(token)` — refresh an existing token. `token` may be:

- An **integer** — credential ID of a stored PRT in the Hub. The credential's
  `secret` (the JSON token blob) is loaded automatically.
- A **JSON string** starting with `{` — the inline token JSON.
- A **file path** — JSON file containing the token blob.

The refreshed token is stored as a new credential in the Hub.

### GATHER

#### gather
`gather(token, mfa=False, skipfirst=False)` — run **ROADrecon `gather`**, the
canonical Azure AD bulk dump. Same semantics as the standalone tool: dumps
users, groups, apps, devices, service principals, role assignments, OAuth
permissions, *etc.* into a SQLite DB.

- `token` follows the same flexible format as `authrefreshtoken` (CID / inline
  JSON / file path).
- `mfa = True` enables the MFA-required token-acquisition path (when the
  token is from an MFA-satisfied auth context).
- `skipfirst = True` skips the user/group enumeration phase — useful when
  you want to re-run only the post-processing on an existing DB.

The output DB is written as `roadrecon_<YYYYMMDD_HHMMSS>.db` and moved into
the OctoPwn working directory; the file path is printed in the session
window.

### PLUGINS

#### xlsexport
`xlsexport(dbfile, outformat='xlsx', verbose=False)` — export the full
ROADrecon DB into a single Excel workbook (or other supported format).
Supported output formats are whatever the underlying
[`aroadtools.roadrecon.plugins.xlsexport`](https://github.com/dirkjanm/ROADtools)
supports — `.xlsx` is the default and what every analyst will want.

#### policies
`policies(dbfile)` — parse the Conditional Access Policies in the ROADrecon
DB and emit a standalone `caps.html` report you can open in a browser. The
single most useful artifact from a tenant audit — it's the human-readable
view of "which CA policies apply to whom under what conditions".

---

## Typical workflows

### 1. Full tenant audit from cleartext credentials

```
roadtools> setparam tenant contoso.onmicrosoft.com
roadtools> userpass alice@contoso.onmicrosoft.com 'Welcome2026!'
# A PRT credential appears in the Hub, e.g. CID 17.
roadtools> gather 17
# DB written to /browserfs/volatile/roadrecon_20260509_2311.db
roadtools> xlsexport /browserfs/volatile/roadrecon_20260509_2311.db
roadtools> policies /browserfs/volatile/roadrecon_20260509_2311.db
```

### 2. Already have a refresh token (from another tool)

```
roadtools> setparam tenant contoso.onmicrosoft.com
roadtools> authrefreshtoken /browserfs/volatile/refresh.json
# A new fresh PRT lands in the Hub.
roadtools> gather <new CID>
```

---

## Limitations and caveats

- **Conditional Access can block the auth** even with valid creds — typical
  blockers are device-compliance requirements, MFA enforcement, and
  geo-fencing. Run [`userdiscovery`](#userdiscovery) first to understand the
  tenant's auth model.
- **`gather` can be slow.** A big tenant takes 10–30 minutes; the session
  window streams progress lines.
- **Plugin output goes to fixed filenames** in the working directory
  (`caps.html`, `export_*.xlsx`). Re-running clobbers earlier outputs;
  rename or move first if you want to keep them.
- **No automatic credential enrichment** — tokens land as `stype = PRT` but
  the Hub doesn't yet auto-derive the username's UPN / SID from the token
  payload. Tag manually if you need that.

---

## See also

- [ROADtools (Dirk-jan Mollema)](https://github.com/dirkjanm/ROADtools) — the
  upstream framework. The CLI flags map directly onto OctoPwn's
  parameter names.
- [DPAPI utility → `cloudapkd`](dpapi.md#cloudapkd) — for decrypting CloudAP
  PRT secrets when you have local DPAPI material (the other half of the
  Azure-credential picture).
- [Credentials Hub](../../user-guide/credentials.md) — where the PRT credentials
  land for re-use.
