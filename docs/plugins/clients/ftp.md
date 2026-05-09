# FTP Client

The **FTP Client** speaks plain File Transfer Protocol (RFC 959) against FTP servers. It wraps [`asyncftp`](https://github.com/skelsec/asyncftp) and provides the standard set of FTP commands — connection management, navigation, file operations, server-side metadata queries — together with an escape hatch for sending arbitrary FTP control-channel commands.

The client is intentionally minimal. There is no graphical file browser equivalent to the SSH or NFS3 clients; everything is done from the console (or the auto-generated Commands tab in the session window). Default port `21`.

---

## Authentication

The client supports a single authentication protocol (`PLAIN`) with two credential variants.

| `atype` | Secret type | Description                                                            | Example                  |
| ------- | ----------- | ---------------------------------------------------------------------- | ------------------------ |
| `PLAIN` | `password`  | `USER` + `PASS` exchange with a username and password.                 | `username:Pa55w0rd!`     |
| `PLAIN` | `none`      | Anonymous login — typically `USER anonymous` + an empty / dummy `PASS`. | n/a                      |

There is no support for FTP over TLS (`FTPS` / explicit `AUTH TLS` / implicit FTPS on port 990), nor for any GSSAPI / Kerberos extensions. For SSH-tunnelled file transfer use the [SSH client](./ssh.md) and its SFTP support, which is a separate protocol.

!!! warning "Credentials travel in cleartext"
    Plain FTP transmits the username, password, and all subsequent control- and data-channel traffic without encryption. Treat any FTP session as observable on the wire.

---

## Connection model

A successful `login` opens a single TCP control connection to the server, performs the authentication exchange, prints the server banner, and leaves the session ready for command issuance. Data-bearing commands (`list`, `get`, `put`) negotiate a fresh **passive-mode** data connection per call.

The server's session-level current working directory is held server-side; OctoPwn tracks it implicitly via the `cwd` / `cdup` / `pwd` commands. There is no client-side cache of directory entries.

!!! note "Only passive mode is supported"
    The FTP client currently supports passive-mode (`PASV` / `EPSV`) data connections only. Active-mode (`PORT` / `EPRT`) data connections are not implemented, and the client cannot fall back to active mode if the server refuses passive. Servers configured to accept active mode only are not reachable.

---

## Command aliases

The following short aliases map to their canonical command name. They are intended for users familiar with POSIX shell conventions.

| Alias  | Resolves to |
| ------ | ----------- |
| `cd`   | `cwd`       |
| `ls`   | `list`      |
| `rm`   | `delete`    |
| `mv`   | `rename`    |

---

## Commands

### CONNECTION

#### login
Opens the control connection to the FTP server, performs the `USER` / `PASS` exchange against the bound credential, and prints the server banner.

#### logout
Sends `QUIT` to the server, closes the control connection, and resets the session state. Safe to call when no connection is active.

---

### NAVIGATION

#### cwd
Changes the server-side current working directory. Aliased as `cd`.

##### Parameters
- **path**: Target directory (absolute or relative to the current directory).

#### cdup
Moves the server-side current working directory up one level (FTP `CDUP`).

#### pwd
Prints the server-side current working directory (FTP `PWD`).

---

### FILE OPERATIONS

#### list
Lists the contents of the current server-side directory using the FTP `LIST` command. The returned format is server-defined (typically a `ls -l`-style listing on UNIX servers, a different format on Windows IIS servers, etc.). Aliased as `ls`.

#### get
Downloads a file from the FTP server into OctoPwn's working directory.

##### Parameters
- **remotepath**: Path of the file on the FTP server.
- **localpath** *(optional)*: Destination path inside OctoPwn's working directory. If omitted, the file is saved under the same basename as the remote path. Both supplied and derived paths are jailed to the working directory; attempts to escape (`..`, absolute paths outside workdir) are rejected.

#### put
Uploads a local file to the FTP server using `STOR` (overwrites the remote file if it already exists).

##### Parameters
- **localpath**: Source file inside OctoPwn's working directory (jailed — paths outside workdir are rejected).
- **remotepath** *(optional)*: Destination path on the FTP server. If omitted, the file is uploaded under the local basename in the server's current working directory.

#### rename
Renames a file or directory on the server (FTP `RNFR` + `RNTO`). Aliased as `mv`.

##### Parameters
- **oldpath**: Existing path on the server.
- **newpath**: New path on the server.

#### delete
Deletes a file on the server (FTP `DELE`). Aliased as `rm`. For directories, use [`rmdir`](#rmdir).

##### Parameters
- **path**: Path of the file to delete.

#### mkdir
Creates a directory on the server (FTP `MKD`).

##### Parameters
- **path**: Path of the directory to create.

#### rmdir
Removes a directory on the server (FTP `RMD`). The directory must be empty.

##### Parameters
- **path**: Path of the directory to remove.

#### size
Returns the size of a file in bytes via the `SIZE` extension command. Note that `SIZE` is an extension (RFC 3659) and is not supported by every server — check [`feat`](#feat) first if in doubt.

##### Parameters
- **path**: Path of the file on the server.

---

### INFO

#### feat
Lists the FTP extensions advertised by the server via the `FEAT` command (e.g. `MLSD`, `MLST`, `SIZE`, `MDTM`, `UTF8`, `AUTH TLS`). Useful for confirming whether features such as `SIZE` or extended directory listings are available before relying on them.

#### syst
Returns the server's reported operating system identifier via the `SYST` command (e.g. `UNIX Type: L8`, `Windows_NT`).

#### stat
Returns a server-defined status string via the `STAT` command. Without arguments, this typically returns connection-wide information (server uptime, current user, transfer mode).

#### rhelp
Asks the server for help text via the `HELP` command. With no argument, the server returns its supported commands; with a command name, it returns help for that specific command. The local OctoPwn `help` command is unaffected.

##### Parameters
- **command** *(optional)*: A specific FTP command name (e.g. `RETR`, `STOR`, `LIST`).

---

### RAW

#### rawcmd
Sends an arbitrary line on the control connection and returns the server's response. Intended for issuing FTP commands that do not have a dedicated wrapper (e.g. `MDTM`, `OPTS UTF8 ON`, vendor-specific extensions). The command line is sent verbatim — no quoting or escaping is applied.

##### Parameters
- **command**: The raw FTP command line (e.g. `MDTM /pub/file.bin`, `OPTS UTF8 ON`, `SITE CHMOD 644 /pub/file.bin`).

!!! warning "No correlation with data-channel commands"
    `rawcmd` only handles the control-channel exchange. Commands that require a data connection (`RETR`, `STOR`, `LIST`, `NLST`, `MLSD`) will start the transfer server-side but the data will not be read or written by `rawcmd` itself — use the dedicated wrappers (`get`, `put`, `list`) for those.

---

## Limitations

- **Plain FTP only.** No FTPS (explicit `AUTH TLS` or implicit on port 990). Credentials and data travel in cleartext.
- **No GSSAPI / Kerberos.** The only supported authentication is `USER` / `PASS` with a password or anonymous credential.
- **Passive mode only.** Active-mode (`PORT` / `EPRT`) data connections are not implemented; servers that accept active mode only are not reachable. See the [Connection model](#connection-model) note above.
- **No transfer resume.** `get` and `put` are single-pass; partial transfers cannot be restarted via `REST`.
- **No transfer-mode switching exposed.** The library handles `TYPE` internally; there is no command to explicitly toggle between ASCII and binary mode.
- **No SFTP.** SFTP is an SSH subsystem, not FTP. Use the [SSH client](./ssh.md) for SFTP transfers.
- **No graphical file browser.** Browsing is done via `cwd` / `list`. The session window's Commands tab provides a visual launcher for individual commands but not a tree view.
- **Server-defined `list` format.** The `LIST` output is whatever the server emits; there is no client-side parser exposed via the CLI. For machine-readable listings, prefer servers that support `MLSD` / `MLST` (advertised by `feat`) and use `rawcmd` to invoke them, or rely on the GUI's directory listings which use `MLSD` internally.
