# Utilities Overview

OctoPwn's **utilities** are everything in the toolkit that **isn't** a
network client or a scanner. They cover three broad areas:

1. **Offline analysis & decryption** — parse files you've already collected
   (LSASS minidumps, registry hives, NTDS.dit, DPAPI artefacts) and turn
   them into Hub credentials.
2. **AD modelling & exploitation** — collect a domain into a
   BloodHound-compatible graph, query it, and execute the resulting attack
   paths edge-by-edge.
3. **Operator helpers** — local password cracking, file hunting across
   the four supported protocols (SMB / FTP / SFTP / NFS), local PTY
   shell, plugin runtime, and Azure AD / Entra reconnaissance.

The utilities live in the **UTIL** category in the OctoPwn UI.

---

## At a glance

### Offline analysis & decryption

- **[PYPYKATZ](pypykatz.md)** — LSASS / registry / NTDS parser, plus
  one-shot hash calculators (`nt`, `lm`, `msdcc`, `msdcc2`, `kerberos`).
- **[DPAPI](dpapi.md)** — the decryption side of the DPAPI workflow:
  master keys, vaults, credential files, Chrome / WiFi / SecureString /
  CloudAP PRT.
- **[NMAP](nmap.md)** / **[MASSCAN](masscan.md)** — XML report parsers
  that feed the [Targets window](../../user-guide/target.md).

### AD modelling & exploitation

- **[BLOODHOUND](bloodhound.md)** — collect a live AD into a
  BloodHound-compatible zip with optional SMB-side enrichment
  (sessions / local groups / registry).
- **[NEO4J](neo4j.md)** — query an external Neo4j instance (the one
  backing BloodHound CE) directly from an OctoPwn session.
- **[DOMAIN](domain.md)** — the attack-path engine: load a domain,
  compute viable / dangerous paths, walk the abusable edges with
  best-effort cleanup.

### Operator helpers

- **[HASHCAT](hashcat.md)** — wrap a local Hashcat binary and crack
  hashes from the Hub automatically as they appear.
- **[SNAFFLER](snaffler.md)** — find interesting files across SMB / FTP
  / SFTP / NFS, optionally feed matches through an LLM for structured
  credential extraction.
- **[TERMINAL](terminal.md)** — open an interactive `bash` PTY in an
  OctoPwn window (server / Enterprise build only).
- **[ROADTOOLS](roadtools.md)** — Azure AD / Entra reconnaissance
  (token acquisition, ROADrecon `gather`, CA policy parser, XLS export).
- **[PLUGINLOADER](pluginloader.md)** — load and execute custom plugins
  (the [`OctoPwnPlugin`](pluginloader.md#authoring-plugins) class).
- **[IDE](ide.md)** — in-browser editor for authoring plugins, with
  language-server autocompletion.
- **[Python Console](python-console.md)** — one-shot Python evaluation
  against the live `octopwnobj`.

---

## Choosing the right utility

| Goal | Start with |
| --- | --- |
| I have an LSASS dump / hive / NTDS.dit and want creds out of it | [PYPYKATZ](pypykatz.md) |
| I have DPAPI master keys / blobs and want plaintexts | [DPAPI](dpapi.md) |
| I need a BloodHound zip of a live domain | [BLOODHOUND](bloodhound.md) |
| I have a BloodHound zip and want shortest-path-to-DA + auto exploit | [DOMAIN](domain.md) |
| I have a BloodHound CE up and just want to run Cypher | [NEO4J](neo4j.md) |
| I want every credential I get auto-cracked | [HASHCAT](hashcat.md) |
| I want to find passwords scattered in shares / file servers | [SNAFFLER](snaffler.md) |
| I want a local shell next to my OctoPwn project | [TERMINAL](terminal.md) |
| I'm doing Azure AD work | [ROADTOOLS](roadtools.md) |
| I want to extend OctoPwn with my own logic | [IDE](ide.md) → [PLUGINLOADER](pluginloader.md) |

---

## Tier availability

A few utilities are **Enterprise-only** because they either depend on a
local subprocess (no WASM equivalent) or wrap features that are part of
the Enterprise feature set:

- Enterprise-only: `HASHCAT`, `TERMINAL`, `SNAFFLER`, `BLOODHOUND`,
  `NEO4J`, `DOMAIN`, `PLUGINLOADER`.
- Community / Pro: `PYPYKATZ`, `DPAPI`, `NMAP`, `MASSCAN`, `ROADTOOLS`.

The IDE and Python Console are part of the OctoPwn UI and are available
in every build.

Automation utilities (`AUTOPWN`, `AUTOSCANNER`, `AUTOSCANNER2`,
`AUTOPWNMACHINE`, `AUTOMATION`, `FLOWGRAPH`) are documented separately
under the **Automations** section.
