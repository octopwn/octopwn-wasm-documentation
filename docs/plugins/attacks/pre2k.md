# Pre-Windows 2000 Compatibility Attack

The **PRE2K** attack abuses a long-standing AD quirk: machine accounts created
through the legacy "Pre-Windows 2000 compatibility" code path get a default
password derived from the machine's own `sAMAccountName`. Specifically, the
password is set to the machine name **lowercased** and **truncated** — and if
the machine never finishes its first AD logon, that default password is never
rotated.

The attack:

1. Enumerates machine accounts via LDAP.
2. For each account, builds the candidate default password and **tries an SMB
   bind**.
3. Stores any working `<machine>$ : <password>` pair as a project credential.

Hits are gold for both **Kerberoast-style cracking** (the password is short
and predictable so it cracks instantly anyway) and as a foothold to
**rotate the machine's password yourself** before it gets used by anything
else — see "Output and follow-up" below.

---

## How it works

1. **LDAP session** is opened against `target` using `credential` (NTLM or
   Kerberos, both LDAP and LDAPS tried in turn). The credential needs the
   bare minimum: read access to the directory's machine accounts.
2. **Two enumeration modes** depending on `usefilter`:
    - **`usefilter = False` (default)** — every machine account in the domain
      is checked. Maximum coverage; loud (one SMB connect per machine).
    - **`usefilter = True`** — only machines matching
      `(&(userAccountControl=4128)(logonCount=0))` are checked. That
      `userAccountControl` value is `WORKSTATION_TRUST_ACCOUNT (0x1000)` +
      `PASSWD_NOTREQD (0x20)` — the bit pattern set by the legacy "Pre-Windows
      2000 compatibility" tooling. `logonCount=0` ensures the machine has
      **never logged on**, so the default password is still in place. This is
      the stealthy / efficient mode — recommended for first-pass scans.
3. **Per-account default-password derivation**:

    ```python
    password = sAMAccountName.lower()
    if len(password) > 15:
        password = password[:14]      # truncate at 14 (legacy 15-char field)
    else:
        password = password[:-1]      # strip the trailing '$'
    ```

    So `WORKSTATION01$` becomes `workstation01`,
    `LONG-MACHINE-NAME-01$` becomes `long-machine-n` (14 chars), *etc.*
4. **SMB bind attempt** as `<sAMAccountName> : <derived password>` (NTLM)
   against the target DC's `445/TCP`. Two acceptance signals:
    - The bind **succeeds** → password is correct and the account is
      currently usable.
    - The bind **fails with `STATUS_NOLOGON_WORKSTATION_TRUST_ACCOUNT` /
      `STATUS_NOLOGON_SERVER_TRUST_ACCOUNT`** → the password is correct,
      but the account type doesn't allow interactive logon. **Still
      counted as a hit** — the credential is valid for Kerberos, just not
      for SMB interactive auth.
5. **Hits are added to the Credentials Hub** with
   `stype = password`, `source = PRE2K-<session-id>`, `username =
   <sAMAccountName>` (with the trailing `$`), `domain = <realm>`.

---

## Prerequisites

- A **valid domain credential** to read LDAP. Any user — `Domain Users` is
  enough to enumerate every machine account's `sAMAccountName` and
  `userAccountControl`.
- **Outbound `445/TCP`** from the agent to the target (typically a DC, but
  any SMB server in the domain that authenticates against the same KDC
  works as a verifier).
- **Outbound `389/636/TCP`** to the same DC for the LDAP enumeration.

---

## Parameters

### Normal parameters

#### `target`
Target ID of a Domain Controller (used for both LDAP enumeration and SMB
bind verification). Required.

#### `credential`
Credential ID of any domain user. Used for the LDAP read.

#### `usefilter`
Default: `False`. When `True`, only enumerate machines with the legacy
"Pre-Windows 2000 compatibility" UAC bits set **and** `logonCount = 0`.
**Strongly recommended for stealth** and for cutting attack runtime from
"every machine in the domain" down to "the handful that match".

#### `proxy`
Optional. Proxy ID for both LDAP and SMB.

### Advanced parameters

The standard `ScannerBaseParameters` set: `maxruntime`, `resultsfile`,
`showerrors`, `timeout`, `workercount`, `wsnetreuse`. Defaults are fine.

---

## Output

```
domain          username             password
CORP.LOCAL      legacy-srv-01$       legacy-srv-01
CORP.LOCAL      build-vm$            build-vm
```

Each hit is added to the [Credentials Hub](../../user-guide/credentials.md)
as a `password`-type credential.

---

## Output and follow-up

What you do with a Pre-2k hit depends on what you want:

- **Take over the machine immediately.** Use the credential with the
  [Kerberos client](../clients/kerberos.md) — request a TGT for the machine
  account, then use that TGT to enumerate its local secrets via the
  [SMB client](../clients/smb.md) (`regdump` / `dpapi` / *etc.*) or pivot
  laterally as `<machine>$`.
- **Forge tickets.** A machine account's TGT is enough material to forge
  Silver Tickets for the SPNs it owns. Pair with [`KERBEROAST`](kerberoast.md)
  / [`DCSYNC`](dcsync.md) for a full chain.
- **Rotate the password yourself** to lock out the legitimate machine setup.
  In the [Kerberos client](../clients/kerberos.md), request a TGT and use
  the password-change facility (`changepw` / `setpassword` depending on
  client version) to put a value of your choice on the account. The
  legitimate setup process will then fail to join, and you keep the
  account.
- **Just record the hit.** On engagements where the goal is "demonstrate
  pre-2k compat is enabled", the hit alone is the deliverable.

---

## Limitations and caveats

- **Default `usefilter = False` is loud.** Every machine in the domain
  generates one SMB connect attempt with a deliberately wrong-but-plausible
  password — that's a lot of `4625` failed-logon events on the DC. Set
  `usefilter = True` unless you're operating in a lab.
- **The credentials are "first-use only" in many environments.** A genuine
  Pre-Windows 2000 compat account is supposed to immediately rotate its
  password on first real logon. So if you find a hit and hesitate, the
  legitimate machine joining the domain will rotate the password and your
  hit becomes invalid. Treat hits as time-sensitive.
- **Some accounts pass the LDAP filter but no longer have the default
  password** — administrators sometimes manually rotate without clearing the
  PASSWD_NOTREQD flag. Those will silently fail the SMB bind; no false
  positives.
- **Unicode / non-ASCII machine names** can lead to ambiguous lower-casing
  if the locale of the original setup didn't match what `str.lower()`
  produces in OctoPwn. Edge case — usually irrelevant.

---

## See also

- [`TIMEROAST`](timeroast.md) — companion attack against the same class of
  weak machine-account passwords, but enumerated via NTP RID-roasting
  instead of brute. Run both: PRE2K finds default-password machines that
  have never logged on, TIMEROAST finds *any* machine with a weak password
  including those whose Pre-Windows-2000 password was set manually long
  after creation.
- [LDAP client](../clients/ldap.md) — for inspecting the matched machine
  objects and their `userAccountControl` flags before / after the attack.
- [Kerberos client](../clients/kerberos.md) — for using the recovered
  machine credential (TGT request, password change).
- [SMB client](../clients/smb.md) — for using the recovered credential
  against actual SMB targets (the credential authenticates to `445`, even
  if the verifier-DC didn't allow interactive logon).
