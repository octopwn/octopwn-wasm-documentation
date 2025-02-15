# SMB File Enumerator Scanner (snaffler)

The **Snaffler Scanner** in OctoPwn enumerates SMB shares and scans for files containing sensitive data, such as credentials, configuration files, or private keys. This scanner is based on the popular tool [Snaffler](https://github.com/SnaffCon/Snaffler) and automates the process of identifying and downloading interesting files. All downloaded files are saved to OctoPwn's file browser at `/browserefs/volatile/snaffler_downloads` for review and analysis.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication.

Enter the ID of the credential stored in the Credentials Window.

#### keepfiles
Specifies the folder enumeration depth.

Defines how deep the scanner will traverse folder structures to search for files.

#### maxdownloads
Specifies the maximum number of concurrent downloads per machine.
#### maxdownloadstotal
Specifies the maximum number of concurrent downloads across all targets.

#### maxfilesize
Specifies the maximum file size to download (in bytes).

Limits the file size to avoid downloading excessively large files. Files larger than the specified size are skipped.

#### rulesdir
Specifies the directory containing rules for identifying interesting files.

Rules can be customized to target specific file types or patterns. If not provided, default rules are applied. Rules will need to be uploaded into a directory in OctoPwn's volatile. Rules are written as `.toml`, an example can be found [here](https://github.com/SnaffCon/Snaffler/blob/master/Snaffler/SnaffRules/DefaultRules/FileRules/Discard/DiscardByFileExtension.toml)

#### targets
Specifies the targets to scan.

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
