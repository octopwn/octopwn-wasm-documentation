# MSSQL Client

The **MSSQL Client** is OctoPwn's interactive interface for Microsoft SQL Server. It speaks the TDS protocol (the same one `sqlcmd` and SSMS use) and gives you the standard SQL toolset — running queries, navigating databases and tables — plus a heavy battery of offensive capabilities: linked-server pivoting, `xp_cmdshell` execution, OLE-automation file transfer, NTLM coercion, dump-the-hashes, and an automated impersonation-graph privilege escalation engine.

---

## Transport

There are **two transports** for the same underlying client:

| Module name | Transport             | Default port | Use it when                                                           |
| ----------- | --------------------- | ------------ | --------------------------------------------------------------------- |
| `MSSQL`     | TCP (TDS)             | `1433`       | The SQL Server is reachable over TCP — the normal case.               |
| `MSSQLPIPE` | TDS over SMB **named pipe** | `445` (SMB) + a named pipe | TCP to the SQL Server is blocked or not exposed, but you can reach the host over SMB. |

Functionally the two are **100% identical** — every command on this page works on both. The only differences are at session-creation time: `MSSQLPIPE` requires a `PIPENAME` parameter (typically `sql\query` for the default instance, or `MSSQL$<INSTANCE>\sql\query` for named instances) and an SMB credential context (`SMBCREDID` / `SMBATYPE`) so the inner SMB connection can authenticate before the TDS handshake takes place over the pipe.

---

## Authentication

MSSQL has historically used **two unrelated authentication models** and OctoPwn exposes both. Picking the wrong one is the single most common reason a session fails to log in, so it is worth taking a moment to get this right.

### `PLAIN` — SQL Server logins (the old "SQL authentication")

Use this when the credential you are presenting is a **SQL Server login**, not a Windows / Active Directory account. Classic examples: `sa`, `dbadmin`, `webapp_user`, or any account that lives **inside** SQL Server's own `master.sys.sql_logins` table and was created with `CREATE LOGIN ... WITH PASSWORD = '...'`.

| Secret type | Description                                           |
| ----------- | ----------------------------------------------------- |
| `password`  | Cleartext SQL login password.                         |
| `none`      | Empty / no password (rarely accepted by real servers). |

!!! warning "`PLAIN` does NOT do NTLM or Kerberos"
    `PLAIN` corresponds to the legacy "SQL Authentication" (sometimes called "Mixed Mode"). It carries the username and password verbatim inside the TDS login record. It will **not** work with NT hashes, Kerberos tickets, or anything else from the AD credential family — for those, pick `NTLM` or `KERBEROS` instead.

### `NTLM` — Domain accounts via NTLM SSP

Use this when the credential is a **Windows / domain account** (`DOMAIN\user`, `user@domain.local`) and you want NTLM to negotiate the authentication.

| Secret type     | Description                                                 |
| --------------- | ----------------------------------------------------------- |
| `password`      | Cleartext password.                                         |
| `pwhex`         | Hex-encoded UTF-16LE password.                              |
| `nt` / `rc4`    | NT hash (pass-the-hash).                                    |
| `agentproxy`    | Remote NTLM signer over the wsnet agent proxy.              |
| `sspiproxy`     | OS SSPI session via the wsnet agent proxy (Windows agent).  |

### `KERBEROS` — Domain accounts via Kerberos

Use this when the credential is a Windows / domain account and you want or need a Kerberos ticket. This is the only auth choice if the SQL Server is configured to require Kerberos (`ALTER SERVER CONFIGURATION SET … LOGIN MODE = KERBEROS_AUTHENTICATION_ONLY`).

