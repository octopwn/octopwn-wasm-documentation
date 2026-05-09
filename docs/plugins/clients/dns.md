# DNS Client

The **DNS Client** is a thin wrapper around [unidns](https://github.com/skelsec/unidns) that gives OctoPwn an interactive console for talking to a specific DNS server. You'll usually create one for two reasons: to perform ad-hoc forward and reverse lookups against an *internal* DNS server during recon, and to plug that server in as the **framework-wide name resolver** so every other module (clients, scanners, attacks) routes its name lookups through it.

The default port is `53` and **no credential is required** — DNS is unauthenticated, so the client uses the `NONE` authentication type. Just add the DNS server as a target, create a session against it, and every command works immediately.

!!! info "Transport"
    Both **TCP** and **UDP** are supported. TCP is the default — it sidesteps the 512-byte UDP truncation problem at the cost of a slightly slower handshake, which is what you usually want when querying internal servers through SOCKS proxies or wsnet.

---

## Features

- Single A / AAAA / PTR queries with auto-detection of the query type from the input.
- Bulk hostfile / IP / CIDR resolution to disk, optionally ingesting every result as a new target.
- Back-fill of missing IPs or hostnames on targets that are already in your project.
- Pluggable as the framework-wide resolver, replacing the default fallback chain.

---

## Wiring it up as the global resolver

OctoPwn resolves hostnames in many places — when you `addtarget foo.corp.local`, when a scanner expands `g:webservers`, when an attack module dereferences a UNC path, and so on. By default these lookups go through one of two fallback resolvers:

| Edition        | Default resolver                                                                                                                                |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Pro**        | The wsnet-based resolver — effectively Python's `socket` resolver running **inside the wsnet proxy process** (so it inherits *that* host's DNS configuration). |
| **Enterprise** | Python's `socket` resolver running on the **OctoPwn server itself**.                                                                            |

Both fallbacks are fine for resolving public names, but they will *not* see your target environment's internal DNS zones. To fix that, point the global resolver at a DNS client session:

1. **Create a DNS client** against the internal DNS server (typically a domain controller).
2. **Note its session ID** — visible in the Sessions Window or returned when you create the session from the CLI.
3. **Set it as the resolver** in one of two ways:
    - From the main console: `resolver <session_id>`. Run `resolver` with no argument to see the current value.
    - From the GUI: *Global Settings → Set Resolver* and enter the session ID.
4. From this point on every name lookup in the framework is forwarded to that DNS session — `resolve foo.corp.local` on the main console, `addtarget` with a hostname, scanner-side hostname expansion, and so on.

To revert to the built-in fallback, run `clearresolver` on the main console (or clear the field in the GUI).

!!! tip "Verifying the wiring"
    After setting the resolver, run `resolve <known.internal.name>` on the main console — if it answers with the right IP, the rest of the framework will follow suit.

---

## Commands

The DNS client groups its commands into three categories matching how you typically use it: ad-hoc lookups (`BASIC`), back-filling existing targets (`TARGETS`), and bulk file-based work (`FILE`).

### BASIC

#### query
Sends a single DNS query and prints the result to the console.

If `qtype` is omitted, the client picks one for you: a `PTR` lookup if `name` parses as an IP address, otherwise an `A` lookup. Pass `qtype` explicitly when you want something else.

##### Parameters
- **name**: The DNS name (or IP, for reverse lookups) you want to resolve.
- **qtype**: The query type. Supported values are `A`, `AAAA` and `PTR`. Auto-detected from `name` when left empty.
- **search**: A comma-separated list of DNS suffixes. **Only applied to `A` and `AAAA` queries** — each suffix is appended to `name` (`name.suffix`) and queried in turn, which is handy when you want to expand short names against several internal zones in one shot. Leave empty for fully qualified lookups.

##### Examples

```text
# Forward lookup
SQL > query dc01.corp.local
[A] dc01.corp.local -> 10.10.10.5

# Reverse lookup (qtype auto-selected as PTR)
SQL > query 10.10.10.5
[PTR] 10.10.10.5 -> dc01.corp.local.

# Short-name expansion against multiple zones
SQL > query dc01 A corp.local,dev.corp.local
[A] dc01.corp.local -> 10.10.10.5
[A] dc01.dev.corp.local -> 10.20.10.5
```

---

### TARGETS

#### resolvtargets
Walks every target in the current project that has only an IP **or** only a hostname (but not both) and uses the DNS server to fill in the missing half. Targets that are already fully resolved or marked as hidden are skipped.

This is the fastest way to enrich a target list you imported from a port scan or an external scanner — give them all hostnames in one pass before kicking off domain-aware modules.

##### Parameters
- **targetspec**: Which targets to operate on. Defaults to `all`. Accepts the standard target-spec formats:
    - **ID**: target ID from the Targets Window.
    - **IP**: single IP (`192.168.1.1`).
    - **CIDR**: range in CIDR notation (`192.168.1.0/24`).
    - **Hostname**: a resolvable hostname.
    - **Control word**: `all` for every stored target.
    - **Single group**: `g:<groupname>`.
    - **Multiple groups**: `g:<group1>,g:<group2>`.
    - **Port group**: `p:<port>` or `p:<port>/<protocol>`.
- **search**: Comma-separated DNS suffix list — same semantics as `query.search`, only applied when filling in an IP from a hostname.

---

### FILE

#### resolvfile
Bulk-resolves a file of hostnames, IP addresses and CIDR ranges. Hostnames are resolved A/AAAA, IPs PTR, and CIDR ranges are **expanded to every individual address** before resolving — so `10.0.0.0/24` produces 256 PTR queries.

The output is written tab-separated to `<filename>_resolved.txt` next to the input file.

##### Parameters
- **filename**: Path to the input file. One name / IP / CIDR per line; blank lines are skipped.
- **store**: When `True`, every successfully resolved entry is also added to the project as a new **Target** (sourced as `resolvfile` against the current DNS session ID), and the Targets Window is refreshed at the end. Defaults to `False` — flip it on when you're using `resolvfile` to seed a target list rather than just dump a CSV.
- **search**: Comma-separated DNS suffix list. Same semantics as `query.search`.

!!! warning "CIDR expansion"
    There is no upper bound on the size of the network you can pass — a `/16` will issue 65 536 PTR queries against the DNS server. Throttle yourself by splitting the input file or by using a smaller CIDR if you don't want to be noisy.

---

## Limitations

- The console wrapper only exposes `A`, `AAAA` and `PTR`. Other record types (`SRV`, `MX`, `TXT`, `CNAME`, `NS`, …) aren't reachable from these commands today — for SRV/zone enumeration against Active Directory, use the LDAP client's `dnsdump` / `dnszones` / `dnsqueryall` commands instead.
- **DNS zone transfers (`AXFR` / `IXFR`) are not supported yet.** If you need a full zone dump against an Active Directory DNS server, fall back to the LDAP client's `dnsdump`.
- DNSSEC validation and EDNS0 customisation are not exposed by the wrapper.
