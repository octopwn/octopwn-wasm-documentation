# Jackdaw Scanner plugin

# Features
- LDAP enumeration
- SMB enumeration
- Kerberos attacks

# Description
This scanner plugin is akin to Bloodhound's ingestor, but doesn't produce the same output.  
Jackdaw performs LDAP enumeration including fetching User/Machine/OU/Group/... objects from the LDAP server including basic attributes and their Security Descriptor. On SMB it performs session enumeration and share enumeration.  
All results are stored in a SQLite database.

# Parameters
## sqlfile
## credential
## target
## dnstarget
## proxy
## use_ldaps
## ldap_worker_cnt
## ldap_timeout
## ldap_authtype
## smb_authtype
## smb_worker_cnt
## smb_gather_types
## smb_enum_shares
## smb_host_timeout
## calc_edges
