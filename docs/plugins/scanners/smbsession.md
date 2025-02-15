# SMB Session Enumeration Scanner (smbsession)

The **SMB Session Enumeration Scanner** in OctoPwn enumerates active SMB user sessions on target servers. **Session enumeration** provides a snapshot of the currently logged-in users on a system. This information is useful during penetration tests to identify the systems high-value accounts are logged in to, such as domain administrators or service accounts, that can be targeted for privilege escalation or lateral movement by dumping lsass. 
### Challenges with Newer Windows Versions

Session enumeration is no longer possible by default on newer versions of Windows (starting with Windows 10 and Server 2016) due to improved security configurations. Microsoft has restricted the ability to enumerate user sessions via SMB to mitigate the risk of unauthorized access. However, if systems are misconfigured or running older versions of Windows, session enumeration might still be feasible.

### Alternatives for Session Enumeration

1. **SCCM (System Center Configuration Manager)**:
 SCCM logs user session information, which can be accessed if SCCM servers are compromised.

2. **WMI (Windows Management Instrumentation)**:
   WMI can be used to query session information, provided the attacker has sufficient privileges.


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
### Advanced Parameters

#### authtype
Specifies the authentication protocol.

Available protocols:
- `NTLM`
- `Kerberos`

#### dialect
Specifies the SMB connection dialect. Fixed to `SMB2` for this scanner.
#### krbetypes
Specifies the Kerberos encryption types to use during the scan.

Provide a comma-separated list of encryption types (e.g., `23,17,18`).
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

#### timeout
Sets the timeout (in seconds) for each target.

#### workercount
Specifies the number of parallel workers for the scan.
