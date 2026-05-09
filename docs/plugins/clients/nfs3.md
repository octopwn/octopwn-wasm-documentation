# NFS3 Client

The **NFS3 Client** speaks NFS version 3 against UNIX-style file servers. It wraps [`anfs`](https://github.com/skelsec/anfs) and exposes both a CLI for scripted file operations and — as with the SSH client — a **graphical filesystem browser**, which is the default tab when the session opens.

NFSv3's connection model differs significantly from SMB or SFTP, and its authentication model has practical limitations that are worth understanding before working with the client. The following sections cover both, then describe the GUI and the available CLI commands.

---

## NFSv3 protocol overview

Unlike SMB (one TCP connection, name-the-share, browse) or SSH+SFTP (one connection, one subsystem), an NFSv3 conversation involves **three separate RPC programs** that are typically queried in sequence:

| Step | RPC program       | What it tells you                                              | Default port            |
| ---- | ----------------- | -------------------------------------------------------------- | ----------------------- |
| 1    | **portmap / rpcbind** (program 100000) | Which programs the server runs and on which ports.             | TCP/UDP **111**         |
| 2    | **mountd** (program 100005)            | Which directories (`exports`) you're allowed to mount, and gives you a per-mount **file handle** that's needed for everything else. | Dynamic (look it up via portmap) |
| 3    | **nfs** (program 100003)               | Actual filesystem operations (`READDIR`, `READ`, `LOOKUP`, etc.) using that file handle. | Usually TCP/UDP **2049** |

So a typical session, in OctoPwn's terms, walks like this:

1. **Open the session** — pointing at the NFS server's portmapper port (default `111`). Connection settings let you set the target host and pick a proxy if you need to pivot.
2. **`login`** — connects to mountd via portmap and validates that the connection can be established.
3. **`mounts`** — asks mountd for the list of exported directories. **This is the equivalent of "list shares"** — without it you don't know what mountpoints are available.
4. **`mount <path>`** — picks a specific export, gets the root file handle for it, and connects to the NFS service. The session prompt switches to `[<mountpoint>]>`.
5. **Walk the filesystem** with `ls`, `cd`, `get`, `mkdir`, etc.

The GUI mirrors the same flow under the hood: opening the **Files** tab triggers a `remoteMounts` to enumerate exports, and double-clicking one mounts it transparently.

!!! tip "If `mounts` returns nothing"
    Either the server has zero exported directories visible to anonymous clients, or you can reach mountd but not the actual NFS port (firewall between them is common). Try [`services`](#services) — if portmapper says NFS is on `2049` but you can't actually mount anything, it's almost always a firewall in the middle.

---

## Authentication

NFSv3's authentication is performed at the RPC layer using one of several **credential flavours** (`AUTH_NULL`, `AUTH_SYS`, `RPCSEC_GSS`, etc.) attached to every request. The OctoPwn NFS3 client supports two of these flavours, with a known limitation on the more capable of the two.

| `atype` | What is sent on the wire                                                                                                                                                                                       | Server-side conditions for success                                                                       |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `NONE`  | `AUTH_NULL` — empty credential, no identity claim.                                                                                                                                                             | The export permits anonymous access.                                                                     |
| `SYS`   | An `AUTH_SYS` credential populated with `uid=0`, `gid=0`, no auxiliary GIDs, and machine name `"anfs"`. The credential metadata bound to the session (`uid`, `gid`, `gids`, `machinename`) is currently ignored. | The export permits root access (`no_root_squash`), or the server maps the presented uid to a local user. |

!!! note "Credential metadata is not currently propagated"
    The `SYS` flavour does not yet honour the bound credential's `uid` / `gid` / `gids` / `machinename` fields and always presents `uid=0`. A corresponding `#TODO: multiple auth types, SYS should be having parameters` lives in `octopwn/common/connectionhelpers/factory.py:get_nfs_factory`. Until that work is completed, selecting `SYS` is equivalent to authenticating as the server's local `root` user.

!!! note "RPCSEC_GSS (Kerberos) is not supported"
    The client does not implement `RPCSEC_GSS`, so exports configured with `sec=krb5`, `sec=krb5i`, or `sec=krb5p` cannot be accessed.

### Practical outcomes per export configuration

- **`no_root_squash`** — `SYS` is treated as the server's local `root`. Full read/write access is typically available.
- **`root_squash`** (the default on most distributions) — root is remapped to the anonymous user (usually `nobody`). World-readable files can be read; writes that require ownership will fail with `EACCES`. Accessing files owned by a specific local user requires presenting that user's uid, which is not currently supported.
- **`all_squash`** — every request is mapped to the anonymous user regardless of the presented uid.
- **`sec=krb5*`** — connections cannot be established.

---

## Privileged source ports are not supported

Most NFS servers — Linux included, by default — accept client connections only from a **privileged source port** (`< 1024`). This is enforced via the `secure` export option, which is the default.

OctoPwn does not currently bind to privileged source ports. The WASM/browser runtime has no socket-bind capability, and the Enterprise server runtime does not assume `CAP_NET_BIND_SERVICE` either. As a result, connecting to an export that enforces `secure` will fail. Common symptoms include:

- The portmap query (`111`) succeeds, but `mounts` returns an error.
- `mount <path>` returns an `mount3err_acces` / "permission denied" response even against an otherwise unrestricted export.
- The server resets the TCP connection.

There is no client-side workaround at this time. The only way to make such an export reachable is to disable the privileged-port requirement on the server side (the `insecure` export option in Linux's `/etc/exports`, applied with `exportfs -ra`).

---

## Session window (the GUI experience)

| Tab          | What it is                                                                                                                                                                                                  |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Files**    | **Default tab.** A full NFSv3 file browser — directory tree, multi-select, drag-and-drop upload, download (single or batch), in-browser view for text/PDF, right-click context menu. Mountpoint discovery happens transparently — you'll see exports as top-level entries on the left. |
| **Commands** | Auto-generated visual command runner — every entry under `help_groups['COMMANDS']` shows up as a button with parameter inputs.                                                                              |
| **Jobs**     | Live table of running operations with PIDs and per-row Stop buttons.                                                                                                                                        |
| **History**  | Scrollable command history with screenshot-output for reporting.                                                                                                                                            |
| **Settings** | Editor for the session parameters (target, atype, timeout, port, …).                                                                                                                                         |
| **Debug**    | Raw protobuf inspector — turns red when active, otherwise hidden.                                                                                                                                            |
| **Console**  | Collapsible bottom drawer — same console as the CLI.                                                                                                                                                         |

!!! tip "Use the file browser"
    The CLI commands below are great for scripting and quick checks, but for actually browsing, downloading, and uploading files the **Files** tab is much faster — it does the `mounts` / `mount` / `readdirplus` plumbing for you and supports drag-and-drop.

---

## CLI commands

Six command groups, all callable from the console drawer or the Commands tab.

### CONNECTION

#### login
Connects to mountd through portmap and validates the connection. Required before any other command.

#### logout
Disconnects from the mount service.

---

### SERVICES

#### services
Dumps **portmapper's program registration table** — i.e. which RPC programs the server is offering and which ports they're listening on. Useful for confirming that NFS (`100003`) and mountd (`100005`) are actually exposed before you start poking at them, and for spotting non-standard ports (some hardened servers put NFS on a port other than 2049).

This does **not** require `login` — it's a portmap-only query.

##### Parameters
None.

---

### MOUNT

#### mounts
Asks mountd for the list of exported directories — the NFS equivalent of "list shares". Caches the result for `mountinfo`. **You almost always want to run this first** to know what to feed into `mount`.

##### Parameters
None.

#### mountinfo
Prints the cached export details from the most recent `mounts` call (host restrictions, allowed clients per export, etc.). If `mounts` hasn't been run yet it'll prompt you to do so.

##### Parameters
None.

#### mount
Picks a specific export, asks mountd for the root file handle, and opens an NFS connection to the file service. Switches the session into "browsing this mountpoint" mode (the prompt changes to `[<mountpoint>]>`). Subsequent `ls` / `cd` / `get` / `mkdir` / etc. operate inside this mountpoint.

##### Parameters
- **mountpoint**: The export path as returned by `mounts` (e.g. `/srv/share`, `/export/home`, `/mnt/data`).

---

### TRAVERSAL

#### ls
Lists the current directory. Output includes type, size, mtime, owner uid/gid, and (for symlinks) the resolved link target. Symlinks are auto-resolved during the underlying `readdirplus` call.

##### Parameters
None.

#### cd
Changes into a subdirectory of the current directory. **Only entries that were present in the most recent listing can be cd'd into** — if a new directory has appeared on the server since the last `ls`, you need [`refreshcurrentdir`](#refreshcurrentdir) first.

##### Parameters
- **dirname**: A directory name from the current `ls` listing.

#### refreshcurrentdir
Re-reads the current directory from the server, refreshing the cached file/directory tables. Run this if you've created files outside OctoPwn or if the server's contents have changed.

##### Parameters
None.

---

### FILEOPS

#### get
Downloads a file from the current directory into OctoPwn's working directory under the same basename. The destination path is **jailed to the working directory** — a hostile NFS server returning entries with `..` in their names can't escape into your local filesystem.

##### Parameters
- **filename**: A file name from the current `ls` listing.

!!! info "No CLI upload command"
    There is no console command for uploading a local file. The available filesystem-mutating commands are `mkdir`, `rmdir`, `rm`, `touch`, and `symlink`. To upload file contents, use the **Files** tab in the GUI.

#### mkdir
Creates a new directory under the current directory. Auto-refreshes the listing afterwards.

##### Parameters
- **dirname**: New directory name.

#### rmdir
Removes a directory from the current directory. Must be empty (NFSv3 RMDIR semantics). Auto-refreshes the listing afterwards.

##### Parameters
- **dirname**: A directory name from the current `ls` listing.

#### rm
Removes a file from the current directory. Auto-refreshes the listing afterwards.

##### Parameters
- **filename**: A file name from the current `ls` listing.

#### touch
Creates an empty regular file in the current directory (NFSv3 `CREATE` with `mode=GUARDED`).

##### Parameters
- **filename**: New file name.

#### symlink
Creates a symbolic link in the current directory pointing at an arbitrary target. Symlink targets are stored as raw strings on the server side — they don't need to actually exist. **This is a frequent privilege-escalation primitive on poorly-configured NFS servers** (e.g. dropping a symlink that points outside the export to coerce a privileged client into following it).

##### Parameters
- **filename**: The link target (the string the symlink resolves to when followed).
- **linkname**: The name of the symlink to create in the current directory.

#### readlink
Reads the target of a symbolic link in the current directory.

##### Parameters
- **filename**: A symlink name from the current `ls` listing.

---

### FILESYSTEM

#### fsinfo
Returns the underlying filesystem's NFSv3 `FSINFO` reply for the file's mount — read/write transfer size hints, max file size, time delta, supported attribute mask, etc. Useful when planning large-file transfers or diagnosing client/server transfer-size mismatches.

##### Parameters
- **filename**: A file or directory name from the current `ls` listing.

#### fsstat
Returns the underlying filesystem's NFSv3 `FSSTAT` reply — total, free, and available bytes and files. Useful for confirming that there is enough space available before initiating large writes.

##### Parameters
- **filename**: A file or directory name from the current `ls` listing.

---

## Limitations

- **NFSv3 only.** NFSv4, NFSv4.1, and pNFS are not supported. NFSv4 does not expose `mountd` as a separate RPC program, so v4-only servers will not respond to the v3 mount calls used by this client.
- **Authentication is limited to `AUTH_NULL` and `AUTH_SYS`.** `RPCSEC_GSS` (Kerberos) is not supported. The `AUTH_SYS` flavour does not currently honour the bound credential's `uid`, `gid`, `gids`, or `machinename` and always presents `uid=0` (see [Authentication](#authentication)).
- **Privileged source ports are not supported.** Exports requiring source ports below 1024 (the default `secure` export option) cannot be reached. The only available workaround is to disable the requirement on the server side.
- **No CLI upload.** `get` is available for downloads; uploads must be performed through the **Files** tab.
- **`cd` is cache-bound.** Only entries present in the most recent directory listing can be navigated into. Use [`refreshcurrentdir`](#refreshcurrentdir) to reload the listing.
- **`mountinfo` depends on `mounts`.** It reads from the cache populated by the most recent `mounts` invocation.
- **One active mountpoint per session.** `mount` switches the active mountpoint; the CLI does not support multiple concurrent mountpoints in a single session. (The GUI works around this by opening short-lived connections per browsed directory.)
- **Symlinks are resolved client-side during `ls`.** Listings of directories containing symlinks pointing at slow or unreachable targets may stall while individual `readlink` calls time out.
- **`services` does not require `login`.** Because it only queries portmap, it can be used as a reachability probe before establishing a full NFS session.
