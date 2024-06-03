# LDAP Client plugin
This section describes the features and functionalities of the LDAP client plugin

## Features
- LDAP browser
- LDAP operations

### Getting started
To use the LDAP Client plugin, select the credentials and the target and then create a client of type SMB in the Main GUI. This will open the SMB2 client window with the selected credentials. For most operations you will need to run the `login` command to get started.

For more information on supported credentials, see the [credentials page](../../user-guide/credentials.html). Please note, that not all authentication methods support all functions.

After sucsessfully creating an LDAP client, the LDAP browser will automatically list the host in the File Browser Window
The ldap browser supports basic ldap listing operations, similar to ADExplorer.

## Commands
As usual, all functionalities will be discussed in command groups which logically group commands of similar nature.

### CONNECTION
#### login
Performs an LDAP login to the target server using the credentials selected when creating the LDAP client. 
#### logout
Terminates the connection after logging out gracefully. If some commands do not return any output try logging out and back in.

### INFO
#### ldapinfo
This command prints out the LDAP root query results. 

information is available to unauth users (without login) - link to none cred
use simple authentication protocol with none credentials

as anonymous user you can get domain name, auth types supported by the server, you can find out what version the server is

sanity check

supportedcontrol: ldap extensions, as ldap only has add, delete, ...; extended controls: These are OIDs, one of these triggers the server to tell you what your username is

#### adinfo
This connection prints out basic information about the current AD forest

attributes of the current forest, password lockout policy, machine account quota
#### whoami
Performs a whoami LDAP query, prints out the domain, username and group membership information of the current user
#### whoamisimple
Performs a whoami LDAP query, prints out only the domain and username.

### ROAST
These commands allow you to list potential targets available for kerberoasting and as-rep roasting. To exploit the vulnerabilities, refer to the [Kerberos Plugin](kerberos.html). If you just want to exploit, then you do not need to list the SPNs here first. It is enough to simply create an LDAP client enter the LDAP client ID in the Kerberos plugin.
#### spns
Lists all user objects who have `servicePrincipalName` set. This serves as enumeration for the Kerberoasting attack. 
#### asrep
Lists all user objects who have the UAC_PASSW_NOTREQ flag set. This serves as enumeration for the AS-REP Roasting attack. 

### ENUMERATION
#### computeraddr
Lists all machine account's DNS name - all computers in the domain
#### targetenum
Fetches all machine account hostnames and adds them to the `Targets Window`. In case a default `resolver` is set up with an active `DNS session` all domain names will be resolved as well before storing them in the `Targets Window`.

#### userenum
TODO Tamas: Please remove

#### dump
Fetches detailed user and machine account information and stores it in two separate .tsv files

#### fulldump
TODO: Not working

#### tree
Prints out a tree from the given DN, with a given depth. (CN=USERS,DC=SEVENKINGDOMS,DC=LOCAL)
params!

##### Parameters
- **dn** (optional): Distinguished name from where the tree should be created. E.g. `CN=Computers,DC=sevenkingdoms,DC=local`
- **level** (optional): Depth of the enumeration

#### bloodhound
This command runs a custom bloodhound ingestor. It will gather information on domains, computers, users, gpos, groups and containers. The output is saved into the FILE browser under `/browserfs/volatile` as a standard bloodhound zip file. 

### QUERY
#### query
Performs a raw LDAP query, prints out the results on the console.

##### Parameters

- **query**: put example of proper ldap query
- **attributes**(optional): specify you want only specific attributes liste eg name

### USER
#### user
Fetches detailed information of a user object based on its SAMAccountName.

##### Parameter
- **samaccountname**: The SAMAccountname (normal username) of the user. E.g. `cersei.lannister`

#### adduser
Adds a new user to the domain with a given DN and password. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection (depends on configuration). When creating a client you need to choose the LDAPS client as client type.

Cannot fulfill request error => use ldaps

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
adds additional hostname to a computer accounts. adds an additional dns entry. 

#### pre2000
Lists all machine account which were created a Pre-Windows 2000 compatible machine account 

-----

### GPO
#### gpos
Lists all GPOs

### LAPS
#### laps
Prints all machine accounts and plaintext passwords for the local admin user of said accounts. You'd need to have the necessary permission to do this.

#### newlaps
Print the encrypted blobs containing all (or some) machine account's local administrator passwords for which your user has access to. You'd need to Decrypt these blobs using an `SMB session`

what is the difference between laps and newlaps?

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
