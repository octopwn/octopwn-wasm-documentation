# NTP Client

The NTP Client within the "OctoPwn" framework facilitates interaction with Network Time Protocol (NTP) servers. This client allows you to query server time and retrieve peer lists.

---

## Features

- **Time Query**: Retrieve the current time from NTP servers.
- **Peer Enumeration**: List peers connected to the target NTP server.
- **Protocol Support**: Fully supports interactions with NTP for enumeration and analysis.

---
## Commands

### CMD

#### gettime
Queries the NTP server to retrieve the current time.

!!! info
    This command can help identify discrepancies in server time, especially helpful when Kerberos won't work, because of a different server time.

#### peerlist
Retrieves a list of peers connected to the target NTP server.

---

