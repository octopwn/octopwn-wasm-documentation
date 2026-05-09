# NTP Client

The **NTP Client** is OctoPwn's interactive console for talking to a Network Time Protocol server (default port `UDP/123`). It's a small client with two purposes — reading the server's authoritative time, and enumerating the peers it's exchanging time with — but both are useful enough on a real engagement that you'll find yourself reaching for it more often than you'd expect.

The default port is `UDP/123` and **no credential is required** — NTP is unauthenticated by design, so the client uses the `NONE` authentication type. Add the NTP server as a target, create a session against it, and every command works immediately.

!!! info "No credentials required"
    The NTP client uses `ATYPE: NONE`. Just point a session at any NTP server and run commands — there's no login step.

---

## Features

- **Server-time query** — read the server's view of "now" as a UTC datetime, ready to be diffed against your own clock.
- **Peer enumeration** — list every peer the server is currently talking to (their addresses, stratums, association IDs and full mode-6 variable set), surfacing infrastructure you may not have known about.

---

## Use cases

- **Diagnosing Kerberos clock skew.** A `KRB_AP_ERR_SKEW` from the [Kerberos client](kerberos.md) almost always means your client clock and the DC clock differ by more than 5 minutes. `gettime` against the DC tells you which side is wrong before you start chasing phantom Kerberos issues.
- **Mapping internal time infrastructure.** In Active Directory environments the PDC emulator is the authoritative time source for the forest; running `peerlist` against any internal NTP server often surfaces upstream stratum-1/2 hosts (GPS clocks, ISP time servers, dedicated time appliances) that aren't in any other inventory you have.
- **Topology side-channel during recon.** Even non-AD NTP servers expose their peer list by default, which is a free way to discover hosts you might not have port-scanned yet.

---

## Commands

The client groups its two commands under a single `CMD` heading.

### CMD

#### gettime
Sends an NTP client-mode request to the server and prints the server's idea of the current time as a UTC `datetime`. Compare it against your own clock to spot drift.

##### Parameters
None — operates on the session's bound target.

!!! tip "Pair with the Kerberos client"
    If you're getting `KRB_AP_ERR_SKEW` (clock skew too great) from the [Kerberos client](kerberos.md), point an NTP session at the same DC and run `gettime`. The difference between that timestamp and your local clock is your skew — fix the side that's wrong (usually your local container / VM) and Kerberos will start working.

#### peerlist
Enumerates every peer the NTP server is currently associated with by walking **NTP mode-6 control messages** — first a `READ_STATUS` request to harvest association IDs, then one `READ_VARS` request per association to pull the full per-peer variable set. Each peer is printed as a single line containing its association data: peer address, stratum, refid, status flags, jitter / offset / delay, and the rest of the standard `ntpq`-style variables.

##### Parameters
None — operates on the session's bound target.

!!! warning "Mode-6 control access is often restricted"
    Modern NTP server configurations frequently include `restrict default … noquery` (or its `chrony` equivalent), which disables mode-6 control responses to protect against amplification attacks and topology disclosure. Against a hardened server `peerlist` will return an empty list, time out, or be silently dropped — that's a configuration choice, not a bug.

---

## Limitations & gotchas

- **`peerlist` depends on mode-6 control responses.** See the warning above — hardened servers won't answer.
- **No mode-7 / `monlist` support.** The infamous Cisco-style monlist amplification query isn't implemented; `peerlist` walks the safer mode-6 control path.
- **No NTP authentication (NTS, symmetric keys, autokey).** The client speaks unauthenticated NTPv3 client-mode and mode-6 control. If you find a server requiring auth, you won't be able to talk to it from here.
- **No round-trip statistics in `gettime` output.** Only the server timestamp is printed — offset / delay / jitter aren't surfaced today. If you need them, sample a few `gettime` calls and diff the timestamps yourself, or fall back to a dedicated NTP debugging tool.
