# SMB PrintNightmare Scanner (smbprintnightmare)

The **SMB PrintNightmare Scanner** in OctoPwn scans for hosts vulnerable to the PrintNightmare exploit. **PrintNightmare** refers to a set of vulnerabilities in the Windows Print Spooler service that allow remote code execution and privilege escalation. These vulnerabilities exploit improperly configured permissions in the Print Spooler service, enabling attackers to add malicious printer drivers to execute arbitrary code on the target system.

PrintNightmare vulnerabilities are not only useful for remote or local privilege escalation but can also facilitate **unconstrained delegation attacks**. Unconstrained delegation allows attackers to retrieve Ticket Granting Tickets (TGTs) of users or systems interacting with the vulnerable machine, potentially including high-privileged accounts such as domain administrators or domain controllers.

Using PrintNightmare you can exploit systems with unconstrained delegation enabled. By coercing authentication from domain controllers or other servers, you can retrieve TGTs. These tickets can then be abused using techniques such as [S4U2Self](../clients/kerberos.html#s4uself) to impersonate accounts for further attacks.

For detailed technical information, visit [The Hacker Recipes](https://www.thehacker.recipes/ad/movement/print-spooler-service/printnightmare).

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication.
Enter the ID of the credential stored in the Credentials Window.

#### targets
Specifies the targets to scan.

A list of targets can be specified in the following formats:

- **ID**: ID of the target server from the Targets Window.
- **IP**: Single IP address (e.g., `192.168.1.1`).
- **CIDR**: IP range in CIDR notation (e.g., `192.168.1.0/24`).
- **Hostname**: Resolvable hostname.
- **File**: Path to a file containing targets (must be in OctoPwn’s `/browserefs/volatile` directory). File lists need to be uploaded into OctoPwn and separated by newlines.
- **Control word**: Use `all` to scan all stored targets.

---

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