| Secret type     | Description                                                 | Example                              |
| --------------- | ----------------------------------------------------------- | ------------------------------------ |
| `password`      | Cleartext password.                                         | `user:Pa55w0rd!`                     |
| `pwhex`         | Hex-encoded UTF-16LE password.                              | `user:70617373…`                     |
| `nt` / `rc4`    | NT/RC4 hash.                                                | `user:aad3b…`                        |
| `aes128`        | AES128 long-term key.                                       | `user:<32-hex>`                      |
| `aes256`        | AES256 long-term key.                                       | `user:<64-hex>`                      |
| `keytab`        | Keytab file in OctoPwn volatile storage.                    | `/browserfs/volatile/svc.keytab`     |
| `keytabb64`     | Base64-encoded keytab inline.                               | `user:<b64>`                         |
| `ccache`        | MIT ccache file in OctoPwn volatile storage.                | `/browserfs/volatile/krb5cc.ccache`  |
| `ccacheb64`     | Base64-encoded ccache inline.                               | `user:<b64>`                         |
| `kirbi`         | `.kirbi` ticket file (Rubeus-style).                        | `/browserfs/volatile/admin.kirbi`    |
| `kirbib64`      | Base64-encoded `.kirbi` inline.                             | `user:<b64>`                         |
| `pfxb64`        | Base64-encoded PFX (PKINIT certificate auth).               | `user:<b64>`                         |
| `agentproxy`    | Remote KDC over the wsnet agent proxy.                      | n/a                                  |
| `sspiproxy`     | OS SSPI session via wsnet agent proxy (Windows agent).      | n/a                                  |

!!! tip "Picking the right `atype` at a glance"
    | The username looks like…             | Pick this `atype`              |
    | ------------------------------------ | ------------------------------ |
    | `sa`, `dbadmin`, `webapp_user`, `internal_etl_user` (no domain prefix, exists inside SQL Server) | `PLAIN`                        |
    | `CONTOSO\jdoe`, `jdoe@contoso.local`, any AD user that maps to `[CONTOSO\jdoe]` server principal | `NTLM` or `KERBEROS`           |
    | A Windows machine account (`CONTOSO\HOST$`)                                                       | `NTLM` or `KERBEROS`           |

---

## GUI experience — the SQL Browser

The MSSQL session window opens on the **SQL Browser** tab by default and is a complete frontend for the database, not a glorified terminal. If you have used SSMS or DBeaver this will feel familiar.

### Layout
- **Left sidebar — Quick Queries**: pre-baked one-click queries for the most common reconnaissance steps — *List Databases*, *Server Version*, *Server Properties*, *Current User*, *Active Connections*. Click one and it loads into the editor; press **Execute** (or `Ctrl+Enter`) to run it.
- **Left sidebar — Database tree**: every database on the server is listed and individually expandable. Expanding a database lazy-loads its tables (with row counts via `sys.tables` ⨯ `sys.partitions`); clicking a table populates the editor with `USE [db]; SELECT TOP 100 * FROM [table];` so you can preview it immediately.
- **Main pane — Monaco SQL editor**: the same editor as VS Code, with SQL syntax highlighting, line numbers, and `Ctrl+Enter` to execute. A **History** dropdown remembers the last 20 queries with their execution time and row count for one-click re-run; **Clear** resets the editor.
- **Main pane — Results grid**: paginated table view (100 rows per page) with sticky headers, NULL highlighting, and one-click **Export TSV** / **Export JSON** of the full result set. Execution time and row count appear next to the title; PRINT / RAISERROR output and TDS errors are surfaced via the console toaster so you don't lose them.
- **Footer console drawer**: an always-available collapsible terminal drawer (drag-resizable) that mirrors all CLI commands, returned text, and server-side `PRINT` / informational messages. You can also type any of the CLI commands documented below directly into it.

### Other tabs in the session window
- **Commands** — clickable buttons for every CLI command, grouped by category. Useful when you want to run something like `dumphashes` without remembering the exact name.
- **Jobs** — long-running background commands and a stop button.
- **History** — full command history for the session.
- **Settings** / **Debug** — connection parameters and protocol-level debug output.

!!! warning "The browser warns you about destructive queries"
    `UPDATE` / `DELETE` statements that lack a `WHERE` clause raise an explicit warning in the toaster before they are sent to the server, but **do not block execution**. There is no transaction wrapping by the browser.

---

## Commands

