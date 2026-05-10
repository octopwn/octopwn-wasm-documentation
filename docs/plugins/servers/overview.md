# Servers — overview

OctoPwn's **servers** host network services from inside the framework so you can run the
classic "rogue server" attack patterns — name-resolution poisoning, NTLM relaying,
WebDAV / HTTP loot-drop sinks, AD CS Web Enrollment relays, and more — without having to
juggle separate Responder / ntlmrelayx / Inveigh deployments.

Unlike the equivalent standalone tools, OctoPwn ships these as **separate, focused
sessions**. The poisoning layer (LLMNR / mDNS / NBT-NS) is one module; each authentication
collector / relay is its own module. You typically start two or more sessions in
parallel — one to misdirect victims, one (or several) to handle the resulting authentication.

## Where servers run

Every server module binds its sockets inside the **OctoPwn agent process**, not in the
browser. In a typical setup that is:

- **Pro / WASM mode**: the wsnet agent on whichever native host you are bridging the
  browser to.
- **Enterprise mode**: the OctoPwn server process on whichever host it is deployed.

A purely browser-only deployment (no native bridge) cannot host servers — there is no
raw-socket access from Emscripten. Each server page calls out the specific platform
caveats that apply (privileged ports, conflicts with the host's own services, the same
L2 / multicast segment as the victims, etc.).

## Available servers

The currently shipped server modules:

- **[Spoofer](spoofer.md)** — unified LLMNR + mDNS + NBT-NS poisoner. Replaces the
  legacy single-protocol `LLMNR`, `MDNS` and `NBTNS` servers. Pair it with one or more
  Relay servers below to capture or relay the resulting authentication.
- **NTLM relay family** — five focused variants, one page per back-end:
    - **[RelaySMB](relaysmb.md)** — relay to a list of SMB targets, auto-loot via
      `regdump` + `dpapisecrets` on success.
    - **[RelayLDAP](relayldap.md)** — relay to LDAP / LDAPS / StartTLS DCs for ACL
      writes, RBCD, Shadow Credentials, etc.
    - **[RelayMSSQL](relaymssql.md)** — relay to MSSQL servers, useful for
      SQL-coercion chains and service-account abuse.
    - **[RelayESC8](relayesc8.md)** — relay to AD CS Web Enrollment, output is a
      ready-to-use PFX certificate.
    - **[RelayNTLMReflection](relayreflection.md)** — relay back to the source host
      (the classic CVE-2019-1040-style self-relay path).

Additional server modules — `WSNET` (agent bridge), `HTTPFILE`, `WEBDAV`,
`REMOTECONTROL`, `REMOTECONTROLJS` — are exposed by the framework and will be documented
in subsequent passes.

## Typical workflow

1. **Pick the auth-collection server(s)** you want to use, based on what you intend to
   capture or relay onto. Start them and verify in their consoles that they are listening.
2. **Get a victim to authenticate to the agent** — either by abusing an existing
   misconfiguration (writable share with malicious `desktop.ini`, MS-RPRN coercion via
   the [SMB client's printerbug](../clients/smb.md#ntlm-coercion), AD CS template,
   crafted email, …) **or** by starting the [Spoofer](spoofer.md) and luring the victim
   onto the agent's IP.
3. **Watch the relay-server consoles** for captured / relayed sessions.
4. **Process the captured material** — Net-NTLMv2 hashes can be cracked offline (Hashcat
   et al.); machine-account credentials and AD CS certificates are auto-stored in the
   project's Credentials Hub for use in subsequent client sessions.
