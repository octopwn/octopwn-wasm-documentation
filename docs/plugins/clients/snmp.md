# SNMP Client

The **SNMP Client** is OctoPwn's interactive console for talking to SNMP-enabled devices — routers, switches, printers, server lights-out controllers, anything that exposes a Management Information Base (MIB). It wraps [`puresnmp`](https://github.com/exhuma/puresnmp) and supports SNMP **v1**, **v2c** and (experimentally) **v3** on the standard `UDP/161` port.

SNMP is criminally underused on internal engagements: network appliances are often deployed with the default `public` / `private` community strings still active, and a single GET against the right OID can hand you a list of running processes, installed software, ARP tables, routing tables, local user accounts or even cleartext device configurations. The OctoPwn client is intentionally minimal — single-OID GET, full bulk walks to the console, and bulk walks straight to a file — so you can pivot quickly between targeted lookups and full MIB dumps.

---

## Authentication

SNMP does **not** use NTLM or Kerberos. The `authtype` selector in the session window is mostly framework plumbing here — the actual authentication mechanism is determined by the SNMP version and the credential's secret type.

!!! info "Credentials carry the community string"
    For SNMP **v1** and **v2c**, the credential's *secret* field is the **community string** (`public`, `private`, the vendor's default, the one you found in a config backup, …). Create a credential with secret type `password`, put the community string in the password field, and pick auth protocol `PLAIN` when you create the session.

    For SNMP **v3**, the credential's *username* is the SNMPv3 user, and its *secret* becomes the SHA1 authentication key (see the [Limitations](#limitations-gotchas) section — v3 is registered but currently incomplete).

---

## Features

- **Single-OID GET** for targeted lookups when you already know what you're after.
- **Bulk walks** to enumerate entire MIB sub-trees in one shot.
- **Bulk walks to file** for dumping large sub-trees (full installed-software lists, full process tables, full routing tables) without flooding the console.
- **Multi-version**: SNMP v1, v2c and v3 are all selectable when creating the session.

---

## Prerequisites

1. **A community string or v3 user.** SNMP devices in the wild almost always have at least `public` (read) and `private` (read/write) in their access lists; the [credentials guide](../../user-guide/credentials.md) covers how to add a credential. For v3 you need a username + auth key.
2. **Pick the right SNMP version.** Use the connection-protocol selector to choose `SNMPV1`, `SNMPV2C` or `SNMPV3` (`SNMP` is an alias for `SNMPV2C`). v1 and v2c are wire-incompatible — getting this wrong is the most common cause of silent timeouts.
3. **`login` first.** Unlike the DNS / NTP clients, `login` here actually opens the connection — `get` / `bulkwalk` / `bulkwalkfile` will fail until you've logged in once per session.

---

## Commands

Two command groups: `LOGIN` is just the connection trigger, everything functional lives under `CMD`.

### LOGIN

#### login
Opens the connection to the SNMP server using the session's bound credential. **Must be called first** — every other command needs an open client.

##### Parameters
None — operates on the session's bound target and credential.

---

### CMD

#### get
Performs an SNMP **GET** for a single OID and prints the response value. The response is rendered as a Python `str(value)` — bytes show up as `b'…'`, integers as their decimal form, etc.

##### Parameters
- **command**: The OID to query, in dotted-decimal form (e.g. `1.3.6.1.2.1.1.1.0` for `sysDescr`). The parameter is named `command` in the CLI for legacy reasons; it's the OID.

##### Common OIDs of interest

| OID                          | Description                                          |
| ---------------------------- | ---------------------------------------------------- |
| `1.3.6.1.2.1.1.1.0`          | `sysDescr` — system description (OS / firmware string) |
| `1.3.6.1.2.1.1.5.0`          | `sysName` — system name (hostname)                   |
| `1.3.6.1.2.1.1.6.0`          | `sysLocation` — administratively-set location string |
| `1.3.6.1.2.1.25.1.6.0`       | `hrSystemProcesses` — number of running processes    |
| `1.3.6.1.2.1.25.4.2.1.2`     | `hrSWRunName` — running program names (table)        |
| `1.3.6.1.4.1.77.1.2.25`      | Windows local user accounts (table)                  |
| `1.3.6.1.2.1.6.13.1.3`       | TCP local port table                                 |
| `1.3.6.1.2.1.25.6.3.1.2`     | `hrSWInstalledName` — installed software (table)     |
| `1.3.6.1.2.1.4.22.1.2`       | ARP / IP-to-physical-address table                   |
| `1.3.6.1.4.1.9.2.1.55`       | Cisco running-config download (writeMem) — vendor-specific |

For the table OIDs (anything ending in `.1.<col>`), use [`bulkwalk`](#bulkwalk) instead of `get` — `get` returns the value at one specific row.

#### bulkwalk
Walks the MIB starting at `startoid` and prints every reachable `oid : value` pair to the console as it arrives. Output is buffered in batches of 10 entries to keep the console responsive on long walks.

This is the bread-and-butter command for SNMP recon — point it at a sub-tree and let it dump everything it finds.

##### Parameters
- **startoid**: The OID to start walking from (e.g. `1.3.6.1.2.1` for `mib-2`, `1.3.6.1.4.1` for the enterprise sub-tree). If left empty, defaults to `0` — i.e. walk *everything* the agent will give you.

##### Useful starting points

- `1.3.6.1.2.1.25.4.2.1` — full process table (PID, name, path, parameters).
- `1.3.6.1.2.1.25.6.3.1` — full installed-software list.
- `1.3.6.1.2.1.4.22.1` — full ARP table.
- `1.3.6.1.2.1.4.21` — IP routing table.
- `1.3.6.1.4.1.77.1.2.25` — Windows local users.
- `1.3.6.1.4.1.9.9.46.1.6.1.1.14` — Cisco VLAN names (vendor-specific).

#### bulkwalkfile
Same walk as `bulkwalk`, but the results are streamed to a file instead of the console. Use this for large sub-trees — full MIB dumps, full ARP tables on Layer-3 devices, full process lists from busy hosts — where you don't want hundreds or thousands of lines spamming the console.

##### Parameters
- **startoid**: Same semantics as [`bulkwalk`](#bulkwalk).
- **fname**: Output filename (saved to `/browserefs/volatile`). If left empty, an auto-generated name `bulkwalk_YYYYMMDDHHMMSS.txt` is used. Each `oid : value` pair is written on its own line.

---

## Limitations & gotchas

- **`login` is required.** Calling `get` / `bulkwalk` / `bulkwalkfile` against a session that hasn't logged in will raise `AttributeError: 'NoneType' object has no attribute …` (because `self.client` hasn't been built yet). Run `login` once per session.
- **SNMP v3 is experimental and untested.** The wiring exists (`V3(username, auth=Auth(secret, sha1))`) but the source explicitly carries a `# not tested!!!!!!!` warning and **does not enable privacy** (priv keys are commented out). If you can choose, target v2c; if you must use v3, expect rough edges and a SHA1-only / no-encryption posture for now.
- **Wrong-version-on-wrong-port behaves as a timeout, not an error.** If the device speaks v2c but you connected as `SNMPV1`, you get silent timeouts rather than a protocol-error response. When in doubt, try v2c first.
- **No SET, no TRAP / INFORM listening.** This is a read-only client today — no `SET` for community-string-write abuse (`private` write community → save device config to TFTP, etc.), and no trap / inform receiver. Use `get` and `bulkwalk` only.
