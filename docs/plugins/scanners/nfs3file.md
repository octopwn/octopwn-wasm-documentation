# NFS3 File Scanner

The **NFS3 File Scanner** in OctoPwn performs file enumeration over NFSv3 shares. It iterates through folders up to a specified depth, collecting file and folder information to identify potential credentials or other sensitive data. 

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication.

Enter the ID of the credential stored in the Credentials Window.

---

#### depth
Specifies the folder enumeration depth.

Controls how many levels deep the scanner will traverse within the NFS directory structure.

---

#### maxitems
Specifies the maximum number of items to enumerate per folder.

Limits the number of items (files and folders) the scanner will retrieve per directory.

---

#### targets
Specifies the targets to scan. 

A list of targets can be specified in the following formats:

- **ID**: ID of the target server from the targets window.
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
Specifies the connection dialect. For this scanner, it is fixed to `NFS3`.

#### krbetypes
Specifies the Kerberos encryption types to use during the scan.

Provide a comma-separated list of encryption types (e.g., `23,17,18`).

- 23 (rc4)
- 17 (aes128)
- 18 (aes256)

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

