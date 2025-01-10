# SMB Fingerprinting Scanner (smbfinger)

The **SMB Fingerprinting Scanner** in OctoPwn enumerates NTLM handshake information from SMB servers, providing details about the target environment. This scanner is particularly useful for initial reconnaissance, enabling penetration testers to gather domain and system details, such as domain names, OS versions, and local time.

The following details are gathered during the scan:

- **domainname**: The domain name of the target.
- **computername**: The target's computer name.
- **dnsforestname**: The DNS forest name of the domain.
- **dnscomputername**: The target's DNS computer name.
- **dnsdomainname**: The DNS domain name of the target.
- **local_time**: The current local time on the target system.
- **os_major_version**: The major version of the target's operating system.
- **os_minor_version**: The minor version of the target's operating system.
- **os_build**: The OS build number.
- **os_guess**: An educated guess of the target's operating system.

---

## Parameters

### Normal Parameters

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
Defines the headers for the scan results. Do not modify, unless you want to remove existing headers from the result.

#### dialect
Specifies the SMB connection dialect. Fixed to `SMB2` for this scanner.
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

#### wsnetreuse
Internal parameter. Do not modify.
