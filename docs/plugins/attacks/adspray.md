# ADSpray Attack

The **ADSpray** attack is OctoPwn's **Active Directory password spray** module.
It tests a small list of likely passwords against many user accounts in parallel,
*safely*: it reads the domain's lockout policy from LDAP up front and self-throttles
so that no single account ever exceeds `lockoutThreshold - 1` failed attempts in
one observation window.

Hits are stored automatically in the
[Credentials Hub](../../user-guide/credentials.md) with `stype = PASSWORD`,
`source = ADSPRAY-<session-id>` — ready to feed into any subsequent attack /
client / scanner.

The two important properties:

- **NT-hash spraying is supported.** If a candidate "password" is a 32-character
  hex string, OctoPwn treats it as an NT hash and uses pass-the-hash for that
  attempt. Mix passwords and NT hashes freely in the same list.
- **Lockout-aware.** ADSpray reads `lockoutThreshold` and `lockOutObservationWindow`
  from the domain object via LDAP and:
    - Skips users whose `userAccountControl` has `ACCOUNTDISABLE` set.
    - Per user, never sends more than `lockoutThreshold - 1` attempts before
      sleeping for `max(lockOutObservationWindow + 1, 60)` seconds and
      continuing.
    - Skips four well-known accounts up front: `krbtgt`, `Guest`,
      `Administrator`, `root`, `admin` (when no explicit `users` list is
      supplied — these accounts have very different lockout behaviour and are
      typically not the target of a spray anyway; if you *want* to spray
      `Administrator`, name it explicitly in `users`).

---

## How it works

1. **LDAP enumeration.** A connection is opened to `target` using `credential`.
   Both NTLM and Kerberos are tried over both LDAP and LDAPS — first one that
   binds wins.
2. **Domain info fetch.** OctoPwn reads the AD info object to get
   `lockoutThreshold` and `lockOutObservationWindow`. These drive the rate
   limiter.
3. **User list construction.**
    - If `users` is empty, fetch every user account from LDAP, filter out
      disabled accounts and the well-known names (above), use the rest.
    - If `users` is non-empty, look each name up in LDAP and use the matched
      `MSADUser` objects (so OctoPwn knows the per-user `badPwdCount` and can
      reason about how many attempts that specific account can still take).
4. **Parallel sprayer.** Up to **100 users at a time** are sprayed in parallel
   (`batch_size = 100`). Each user runs an independent `UserSprayer`:
    - For each candidate password / NT hash, attempt an SMB authentication
      against `target` as `<domain>\<sAMAccountName>:<candidate>`.
    - If the bind succeeds, store the credential and stop spraying *that*
      user.
    - If `lockoutThreshold - 1` failures have been delivered and there are
      still candidates left, sleep `max(lockOutObservationWindow + 1, 60)`
      seconds, then resume.
    - There's a hard-coded **5-second sleep between consecutive attempts per
      user**, to keep the per-user attempt rate well below typical
      brute-force-detection thresholds.
5. **Hits land in the Hub** and the `users / domain / password` row is
   emitted in the result stream.

---

## Prerequisites

- A **working domain credential** to read LDAP. Any low-priv domain user
  works — `Domain Users` is enough to read `lockoutThreshold`,
  `lockOutObservationWindow` and the `sAMAccountName` of every account.
- **Outbound `445/TCP`** from the agent to `target` (the spray attempts go
  to `<target>:445`).
- A **realistic password list** — `passwords` is mandatory and should usually
  contain ≤ 5 entries (`Welcome2024!`, `Summer2024!`, `Password1`, the org
  name + `1`, *etc.*). The whole point of password-spraying is *one
  password against many users*, not many passwords against one user.

---

## Parameters

### Normal parameters

#### `target`
Target ID of the **Domain Controller** (used for both LDAP enumeration *and*
SMB authentication attempts). Required.

!!! note "Spraying SMB ≠ spraying every host"
    The spray happens against the DC's SMB service. This counts as one logon
    attempt against the user account from AD's perspective — exactly what
    `lockoutThreshold` is checked against. You don't gain coverage by
    spraying multiple member servers; you only multiply your noise.

#### `credential`
Credential ID for the **LDAP read** at the start of the run. Any domain user.

#### `passwords`
Comma-separated list of passwords *or* NT hashes (32-char hex strings). Both
can be mixed freely in the same list. Required.

#### `users`
Comma-separated list of `sAMAccountName` values to attack. Optional. When
empty, ADSpray sprays *every enabled, non-system user in the domain*. When
non-empty, those exact users are looked up in LDAP and only they are
sprayed.

#### `proxy`
Optional. Proxy ID for both LDAP and SMB traffic.

### Advanced parameters

The standard `ScannerBaseParameters` set: `maxruntime`, `resultsfile`,
`showerrors`, `timeout`, `workercount`, `wsnetreuse`. See the
[scanner parameters reference](../scanners/baseline.md). Defaults are fine.

---

## Output

For each successful (user, password) pair:

```
user            domain           password
jdoe            CORP.LOCAL       Welcome2024!
svc-jenkins     CORP.LOCAL       3a8b...c4f1     # NT hash hit
```

Hits are also added to the Credentials Hub with `stype = PASSWORD` regardless
of whether the input was a password or an NT hash (the secret is stored as the
matching value — for NT-hash hits the `secret` is the hex hash string).

---

## Operational guidance

- **Pre-flight with [`smblogin`](../scanners/smbbrute.md) for free.** If you
  have access to a list of usernames *but no LDAP read*, you can try a single
  password against many users without LDAP at all. ADSpray's value-add is the
  lockout safety + pulling the user list straight out of LDAP, so use it
  whenever you have any LDAP read.
- **Pull sub-lists from LDAP first.** For wide engagements it's often
  cheaper to pre-extract enabled users matching some criterion via the
  [LDAP client](../clients/ldap.md) (e.g. members of a specific group, OU,
  or accounts whose `pwdLastSet` is recent), save the list, and feed it to
  ADSpray as `users`. This narrows scope without paying the
  `lockoutThreshold - 1` parallelism tax across thousands of accounts you
  don't care about.
- **Combine with [`KERBEROAST`](kerberoast.md).** A successful spray gives
  you a domain user; that user is enough to immediately run KERBEROAST and
  AS-REP roast across the same domain.
- **Lockout policies can be FGPP-overridden per user.** ADSpray reads the
  *domain*-level lockout policy. If the target has a Fine-Grained Password
  Policy with a tighter lockout, ADSpray can over-attempt and lock the
  affected accounts. Check FGPP via the LDAP client's PSO objects before
  spraying high-value users.

---

## See also

- [LDAP client](../clients/ldap.md) — for pre-extracting tailored user lists
  (`pso`, `getuser`, group membership) before spraying.
- [`KERBEROAST`](kerberoast.md) — natural follow-up: any domain user
  obtained via spray is a valid roaster.
- [`SMB client`](../clients/smb.md) — for one-off authentication tests once
  ADSpray gives you a hit.
- [`smbbrute` scanner](../scanners/smbbrute.md) — single-credential SMB-bind
  sweep across many *hosts* (the inverse of password-spray).
