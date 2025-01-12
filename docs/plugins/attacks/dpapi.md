# DPAPI Attack

The **DPAPI Attack** targets the Windows **Data Protection Application Programming Interface (DPAPI)** to remotely extract and decrypt sensitive secrets stored on user and system contexts. This includes browser-stored credentials, Windows Credential Manager data, and encrypted application configuration files. 

DPAPI provides applications with cryptographic services for securely encrypting and decrypting data without requiring manual key management. Secrets protected by DPAPI are encrypted using **master keys**, which are secured by user passwords or domain-level backup keys. By exploiting DPAPI, attackers can access and decrypt sensitive data, enabling lateral movement, privilege escalation, and credential theft.

DPAPI abuse exploits the architecture of how Windows securely stores data:

1. **Master Key Retrieval**: Obtain user- or system-specific master keys.
2. **Key Decryption**: Use passwords, hashes, or domain backup keys to decrypt master keys.
3. **Secret Decryption**: Use master keys to decrypt DPAPI-protected data blobs, such as:
   - **Browser Cookies and Login Data**: Stored in Chrome and other browsers.
   - **Credential Manager Files**: Network share or RDP credentials.
   - **Windows Vaults**: Stores web and application credentials.
4. **Offline Decryption**: Download DPAPI-protected data and decrypt offline using [OctoPwn's DPAPI Utility](../utils/dpapi.html). 

### Practical Scenarios

1. **User Context Access**: Directly decrypt secrets using the target user’s credentials. The clear-text user password is required. Be sure to use credentials that use the user password and not the NTLM Hash! {==not implemented for now==}
2. **Administrator Privileges**: Extract master keys from memory and decrypt secrets for all logged-in users. Extract the computer's DAPI System secrets from any computer.
3. **Domain Backup Keys**: Use domain-wide backup keys to decrypt any user’s master keys and secrets, often referred to as "God Mode." To extract this, extract the dpapi system secrets from the Domain Controller.

!!! info
    For a detailed guide on offensive DPAPI abuse, see: [Operational Guidance for Offensive User DPAPI Abuse](https://posts.specterops.io/operational-guidance-for-offensive-user-dpapi-abuse-1fb7fac8b107).

OctoPwn will by default always attempt to extract DPAPI System and User secrets. 

This attack utilizes the Windows Remote Registry Service. The Remote Registry Service allows for remote query and modification of the registry on a Windows machine.

While not enabled by default for security reasons, many systems are configured to start this service upon a remote request. If the initial attempt to connect fails, OctoPwn will try to start the service automatically or you can try using the [`serviceen RemoteRegistry` in the SMB Client](../clients/smb.html) to manually start the RemoteRegistry service. The remote query then often succeeds on a subsequent try as the service initializes, so try again if it doesn't succeed the first time. Also, you might be stopped by Windows Defender, if that is turned on at the remote system.


- you need to be local admin
- only one host per time
- do it again
---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credentials to use for the attack.
#### skipusers
Indicates whether to skip user-specific DPAPI secrets and only target system secrets.
#### targets
Specifies the targets for the attack.

A list of targets can be specified in the following formats:

- **ID**: ID of the target server from the Targets Window.
- **IP**: Single IP address (e.g., `192.168.1.1`).
- **CIDR**: IP range in CIDR notation (e.g., `192.168.1.0/24`).
- **Hostname**: Resolvable hostname.
- **File**: Path to a file containing targets (must be in OctoPwn’s `/browserefs/volatile` directory). File lists need to be uploaded into OctoPwn and separated by newlines.
- **Control word**: Use `all` to attack all stored targets.

---

### Advanced Parameters

#### __info
This parameter is just for information purposes.
#### __resultHeaders
Specifies the headers for the results output. Do not alter.
#### authtype
Specifies the authentication protocol to use (e.g., NTLM).

#### dialect
Specifies the SMB connection dialect (e.g., SMB2).

#### krbetypes
Specifies Kerberos encryption types to use for authentication.

#### krbrealm
Specifies the Kerberos realm for authentication.

#### maxruntime
Specifies the maximum runtime for the attack.

#### proxy
Specifies the proxy ID to use for the attack.

#### resultsfile
Specifies a file for saving the attack results.

The file will be saved in OctoPwn’s `/browserefs/volatile` directory.

#### showerrors
Determines whether errors encountered during the attack should be displayed.
