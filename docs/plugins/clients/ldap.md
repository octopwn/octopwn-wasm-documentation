# LDAP Client plugin
This section describes the features and functionalities of the LDAP client plugin

## Features
- LDAP browser
- LDAP operations
- Full Active Directory Dump
- Custom BloodHound Ingestor
- Operations on Users such as changing passwords, adding SPNs, adding users to a group 
- Adding machine accounts
- Viewing Group Policies
- Extracting LAPS Passwords
- Viewing group memberships
- Enumerating trusts
- Altering security descriptors and AD attributes(e.g. such as adding dcsync privileges, changing owner, adding to `allowedtoactonbehalfofotheridentity` attribute for Resource-Based Constrained Delegation abuse)
- Listing Group-Managed Service Accounts
- Enumerate Certificates and checking for vulnerable certificate templates
- Enumeration AD objects that have delegation privileges
 
### Getting started
To use the LDAP Client plugin, select the credentials and the target and then create a client of type SMB in the Main GUI. This will open the SMB2 client window with the selected credentials. For most operations you will need to run the `login` command to get started.

For more information on supported credentials, see the [credentials page](../../user-guide/credentials.html). Please note, that not all authentication methods support all functions.

After sucsessfully creating an LDAP client, the LDAP browser will automatically list the host in the File Browser Window
The ldap browser supports basic ldap listing operations, similar to ADExplorer.

### Supported Authentication Types
| Authentication Protocol | Secret Type | Description | Example |
| ----- | ----- | ------| ----- |
| NTLM | Password | Plaintext Password | MyPassw0rd | 
| NTLM | NT | NT Hash | 8846F7EAEE8FB117AD06BDD830B7586C |
| NTLM | RC4 | RC4 NT Hash - same as NT | 8846F7EAEE8FB117AD06BDD830B7586C |
| NTLM | AES | AES Key (contains a salt such as TEST.LOCALusername) - can be used in stead of the NT Hash | d74ff0ee8da3b9806b18c877dbf29bbde50b5bd8e4dad7a3a725000feb82e8f1 |
| NTLM | NONE | Null authentication |  |
| Kerberos | NT | NT Hash | 8846F7EAEE8FB117AD06BDD830B7586C |
| Kerberos | RC4 | RC4 NT Hash | 8846F7EAEE8FB117AD06BDD830B7586C |
| Kerberos | AES | AES Key (contains a salt such as TEST.LOCALusername) - can be used instead of the NT Hash | d74ff0ee8da3b9806b18c877dbf29bbde50b5bd8e4dad7a3a725000feb82e8f1 |
| Kerberos | P12/PFX | Certificate - upload the certificate to volatile storage and then enter certfile path relative from `/browserefs/volatile`. If the certfile has a password, enter it as a secret | Administrator.pfx |
| Kerberos | CCACHE | Kerberos credentials in binary CCACHE file format  | Administrator.ccache |
| Kerberos | KEYTAB | Kerberos credentials in binary KEYTAB file format | Administrator.keytab |
| Kerberos | KIRBI | Kerberos credentials in binary KIRBI file format | Administrator.kirbi |
| Kerberos | KIRBI | Kerberos credentials in base64 KIRBI file format | doIF9DCCBfCg ...(snip)... ZXVzLmdob3N0cGFjay5sb2NhbA== |
| Kerberos | NONE | Null authentication |  |
| SSL | P12/PFX, PEM |  | |
| SIMPLE | Password |  | |
| SICILY | Password, NT Hash, AES |  | |


**NTLM (NT LAN Manager)**: A challenge-response authentication protocol used to authenticate a client to a network server on a Windows domain. It's commonly used for SMB and LDAP in environments where Kerberos might not be feasible.

**Kerberos**: A network authentication protocol designed to provide strong authentication for client/server applications by using secret-key cryptography. It's highly recommended for environments that require robust security, especially in Active Directory setups.

