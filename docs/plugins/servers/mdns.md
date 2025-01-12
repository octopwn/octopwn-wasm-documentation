# mDNS Server

The **mDNS Server** in OctoPwn operates similarly to the mDNS poisoning functionality of tools like [Responder](https://github.com/lgandx/Responder). It can run in two modes: **Analysis Mode**, which observes and logs mDNS requests and responses, and **Spoofing Mode**, which spoofs or poisons responses to trick target machines into disclosing sensitive information such as NTLM hashes. The hashes can then be cracked offline with tools like hashcat. This server can also be used in conjunction with the [Relay Server](relay.html) to provide functionality similar to [impacket's ntlmrelayx](https://github.com/fortra/impacket/blob/master/examples/ntlmrelayx.py). 

mDNS (Multicast DNS) is a protocol used to resolve names within a local network without relying on a DNS server. Attackers can exploit this protocol by spoofing responses to multicast queries, causing victims to send sensitive information, such as NTLM hashes, to the attacker.

For more information, see: [The Hacker Recipes](https://www.thehacker.recipes/ad/movement/mitm-and-coerced-authentications/llmnr-nbtns-mdns-spoofing)

!!! warning
	Ensure the necessary firewall ports are open on the host with the listening proxy (where wsnet is running):
	
	- **UDP 5353**: Used by mDNS.
	- **TCP 5353**: Occasionally used for mDNS traffic.

---

## Parameters

### Normal Parameters

#### localip
Specifies the local IP address for the server. Necessary if spoofing is enabled and a proxy is in use.  
- **Example**: `192.168.1.1`.

#### spoof
Enables or disables spoofing mode.  
- Set to `0` for Analysis Mode.  
- Set to `1` for Spoofing Mode.

#### spooftable
Controls how responses are spoofed. This needs to be two comma-separated values, e.g., `*,SELF`.  
**Options**: 

  - **1st parameter**: Define which requests to reply to. `*`: Reply to all requests. Alternatively, you can respond only to requests from a specific IP Address by specifying the IP address instead.  
  - **2nd parameter**: Define with which IP to respond. `SELF`: Respond with the local IP address. This will use the IP entered in the `localip` parameter. Alternatively, enter an IP address you want to respond with.

---

### Advanced Parameters

#### proxy
Specifies the proxy ID to route traffic through.

#### resultsfile
Defines the file path for saving captured results.
