# Jackdaw Scanner plugin

## Features
- LDAP enumeration
- SMB enumeration

## Description

The **Jackdaw Scanner** in OctoPwn performs comprehensive LDAP and SMB enumeration in an Active Directory (AD) environment. It gathers extensive information about users, groups, computers, organizational units (OUs), and their associated security descriptors. Jackdaw also enumerates SMB sessions and shares. All collected data is stored in a SQLite database, enabling detailed analysis of domain object interactions and potential attack paths. This scanner is akin to BloodHound’s ingestor but generates a different output format focused on broad enumeration and data correlation. 

!!! info 
	More information about Jackdaw can be found here: [https://github.com/skelsec/jackdaw](https://github.com/skelsec/jackdaw)


---
## Parameters

### Normal Parameters

#### calc_edges
Determines whether to calculate edges between nodes at the end of enumeration. This saves time on collection but will then need to be done manually using the `calcedges`option of jackdaw. 
#### credential
Specifies the ID of the credential to use for authentication. Enter the ID of your credential from the credentials window here.
#### dnstarget
Optional parameter to specify the DNS target by its ID.
{==What is this==}
#### ldap_authtype
Specifies the authentication type for LDAP operations. Possible values are: `NTLM` or `Kerberos`

#### ldap_worker_cnt
Sets the number of worker threads for LDAP enumeration. 

#### smb_authtype
Specifies the authentication type for SMB operations. Possible values are: `NTLM` or `Kerberos`

#### smb_enum_shares
Determines whether to enumerate SMB shares.

#### smb_gather_types
Specifies the types of information to gather during SMB enumeration.

Available options include:

- `users`
- `groups`
- `computers`
- `shares`
- `sessions`
- `acls`
- `policies`
- `trusts`
- `spns`
- `dns`
- `services`
- `printers`
- `wmi`
- `registry`
- `files`
- `vulns`
- `all`
#### smb_host_timeout
Sets the timeout (in seconds) for SMB host enumeration.

#### smb_worker_cnt
Specifies the number of worker threads for SMB enumeration.


---
### Advanced Parameters

#### ldap_timeout
Sets the timeout (in seconds) for LDAP queries.
#### proxy
Specifies the proxy ID to use for the scan.
Enter the ID of the proxy to route the scan through. Proxies must be configured in the Proxy Window.

#### timeout
Sets the overall timeout (in seconds) for the scan.
