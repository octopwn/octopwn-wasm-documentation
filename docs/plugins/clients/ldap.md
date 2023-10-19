# LDAP Client plugin
This section describes the features and functionalities of the LDAP client plugin

## Features
- LDAP browser
- LDAP operations

### LDAP browser
After sucsessfully logging in to the target server, the SMB file browser will automatically list the host in the File Browser Window
The file browser supports basic file operations as you'd expect from a file browser like downloading and uploading files, removing and creating directories.

## Commands
As usual, all functionalities will be discussed in command groups which logically group commands of similar nature.

### CONNECTION
#### login
#### logout

### INFO
#### ldapinfo
This command prints out the LDAP root query results.
#### adinfo
This connection prints out basic information about the current AD forest
#### whoami
Performs a whoami LDAP query, prints out the domain, username and group membership information of the curret user

### ROAST
#### spns
Lists all user objects who have `servicePrincipalName` set.

#### asrep
Lists all user objects who have the UAC_PASSW_NOTREQ flag set.

### ENUMERATION
#### computeraddr
Lists all machine account's DNS name
#### targetenum
Fetches all machine account hostnames and adds them to the `Targets Window`. In case a default `resolver` is set up with an active `DNS session` all domain names will be resolved as well before storing them in the `Targets Window`

#### userenum

#### dump
Fetches detailed user and machine account information and stores it in two separate .tsv files

#### tree
Prints out a tree from the given DN, with a given depth.

### QUERY
#### query
Performs a raw LDAP query, prints out the results on the console.

### USER
#### user
Fetches detailed information of a user object based on its SAMAccountName
#### adduser
Adds a new user to the domain with a given DN and password. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection.

#### deluser
Deletes a user account given its DN. This will only work if you have the correct permissions assigned to the user account you created the session with.

#### changeuserpw
Changes a user's password. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection.

#### unlockuser
Unlocks a user account. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection.

#### enableuser
Enables a user account. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection.

#### disableuser
Disables a user account. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection.

#### addspn
Assigns an SPN to a given DN. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection.

#### delspn
Removes an SPN record from a given DN. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection.

#### addusertogroup
Assigns a user to a specific group. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection.

#### deluserfromgroup
Removes a user from a group. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection.

### MACHINE
#### machine
Fetches detailed information of a user object based on its SAMAccountName

#### addhostname

#### pre2000
Lists all machine account which were created a Pre-Windows 2000 compatible machine account 

### GPO
#### gpos
Lists all GPOs

### LAPS
#### laps
Prints all machine accounts and plaintext passwords for the local admin user of said accounts. You'd need to have the necessary permission to do this.

#### newlaps
Print the encrypted blobs containing all (or some) machine account's local administrator passwords for which your user has access to. You'd need to Decrypt these blobs using an `SMB session`

### GROUP
#### groupmembership

#### groupmembers

#### dadms
Lists first degree domain admins.

### TRUSTS
#### trusts
Lists AD trusts.

### SCHEMA
#### schemaentry
Used for debugging purposes.
#### allschemaentry
Used for debugging purposes. Do not use this!

### SECURITY DESCRIPTOR
#### changeowner
Changes the Owner entry in the nTSecurityDescriptor attribute of a given DN
#### addprivdcsync
Adds DCSync privileges to a a user specified by DN on the current forest.

#### addprivaddmember
Adds AddMember privileges to a user on a group

#### setsd
Replaces the security descriptor of a given DN.

#### getsd
Fetches the security descriptor of a given DN

#### addallowedtoactonbehalfofotheridentity


### SID
#### sidresolv
#### sid2dn
Fetches the DN for an object identified by its SID
#### dn2sid
Fetches the SID of an object identified by its DN
#### dn2sam
Fetches the sAMAccountName of a given object identified by its DN
#### sam2dn
Fetches the DN of an object by its sAMAccountName

### GMSA
#### gmsa


### PKI
#### certify
Lightweigth certipy implementation. When the command field is `vuln` it will show potentically vulnerablecertificate templates.

#### rootcas
Lists all root certificate authorities

#### ntcas
Lists all NT certificate authorities

#### aiacas

#### enrollmentservices
Lists all enrollment services

#### addcerttemplatenameflagaltname
Modifies a certificate template by giving the 
#### addenrollmentright
#### certtemplates
Lists all certificate templates with attributes when `name` parameter is left empty, otherwise it only lists the specific template attributes.

### DELEGATION
#### unconstrained
Lists all unconstrained delegetion objects
#### constrained
Lists all constrained delegation objects
#### s4u2proxy


### DNS
#### dnszones
Lists all dns zones
#### dnsdump
Fetches all DNS entries when the `zone` parameter is empty and stores them in a .tsv file. In case the `zone` parameter is set it will only fetch DNS entries for that gibven zone.
