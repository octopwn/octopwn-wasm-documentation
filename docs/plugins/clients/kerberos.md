# Kerberos Client plugin
This section describes the features and functionalities of the Kerberos client plugin

## Features
- Kerberos operations

## Commands
As usual, all functionalities will be discussed in command groups which logically group commands of similar nature.

### BASIC
#### tgt
Fetches a TGT from the server using the credentials you used when starting the session.  
Resulting TGT will be printed to the console and added as a new credential in the `Credentials Window`

#### tgs
Fetches a TGS for a given SPN, using the credentials you used when starting the session.
Resulting TGS will be printed to the console and added as a new credential in the `Credentials Window`. It is NOT usable for authentication from the credentials window however, this is in the TODO list.

#### s4uproxy
TBD

#### s4uself
TBD


### ROAST
#### kerberoast
Performs SPNRoast (kerberoast) attack, prints the results to the console.  
TIP: Instead of using username, you can use a `Session ID` of an established `LDAP` or `LDAPS` session, in this case all vulnerable users will be kerberoasted. 


krbtgt@sevenkingdoms.local - get from ldap client

just put ldap client id then it uses the ldap client to list all spns and - kerberoast all

#### asreproast
Performs asreproast attack, prints the results to the console.
TIP: Instead of using username, you can use a `Session ID` of an established `LDAP` or `LDAPS` session, in this case all vulnerable users will be asreproasted. 

### PKI
#### nt
Fetches the NT hash of the user. Only works if you created the session using a certificate type credential.

### ATTACKS
#### cve202233679
Performs CVE-2022-33679 attack against a vulnerable user. If succseeds you will get a TGT for that user.
