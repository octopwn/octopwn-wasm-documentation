# Relay Server

The **Relay Server** in OctoPwn enables NTLM relaying attacks by capturing NTLM authentication requests and relaying them to SMB, HTTP, or LDAP services. This can be used for various attack scenarios, including **NTLM relaying to ADCS HTTP endpoints**, **abusing non-enforced LDAP signing**, and **local privilege escalation**. The server can be used alongside coercion techniques such as **printerbug**, **MS-RPRN**,  or **WebDAV** or in conjunction with the [LLMNR](llmnr.html) and [mDNS](mdns.html) servers to poison responses and redirect authentication attempts.

NTLM relaying allows attackers to impersonate a victim by capturing their NTLM authentication and relaying it to another target system. This is commonly used for lateral movement and privilege escalation.

## NTLM Relaying

### What Is NTLM Relaying?
NTLM relaying is a type of Man-in-the-Middle (MitM) attack where an attacker captures NTLM authentication requests from a victim and forwards them to a target server. This allows the attacker to authenticate as the victim on the target system. However, note that:
- NTLM authentication cannot be relayed back to the originating machine.
- NTLM relaying is viable only if SMB signing, HTTP signing, or LDAP signing is **not enforced** on the target systems.

!!! info
	For more information, see: [The Hacker Recipes - NTLM Relay](https://www.thehacker.recipes/ad/movement/ntlm/relay)

### LDAP Relaying
LDAP relaying involves forwarding NTLM authentication requests to an LDAP server to modify directory entries or escalate privileges. It requires:
- The target LDAP server must have signing disabled.
- The relayed account must have sufficient privileges to perform the intended operations.

For example, LDAP relaying can be used to grant **delegate access** to a user or system account, which can then be abused for privilege escalation.

### Coercion Methods
Coercion techniques force a target system to authenticate to an attacker's server. Examples include:

- **Printerbug**: Exploits the MS-RPRN interface to trigger authentication.
- **WebDAV**: Triggers authentication by hosting malicious files via WebDAV. Requires the WebClient Service to be running.
- **MS-EFSRPC**: Exploits the Encrypting File System Remote Protocol to coerce authentication.

!!! info
	For coercion techniques, see:  [MITM and coerced auths - TheHackerRecipes](https://www.thehacker.recipes/ad/movement/mitm-and-coerced-authentications/)

---

## Use Cases

### 1. Gathering Net-NTLMv2 Hashes
Use the Relay Server alongside the **LLMNR** or **mDNS Server** to gather Net-NTLMv2 hashes by poisoning name resolution responses. You can then use hashcat to crack the Net-NTLMv2 hashes.

### 2. NTLM Relaying to ADCS HTTP Endpoints (ESC8)
Relaying NTLM authentication to an ADCS server allows attackers to obtain a certificate that can be used to impersonate the relayed account. This is especially useful for gaining domain persistence or escalating privileges. Steps include:
1. Identify an ADCS server using [OctoPwn's ldap client](../clients/ldap.html#certify). 
2. Verify if the Web Enrollment feature is enabled.
3. Use the Relay Server to forward NTLM authentication to the ADCS endpoint.

### 3. Abusing Non-Enforced LDAP Signing
Relay NTLM authentication to an LDAP server to grant delegate access or perform other directory modifications. This only works when receiving authentications via HTTP, e.g. by coercing WebDAV.

### 4. Escalate Local Privileges with User Account Picture and HTTP Relay

You can force the computer account to authenticate and escalate privileges locally by accessing `\\myhost@8080\fake\wallpaper.jpg` from the user account picture dialog in the account system settings. This requires the WebClient Service to be running. 

---
## Parameters

### Normal Parameters

#### adcstemplate
Specifies the ADCS template to request certificates for.  

When relaying to LDAP this will allow you to request a certificate for the relayed account to authenticate against the domain later and move laterally. Depending on which account type you are relaying, you need to specify which adcs template you want to use.

- **Options**: 

	- `User`: Will request a certificate for a user.
	- `Machine`: Will reqeust a certificate for a machine account.
	- `DomainController`: Will request a a certificate for a domain controller machine account. 
	- `Unknown`: Will try get a certificate for both User and Machine, taking whichever works. Will not work if the machine you coerced is a domain controller.

#### connectproxy
Specifies the proxy ID used for outgoing relay connections. Allows using a different proxy for relayed traffic than for listening traffic, e.g. if the target server is in a different network segment from the listening relay server.

#### debug
Enables or disables debug mode for detailed logs.  

#### httpproxyserverport
Port for the HTTP proxy server. Used when relaying HTTP authentication.  You will need to open this port in the firewall.

- **Default**: `8080`.

#### httpserverport
Port for the HTTP server to listen for incoming connections.  
- **Default**: `80`.

#### httpsserverport
Port for the HTTPS server to listen for incoming connections.  
- **Default**: `443`.

#### httptargets
Specifies a list of HTTP targets for relaying authentication. Use this if you want to relay the authentication to HTTP.

#### ldaptargets
Specifies a list of LDAP targets for relaying authentication. Use this if you want to relay authentication to LDAP. Note that you cannot relay SMB to LDAP. Only HTTP to LDAP works.

#### serverip
The local IP address or interface to bind the Relay Server to.  
- **Default**: `0.0.0.0`.

#### serverproxy
Specifies the proxy ID for listening traffic. This will specify on which wsnet client/proxy you want to listen on for incoming traffic. When coercing, you will need to set the ip address of this host as the listener host. 

---

### Advanced Parameters

#### resultsfile
Defines the file path for saving relay logs or results.

---

