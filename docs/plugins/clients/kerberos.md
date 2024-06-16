# Kerberos Client plugin
This section describes the features and functionalities of the Kerberos client plugin

## Features
- Kerberos operations

## Commands
As usual, all functionalities will be discussed in command groups which logically group commands of similar nature. 

### BASIC

!!! info
	For Kerberos authentication to work properly, you need to set the Global Realm and create a DNS resolver client and set the Global Resolver as well. {{==TODO: Show in GUI how to do that ==}}

#### tgt
Fetches a Kerberos Ticket-Granting-Ticket (TGT) from the server using the credentials you used when starting the session. The TGT allows you authenticate int the domain using Kerberos. In order to retrieve a TGT you will need a valid credentials. 

Resulting TGT will be printed to the console in the kirbi format with base64 encoding and added as a new credential in the `Credentials Window`. You can then use the credentials directly for authenticating with Kerberos in all other tools. If you wish to convert you ticket to ccache format you can use the minikerberos library: [minikerberos](https://github.com/skelsec/minikerberos) with `minikerberos-kirbi2ccache`

##### Parameter
- **etype** (optional): This is the Kerberos encryption type, with which returned TGT is encrypted. Typical etypes are 18 for AES and 23 for MD5/RC4. If you get the error `KDC_ERR_ETYPE_NOTSUPP` try using a different encryption type. 

#### tgs
Fetches a TGS (Service Ticket) for a given SPN, using the credentials you used when starting the session. 

Resulting TGS will be printed to the console in kirbi format with base64 encoding and added as a new credential in the `Credentials Window`. It is NOT usable for authentication from the credentials window however, this is in the TODO list. {==Is this still not supported on release? ==}  If you wish to convert you ticket to ccache format you can use the minikerberos library: [minikerberos](https://github.com/skelsec/minikerberos) with `minikerberos-kirbi2ccache`

##### Parameter

- **spn**: The service principal name of the Service you want to get the TGS for. This must be in the format of `service/host@domain`, e.g. `ldap/kingslanding.sevenkingdoms.local@sevenkingdoms.local`. You can list the SPNs of a system using the [machine](ldap.html#machine) command in the LDAP client and looking at the `servicePrincipalName` attribute. 

#### s4uproxy

S4U2Proxy is a part of Kerberos constrained delegation within Microsoft Active Directory environments. It is used to extend the capabilities of Kerberos authentication to allow a service to request access to another service on behalf of a user. This is particularly useful in scenarios where services need to interact with each other seamlessly on behalf of users without needing to re-authenticate. For example, a user accesses a web application hosted on an IIS server. This server needs to retrieve data from a SQL database on behalf of the user. With S4U2Proxy, after authenticating the user, the IIS server can request access to the SQL server as if it were the user, using the user's rights and permissions. This s4u2proxy extension allows a service that has already obtained a service ticket on behalf of a user (using S4U2self) to request access to a second service on behalf of the same user. This is done without the user's direct involvement in the second service's authentication process.

S4u2proxy is typically combined with S4U2self to fully exploit Kerberos delegation capabilities for impersonation and access control bypass. Here’s how the two can work together in an attack scenario:

1. **Initial Access and Service Account Compromise**:
        The attacker first needs to gain control over a service account that is configured to use Kerberos constrained delegation with S4U2Proxy. This could be through credential theft, exploiting a vulnerable service, or other means. To determine if a service account is configured to use constrained delegation with S4U2Proxy in Active Directory (AD), you need to inspect the `msDS-AllowedToDelegateTo` attribute. This attribute lists the service principal names (SPNs) to which the account is allowed to delegate.

2. **Using S4U2self**:
        Once control of a service account is established, the attacker can use the S4U2self extension to obtain a Kerberos Service Ticket on behalf of any user to the service itself, even if that user has not logged on using Kerberos or has used a different authentication method like NTLM. This is typically the first step because S4U2Proxy requires a valid forwardable ticket, which S4U2self can provide.

3. **Using S4U2Proxy**:
        With the service ticket obtained from the S4U2self step, which must be forwardable, the attacker then uses S4U2Proxy to request access to another service on behalf of the user. This second service is one to which the initially compromised service account has been granted rights to delegate.

4. **Impersonating the User**:
        The final service ticket obtained via S4U2Proxy can be used to access resources or perform actions on other services as the impersonated user, bypassing the need for the user's credentials and directly exploiting the delegation configuration.

##### Parameters

- **spn**: Service Principal name in the format `service/host@domain`, e.g. `ldap/kingslanding.sevenkingdoms.local@sevenkingdoms.local`
- **targetuser**: User you want to target in the format `samAccountName@domain`, e.g. `Administrator@sevenkingdoms.local`

!!! troubleshooting
	- If you get the Exception: `not enough values to unpack` the format of the SPN is incorrect. It must be `service/host@domain`
{==not tested, got same error as in s4uself==}

#### s4uself

S4U2self, short for "Service for User to Self", is a Kerberos extension that allows a service to request a service ticket for itself on behalf of a user. S4U2self is designed to be used in environments where a service needs to impersonate a user to access resources or perform operations, even if the user has not authenticated to the service using Kerberos. It can be used 

It can also be used to take a valid TGT of a computer account and turn it into a valid TGT for a user with local admin rights on the machine. 
If you have a TGT of a Machine e.g. WKSTN-2$ (e.g. via unconstrained delegation) you can abuse s4u2self to gain Remote Code Execution with a local admin. Using a TGT of a machine account it is not possible to access the machine remotely because machines do not get remote local admin access on themselves. What we can do instead is abuse S4U2Self to obtain a usable TGS as a user we know is a local admin (e.g. a domain admin). (Another way to get local admin would be a dcsync, but that only works if the target machine is the DC) To abuse this scenario, use the TGT of the machine account to create a kerberos client and then enter any local admin of that machine as the `targetuser` parameter.

##### Parameter

- **targetuser**: 

{==DC_ERR_S_PRINCIPAL_UNKNOWN Detail: "Server not found in Kerberos database" Btw, here is no spn parameter. spn is used in minikerberos Is this missing, or is it using some default spn? ==}

TBD


### ROAST
#### kerberoast

Performs SPNRoast (kerberoast) attack, prints the resulting TGS tickets to the console which can then be cracked offline. To roast all vulnerable users, simply use the session id of an establish LDAP session. 

!!! tip
	Instead of using the samAccountName, you can use a `Session ID` of an established `LDAP` or `LDAPS` client session, in this case all vulnerable users will be kerberoasted.

The Kerberoast attack allows you to retrieve TGS tickets of users with an SPN record. In the default configuration the TGS tickets are encrypted with RC4 (Kerberos etype 23), which allows offline cracking of the tickets in a short amount of type. If RC4 is disabled in the domain it is still possible to retrieve AES encrypted (Kerberos etype 18) TGS tickets, but cracking them will take a longer amount of time. If a service account uses an insecure password, this can be used to take over the accounts. It is also possible to use a targeted Kerberoasting attack if you have Write privileges on the SPN attribute in the AD by setting an SPN and then cracking the password using Kerberoasting.
 

##### Parameters

- **spn**: The samAccountName of the user you want to get the Kerberos ticket of in the format `samAccountName@domain`, e.g. `mssqlsvc@sevenkingdoms.local` OR the session id of the LDAP client session, which will kerberoast all users.

- **crossdomain** (optional): If the targeted user is in another domain you need to set this to "True". Otherwise you can ignore it.
- **etype_tgt** (optional): {==???==}
- **etype_tgs** (optional): Encryption types to use for the resuting TGS ticket. Default: 23,17,18

#### asreproast
Performs the asreproast attack, prints the resulting ticket to the console which can then be cracked offline. 

!!! tip
	Instead of using the username, you can use a `Session ID` of an established `LDAP` or `LDAPS` session, in this case all vulnerable users will be asreproasted. 

ASREPRoast is a type of security exploit targeting users who do not have the Kerberos pre-authentication feature enabled. This vulnerability permits attackers to request authentication on behalf of a user from the Domain Controller (DC) without possessing the user's password. In response, the DC issues a message encrypted with a key derived from the user's password, which attackers can then try to decrypt offline to crack the user's password.

##### Parameter

- **user**: The samAccountName of the user you want to AR-REP roast in the format format `samAccountName@domain`, e.g. `cersei.lannister@sevenkingdoms.local` OR the session id of the LDAP client session, which will asreproast all users.

### PKI
#### nt
Fetches the NT hash of the current user. Only works if you created the session using a certificate type credential (choose Auth protocol P12). Otherwise you will get the exception `'AIOKerberosClient' object has no attribute 'get_NT_from_PAC'`. 

### ATTACKS
#### cve202233679
Performs CVE-2022-33679 attack against a vulnerable user. This requires a user with disable preauthentication, similar to AS-REP roasting. If it succeeds you will get a TGT for that user. {==How do I give the script a user? Or does it enumerate vulnerable ones automatically and does it for all then? Or do I need to authenticate the kerberos client with it?==}

CVE-2022-33679 exploits a vulnerability in Windows Kerberos authentication, specifically through the use of the deprecated RC4 encryption algorithm. If a user account is configured to not require Kerberos preauthentication an attacker can directly submit a request specifying the RC4 encryption, which is inherently weaker. The Kerberos Key Distribution Center (KDC) then processes this request and issues an encrypted Ticket Granting Ticket (TGT) using RC4. The attacker can subsequently attempt to decrypt the TGT offline, exploiting the known vulnerabilities of the RC4 algorithm. 
