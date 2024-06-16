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
Performs an LDAP login to the target server using the credentials selected when creating the LDAP client. If you get the error `'LDAPClient' object has no attribute 'connection'` you simply forgot to logon.
#### logout
Terminates the connection after logging out gracefully. If some commands do not return any output try logging out and back in.

### INFO
#### ldapinfo
This command prints out the LDAP root query results. This information is available to unauthenticated users (without NONE type credentials). To authenticate without any credentials, create credentials without any information of type of NONE. Then use these credentials and create an LDAP client with the Authentication Protocol SIMPLE selected in the dropdown. You will still need to first run the `login` command before being able to use the command. 

This command can act as a simple sanity check and enables you to retrieve the domain name, version and  auth types supported by the server without any credentials.

The output of the supportedControl attribute defines LDAP extension (as LDAP only comes with simple actions such as add, delete, ...). These represent the supported Object Identifiers (OIDs). 

#### adinfo
This connection prints out basic information about the current AD forest, such as the domain name. The returned attributes are useful for determining further attack proceedings. It contains the password lockout policy you need to know to if you want to conduct password spraying attacks without locking out users. The machine account quota determines how many machine accounts a normal domain user can add (This can be useful for some delegation attacks such as a resource based contrained delegation attack - for more info on that attack see the command: [addallowedtoactonbehalfofotheridentity](#addallowedtoactonbehalfofotheridentity) and some more detailed information at https://www.thehacker.recipes/ad/movement/kerberos/delegations/rbcd).

#### whoami
Performs a whoami LDAP query, prints out the domain, username and group membership information of the current user. Since a lot of further commands will need the full distinguished name (DN) for operation, note that you can convert the SID to a distinguished name using the `sid2dn` command. You might also want to find other users in the groups you are in, using the DN you can then also use the `groupmembers` command to list all group members in groups with you.

#### whoamisimple
Performs a whoami LDAP query, prints out only the domain and username in a single line.

### ROAST
These commands allow you to list potential targets available for kerberoasting and as-rep roasting. To exploit the vulnerabilities, refer to the [Kerberos Plugin](kerberos.html). If you just want to exploit, then you do not need to list the SPNs here first. It is enough to simply create an LDAP client enter the LDAP client ID in the Kerberos plugin.
#### spns
Lists all user objects who have `servicePrincipalName` set. This serves as enumeration for the Kerberoasting attack. If a user (other than `krbtgt`) has an SPN set it is possible to retrieve a TGS ticket and possibly decrypt the password of the user offline, if you are able to crack the password.  

#### asrep
Lists all user objects who have the UAC_PASSW_NOTREQ flag set. This serves as enumeration for the AS-REP Roasting attack. If a user has this flag set it is possible to retrieve their AS-REP hashes and crack the and then crack the password of the user offline.

### ENUMERATION
#### computeraddr
Lists all machine account's DNS name. This lists all computers in the domain. This can be used to identify possibly interesting targets in the domain without doing a port scan on the netowrk. 
#### targetenum
Fetches all machine account hostnames and adds them to the `Targets Window`. In case a default `resolver` is set up with an active `DNS session` all domain names will be resolved as well before storing them in the `Targets Window`. To do that, create a client of type DNS. {==Is that how I do that? I tried the DNS client and it didnt really work...==}

#### userenum
{==TODO Tamas: Please remove==}

#### dump
Fetches detailed user and machine account information and stores it in two separate .tsv files. To access the files go to the file browser window and browse to `/browserfs/volatile`. From there you can download the file to your local Downloads folder. We recommend checking the user and machine descriptions for passwords or otherwise sensitive information.

#### fulldump
{==TODO: Not working==}

#### tree
Prints out a tree from the given DN, with a given depth.

##### Parameters
- **dn** (optional): Distinguished name from where the tree should be created. E.g. `CN=Computers,DC=sevenkingdoms,DC=local`. If no parameter is given the base domain level (such as `DC=sevenkingdoms,DC=local` is listed)
- **level** (optional): Depth of the enumeration

#### bloodhound
This command runs a custom [bloodhound](https://bloodhound.readthedocs.io/en/latest/index.html) ingestor. It will gather information on domains, computers, users, gpos, groups and containers. The output is saved into the FILE browser under `/browserfs/volatile` as a standard bloodhound zip file. You can then import the file into bloodhound. 

### QUERY
#### query
Performs a raw LDAP query, prints out the results on the console.

##### Parameters

- **query**: This is your raw ldap query, such as (`(&(objectClass=user))`)
- **attributes**(optional): Specify which attributes you want to query specifically (e.g. `objectName,description`) By default all attributes will be shown.

#### modify
Performs an LDAP query to modify any attribute you define, as long as you have the permission to do that. 

##### Parameters

- **dn**: This the distinguished name of the object you want to modify. (e.g. `CN=renly.baratheon,OU=Crownlands,DC=sevenkingdoms,DC=local`)
- **attribute**: Specify which attribute you want to modify. (e.g. `displayName`) 
- **value**: Specify the value the attribute should be set to.

### USER
#### user
Fetches detailed information of a user object based on its SAMAccountName. The information can be useful to show the groups a user is a member of, if he is enabled, or when he last logged in. 

##### Parameter
- **samaccountname**: The SAMAccountname (normal username) of the user. E.g. `cersei.lannister`

#### adduser
Adds a new user to the domain with a given DN and password. This will only work if you have the correct permissions assigned to the user account you created the session with.

##### Parameters
- **user_dn**: The distinguished name of the user you want to add. (e.g. `CN=mynewuser,OU=Users,DC=sevenkingdoms,DC=local`)
- **password**: The password you want to set. Please note that it needs to correspond to the password policy, or the command will fail. 

!!! question "Troubleshooting"
	- You get the error: `Cannot fulfill request error`: You have to use an encrypted connection to modify the password. When creating a client you need to choose the `LDAPS` instead of `LDAP` as client type!
	- Error: `LDAP Add operation failed on DN user! Result code: "noSuchObject"`: You probably used the SAM Account name. You need to use the full distinguished name.
	- Result code: `entryAlreadyExists`: The user already exists. If you want to change the password of an existing user, use the `changeuserpw` function
	- Result code: `unwillingToPerform`: The password does not correspond to the password policy, choose a better password.
	- Result code: `insufficientAccessRights`: You do not have the permissions to perform the operation. Use a user with the appropriate privileges.

#### deluser
Deletes a user account given its DN. This will only work if you have the correct permissions assigned to the user account you created the session with.

##### Parameter
- **user_dn**: The distinguished name of the user you want to delete. (e.g. `CN=idontwantyou,OU=Users,DC=sevenkingdoms,DC=local`)

#### changeuserpw
Changes a user's password. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection. 

##### Parameters

- **user_dn**: The distinguished name of the user you want to change the password of. (e.g. `CN=cersei.lannister,OU=Users,DC=sevenkingdoms,DC=local`)
- **newpass**: The new password you want to set. The new password needs to comply to the password policy! 
- **oldpass**: {==What do I need it for? to change it myself? If I try that I get the error==}

```
changeuserpw user_dn=CN=m.steip,OU=Crownlands,DC=sevenkingdoms,DC=local, newpass=Passw0rd1, oldpass=Passw0rd
Error:  Exception: LDAP Modify operation failed on DN CN=m.steip,OU=Crownlands,DC=sevenkingdoms,DC=local! Result code: "constraintViolation" Reason: "b'0000052D: AtrErr: DSID-03190FC9, #1:\n\t0: 0000052D: DSID-03190FC9, problem 1005 (CONSTRAINT_ATT_TYPE), data 0, Att 9005a (unicodePwd)\n\x00'"
Traceback:   File "./octopwn/clients/ldap/console.py", line 778, in do_changeuserpw
```

??? question "Troubleshooting"
	- You get the error: `Cannot fulfill request error`: You have to use an encrypted connection to modify the password. When creating a client you need to choose the `LDAPS` instead of `LDAP` as client type!
	- Error: `LDAP Add operation failed on DN user! Result code: "noSuchObject"`: You probably used the SAM Account name. You need to use the full distinguished name.
	- Result code: `unwillingToPerform`: The password does not correspond to the password policy, choose a better password.
	- Result code: `insufficientAccessRights`: You do not have the permissions to perform the operation. Use a user with the appropriate privileges.

#### unlockuser
Unlocks a user account. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection.

{==ERROR==}

```
>>> unlockuser user_dn=CN=m.steip,OU=Crownlands,DC=sevenkingdoms,DC=local
Error:  Exception: Unknown conversion type for key "lockoutTime"
Traceback:   File "./octopwn/clients/ldap/console.py", line 790, in do_unlockuser
Traceback: 
Traceback:   File "/lib/python3.11/site-packages/msldap/connection.py", line 589, in modify
Traceback:     'changes' : encode_changes(changes)
Traceback:                 ^^^^^^^^^^^^^^^^^^^^^^^
Traceback: 
Traceback:   File "/lib/python3.11/site-packages/msldap/protocol/typeconversion.py", line 469, in encode_changes
Traceback:     raise Exception('Unknown conversion type for key "%s"' % k)
Traceback: 
```

#### enableuser
Enables a user account. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection.

##### Parameter
- **user_dn**: The distinguished name of the user you want to enable. (e.g. `CN=disabledUser,OU=Users,DC=sevenkingdoms,DC=local`)

#### disableuser
Disables a user account. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection.

##### Parameter
- **user_dn**: The distinguished name of the user you want to disable. (e.g. `CN=enabledUser,OU=Users,DC=sevenkingdoms,DC=local`)

#### addspn
Assigns an SPN to a given DN, similar to the setspn command. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection. 
This can be useful for a targeted kerberoasting attack, if you don't want to change the password. More information can be found here: [Targeted Kerberoasting](https://www.thehacker.recipes/ad/movement/dacl/targeted-kerberoasting)

##### Parameters
- **user_dn**: The distinguished name of the account you want to set the SPN on. (e.g. `CN=cersei.lannister,OU=Crownlands,DC=sevenkingdoms,DC=local`)
- **spn**: The service principal name you wish to set. (e.g. `MSSQLSvc/kingslanding.sevenkingdoms.local`)

#### delspn
Removes an SPN record from a given DN. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection.

##### Parameters
- **user_dn**: The distinguished name of the user you want to delete the SPN from. (e.g. `CN=cersei.lannister,OU=Crownlands,DC=sevenkingdoms,DC=local`)
- **spn**: The service principal name you wish to set. (e.g. `MSSQLSvc/kingslanding.sevenkingdoms.local`)

{==throws an error but works==}

```
>>> delspn user_dn=CN=m.steip,OU=Crownlands,DC=sevenkingdoms,DC=local, spn=MSSQLSvc/kingslanding.sevenkingdoms.local
SPN removed!
Error:  Exception: object of type 'bool' has no len()
Traceback:   File "/lib/python3.11/site-packages/octopwn/clients/base.py", line 638, in remote_command_internal
Traceback:     elif len(res) != 2:
Traceback:          ^^^^^^^^
Traceback:
```

#### addusertogroup
Assigns a user to a specific group. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection.

##### Parameters
- **user_dn**: The distinguished name of the user you want to add to a group. (e.g. `CN=cersei.lannister,OU=Crownlands,DC=sevenkingdoms,DC=local`)
- **group_dn**: The distinguished name of the group you want to add the user to. (e.g. `CN=Domain Admins,CN=Users,DC=sevenkingdoms,DC=local`) If you don't know the DN of a group name, you can retrieve it using the SAM account name with the `sam2dn` command. 

#### deluserfromgroup
Removes a user from a group. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection.

##### Parameters
- **user_dn**: The distinguished name of the user you want to remove from a group. (e.g. `CN=cersei.lannister,OU=Crownlands,DC=sevenkingdoms,DC=local`)
- **group_dn**: The distinguished name of the group you want to remove the user from. (e.g. `CN=Domain Admins,CN=Users,DC=sevenkingdoms,DC=local`) If you don't know the DN of a group name, you can retrieve it using the SAM account name with the `sam2dn` command. 

### MACHINE
#### machine
Fetches detailed information of a computer object based on its SAMAccountName. 

##### Parameter
- **samaccountname**: The SAMAccountName of the computer you wish query information for. (e.g. `KINGSLANDING$`). For machine accounts you MUST include the `$` sign.

#### addhostname
Adds an additional hostname to a computer account. You need the appropriate permissions to write the hostname.

##### Parameters

- **user_dn**: The distinguished name of the computer account to which you want to the DNS hostname to. (e.g. `CN=KINGSLANDING,OU=Domain Controllers,DC=sevenkingdoms,DC=local`) {==Is the name of the parameter incorrect here?==}
- **hostname**: The DNS name you want to point to the computer specified in the `user_dn` parameter. (e.g. `test2.sevenkingdoms.local`)

{==Where is this added? I can't seem to resolve this additional hostname after successfully adding it... I can see it in the SPNs though==}

#### pre2000
Lists all machine account which were created a Pre-Windows 2000 compatible machine account. This computer accounts have insecure passwords set. More information can be found here: [Pre-Windows 2000 computers](https://www.thehacker.recipes/ad/movement/domain-settings/pre-windows-2000-computers)

-----

### GPO
#### gpos
Lists all Group Policy objects in the current domain.

### LAPS
The Local Administrator Password Solution (LAPS) from Microsoft which exists in a legacy and a newer Windows LAPS implementation, manages unique local administrator passwords for domain-joined computers and securely stores them in Active Directory (AD). To access LAPS-managed passwords, users require specific privileges: the "Read" permission on the ms-Mcs-AdmPwd attribute, membership in designated AD groups like "Domain Admins," or specifically delegated permissions.

#### laps
This is the legacy LAPS implementation. It prints all machine accounts and plaintext passwords for the local admin user of said accounts. You'd need to have the necessary permission to do this. The legacy LAPS allows reading the password from the object directly.

#### newlaps
This is the new Windows LAPS implementation. It prints the encrypted blobs containing of all (or some) machine account's local administrator passwords for which your user has access to. You need to decrypt these blobs using an `SMB session`. 

{==How do I use this with an SMB session? do i just create the SMB session and it works automatically? Don't have LAPS in my lab==}

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
