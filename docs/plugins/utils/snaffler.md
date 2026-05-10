# Snaffler Utility

The **Snaffler** utility is OctoPwn's port / wrapper of the
[Snaffler](https://github.com/SnaffCon/Snaffler) "find interesting files"
philosophy, built on top of [`pysnaffler`](https://github.com/skelsec/pysnaffler).
It walks remote filesystems looking for files whose **name, share, path, or
contents** match Snaffler's rule set, downloads the candidates, and runs the
content rules on them locally.

Where it differs from the standalone Snaffler tool:

1. It is **session-aware** — instead of "give it a username and a network
   range" you point it at an existing OctoPwn client session and it reuses
   that session's authenticated context.
2. It works against **four protocols**, not just SMB:
   **SMB**, **FTP**, **SFTP** (via the SSH client), and **NFSv3**.
3. It can **autosnaffle** — register a session-creation hook so every new
   client session that lands in the project is enumerated automatically.
4. Optionally, an **LLM** can be invoked on each "matched" file to extract
   credentials in structured form and add them straight to the
   [Credentials Hub](../../user-guide/credentials.md). This is opt-in via the
   `use_llm` parameter and requires an LLM endpoint configured at the
   OctoPwn level.

There is also a [`SNAFFLER` scanner](../scanners/snaffler.md) in the
scanners section — that one operates as a stand-alone scanner over a target
list and credential. The util documented here is the **interactive,
session-following** flavour.

---

## How it works

For each target session:

1. The util **opens the matching enumerator** (SMB share walk, FTP listing,
   SFTP `enum_all`, NFS export listing + per-mount walk).
2. Each entry passes through Snaffler's **rule set** in three places:

    - **prefilter** — runs without downloading anything; decides whether to
      descend into a directory / share / mount based on path / name only.
    - **enum_file** — once a file entry is encountered, the rule set
      decides whether the file is interesting enough to download (matching
      filename rule, extension, etc.).
    - **content rules** — the downloaded file is parsed; matching content
      regions are extracted with a configurable amount of leading / trailing
      context (`chars_before_match` / `chars_after_match`).

3. Files that match are **downloaded** to a temp file and (optionally) kept
   in a per-session zip archive (`<client_id>.zip`) inside
   `snaffler_downloads/` in the working directory. You decide whether to
   keep all downloaded files or only the ones that contained secrets via
   the `keepfiles` / `keepmarkedfiles` parameters.

4. If `use_llm = True`, every matched file is also handed to an LLM with a
   structured-output prompt asking for `{domain, username, secret,
   secrettype}` tuples. The util **double-checks** the LLM's answer
   against the file body to filter out the most obvious hallucinations
   before adding the result as a Hub credential tagged
   `source = snaffler_llm`.

5. A **watchdog** prints aggregate stats every 5 seconds while a snaffle is
   running (`files / downloaded / processed / kept / errors / seen /
   skipped`).

---

## Parameters

| Parameter | Default | Purpose |
| --- | --- | --- |
| `rulesdir` | none | Directory of custom Snaffler rules. Empty / unset means use the bundled default ruleset. |
| `maxfilesize` | `10485760` (10 MB) | Skip any file larger than this. |
| `maxdownloads` | `4` | Concurrent downloads per host. |
| `maxdownloadstotal` | `20` | Concurrent downloads across all hosts. |
| `keepfiles` | `False` | Keep **every** downloaded file in the per-session zip. |
| `keepmarkedfiles` | `True` | Keep only files that contained at least one match. |
| `maxfiles` | `10000` | Per-host file count cap (0 / negative disables the cap). |
| `depth` | `6` | Directory recursion depth. |
| `workercount` | `10` | Internal `pysnaffler` worker count. |
| `use_llm` | `True` | Hand matched files to an LLM for structured credential extraction. |
| `llm_model` | `phi4` | LLM model identifier (whatever the configured backend understands). |
| `llm_system` | bundled prompt | System prompt used for the LLM call. |
| `skiptoplevel` | `['IPC$', 'C$', 'ADMIN$']` | Top-level shares / exports to skip outright. |
| `debug` | `True` | Print per-file debug logs. |

---

## Commands

### GENERIC

#### snafflesession
`snafflesession(sessionid)` — snaffle one specific client session **right
now**. The session must be a `CLIENT` session of one of the supported
subtypes (SMB, FTP, SSH, NFS). For SMB / NFS the util will trigger a
login if the session is not already authenticated.

#### autosnaffle
`autosnaffle()` — register a session-creation handler with the OctoPwn
core. From this point on, **every new client session** that lands in the
project is queued (with deduplication) and snaffled in the background.

A status watchdog starts at the same time and prints aggregate stats every
five seconds. There is no built-in `disableautosnaffle` — to stop, simply
end the util session.

---

## Per-protocol notes

### SMB
Walks every share except those listed in `skiptoplevel` (default skips the
admin shares). Files are downloaded with `aiosmb`'s file API; rules are
matched against the **UNC path** (e.g. `\\dc01\public\creds.txt`) so
share-aware rules work as written.

### FTP
Uses the [FTP client's](../clients/ftp.md) underlying connection. Because
FTP allows only one operation per connection, every file download spins up
a fresh sub-connection — be mindful of `maxdownloads` against servers that
rate-limit connection rate.

### SFTP (via SSH)
Uses the [SSH client's](../clients/ssh.md) SFTP subsystem. There is a
hard-coded **Linux skip list** (`/bin`, `/usr`, `/sbin`, `/boot`, `/lib`,
`/proc`, `/dev`, …) at the prefilter stage so the snaffle doesn't drown in
binaries / virtual filesystems. Walk starts from `/`.

### NFSv3
Walks **every export** the server advertises, not just one. The util
queries `mountd` first to enumerate mount points, then mounts each one and
walks. See the [NFSv3 client docs](../clients/nfs3.md) for the auth model
caveats — the same caveats apply here (low source port, `AUTH_SYS` UID/GID,
etc.).

---

## Output

For every snaffled session the util writes a zip
`snaffler_downloads/<client_id>.zip` inside the working directory.
The zip contains:

- A `filelist.txt.gz` — gzip-compressed list of every path the walker
  visited (regardless of match). Useful for post-hoc review of what was
  *actually* enumerated.
- One archive entry per file kept according to `keepfiles` /
  `keepmarkedfiles`, named after its full remote path (UNC for SMB,
  absolute path for SFTP / NFS).

LLM-extracted credentials are added to the Hub with
`source = snaffler_llm` and the appropriate `stype`
(`PASSWORD` / `NT` / `SECURESTRING`). Manual review is strongly
recommended — the LLM heuristic is only a first pass.

---

## Limitations and caveats

- **`AUTOSNAFFLE` has no off switch.** Once registered, the handler stays
  registered for the lifetime of the util session. Restart the util if you
  want to stop it.
- **LLM credentials may hallucinate.** The built-in cross-check rejects
  the obvious cases (LLM invented a username / secret that isn't in the
  file body) but a confident-but-wrong LLM can still sneak through.
  Review `snaffler_llm`-tagged credentials before relying on them.
- **`keepfiles = True` can fill up the working directory fast** on
  filesystems that are mostly text / config — the cap is on file count
  per host, not on aggregate size. Combine with `maxfilesize` for
  protection.
- **Symlink loops are not detected** on SFTP / NFS. The `depth` cap is
  the only thing keeping the walker from spinning forever in a
  pathological tree.
- **Only client sessions** with subtypes starting with `SMB`, `FTP`, `SSH`,
  or `NFS` are considered. Anything else (RDP, MSSQL, WMI, …) is logged
  and skipped.

---

## See also

- [SNAFFLER scanner](../scanners/snaffler.md) — the same idea expressed as
  a scanner: targets list + credential, no session-following.
- [SMB client](../clients/smb.md), [FTP client](../clients/ftp.md),
  [SSH client](../clients/ssh.md), [NFSv3 client](../clients/nfs3.md) —
  the four protocols the util can drive.
- [pysnaffler](https://github.com/skelsec/pysnaffler) — the underlying
  rule engine. Custom rules dropped in `rulesdir` follow its format.
- [Snaffler](https://github.com/SnaffCon/Snaffler) — the original C# tool.
