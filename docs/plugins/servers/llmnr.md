# LLMNR Server

The **LLMNR Server** in OctoPwn operates similarly to the LLMNR poisoning functionality of tools like [Responder](https://github.com/lgandx/Responder). It can run in two modes: **Analysis Mode**, which observes and logs LLMNR requests and responses, and **Spoofing Mode**, which spoofs or poisons responses to trick target machines into disclosing sensitive information such as NTLM hashes. The hashes can be cracked offline with tools such as hashcat. It is also possible to use the LLMNR Server in conjuction with the [Relay Server](relay.html), which then provides similar functionality to [impacket's ntlmrelayx](https://github.com/fortra/impacket/blob/master/examples/ntlmrelayx.py). 

LLMNR (Link-Local Multicast Name Resolution) is a protocol used to resolve names in local networks when DNS is unavailable. Attackers can exploit this protocol by spoofing responses to name resolution requests, causing victims to send sensitive information, such as NTLM hashes, to the attacker.

For more information, see:  [The Hacker Recipes](https://www.thehacker.recipes/ad/movement/mitm-and-coerced-authentications/llmnr-nbtns-mdns-spoofing)

!!! warning
	Ensure the necessary firewall ports are open on the host with the listening proxy (where wsnet is running):
	
	- **UDP 5355**: Used by LLMNR.
	- **TCP 5355**: Occasionally used for LLMNR traffic.

---

## Parameters

### Normal Parameters

#### localip
Specifies the local IP address for the server.  Necessary if spoofing is enabled and a proxy is in use.  
- **Example**: `192.168.1.1`.
#### spoof
Enables or disables spoofing mode.  
- Set to `0` for Analysis Mode.  
- Set to `1` for Spoofing Mode.

#### spooftable
Controls how responses are spoofed.  This needs to be two comma-separated values, e.g.:  `*,SELF`

**Options**:  

  - **1st parameter**: Define which requests to reply to. `*`: Reply to all requests. Alternatively you can respond only to requests from a specific IP Address by specifying the IP address instead.
  - **2nd parameter**: Define with which IP to respond with. `SELF`: Respond with the local IP address. This will use the IP entered in the `localip` parameter. Alternatively enter an IP address you want to respond with. 
  
### Advanced Parameters

#### proxy
Specifies the proxy ID to route traffic through.

#### resultsfile
Defines the file path for saving captured results.



relay server -either together with llmnr, ... or smb coercion


|                     |     |                                                 |         |     |                                                                                                                                                                                                                                                          |
| ------------------- | --- | ----------------------------------------------- | ------- | --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| adcstemplate        | str | ADCS template name                              | Unknown | No  | you get a certificate you can authenticate with, depending on who you are relaying<br>Values: User, Machine, DomainController, Unknown (if you don't know if user and machine, will try both, going to fail if machine you coerced is domain controller) |
| connectproxy        | str | Proxy ID used when creating interactive clients |         | No  | different proxy for relay connection - sending (other one than listening on)                                                                                                                                                                             |
| debug               | str | Enable debug mode                               | 0       | No  | debug prints                                                                                                                                                                                                                                             |
| httpproxyserverport | str | HTTP Proxy server port                          | 8080    | Yes | if proxy is used on the network - port will be listend to on the serverproxy                                                                                                                                                                             |
| httpserverport      | str | HTTP server port                                | 80      | Yes | listening for connections                                                                                                                                                                                                                                |
| httpsserverport     | str | HTTPS server port                               | 443     | Yes | listening for connections                                                                                                                                                                                                                                |
| httptargets         | str | List of HTTP targets to connect to              |         | No  | targets we want to relay authentication to                                                                                                                                                                                                               |
| ldaptargets         | str | List of LDAP targets to connect to              |         | No  | targets we want to relay ldap auth to                                                                                                                                                                                                                    |
| serverip            | str | IP address to listen on (for all servers)       | 0.0.0.0 | No  | which interface to listen on                                                                                                                                                                                                                             |
| serverproxy         |     |                                                 |         |     | listening proxy id                                                                                                                                                                                                                                       |