The CLI surface is organized into the same groups you see in `help`. Every command also returns a structured result for scripting consumption (typically a JSON-serialised cursor); the `to_print` argument controls whether the human-readable form is also written to the console.

### CONNECTION

#### login
Opens the TDS connection (over TCP for `MSSQL`, over the SMB pipe for `MSSQLPIPE`), performs the authentication exchange selected by the session's `atype`, and starts a connection-monitor task that auto-fires `logout` if the server drops the connection. After login the prompt is updated to `[<system_user>@<server-link-chain>]:<database>$` so you always know who you are and where you are.

#### logout
Disconnects the TDS session, cancels the connection monitor, and resets internal state (the linked-server chain in particular). Always returns the prompt to the disconnected state, even on error.

---

### QUERY

#### query
Sends a raw T-SQL statement to the server and prints the result through `tabulate`. If a [`uselink`](#uselink) chain is active, the query is automatically wrapped in nested `EXEC ('…') AT [linked_server]` calls so that it executes on the deepest server in the chain.

##### Parameters
- **sql**: The T-SQL statement (or batch — `;`-separated statements work).
- **to_print** *(optional, bool, default `True`)*: Whether to print the formatted result table.

#### queryfile
Reads a `.sql` file from the OctoPwn volatile filesystem and executes its contents as a single batch. Useful for canned recon scripts. Path follows the standard OctoPwn workdir conventions.

##### Parameters
- **file**: Path to the SQL file.

---

### ENUM

A curated set of recon queries against `sys.*` views. All of them honour the active linked-server chain so they can be used to enumerate any server reachable through one or more hops.

| Command           | What it returns                                                                                      |
| ----------------- | ---------------------------------------------------------------------------------------------------- |
| `enumdatabases`   | All databases plus their `is_trustworthy_on` flag (relevant for [PRIVESC](#privesc)).                |
| `enumlogins`      | All server-level principals from `sys.server_principals` joined with `syslogins` to surface server-role memberships (`sysadmin`, `securityadmin`, `serveradmin`, `setupadmin`, `processadmin`, `diskadmin`, `dbcreator`, `bulkadmin`). |
| `enumusers`       | All database users in the current database via `sys.sysusers`, with each user's mapped server login. |
| `enumusers2`      | Same target as `enumusers` but using `EXEC sp_helpuser` instead — different output shape, sometimes more readable. |
| `enumtables`      | All tables across all online user databases (excluding `master`, `model`, `msdb`, `tempdb`).         |
| `enumowner`       | Databases and the login that owns each one — a quick `db_owner` ⇒ `sysadmin` chain search.           |
| `enumimpersonate` | All `IMPERSONATE` permissions visible at both database and server level. Pre-cursor for [PRIVESC](#privesc). |
| `enumlinks`       | All linked servers (`sp_linkedservers`) and their stored credential mappings (`sp_helplinkedsrvlogin`). The basis for [`uselink`](#uselink) pivoting. |
| `ridbrute`        | Brute-forces RIDs (default 0–4000) against the SQL Server's domain to enumerate domain principals via `SUSER_SNAME(SID_BINARY(...))`. **Requires** the SQL Server to be domain-joined. Optional `max_rid` argument. |

##### Parameters (all `enum*` commands except `ridbrute`)
- *(none — they take no arguments)*

##### `ridbrute` parameters
- **maxrid** *(optional, int, default `4000`)*: Highest RID to test. Higher values find more accounts at the cost of more queries.

---

### FORMAT

Formatting and output-redirection knobs for the current session. None of these touch the server.

#### settableformat
Changes how query results are rendered to the console. Accepts any format name supported by Python's `tabulate` library (`grid`, `plain`, `simple`, `github`, `fancy_grid`, `psql`, `html`, `latex`, etc.). An invalid value lists all valid names instead of changing anything.

##### Parameters
- **tablefmt**: The format name.

#### gettableformat
Prints the currently active table format.

#### showquery / hidequery
Toggle whether each `query` echoes the literal SQL text it is about to send (useful when debugging the linked-server chain wrapping). Defaults to hidden.

#### setfileout
Redirects future query output to a file in the OctoPwn volatile filesystem. The full `tabulate`-rendered result is written verbatim instead of being printed to the console. One file per `query` invocation — the file is overwritten each time.

##### Parameters
- **file**: Path to the output file.

#### showfileout
Prints the currently configured output file path (or `None`).

#### clearfileout
Disables the file-output redirection — query output goes back to the console.

---

### IMPERSONATE

`EXECUTE AS` helpers. After running one of these, every subsequent `query` runs in the impersonated context until you `REVERT` (which you can do with a manual `query "REVERT;"`).

#### executeasuser
Issues `EXECUTE AS USER = '<user>'` — switches to a database user. The user must exist in the current database and the session must hold `IMPERSONATE` on that user.

##### Parameters
- **user**: Database user name to impersonate.

#### executeaslogin
Issues `EXECUTE AS LOGIN = '<user>'` — switches to a server login. The login must exist on the server and the session must hold server-level `IMPERSONATE` on that login.

##### Parameters
- **user**: Server login name to impersonate.

!!! info "Inside an active link chain"
    When a [`uselink`](#uselink) chain is active, `executeasuser` / `executeaslogin` do **not** send their statement to the server — they update the `EXEC ('<user> <query>') AT <server>` wrapper used for the deepest hop, so subsequent queries impersonate the given principal **on the linked server** instead.

---

### LINK

Pivot through MSSQL **linked servers** — a built-in DBA feature that maps another SQL Server (or any OLE-DB source) to a name and lets you run queries against it via `EXEC ('…') AT [server]`. OctoPwn lets you nest the wrappers so a single query reaches an arbitrary depth of pivots.

#### uselink
Pushes a linked server onto the chain. Subsequent queries are wrapped in `EXEC` calls that route them through every server on the chain in order. Two special arguments reset the chain:

- `uselink localhost` — pop the entire chain, queries run locally again.
- `uselink ..` — pop just the deepest hop.

##### Parameters
- **server**: Linked-server name (as shown by `enumlinks` in the [ENUM](#enum) group), `localhost`, or `..`.

#### execonlink
One-shot version of [`uselink`](#uselink) — runs a single SQL statement on a named linked server without altering the active chain.

##### Parameters
- **server**: Linked-server name.
- **sql**: The T-SQL statement to run on the linked server.

#### xpcmdshellonlink
Convenience wrapper for `EXEC ('xp_cmdshell ''<command>''') AT [server]` — runs an OS command on a linked server without changing the active chain. Requires `xp_cmdshell` to be enabled on that linked server (you can use [`enablexpcmdshell`](#enablexpcmdshell) via [`uselink`](#uselink) first).

##### Parameters
- **server**: Linked-server name.
- **command**: The OS command to run via `xp_cmdshell`.

---

### FILE

Remote filesystem helpers using SQL Server's built-in extended stored procedures and OLE Automation. Most of these need `sysadmin` or specific extended-procedure permissions.

#### xpdirtree
Recursive directory listing via `xp_dirtree`. Famously useful for **NTLM coercion** — pointing it at a UNC path (`\\attacker\share`) makes the SQL Server account authenticate to the listener. Listed here for the local case; for the coercion-only case there is the dedicated [`coerce`](#coerce) command.

##### Parameters
- **path**: Local path or UNC path.

#### xpfileexist
Checks whether a single file or directory exists on the SQL Server using `xp_fileexist`. Returns and prints a friendly `File EXISTS` / `does NOT exist` line.

##### Parameters
- **path**: Local or UNC path.

#### putfile
Uploads a local file to the SQL Server's filesystem via OLE Automation (`sp_OACreate ADODB.Stream`). Auto-enables the *Ole Automation Procedures* server-level configuration (which is normally off by default). After the upload it issues an `xp_fileexist` check and reports the verification result.

##### Parameters
- **localpath**: Path to the local file.
- **remotepath**: Destination path on the SQL Server (Windows-style, e.g. `C:\Windows\Temp\implant.exe`).

!!! warning "Requires `sysadmin` and is loud"
    OLE Automation Procedures are off by default and turning them on requires `sysadmin`. The setting is left **enabled** after the upload — re-disable it with `query "EXEC master.dbo.sp_configure 'Ole Automation Procedures', 0; RECONFIGURE;"` if you care about leaving things as you found them. The whole sequence is also a well-known IDS / EDR pattern.

#### getfile
Downloads a file from the SQL Server using `OPENROWSET(BULK …, SINGLE_BLOB)`. Returns the binary contents and writes them to the given local path.

##### Parameters
- **remotepath**: Source path on the SQL Server.
- **localpath**: Destination path in the OctoPwn volatile filesystem.

!!! warning "Requires `BULK` permission (typically `sysadmin`)"
    `OPENROWSET BULK` requires either `sysadmin` or the `ADMINISTER BULK OPERATIONS` server permission. Without it the read fails with a permission error.

---

### CMD

OS command execution and the configuration knobs around it.

#### xpcmdshell
Runs an OS command on the SQL Server via the legendary `xp_cmdshell` extended stored procedure. Requires `xp_cmdshell` to be enabled at the server level — see [`enablexpcmdshell`](#enablexpcmdshell).

##### Parameters
- **command**: The OS command to execute (`whoami`, `powershell -enc <b64>`, etc.).

#### enablexpcmdshell
Turns on `xp_cmdshell` server-wide by calling `sp_configure 'show advanced options', 1; RECONFIGURE; sp_configure 'xp_cmdshell', 1; RECONFIGURE;`. Requires `sysadmin`.

#### disablexpcmdshell
The mirror image of `enablexpcmdshell` — turns it off again. Run this when you're done.

#### checkadmin
Checks whether the current effective principal is a member of the `sysadmin` server role (`SELECT IS_SRVROLEMEMBER('sysadmin')`). Useful right after [`uselink`](#uselink) or `EXECUTE AS` to know whether you can call the destructive commands.

---

### COERCE

Forces the SQL Server's service account to authenticate to a host you control over UNC, capturing the resulting NTLM exchange (or relaying it). The command iterates through a curated catalog of T-SQL statements that touch UNC paths in different ways — different statements are blocked by different permission checks, so trying multiple modules increases the odds of getting at least one auth attempt out.

#### coerce
Iterates the chosen module(s) and reports per-statement success / failure. Even one accepted statement is enough to land an NTLM hash on your listener.

##### Modules
- `fileaccess` — `xp_dirtree`, `xp_fileexist`, `xp_subdirs`, `sys.dm_os_file_exists`. **Works without sysadmin in many configurations** — try this one first.
- `backup` — `BACKUP` and `RESTORE` to a UNC `DISK = '\\…'`. Needs DB-level permissions on a target database; the bundled set uses `[TESTING]` — adjust to a database you can actually access if needed.
- `bulk` — `BULK INSERT`, `OPENROWSET`, `OPENDATASOURCE`. Needs `ADMINISTER BULK OPERATIONS` or `sysadmin`.
- `crypto` — `CREATE ASSEMBLY`, `CREATE CERTIFICATE … FROM EXECUTABLE FILE`, `BACKUP MASTER KEY`, etc. Needs `CONTROL SERVER` for some, `db_owner` for others.
- `audit` — `sys.fn_xe_file_target_read_file`, `fn_get_audit_file`, `fn_trace_gettable`, `CREATE SERVER AUDIT`. Mostly `sysadmin`.
- `misc` — exotic ones: `DBCC checkprimaryfile`, `CREATE CRYPTOGRAPHIC PROVIDER`, `CREATE EXTERNAL FILE FORMAT`, `xp_cmdshell 'dir …'`, `fn_dump_dblog`.
- `all` — runs every module above in sequence.

##### Parameters
- **target**: The host (or IP) to coerce the SQL Server to authenticate to. Used as `\\<target>\share` in every statement.
- **module** *(optional, str, default `all`)*: One of the module names above, or `all`.

!!! tip "Set up the listener first"
    Start the [Relay server](../servers/relay.md), [LLMNR](../servers/llmnr.md) / [mDNS](../servers/mdns.md) poisoning, or any responder-style listener on `target` **before** running `coerce`, otherwise the captured authentication will be lost.

---

### PRIVESC

Automated `sysadmin` escalation: builds a graph of who-can-impersonate-whom and who-owns-what, walks it for a path that ends in either `sysadmin` or `db_owner` on a `TRUSTWORTHY` database whose owner is `sysadmin`, and (when the operator says go) exploits it. Cleanup is automatic but optional.

#### enumpriv
Builds the impersonation graph and reports the discovered escalation path (if any). Caches the chosen target so the `privesc` command (below) can exploit it without recomputing.

Two exploitation methods are recognised:

1. **Impersonation chain** — there exists a sequence `current_user → grantor_1 → … → grantor_n` where `grantor_n` is `sysadmin` and each step has `IMPERSONATE` on the next. The chain is encoded as a series of `EXECUTE AS LOGIN` statements followed by `EXEC sp_addsrvrolemember <current_user>, 'sysadmin'`.
2. **TRUSTWORTHY db_owner** — the current user (or someone reachable via impersonation) is `db_owner` of a database whose `is_trustworthy_on = 1` and whose owner is a `sysadmin`. A stored procedure with `WITH EXECUTE AS OWNER` runs `sp_addsrvrolemember` at sysadmin level inside that database.

#### privesc
Exploits the path cached by [`enumpriv`](#enumpriv). After the call, re-checks whether the current user is now `sysadmin` and reports success or failure. **Run [`enumpriv`](#enumpriv) first** — `privesc` refuses to run with no cached path.

#### privescrollback
Removes the `sysadmin` server role from the current user via `sp_dropsrvrolemember`, then re-checks. Run this after you're done — leaving the role in place is the kind of thing that gets noticed.

---

### DUMP

#### dumphashes
Reads the password-hash column from `master..sysxlogins` (legacy) or `master.sys.sql_logins` (modern), classifies each hash by prefix (`MSSQL-1731` / `MSSQL-132` / `MSSQL-131`), and stores them as credentials in the OctoPwn credential store for offline cracking with hashcat or similar. Requires `sysadmin`.

Returned hashes correspond to **SQL Server logins** — they can later be replayed against MSSQL with `PLAIN` auth, or cracked to recover the cleartext password.

---

## Limitations

- **Pick the right `atype`.** `PLAIN` is for SQL Server logins (`sa`, `dbadmin`, …); `NTLM` / `KERBEROS` is for AD accounts. Mixing them up is the most common source of "login failed for user".
- **`MSSQLPIPE` needs SMB.** If both TCP/1433 and SMB/445 are blocked, you cannot reach the server from this client at all.
- **`enumtables` skips `master`, `model`, `msdb`, `tempdb`.** Query them via `query` directly if you actually need them.
- **`ridbrute` needs a domain-joined SQL Server.** `DEFAULT_DOMAIN()` returning empty / NULL means the server is in a workgroup or the principal cannot read its domain — the command bails out with an explanatory message.
- **`putfile` leaves *Ole Automation Procedures* enabled.** It is turned on automatically and never turned off again. Reset it manually if cleanliness matters.
- **`getfile` requires `BULK` permission**, typically `sysadmin` — without it, the read fails with a permission error.
- **`xp_cmdshell` is disabled by default on modern SQL Server.** Run [`enablexpcmdshell`](#enablexpcmdshell) before `xpcmdshell` (and remember to [`disablexpcmdshell`](#disablexpcmdshell) when done).
- **`coerce` is loud.** Each statement is a fingerprintable pattern (`UNC` paths in `xp_dirtree`, `BACKUP DATABASE TO DISK = '\\…'`, …). Use it deliberately.
- **`privesc` modifies `sysadmin` membership and may create a stored procedure.** It tries to clean up after itself, but a network glitch in the middle leaves residue. Always pair it with [`privescrollback`](#privescrollback).
- **No transaction wrapping.** Neither the SQL Browser nor the CLI wraps queries in transactions — `BEGIN TRANSACTION` / `ROLLBACK` is the operator's responsibility.
