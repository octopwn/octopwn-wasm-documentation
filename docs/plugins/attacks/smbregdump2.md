# SMBRegDump2 Attack

The **SMBRegDump2 Attack** is a modified version of SMBRegDump that leverages the **Remote Registry Service** on Windows systems to remotely access and parse registry hives over SMB. Unlike SMBRegDump, this attack does not create any files on the disk. Instead, it modifies the **security descriptor** of protected registry keys to grant temporary access, reads the keys remotely, and then restores the original permissions. 

This approach enables the extraction of **SAM**, **SYSTEM**, and **SECURITY** secrets, such as local account hashes, without leaving artifacts on the disk. If local account hashes are successfully extracted, they will be automatically added to the **Credentials Window** in OctoPwn for further lateral movement steps.

This attack works because, by default, local administrators have write access to modify the security descriptors of registry keys, even if they cannot read the keys initially.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication on the target. This needs to be a local admin.
#### targets
Specifies the list of targets to scan.

A list of targets can be specified in the following formats:

- **ID**: ID of the target server from the Targets Window.
- **IP**: Single IP address (e.g., `192.168.1.1`).
- **CIDR**: IP range in CIDR notation (e.g., `192.168.1.0/24`).
- **Hostname**: Resolvable hostname.
- **File**: Path to a file containing targets (must be in OctoPwn’s `/browserefs/volatile` directory). File lists need to be uploaded into OctoPwn and separated by newlines.
- **Control word**: Use `all` to scan all stored targets.

#### srvwaittime
Defines the maximum time (in seconds) to wait for a server response before giving up.

### Advanced Parameters

#### authtype
Specifies the authentication protocol to use (e.g., NTLM).

#### dialect
Specifies the SMB connection dialect (e.g., SMB2).

#### krbetypes
Defines the Kerberos encryption types to use during authentication.

#### krbrealm
Specifies the Kerberos realm for authentication, if applicable.

#### maxruntime
Sets the maximum runtime for the attack.

#### proxy
Specifies the proxy ID to use for routing the attack.
#### resultsfile
Specifies the path for saving scan results.

#### showerrors
Determines whether to display errors encountered during the scan.

#### timeout
Sets the timeout in seconds for each target.

#### workercount
Specifies the number of parallel workers for the attack.
