# SMBProto Scanner 

The **SMBProto Scanner** is similar to the **SMBSig Scanner** but provides additional information on supported smb dialects. This scanner requires 5-6 connection attempts to complete its operations, making it slower than SMBSig. 

If you are only interested in checking SMB signing, it is recommended to use the [SMBSig Scanner](smbsig.html) instead.

---

## Parameters

### Normal Parameters

#### targets
Specifies the list of targets to scan.

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

#### dialect
Specifies the SMB connection dialect to test (e.g., SMB2).

#### maxruntime
Sets the maximum runtime for the scan.

#### proxy
Specifies the proxy ID to use for routing the scan.

#### resultsfile
Defines the file path for saving scan results.
#### showerrors
Determines whether errors encountered during the scan should be displayed.

#### timeout
Sets the timeout in seconds for each target.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter; do not modify.
