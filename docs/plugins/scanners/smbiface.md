# SMB Interface Scanner (smbiface)

The **SMB Interface Scanner** in OctoPwn enumerates all network interfaces and their assigned IP addresses of target hosts via SMB. This scanner is particularly useful for identifying servers connected to multiple network segments, which may provide opportunities for lateral movement and access to restricted networks.

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

#### __info
This parameter is just for information purposes.

#### __resultHeaders
Defines the headers for the scan results. This should not be changed.

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
