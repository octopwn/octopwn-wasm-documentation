# SMB File Scanner (smbfile)

The **SMB File Scanner** in OctoPwn performs file enumeration over SMB shares, traversing folders up to a specified depth to collect file and folder information. This scanner helps penetration testers uncover misconfigured SMB shares, credentials, configuration files, or other sensitive data.

The scanner is particularly useful for the following:

1. **Identify Sensitive Files**:
Locate credentials, configuration files, or other sensitive data exposed on SMB shares.

2. **Assess Permissions**:
Test shares for writable permissions to identify potential misconfigurations or opportunities for exploitation.

3. **Directory and File Security**:
Retrieve and analyze security descriptors of files, directories, and shares to assess access controls.
One common misconfiguration are writeable SYSVOL Shares. This would enable an attacker with write-access  to overwrite to scripts or group policies, which are in turn executed by multiple clients.


??? info "Faster Share Enumeration"
	Note that smb file enumeration can be very slow through the browser or on a a slow network connection from inside of octopwn. Alternatively you can use the python enumerator [asmbshareenum](https://github.com/skelsec/aiosmb/blob/main/aiosmb/examples/smbshareenum.py) on a system directly. To start using it, simply install [aiosmb](https://github.com/skelsec/aiosmb) in a python venv.
	
	

	### asmbshareenum Usage
	
	#### Arguments
	
	- **--depth [x]:** Recursion depth, -1 means infinite
	- **-w [x]**: --smb-worker-count: Parallell count
	- **-o [filename]**: output to this file 
	- **--json**: json format
	- -**-sharesd**: Fetch share security descriptor
	- -**-dirsd**: Fetch directory security descriptor
	- -**-filesd**: Fetch file security descriptor
	- -**-es "a,b,c"**: Exclude shares
	- -**-ed "a,b,c"**: Exclude directories
	
	#### Password Authentication
	
	```python
	asmbshareenum --url 'smb2+ntlm-password://%user%:%password%@%target%' %target% --progress --depth 3 -o shareoutput.txt
	```
	#### NTLM Authentication
	
	```python
	asmbshareenum --url 'smb2+ntlm-nt://%user%:%ntlm%@%target%' %target% --progress --depth 3 -o shareoutput.txt
	```


---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication.

Enter the ID of the credential stored in the Credentials Window.

#### depth
Specifies the folder enumeration depth.

Controls how many levels deep the scanner will traverse within the SMB directory structure. A higher depth means this will take more time. 

#### dirsd
Determines whether to list directory security descriptors.

Enabling this option retrieves the security descriptors of directories. Note that this operation can be slow.

#### excludedir
Specifies a list of directory names to exclude from the scan.

Provide a comma-separated list of directory names that the scanner should skip during enumeration.
#### excludeshare
Specifies a list of share names to exclude from the scan.

Provide a comma-separated list of share names that the scanner should skip during enumeration.

#### filesd
Determines whether to list file security descriptors.

Enabling this option retrieves the security descriptors of files. Note that this operation can be slow.

#### maxitems
Specifies the maximum number of items to enumerate per folder.

Limits the number of items (files and folders) the scanner will retrieve per directory.

#### sharesd
Determines whether to list share security descriptors.

Enabling this option retrieves the security descriptors of SMB shares. Note that this operation can be slow.

#### targets
Specifies the targets to scan.

A list of targets can be specified in the following formats:

- **ID**: ID of the target server from the Targets Window.
- **IP**: Single IP address (e.g., `192.168.1.1`).
- **CIDR**: IP range in CIDR notation (e.g., `192.168.1.0/24`).
- **Hostname**: Resolvable hostname.
- **File**: Path to a file containing targets (must be in OctoPwn’s `/browserefs/volatile` directory). File lists need to be uploaded into OctoPwn and separated by newlines.
- **Control word**: Use `all` to scan all stored targets.
#### writetest
Determines whether to check if a share is writable.

Enabling this option tests if the scanner can write to the share, indicating possible misconfigurations. 

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
