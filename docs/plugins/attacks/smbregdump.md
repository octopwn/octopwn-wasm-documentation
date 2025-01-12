# SMBRegDump Attack

The **SMBRegDump Attack** leverages the **Remote Registry Service** on Windows systems to remotely access and dump registry hives over SMB. These hives are dumped onto disk on the remote system and is then parsed remotely to extract the SAM, SYSTEM and SECURITY secrets, such as local account hashes. If local account hashes are extracted successfully, they will be automatically added in the credentials window of OctoPwn for further lateral movement steps.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication on the target. This needs to be a local admin.
#### srvwaittime
Defines the maximum time (in seconds) to wait for a server response before giving up.
#### targets
Specifies the list of targets to scan.

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
Specifies the authentication protocol to use (e.g., NTLM).

#### dialect
Specifies the SMB connection dialect (e.g., SMB2).

#### krbetypes
Defines the Kerberos encryption types to use during authentication.
#### krbrealm
Specifies the Kerberos realm for authentication, if applicable.

#### maxruntime
Sets the maximum runtime for the attack.
