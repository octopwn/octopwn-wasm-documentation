# SMB Signature Scanner (smbsig)

The **SMB Signature Scanner** in OctoPwn checks whether SMB signing is enabled and whether it is enforced on target SMB servers. SMB signing ensures the integrity of SMB messages by adding a cryptographic signature to each message. However, if SMB signing is enabled but not enforced, attackers can perform **SMB relaying**.

**SMB Relaying** is an attack that allows adversaries to intercept and relay SMB authentication requests to another target, effectively impersonating the victim. This can be used to gain unauthorized access to resources or escalate privileges within a network. Note that OctoPwn has built-in SMB Relaying capabilities with the [Relaying Server](../servers/relay.html).

subset of smbproto - will only check if signing is enabled and enforced 
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
Defines the headers for the scan results. Do not change this.

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
