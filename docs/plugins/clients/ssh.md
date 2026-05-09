# SSH Client

The **SSH Client** is the most feature-rich client in OctoPwn. It wraps [`amurex`](https://github.com/skelsec/amurex) for the SSH transport layer and bundles four very different operator surfaces into a single session: an interactive shell with multi-tab terminals, an SFTP file browser, an opinionated post-exploitation enumeration toolkit, and a SOCKS proxy that lets every other module in OctoPwn pivot through the SSH host. Default port `22`.

Open the session window after login and you'll see why this page is longer than the others — what looks like a thin `ssh` wrapper from the CLI is, through the GUI, a self-contained operator workspace.

---

## Authentication

Only **password** and **public-key** authentication are supported — the same surface as the [sshlogin scanner](../scanners/sshlogin.md), since both share the underlying `amurex` SSH client. Other SSH mechanisms (GSSAPI/Kerberos, host-based, certificate, keyboard-interactive) are **not** implemented and will be skipped even if the server advertises them.

| Authentication Protocol | Secret Type | Description                                                                                                        | Example                      |
| ----------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------ | ---------------------------- |
| **Plain**               | Password    | Authenticates with a username and password.                                                                        | `username:password`          |
| **SSH Private Key**     | Private Key | Authenticates using an SSH private key. The private key must be uploaded to OctoPwn's volatile storage beforehand. | `/browserfs/volatile/id_rsa` |

!!! warning "Host-key verification is disabled by default"
    The client sets `skip_hostkey_verification = True` so it'll happily connect to any server presenting any host key. Convenient for credential validation across many unknown hosts; if you need integrity guarantees against a specific known host, validate the banner / key fingerprint out-of-band before trusting the session.

---

## What `login` actually does

`login` runs five steps under the hood; understanding them helps make sense of the rest of the session:

1. **Open the SSH transport** with the bound credential and target.
2. **Print the server banner** so you can identify the OS / SSH implementation early.
3. **Open an SFTP subsystem** opportunistically — failure is non-fatal (the SFTP browser tab simply stays disabled).
4. **Probe the OS** by running `id` over a short-lived exec channel. A non-empty response is treated as Linux with shell access; an empty response means a network device or restricted shell.
5. **Probe Linux privileges** (Linux + shell access only) by running `id; sudo -ln` and pattern-matching `(root)`, `NOPASSWD: ALL`, `(ALL : ALL) ALL` (admin) or `(sudo)` (sudo group, but not yet validated). The verdict is printed to the console.

The resulting state — OS platform, shell access, admin verdict — drives which enumeration commands will work. Re-run [`checkadmin`](#enumeration) at any time to refresh it.

---

## Session window (the GUI experience)

The SSH client's winbox window is divided into seven tabs plus a bottom console drawer. The header carries a connection-status pill (`Connected` / `Connecting` / `Disconnected`) and a Login/Logout button.

| Tab            | What it is                                                                                                                                                                                                                                            |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Terminals**  | Multi-tab full **xterm.js** terminals. The first PTY is auto-created on login. Click the tab badge to focus a session, the **+** button to spawn another. Per-tab search, clear, and download-as-log. Optional **session recording** when spawning. |
| **Files**      | Full **SFTP file browser** — directory tree on the left, sortable file list on the right, multi-select, drag-and-drop upload, download (single or batched), in-browser view for text/PDF, right-click context menu, transfer-progress panel, operation queue. |
| **Commands**   | Auto-generated visual command runner — every entry under `help_groups['COMMANDS']` shows up as a button with parameter inputs, parsed straight from the session's command descriptor.                                                                  |
| **Jobs**       | Live table of currently-running operations with PIDs and per-row Stop buttons. Useful for cancelling long-running enumeration commands without killing the session.                                                                                    |
| **History**    | Scrollable command history with a "screenshot output" capability — turns the rendered output of any past command into an image you can drop into a report.                                                                                            |
| **Settings**   | Editor for the session parameters (target, credential, timeouts, etc.).                                                                                                                                                                                |
| **Debug**      | Raw protobuf message inspector — turns red when active, otherwise hidden.                                                                                                                                                                              |
| **Console**    | Collapsible / resizable bottom drawer with the same console you'd type into on the CLI, plus search, clear, and log-download.                                                                                                                          |

!!! tip "The GUI and CLI control the same session"
    Anything you type in the **Console** drawer hits the same backend the **Commands** tab does. Use the GUI buttons for discovery, drop into the console for repeatable workflows.

!!! info "Under the hood — GUI plumbing"
    The terminal and SFTP browser are driven by a small set of streamed commands (`sendchar`, `resize`, `sendshellcmd`, `remoteListDirectory`, `remoteDownloadFile`, `remotecreateFile`, …). They're not meant to be invoked by users — typing `sendchar` from the console serves no purpose — but they're why those features feel native instead of bolted on.

---

## CLI commands

Six command groups, all callable from the console drawer or the Commands tab.

### CONNECTION

#### login
Opens the SSH connection, runs the auto-detection sequence described in [What `login` actually does](#what-login-actually-does), and flips the session into the connected state. Required before everything except the no-op `logout`.

#### logout
Closes every active PTY session, tears down the SSH connection, and notifies the GUI to flip the connection-status pill.

---

### SHELL

#### ptyshell
Spawns an interactive PTY-backed shell on the target and registers it as a new terminal tab in the GUI (unique session ID, focused automatically). Multiple PTYs can coexist in the same SSH connection.

##### Parameters
- **record** *(optional, bool, default `False`)*: Set to `True` to record the session to disk in OctoPwn's volatile storage. Two files are written: `ssh_session_<hex>` (raw stdout/stderr bytes) and `ssh_session_<hex>.time` (per-write `<seconds_since_last_write> <byte_count>` lines).

!!! info "Session recording — replay format is custom for now"
    The recording layout is roughly `script(1)` / `scriptreplay(1)` shaped but isn't a clean drop-in for either standard replayer (and isn't asciinema-compatible either). Until that's standardised, replay needs a small custom script that walks the `.time` file and feeds the data file at the recorded pace. Migrating to **asciinema cast v2** is on the to-do list — the source carries a corresponding TODO comment in `__recorder`.

---

### EXEC

#### exec
Runs a single command non-interactively over a fresh SSH `exec` channel and prints both stdout and stderr to the console (stderr is prefixed with `[STDERR]`). Good for one-shot commands when you don't need a full PTY.

##### Parameters
- **command**: The remote command line (e.g. `cat /etc/hostname`, `uname -a`).
- **codec** *(optional, str, default `utf-8`)*: Decoder for the command output.

---

### ENUMERATION

Eleven opinionated post-exploitation helpers. **All of them require an active shell on the target** — they print a clear "shell access required" message and bail immediately on network devices / restricted shells. None of them stream credentials back into the Credentials Window today; output goes to the console (and the GUI's command history, where you can screenshot it).

| Command           | What it does                                                                                                                                                  | Notes / side-effects                                                                              |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `checkadmin`      | Re-runs the OS detection + Linux-privilege probe described in [What `login` actually does](#what-login-actually-does).                                          | Updates the session's `shell_access` / `admin_privs` flags in place.                              |
| `sudocheck`       | Actively validates whether the current user can elevate via `sudo`, by running a real `sudo` invocation and checking the result.                              | **Requires a password credential** (reads it from the session's `cid`). **Touches `/tmp` temporarily.** Two methods: `sudo-stdin` (default) and `mkfifo`. |
| `awscreds`        | `find … -name credentials -exec grep aws_ {}` over a configurable set of paths, prints the contents of every match.                                           | Default search paths: `/home/`, `/tmp/`. Override via the `search_paths` argument.                |
| `sshkeys`         | Hunts SSH key material (`id_rsa` / `id_dsa` / `id_ecdsa` / `id_ed25519` and their `.pub` counterparts, `authorized_keys`, `known_hosts`, `*.pem`).            | **Prints private-key contents in full** to the console. Default paths: `/home/ /root/ /tmp/`.    |
| `credhunt`        | Looks for ~16 well-known credential files (`.git-credentials`, `.netrc`, `.pgpass`, `.my.cnf`, `.env`, `wp-config.php`, `.docker/config.json`, `shadow`, `.k5login`, `database.yml`, …) and dumps the first 30 lines of each match. | Default paths: `/home/ /root/ /tmp/ /opt/ /var/ /srv/ /etc/`.                                     |
| `sysinfo`         | Hostname, current user, `id`, kernel, architecture, uptime, `/etc/os-release`, CPU model + count, `free -h`, `df -h`.                                          | Pure read-only.                                                                                   |
| `netinfo`         | Network interfaces (`ip a` / `ifconfig`), routing table, ARP cache, DNS config, `/etc/hosts`, listening ports (`ss -tlnp` / `netstat -tlnp`).                  | The natural pre-flight for [`createsocksproxy`](#createsocksproxy).                                |
| `findsuid`        | `find / -perm -4000`, `find / -perm -2000`, plus world-writable directories outside `/tmp /dev /proc /sys /run`.                                              | Cross-reference the output with [GTFOBins](https://gtfobins.github.io/).                          |
| `crontabs`        | `/etc/crontab`, `/etc/cron.{d,daily,hourly,weekly,monthly}/`, the current user's crontab, contents of `/etc/cron.d/*`, and `systemctl list-timers`.            | Comments are filtered out so noise stays low.                                                     |
| `shellhistory`    | Harvests `bash_history`, `zsh_history`, `mysql_history`, `psql_history`, `python_history` and friends. Tails the **last 30 lines** of each file and tags lines containing credential-suggesting keywords (`pass`, `key=`, `mysql`, `curl`, `ssh `, …) with `<<<`. | Default paths: `/home/ /root/`.                                                                  |
| `containercheck`  | Detects Docker / LXC / Kubernetes by looking at `/.dockerenv`, `/proc/1/cgroup`, `/.dockerinit`, container-shaped hostnames, and `KUBERNETES_*` / `DOCKER_*` env vars. Also prints PID 1's command line, capabilities, and overlay/aufs mount evidence. | Pure read-only — useful for adjusting your post-ex strategy when you've landed in a container.    |

!!! tip "Most of these are scripted shell pipelines, not magic"
    Every enumeration command above is a hand-written shell pipeline executed via `exec`. If a command misses something on your target, you can usually replicate the underlying `find …` / `cat …` invocation directly through `exec` and adjust to taste.

---

### FILE

#### getfile
Downloads a remote file via the SFTP subsystem. Fails fast if the SFTP session wasn't established at login (e.g. the server doesn't ship an SFTP subsystem).

##### Parameters
- **remotepath**: Absolute remote path.
- **localpath**: Destination path inside OctoPwn's volatile storage.

#### putfile
Uploads a local file via the SFTP subsystem.

##### Parameters
- **localpath**: Source path inside OctoPwn's volatile storage.
- **remotepath**: Absolute destination path on the target.

!!! tip "Or just use the Files tab"
    For interactive transfers, the **Files** tab (drag-and-drop upload, multi-select download, transfer-progress panel) is usually the smoother path. `getfile` / `putfile` are the scriptable equivalents for repeatable workflows.

---

### PROXY

#### createsocksproxy
**Registers a SOCKS proxy in OctoPwn that tunnels TCP connections through this SSH session.** Once created, the proxy shows up in the Proxy Window with a description of `SSH[<session_id>]`, and any other client / scanner / attack module in OctoPwn can route through it by selecting that proxy ID.

This is the practical pivot story for any time you have shell on a Linux jump host that can reach an internal segment your operator workstation can't:

1. SSH-login to the jump host, run `createsocksproxy`.
2. Note the new proxy ID from the Proxy Window.
3. Create your next client (SMB, LDAP, MSSQL, …) against an internal target and select that proxy for it. Traffic will be tunnelled over the SSH connection via `direct-tcpip` channels (i.e. a standard SSH local port forward, but registered as an OctoPwn proxy rather than bound to a local TCP port).

##### Parameters
None.

!!! warning "Proxy lifetime"
    The proxy is bound to the SSH session that created it. If you log out of the SSH client, in-flight tunnels through the proxy will fail — destroy and re-create dependent client sessions if you intend to keep working after the SSH session is gone.

---

## Limitations & gotchas

- **Auth methods**: only password and public key. GSSAPI/Kerberos, host-based, certificate, and keyboard-interactive aren't implemented.
- **Host-key verification is permanently off** in the current build (`skip_hostkey_verification = True`). If you need to assert you're talking to the *expected* host, validate the banner / fingerprint out-of-band.
- **Enumeration commands are Linux + shell-access only.** They print "Shell access required" and bail on network devices, restricted shells, and Windows OpenSSH targets.
- **`sudocheck` requires a password credential** bound to the session — it can't validate sudo when authentication was done via SSH key only. The check also temporarily writes to `/tmp/<uuid>` and removes it; expect a brief disk footprint.
- **`sshkeys` prints private keys in full** to the console. Mind your screen when demoing.
- **`credhunt` and `shellhistory` only show the first 30 / last 30 lines** of each file. For full content, use `getfile` to download the file or `exec cat <path>`.
- **Session recording uses a custom format** (`<basename>` raw bytes + `<basename>.time` per-write timing sidecar). Replaying it needs a small custom script today; an asciinema-compatible cast format is on the to-do list (see `__recorder` in `octopwn/clients/ssh/console.py`).
- **`createsocksproxy` ties the proxy to the SSH session** — log out of the SSH client and any tunnels through that proxy break.
