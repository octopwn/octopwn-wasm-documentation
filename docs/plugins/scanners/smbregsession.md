# SMB Registry Session Scanner (smbregsession)

The **SMB Registry Session Scanner** enumerates **local user SIDs** on each target host by reading the SAM registry hive through the Remote Registry service over SMB (port 445). For each discovered SID it tries to resolve the matching SAM account name. Results contain the target IP, the user SID and the resolved username when available.

Identifying local accounts that exist outside of Active Directory — service accounts, local admins with non-default names, leftover test accounts — is useful for many things. The SID list also confirms whether the default `Administrator` account (well-known SID ending in `-500`) has been renamed, which is a common AD-hardening footgun, and the resulting account list feeds straight into targeted brute-force or pass-the-hash workflows.

## SID resolution strategy

The scanner resolves SID → username in two passes:

1. **Pre-loaded cache from project data.** When the scan starts it walks every `USERS` entry stored in the project (typically populated by an earlier LDAP dump or `userenum` run) and builds an in-memory `objectSid → sAMAccountName` cache. This makes domain-SID resolution instantaneous and offline.
2. **Live LDAP fallback.** If the cache misses but you have a logged-in `LDAP` or `LDAPS` client session whose `domain_sid` matches the SID's domain prefix, the scanner asks that session to resolve the SID over the wire — without opening any new binds.

If neither pass yields a username, the SID is reported with an empty `USERNAME` field.

!!! tip "Better resolution = log into LDAP first"
    Run `userenum` (or do a full LDAP dump) **before** scanning so that the SID cache is fully populated. Without LDAP context many SIDs will stay unresolved.

!!! tip "Combine with other secret-mining scanners"
    - [smbpshistory](smbpshistory.md) — PSReadline command history files.
    - [event6secrets](event6secrets.md) — credentials embedded in event logs.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication.

Enter the ID of the credential stored in the Credentials Window. Local-admin (or sufficient registry rights) is required to open the SAM hive.

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

#### maxruntime
Specifies the maximum runtime per host (in seconds). Set to `-1` to disable.

#### proxy
Specifies the proxy ID to use for the scan.

Enter the ID of the proxy to route the scan through. Proxies must be configured in the Proxy Window.

#### resultsfile
Specifies a file for saving the scan results.

The file will be saved in OctoPwn’s `/browserefs/volatile` directory.

#### showerrors
Determines whether errors encountered during the scan should be displayed.

#### timeout
Sets the timeout (in seconds) for each connection attempt.

#### triggerports
Ports which trigger an automated `smbregsession` scan when discovered by other scanners. Pre-populated with `445/TCP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