**SSL (Secure Sockets Layer)**: Provides encryption for data transfers, creating a secure channel over potentially insecure networks. Primarily used in LDAP configurations when data security and privacy are of paramount importance.

**SIMPLE**: The most basic form of authentication that transmits credentials in plain text. It is generally not recommended for secure environments unless additional security measures, like encryption, are already in place.

**SICILY (Security Integrated Channel over LDAP Integrated Cryptographic Login)**: Microsoft's proprietary authentication protocol that supports multiple authentication methods including NTLM and sometimes Kerberos. It provides a more integrated authentication approach, particularly useful in Microsoft-centric environments.


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

!!! info
	To run a Kerberoasting attack on all users you can enter the Client ID of this LDAP plugin in the [kerberoast](kerberos.html#kerberoast) command. 

#### asrep
Lists all user objects who have the UAC_PASSW_NOTREQ flag set. This serves as enumeration for the AS-REP Roasting attack. If a user has this flag set it is possible to retrieve their AS-REP hashes and crack the and then crack the password of the user offline.

### ENUMERATION
#### computeraddr
Lists all machine account's DNS name. This lists all computers in the domain. This can be used to identify possibly interesting targets in the domain without doing a port scan on the netowrk. 
#### targetenum
Fetches all machine account hostnames and adds them to the `Targets Window`. In case a default `resolver` is set up with an active `DNS session` all domain names will be resolved as well before storing them in the `Targets Window`. To do that, create a client of type DNS. 

!!! info "Troubleshooting"
	Make sure you have clicked the login button, otherwise you will get the error `Exception: 'NoneType' object has no attribute '_ldapinfo'`.
##### Parameters
- resolve: Specifies if you want the DNS resolver to automatically resolve the target host names so they are correctly populated in the targets window. 

#### dump
Fetches detailed user and machine account information and stores it in two separate .tsv files. To access the files go to the file browser window and browse to `/browserfs/volatile`. From there you can download the file to your local Downloads folder. We recommend checking the user and machine descriptions for passwords or otherwise sensitive information.

#### tree
Prints out a tree from the given DN, with a given depth.

##### Parameters
- **dn** (optional): Distinguished name from where the tree should be created. E.g. `CN=Computers,DC=sevenkingdoms,DC=local`. If no parameter is given the base domain level (such as `DC=sevenkingdoms,DC=local` is listed)
- **level** (optional): Depth of the enumeration

#### bloodhound
This command runs a custom [bloodhound](https://bloodhound.readthedocs.io/en/latest/index.html) ingestor. It will gather information on domains, computers, users, gpos, groups and containers. The output is saved into the FILE browser under `/browserfs/volatile` as a standard bloodhound zip file. You can then import the file into bloodhound. 

!!! info
	The currently implemented ingestor is written for BloodHound v1, not the newer BloodHound CE. 

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
Changes a user's password. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use an `LDAPS` Client/an encrypted LDAP connection. 

##### Parameters

- **user_dn**: The distinguished name of the user you want to change the password of. (e.g. `CN=cersei.lannister,OU=Users,DC=sevenkingdoms,DC=local`)
- **newpass**: The new password you want to set. The new password needs to comply to the password policy! 
- **oldpass (optional)**: If you want to change your own or another user's password as a non-admin you have to supply the old password. If you are not an administrator, you will need to provide the oldpassword. You can change the password of any user with his old password.
??? question "Troubleshooting"
	- You get the error: `constraintViolation`: Changing the password is only possible from an **encrypted LDAPS Client**. Create an LDAPS client from the clients window on the side and try changing the password with an encrypted session again. 
	- Error: `LDAP Add operation failed on DN user! Result code: "noSuchObject"`: You probably used the SAM Account name. You need to use the full distinguished name.
	- Result code: `unwillingToPerform`: The password does not correspond to the password policy, choose a better password. You need to keep in mind the minimum password age, if you or the user recently changed the password you might not be able to change it immediately. Be aware of the password complexity and length of the password. 
	- Result code: `insufficientAccessRights`: You do not have the permissions to perform the operation. Use a user with the appropriate privileges.

#### unlockuser
Unlocks a user account. This will only work if you have the correct permissions assigned to the user account you created the session with, also you must use `LDAPS` or an encrypted LDAP connection.
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

{==msds-additionaldnshostname, used for https://www.thehacker.recipes/ad/movement/kerberos/delegations/unconstrained==}

##### Parameters

- **user_dn**: The distinguished name of the computer account to which you want to the DNS hostname to. (e.g. `CN=KINGSLANDING,OU=Domain Controllers,DC=sevenkingdoms,DC=local`) {==Is the name of the parameter incorrect here?==}
- **hostname**: The DNS name you want to point to the computer specified in the `user_dn` parameter. (e.g. `test2.sevenkingdoms.local`)

{==Where is this added? I can't seem to resolve this additional hostname after successfully adding it... I can see it in the SPNs though==}

#### pre2000
Lists all machine account which were created a Pre-Windows 2000 compatible machine account. This computer accounts have insecure passwords set. More information can be found here: [Pre-Windows 2000 computers](https://www.thehacker.recipes/ad/movement/domain-settings/pre-windows-2000-computers)

#### computeradd
Adds a machine account with the specified password. By default any domain user can add a machine account to the Active Directory. To check if this is possible, check the `adinfo` command. If it is zero, you will need to have the permission to add machine accounts.

##### Parameters
- **computername**: The name of the computer object you want to add. {==What format? just `computer`or `computer$`?==}
- **password**: The plain text computer password you want the computer object to have.

{==Error:  Exception: 'MSLDAPClientConnection' object has no attribute 'add_computer==}

#### changesamaccountname
Changes the samaccountname attribute of an active directory object. 

##### Parameters
- **dn**: The distinguished name of the user or machine you want to change the samaccountname of. E.g. `CN=cersei.lannister,OU=Crownlands,DC=sevenkingdoms,DC=local`
- **newname**: The new samAccountName. E.g.  `cersei.baratheon`

{== 'MSLDAPClientConnection' object has no attribute 'change_samaccountname' Shouldn't that be under users?==}

### GPO
#### gpos
Lists all Group Policy objects in the current domain.

### LAPS
The Local Administrator Password Solution (LAPS) from Microsoft which exists in a legacy and a newer Windows LAPS implementation, manages unique local administrator passwords for domain-joined computers and securely stores them in Active Directory (AD). To access LAPS-managed passwords, users require specific privileges: the "Read" permission on the ms-Mcs-AdmPwd attribute, membership in designated AD groups like "Domain Admins," or specifically delegated permissions.

#### laps
This is the legacy LAPS implementation. It prints all machine accounts and plaintext passwords for the local admin user of said accounts. You'd need to have the necessary permission to do this. The legacy LAPS allows reading the password from the object directly.

#### newlaps
This is the new Windows LAPS implementation. It prints the encrypted blobs containing of all (or some) machine account's local administrator passwords for which your user has access to. You need to decrypt these blobs using an `SMB session`. 

{==How do I use this with an SMB session? do i just create the SMB session and it works automatically? Don't have LAPS in my lab = > more dev time needed, seperate feature later on==}

### GROUP
#### groupmembership
Retrieves a list of groups to which the specified distinguished name (DN) belongs (is a member of).

##### Parameter
- **dn**: The distinguished name (DN) of the Active Directory (AD) object for which you wish to determine group membership. (e.g. `CN=cersei.lannister,OU=Crownlands,DC=sevenkingdoms,DC=local`).

#### groupmembers
Retrieves a list of members belonging to a specified group.

##### Parameters

- **dn**: The distinguished name (DN) of the group whose members you wish to list. Example: `CN=Remote Desktop Users,CN=Builtin,DC=sevenkingdoms,DC=local`.
- **recursive** (optional): A boolean value indicating whether to retrieve members recursively, including members of subgroups. Set to True for a recursive search or False for a non-recursive search. The default value is True.

#### dadms
Lists first degree domain admins.

### TRUSTS

In Active Directory (AD) environments, trusts can be bidirectional, allowing reciprocal access between domains, or unidirectional, where only one domain has access privileges to the other.

If you have domain admin rights in a child domain, you can exploit trust relationships to directly escalate privileges into a parent domain. This is achievable using either the krbtgt hash or the Trust Key between the domains.

For one-way inbound trusts, where the trust is inbound from the perspective of your controlled domain, it permits entities in your domain to access resources in the trusted foreign domain. You can abuse this by enumerating and identifying foreign domain groups that include users from your domain. By manipulating these relationships and using tools like OctoPwn to handle Kerberos ticket requests, you can impersonate legitimate foreign domain users, gaining access to systems and resources in the trusted domain.

Conversely, one-way outbound trusts can be partially exploited even though they are designed to restrict your domain’s access to the trusted domain. You can leverage shared credentials stored in Trusted Domain Objects (TDOs), which contain the trust keys (inter-realm keys) automatically updated every 30 days. By extracting these keys, you can impersonate trust accounts in the foreign trusted domain, potentially accessing resources despite the one-way nature of the trust.

#### trusts
Lists AD trusts.

### SCHEMA
#### schemaentry
Used for debugging purposes. Do not use this!
#### allschemaentry
Used for debugging purposes. Do not use this!

### SECURITY DESCRIPTOR
#### changeowner
Modifies the owner listed in the `nTSecurityDescriptor` attribute of a specified AD object specified by the distinguished name (DN) in Active Directory.

##### Parameters
- **new_owner_sid**: SID (Security Identifier) of the AD user or group to be granted ownership permissions for the target. Use the `dn2sid` command to convert a DN into a SID. Example: `S-1-5-21-687080233-923555765-3897950641-1116`.
- **target_dn**: The DN of the target object for which the specified user or group in the `new_owner_sid` will be assigned ownership permissions. Example: `CN=Small Council,OU=Crownlands,DC=sevenkingdoms,DC=local`
- **target_attribute** (optional): Specifies the attribute within the AD object that should receive the SID. The default attribute is nTSecurityDescriptor, which contains ownership permissions. Specify this parameter only if you need to write the SID to a different attribute in the AD object.

!!! troubleshooting
	If you get the error `constraintViolation` you probably do not have the appropriate permission to change the owner.

#### addprivdcsync
Adds DCSync rights to the given user by modifying the forest's Security Descriptor to add GetChanges and GetChangesAll ACE. You need permissions to change the forest's security descriptor. 

##### Parameters
- **user_dn**: The user you want to add dcsync privileges for. Example: `CN=tyron.lannister,OU=Westerlands,DC=sevenkingdoms,DC=local`
- **forest** (optional): {==DN Name of the forest I want to change. Write privileges to the forest DN object needed. Will use current DN of the connection if omitted. Can I just put a foreign domain such as `essos.local` here and it works? I did it and it said it's okay, but I wasn't able to dcsync or see it in done, so I guess no. What else would this be for?==}

#### addprivaddmember
Grants a user the AddMember privilege for a specific group within the domain. This action authorizes the user to add members to the group but does not include the user as a member of the group.

##### Parameters
- **user_dn**: The distinguished name (DN) of the user to whom you want to assign the privilege.  Example: CN=tyron.lannister,OU=Westerlands,DC=sevenkingdoms,DC=local
- **group_dn**: The distinguished name (DN) of the group to which the AddMember privilege will be applied. Example: CN=Small Council,OU=Crownlands,DC=sevenkingdoms,DC=local

#### setsd
Replaces the security descriptor of a specified distinguished name (DN) in Active Directory. We recommend fetching the old Security descriptor first with `getsd`and then replacing only the relevant parts.

- **target_dn**: The distinguished name (DN) of the AD object whose security descriptor is to be replaced.
- **sddl**: The raw Security Descriptor Definition Language (SDDL) string that defines the new security settings. For more information on SDDL syntax and structure, refer to Microsoft's official [SDDL documentation](https://learn.microsoft.com/en-us/windows/win32/secauthz/security-descriptor-definition-language).

#### getsd
Fetches the security descriptor of a given DN. 

##### Parameter
 - **dn**: The distinguished name (DN) of the AD object for which the security descriptor will be fetched.

#### addallowedtoactonbehalfofotheridentity

This command can be used to abuse Resource-Based Constrained Delegation. 

Resource-based Constrained Delegation (RBCD) is a powerful mechanism in Active Directory that can be exploited using commands like `addallowedtoactonbehalfofotheridentity` (from the LDAP client), `s4uself`, and `s4uproxy` commands (from the Kerberos client) to escalate privileges and gain unauthorized access to network resources. Here's how these components work together in an RBCD attack scenario:

##### Understanding Resource-Based Constrained Delegation
RBCD allows a computer or service in Active Directory to delegate to another computer or service. This is controlled through the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute on a target computer object, which specifies which principals (users or computers) are permitted to delegate their identity to the target. Modifying this attribute to include an attacker-controlled principal can set the stage for a delegation-based attack.

More detailed information on RBCD can be found [here](https://www.thehacker.recipes/ad/movement/kerberos/delegations/rbcd).

##### Step-by-Step Exploitation Process

- Setup with `addallowedtoactonbehalfofotheridentity`:
  Use the `addallowedtoactonbehalfofotheridentity` command to modify the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute of a target computer object in AD. This is done by specifying a principal that the attacker controls and which has a Service Principal Name (SPN). The SPN is crucial for Kerberos to function properly in these delegation scenarios.

- Ticket Manipulation with `s4uself` command (Kerberos Client):
  s4u2self is a Kerberos extension used to obtain a service ticket on behalf of any user (even those who have not authenticated via Kerberos) to the service running under the account executing the command. In an RBCD context, s4u2self is used to acquire a service ticket for the attacker-controlled account specified in the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute. This service ticket impersonates a high-privilege user.

- Extending Access with `s4uproxy` command (Kerberos Client):
  After obtaining an initial service ticket with `s4uself`, `s4uproxy` can be employed to request access to additional services on behalf of the impersonated user. It uses the previously obtained ticket to request another service ticket for a different service that the initial account is allowed to delegate to. 

##### Practical Application and Parameters
- Using `addallowedtoactonbehalfofotheridentity`:
	- Parameters:
        - **target_dn**: The distinguished name (DN) of the target Active Directory object for which you want to configure delegation. This is usually a computer object within the domain that will be permitted to act on behalf of another identity.
        - **other_identity**: The Security Identifier (SID) of the user or computer that will be allowed to act on behalf of the target specified in `target_dn`. This identity is granted the ability to impersonate the target object when requesting access to resources. 

        {==How do I abuse it with your tool, especially the s4uself and s4uproxy part==}

        ```
        execute-assembly Rubeus.exe s4u /user:computer where we have computer account nt hash of$ /rc4:<rc4 hash of this computer> /impersonateuser:<localadmin da or dc> /msdsspn:cifs/TargetComputer /ptt
        ```

To effectively add permissions using commands like `addallowedtoactonbehalfofotheridentity` in an RBCD scenario, certain prerequisites and permissions are necessary. These are often identified through tools such as BloodHound, which can visualize and pinpoint specific AD permissions and misconfigurations. Here's a brief explanation of what is required to successfully manipulate AD attributes for escalating privileges:

- _GenericWrite_:
    This permission allows a user to modify most attributes of an object in Active Directory, which is essential for setting up conditions for RBCD attacks. It doesn't include permissions to modify security-sensitive attributes directly, but includes the ability to set the msDS-AllowedToActOnBehalfOfOtherIdentity attribute directly.

- _GenericAll_:
    This is a more extensive permission that includes GenericWrite but also allows full control over the object, including the ability to modify security descriptors and change ownership. With GenericAll, an attacker can completely control an AD object, 

- _WriteOwner_:
    This permission specifically allows a user to change the owner of an AD object. Changing ownership is crucial because, as the owner, a user gains the ability to modify the object’s discretionary access control list (DACL). Before utilizing this, you might need to first establish yourself as the owner, which can be facilitated through the `changeowner` command, as described here.

- _Owner_:
	If you are the owner you will need to grant yourself at least GenericWrite privileges on the object you want to modify by using the `setsd` command.

- _WriteDACL_:
    With the ability to modify the DACL of an object, a user can grant themselves or others additional permissions on that object by adjusting the security descriptor using the `setsd` command, allowing you to specify exactly what permissions are added or removed.

### SID
#### sidresolv

Resolves the username and domain for a given Security Identifier (SID).

##### Parameter

- sid: The Security Identifier (SID) of the user or object whose details are to be resolved.

#### sid2dn
Retrieves the Distinguished Name (DN) for an object based on its Security Identifier (SID).

##### Parameter
- **sid**: The SID of the object for which the DN is required.

#### dn2sid
Fetches the Security Identifier (SID) of an object identified by its Distinguished Name (DN).

##### Parameter
- **dn**: The DN of the object whose SID is to be retrieved.

#### dn2sam
{==does not work==}
Retrieves the sAMAccountName of an object identified by its Distinguished Name (DN).

##### Parameter
- **dn**: The DN of the object for which the sAMAccountName is required.

#### sam2dn
{==does not work==}
Fetches the Distinguished Name (DN) of an object using its sAMAccountName.

##### Parameter
- **sAMAccountName**: The sAMAccountName of the object whose DN is needed.

### GMSA
#### gmsa
The `gmsa` command allows for reading the passwords of Group Managed Service Accounts (gMSA), which is used for services and tasks requiring privileged access. Access to read gMSA passwords is permissible only when an entity controls an object with adequate permissions outlined in the target gMSA account’s msDS-GroupMSAMembership attribute's Discretionary Access Control List (DACL). Typically, these are principals explicitly allowed to use the gMSA account. 

More information can be found [here](https://web.archive.org/web/20240228044821/https://cube0x0.github.io/Relaying-for-gMSA/).

### PKI
#### certify
This command is a lightweight implementation of Certipy, designed to analyze certificate templates within an Active Directory environment. Set `cmd` to `vuln` to find vulnerable certificates. It lists all/vulnerable certificate templates (depending on the cmd). 

When using the `vuln` command you can encounter the following outputs:

- Enrollee supplies subject: This is ESC1, see the [SMB Client certreq command](smb.html#certreq) on how to abuse it.
{==TODO What can we do with the others?==} 
- Certificate request agent
- Needs authorized signature
- Needs manager approval
- Owner is low priv user
- Owner can be controlled by current user
- Lowpriv SID has full control
- Lowpriv SID can write DACLs
- Lowpriv SID can change Owner
- Lowpriv SID can write property
- Current user can write DACLs
- Current user can change Owner
- Current user can write property
- Current user has full control

##### Parameters

- **cmd** (optional): This parameter allows the user to specify the command type. Setting this to `vuln` will filter and display only those certificate templates that are potentially vulnerable. If no parameters are used, the command will list all certificate templates available within the directory.
- **username** (optional): Use this parameter to search certificate templates based on specific user permissions. It will return templates where the specified user has permissions
#### rootcas
Lists all root certificate authorities in the domain

#### ntcas
Lists all NT certificate authorities in the domain

#### aiacas

Lists all Authority Information Access authorities in the domain

{==What can I do with these? is this just info? why would I want to know them?==}

#### enrollmentservices
Lists all enrollment services. This can be helpful in identifying if there are services with Certificate Web Enrollment enabled. You can check this by browsing to the host the CA service is running on to `http(s)://%ADCSServer%/certsrv/certfnsh.asp`. If web enrollment is enabled you can abuse ESC8 with ntlmrelayx and coercion.  

More information on that can be found [here](https://dirkjanm.io/ntlm-relaying-to-ad-certificate-services/).

#### addcerttemplatenameflagaltname
Modifies the msPKI-Certificate-Name-Flag value of the specified certificate template and enables ENROLLEE_SUPPLIES_SUBJECT_ALT_NAME bit. If 'flags' is present then it will assign that value.

{==error==}

```
invalidAttributeSyntax" Reason: "b'00000057: LdapErr: DSID-0C090FC7, comment: Error in attribute conversion operation
```

##### Parameters
- **certtemplatename**: Name of the certificate template
- **flags**: {==??? what ==}
#### addenrollmentright
Grants enrollment rights to a user (by DN) for the specified certificate template. Use this if you have permissions to write properties, but don't have enrollment rights yet. 

##### Parameters
- **certtemplatename**: The name of the certificate template to which you whish to add enrollment rights to. Example: `MyEnrollmentAgent`
- **user_dn**: The distinguished name (DN) of the user or group you want to add enrollment rights for on the specified template. Example: `CN=tyron.lannister,OU=Westerlands,DC=sevenkingdoms,DC=local`

#### certtemplates
Lists all certificate templates with attributes their attributes. This does not check for specifically vulnerable templates.  

##### Parameter
- **name** (optional): The name of a specific certificate template you want to view, if you already know the name. If you do not enter anything, all templates will be shown.  

### DELEGATION
#### unconstrained
Identifies all Active Directory objects configured with unconstrained delegation by searching for those marked with the TRUSTED_FOR_DELEGATION flag. For more details on unconstrained delegation, visit: [Unconstrained Delegation - The Hacker Recipes](https://www.thehacker.recipes/ad/movement/kerberos/delegations/unconstrained).

#### constrained
Identifies Active Directory service accounts configured with constrained delegation, allowing them to impersonate users (except those protected against delegation) to access specified services. This command helps audit which services can potentially be accessed via delegation. Note that users flagged as "is sensitive and cannot be delegated" or members of the "Protected Users" group are immune to such delegation attempts, except for the native Administrator account (RID 500), which remains vulnerable even if added to the Protected Users group. For more insights on constrained delegation, you can check [here](
https://www.thehacker.recipes/ad/movement/kerberos/delegations/constrained).

#### s4u2proxy

Lists all s4u2proxy objects.

{==What are s4u2proxy objects?==}


### DNS
#### dnszones
Lists all dns zones

{==Doesn't seem to list anything==}

#### dnsdump
Fetches all DNS entries when the `zone` parameter is empty and stores them in a .tsv file. In case the `zone` parameter is set it will only fetch DNS entries for that gibven zone.

{==Exception==}
```
dnsdump zone=sevenkingdoms.local
Error:  Exception: unknown address family 10
Traceback:   File "./octopwn/clients/ldap/console.py", line 1344, in do_dnsdump
Traceback: 
Traceback:   File "/lib/python3.11/site-packages/msldap/wintypes/dnsp/strcutures.py", line 91, in get_formatted
Traceback:     return MSLDAP_DNS_TYPE_TO_CLASS[self.Type].from_bytes(self.Data)
Traceback:            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Traceback: 
Traceback:   File "/lib/python3.11/site-packages/msldap/wintypes/dnsp/strcutures.py", line 154, in from_bytes
Traceback:     return DNS_RPC_RECORD_AAAA.from_buffer(io.BytesIO(data))
Traceback:            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Traceback: 
Traceback:   File "/lib/python3.11/site-packages/msldap/wintypes/dnsp/strcutures.py", line 159, in from_buffer
Traceback:     res.IpAddress = socket.inet_ntop(socket.AF_INET6, buff.read(16))
Traceback:                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```