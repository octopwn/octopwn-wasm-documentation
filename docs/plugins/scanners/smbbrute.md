# SMB Brute-Force Scanner (smbbrute)

The **SMB Brute-Force Scanner** mounts a credential brute-force or password-spraying campaign against one or more SMB targets using user-supplied username and password lists. The scanner supports **smart throttling** so you can avoid AD account lockouts: a configurable maximum number of attempts per user before sleeping for a configurable interval, and an optional "username-is-password" mode for quick wins.

Each successful login is reported as a row containing the target IP, domain, username and password. Successful credentials are automatically registered in the project so they can be reused by other scanners and clients without any manual copy-paste.

!!! warning "Use with care on production AD"
    Brute-forcing in an Active Directory environment can lock out legitimate users when account lockout policies are tight. Always know the current lockout policy first (`net accounts /domain` or LDAP query), keep `maxattempts` below it, and prefer **password spraying** (one password against many users) over true brute-forcing.

!!! tip "Targeted spraying"
    Combine `smbbrute` with a wordlist tailored to the environment (e.g. `Season+Year`, `Company123`, `Welcome1!`) and the company's leaked-password format. This typically yields better results with far fewer attempts than a generic dictionary attack.

---

## Parameters

### Normal Parameters

#### usernames
List of usernames to try. Either inline values (e.g. `admin,sales,helpdesk`) or paths to text files inside `/browserefs/volatile` (one username per line). Mixing both is supported.

#### passwords
List of passwords to try. Either inline values (e.g. `Welcome1,Spring2024!`) or paths to text files inside `/browserefs/volatile` (one password per line). Mixing both is supported. Ignored when `usernameispassword` is `True`.

#### target
ID of the target host (from the targets window).

#### domain
Domain (NetBIOS or DNS) used during authentication. Leave empty for local accounts / workgroup machines.

#### sleep
Sleep duration (in seconds) inserted **after** `maxattempts` attempts have been made for a given user. Used together with `maxattempts` to stay below the lockout threshold.

#### maxattempts
Maximum number of password attempts to make per user before triggering the `sleep` pause. Defaults to `3`.

#### usernameispassword
When `True`, the scanner skips the `passwords` list entirely and tries each username as its own password. Cheap and fast — surprisingly effective in many environments.

---

### Advanced Parameters

#### authtype
Specifies the authentication protocol.

Available protocols:

- `NTLM`
- `Kerberos`

#### maxruntime
Specifies the maximum runtime per host (in seconds).

#### proxy
Specifies the proxy ID to use for the scan.

Enter the ID of the proxy to route the scan through. Proxies must be configured in the Proxy Window.

#### resultsfile
Specifies a file for saving the scan results.

The file will be saved in OctoPwn’s `/browserefs/volatile` directory. Defaults to `smb_scan_brute_<random>.tsv`.

#### showerrors
Determines whether per-target errors should be displayed.

#### timeout
Sets the timeout (in seconds) for each connection attempt.

#### workercount
Specifies the number of parallel workers for the scan. Defaults to `10`.

!!! info "Legacy scanner"
    `smbbrute` predates the unified `ScanParameter` framework and exposes its options via a flat parameter dictionary instead of normal/advanced sections. The behaviour is unchanged; the options are simply rendered in a single list in the UI.
