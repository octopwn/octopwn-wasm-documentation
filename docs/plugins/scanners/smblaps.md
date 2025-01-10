# SMBLAPS Scanner

The **SMBLAPS Scanner** validates a single **LAPS (Local Administrator Password Solution)** admin user against all hosts in a provided LAPS dump file. This scanner is useful for verifying if dumped LAPS credentials are still valid or identifying the correct local admin username for the target system. 

This scanner requires a **LAPS dump file** containing hostnames and their corresponding local admin passwords in the format `hostname:password`.
## Use Cases

### Credential Validation
- Check if stale LAPS entries are still valid or have been rotated.
- Validate whether the provided local admin username matches the dumped LAPS password.

### Stale Credential Detection
- Identify whether LAPS passwords in the dump file are outdated or no longer functional.

### Identify Correct Local Admin Username
- Use the scanner to test and confirm the correct local administrator username for the specified host.

---

## Parameters

### Normal Parameters

#### authtype
Specifies the authentication protocol to use (e.g., NTLM).
#### domain
Defines the domain name for the admin user, if applicable.
#### lapsfile
Specifies the path to the LAPS dump file containing entries in `hostname:password` format, with one entry per line.
#### targets
Specifies the list of targets to scan.

A list of targets can be specified in the following formats:

- **ID**: ID of the target server from the Targets Window.
- **IP**: Single IP address (e.g., `192.168.1.1`).
- **CIDR**: IP range in CIDR notation (e.g., `192.168.1.0/24`).
- **Hostname**: Resolvable hostname.
- **File**: Path to a file containing targets (must be in OctoPwn’s `/browserefs/volatile` directory). File lists need to be uploaded into OctoPwn and separated by newlines.
- **Control word**: Use `all` to scan all stored targets.
#### username
Specifies the local admin username to test against the LAPS dump file.

---

### Advanced Parameters

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
