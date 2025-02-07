# LDAP Signing Scanner (ldapsig)

The **LDAP Signing Scanner** in OctoPwn determines whether LDAP signing is enforced on target LDAP servers. LDAP signing ensures the integrity and security of communication by requiring digitally signed data. Systems without enforced LDAP signing are more vulnerable to certain attacks, such as LDAP relaying.

LDAP relaying is an attack technique where a malicious actor intercepts and relays LDAP traffic to impersonate the original user or escalate privileges. Without LDAP signing enforcement, attackers can:

- Relay intercepted NTLM authentication requests to the LDAP server.
- Exploit misconfigured systems to escalate privileges or gain unauthorized access.
- Use tools like **ntlmrelayx** or our [relay server](../servers/relay.md) to abuse LDAP features, such as enabling delegation, modifying ACLs, or escalating permissions for user accounts.

 **High-Level Example of LDAP Relaying**
 
1. **Intercept NTLM Authentication**: An attacker captures NTLM hashes using coercion tools (e.g. [printerbug](../clients/smb.html#ntlm-coercion)) or other methods.
2. **Relay to LDAP**: The captured hashes are relayed to an LDAP server without signing enforcement.
3. **Modify Directory Objects**: The attacker performs unauthorized operations, such as enabling delegation on a machine account, or granting higher privileges to their controlled user.

---
## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication. 
Enter the ID of the credential stored in the Credentials Window.
#### targets
Specifies the targets to scan.

A list of targets can be specified in the following formats:

- **ID**: ID of the target server from the targets window.
- **IP**: Single IP address (e.g., `192.168.1.1`).
- **CIDR**: IP range in CIDR notation (e.g., `192.168.1.0/24`).
- **Hostname**: Resolvable hostname.
- **File**: Path to a file containing targets (must be in OctoPwn’s `/browserefs/volatile` directory). File lists need to be uploaded into OctoPwn and separated by newlines.
- **Control word**: Use `all` to scan all stored targets.
- **Single Group**: `g:<groupname>` (e.g., `g:test1`).
- **Multiple Groups**: `g:<groupname1>,g:<groupname2>` (e.g., `g:test1,g:test2`).
- **Port Group**: `p:<port>` (e.g., `p:445`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:445/tcp`).

---

### Advanced Parameters

#### __info
This parameter is just for information purposes.

#### __resultHeaders
Defines the headers for the scan results.

A comma-separated list of result headers for the output, including:

- **LDAP**: Indicates LDAP server availability.
- **LDAPS**: Indicates LDAPS (LDAP over SSL) availability.
- **SIGNING_ENFORCED**: Specifies if signing is enforced.
- **BINDING_ALWAYSCHECK**: Specifies if binding is always checked.
- **BINDING_WHENSUPPORTED**: Specifies if binding is checked when supported.
#### authtype
Specifies the authentication protocol.

Available protocols:

- `NTLM`
- `Kerberos`
#### dialect
Specifies the connection dialect.

Available dialects:

- `LDAP`
- `LDAPS`

#### krbetypes
Specifies the Kerberos encryption types to use during the scan.

Provide a comma-separated list of encryption types (e.g., `23 (rc4),17 (aes128),18 (aes256)`).
#### krbrealm
Specifies the Kerberos realm to use.
Enter the Kerberos realm (domain name) for authentication.

#### maxruntime
Specifies the maximum runtime for the scanner.

#### proxy
Specifies the proxy ID to use for the scan.

Enter the ID of the proxy to route the scan through. Proxies must be configured in the Proxy Window.
#### resultsfile
Specifies a file for saving the scan results.

The file will be saved in OctoPwn’s `/browserefs/volatile` directory.
#### showerrors
Determines whether errors encountered during the scan should be displayed.

