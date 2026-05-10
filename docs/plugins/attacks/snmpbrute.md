# SNMP Community String Brute

The **SNMPBRUTE** attack is OctoPwn's brute-forcer for **SNMPv2c community
strings**. Given one or more targets, it tries a list of candidate community
strings (built-in default of ~150 of the most common ones, or your own list)
against `161/UDP` and stores any hit in the
[Credentials Hub](../../user-guide/credentials.md) for later use with the
[SNMP client](../clients/snmp.md).

The default credential list is the standard "snmp common strings" set
(`public`, `private`, `cisco`, `manager`, `Admin`, `secret`, vendor defaults,
*etc.*) — handy for quick wins; supply your own list when you have a
target-specific dictionary.

---

## How it works

SNMP brute-forcing is unusual because **failed authentication produces no
response** — the agent silently drops the request. There's no
`AUTHENTICATION_FAILED` packet to identify wrong communities; you only ever
see a reply when you guessed correctly. SNMPBRUTE handles this with a
two-phase batched algorithm:

1. **Probe phase.** OctoPwn sends `GetRequest` for `hostnameoid` (default
   `1.3.6.1.2.1.1.1.0` — `sysDescr.0`, the universally readable system
   description) using each candidate community string. Requests are issued
   in batches of 10; after each batch, OctoPwn waits for any response.
   - **No responses** → none of the strings tried so far worked. Continue
     with the next batch.
   - **At least one response** → one of the strings in the consumed
     batches worked. Move to phase 2.
2. **Bisect phase.** Once any string is known to be valid, OctoPwn does a
   **binary-search bisection** over the consumed batches to narrow down
   exactly which string(s) worked, then probes each candidate
   individually to capture the working community.
3. **Hit storage.** Each working community string is added to the Hub:

    ```python
    Credential(
        username = '',
        secret   = <community>,
        stype    = 'password',
        source   = 'SNMPBrute',
        description = 'SNMP community string',
    )
    ```

This bisection trick keeps the total number of UDP packets low even with the
large default credential list — typical run-time per target is a few seconds
on LAN, ~30 s over WAN.

---

## Prerequisites

- **Outbound `161/UDP`** from the agent to the targets (proxy through wsnet
  if needed). UDP unreachables are silently swallowed by the network — if
  the targets are firewalled, the scan completes "successfully" with no
  hits.
- **The targets must run SNMP v1 / v2c.** SNMP v3 (the user-based security
  model) is not in scope — there are no community strings to brute. For
  v3 user discovery / brute, use the [SNMP client](../clients/snmp.md)
  manually or run the [`snmphost`](../scanners/snmphost.md) scanner first
  to fingerprint the SNMP version.

---

## Parameters

### Normal parameters

#### `targets`
List of targets. Standard list / CIDR / file / `all` syntax.

#### `credentials`
List of community strings to try. Default: the built-in
`SNMP_COMMON_STRINGS` set (~150 entries — every common community known to
public dictionaries). Supply your own list (one community per entry,
comma-separated) for targeted brute-force.

### Advanced parameters

#### `protocol`
Default: `SNMP`. Currently always SNMPv2c — the parameter exists for
forward compatibility.

#### `hostnameoid`
Default: `1.3.6.1.2.1.1.1.0` (`sysDescr.0`). The OID OctoPwn `GetRequest`s
to detect a successful auth. Almost every SNMP agent exposes this OID
under its `read-only` view — leave at default unless you have a specific
reason to change it.

The standard `UnCredentialedScannerBaseParameters` set: `maxruntime`,
`resultsfile`, `showerrors`, `timeout`, `workercount`, `wsnetreuse`, plus
`proxy`. Defaults are fine.

---

## Output

```
community
public
private
cisco
```

Each hit lands in the Credentials Hub. Use the credential with the
[SNMP client](../clients/snmp.md) to enumerate everything the agent will
share — interfaces, routing tables, ARP caches, processes, software
inventory, and (with `private` and similar `RW` strings) full
configuration write access on devices that follow the convention.

---

## Pre-flight: fingerprint first

Before throwing the full credential list at every target, run the
[`snmphost`](../scanners/snmphost.md) scanner against the target list with
the most common single string (`public`) to identify which hosts are
actually running SNMP. That cuts the brute-force scope by 90% on most
networks.

```
# Pre-flight in another session window
snmphost> setparam targets 10.0.0.0/24
snmphost> setparam community public
snmphost> scan

# Then SNMPBRUTE only against the hosts that responded.
```

---

## Limitations and caveats

- **SNMP v1 / v2c only.** v3 is out of scope.
- **Only `read` strings are detected.** A device with a
  `read-write`-only string (no `read-only` published) won't return
  `sysDescr.0` to the brute. Set `hostnameoid` to a value that's exposed
  via the device's `RW` view if you suspect this.
- **Retry timing.** UDP packet loss can make a valid community look
  invalid. The two-phase bisection mitigates this somewhat (each
  candidate eventually gets its own retry in phase 2), but on flaky
  networks consider re-running.
- **The `username` field on the resulting credential is empty.** This is
  correct (community strings have no username concept) but trips up
  spreadsheet-style exports — when copying credentials out of the Hub,
  read the `secret` column.
- **Don't brute against your own network without authorization.** SNMPv2c
  community strings are the most common cause of "demonstrating remote
  access via 161 in the engagement scope" — make sure 161 is in scope
  before running this against anything.

---

## See also

- [SNMP client](../clients/snmp.md) — for using the recovered community
  strings (`get`, `walk`, `bulkwalk`, MIB browsing).
- [`snmphost` scanner](../scanners/snmphost.md) — pre-flight host
  discovery (which devices on the subnet actually answer SNMP?).
- [The Hacker Recipes: SNMP](https://www.thehacker.recipes/network-services/snmp)
  — general SNMP enumeration reference.
