# Nmap Utility

The **Nmap** utility parses an [Nmap](https://nmap.org/) XML report and lets
you query the parsed result, list services, and feed the discovered hosts
into the [Targets window](../../user-guide/target.md). It does **not** run
Nmap itself — you bring the XML, it does the parsing.

It is the simpler twin of the [Masscan utility](masscan.md) and works with
both classic Nmap XML and the structurally-equivalent `nmap -sV --output xml`
variants.

---

## Commands

### GENERIC

#### load
`load(filepath)` — load an Nmap XML file. The path must be reachable from
the OctoPwn runtime (the browser virtual filesystem on the WASM build,
or a real path on the server build). Subsequent commands operate on the
last-loaded file.

#### hosts
`hosts(to_print=True)` — list every host entry found in the XML by *any*
address (IPv4, IPv6, MAC). Prints when `to_print=True` (default), always
returns the list to the caller — useful from automation/plugins.

#### ips
`ips(to_print=True)` — same idea but de-duplicates and emits only the IPv4
and IPv6 addresses, dropping MAC addresses and hostnames.

#### ports
`ports(to_print=True)` — list every `IP:port` tuple. One line per open port
per host.

#### services
`services(to_print=True)` — render a table with columns `addr`, `port`,
`protocol`, `service`, `version` for every open port across every host. This
is the most useful view for triage — it surfaces fingerprinted services /
versions at a glance.

#### addtargets
`addtargets()` — register every host that has at least one address in the
[Targets window](../../user-guide/target.md). Each target gets the host's
discovered ports attached and `source = NMAP:<filepath>` so the origin is
traceable in the Hub.

#### storexml
`storexml(filepath)` — alternative bulk import path used by the same
underlying machinery as the [Targets window](../../user-guide/target.md)
"Import Nmap" button. Use this when you want the full target-importer
behaviour from the CLI rather than the lighter-weight `addtargets` path.

---

## Tips

- For everyday use, prefer **`services`** over `ports` — knowing a port is
  open is rarely as useful as knowing it speaks SSH 9.7p1 or MSSQL 2019.
- `addtargets` only adds hosts with at least one open port. Nmap files that
  contain unreachable / dropped hosts are filtered automatically.
- The utility holds the parsed scan in memory until `load` is called again
  — there's no implicit reset between commands.

---

## See also

- [Masscan utility](masscan.md) — same shape for Masscan XML.
- [Targets window](../../user-guide/target.md) — the GUI way to import the
  same XML, plus per-target review before commit.
