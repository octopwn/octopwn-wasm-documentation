# Kerberoast Attack

The **Kerberoast Attack** is a technique used in Active Directory environments to retrieve hashed credentials of service accounts from the Ticket Granting Service (TGS). Service accounts are user accounts with a **Service Principal Name (SPN)** set, often tied to critical services and applications. By extracting the TGS ticket for these accounts, penetration testers can crack the hash offline to recover the plaintext password, potentially gaining access to highly privileged accounts. 

OctoPwn will automatically enumerate vulnerable accounts and run the attack on all identified accounts. Kerberoasted Accounts will be visible in the results page and in the Credentials Window in the Kerberoast Tab. You can immediately copy the hashes for cracking by clicking the Copy Button In the Secret Column.

---

## Attack Overview

1. **Prerequisites**:
   - Valid domain credentials are required to request TGS tickets for service accounts.
   - Access to the domain controller or a Kerberos service is necessary.

2. **Attack Steps**:
   - Identify user accounts with an SPN set (e.g., service accounts). OctoPwn will do this for you automatically. 
   - Request the TGS ticket for these accounts.
   - Retrieve the ticket's hash.
   - Perform offline cracking of the hash using tools like **Hashcat** or **John the Ripper** to recover the service account's password.

3. **Potential Outcomes**:
   - Access to sensitive applications or data tied to the service account.
   - Lateral movement within the domain using the compromised account.
   - Escalation of privileges if the service account has administrative permissions.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the user credentials to use for the attack. These can be normal domain user's credentials. 
#### proxy
Specifies the proxy ID to use for the attack.

Enter the ID of the proxy to route the attack through. Proxies must be configured in the Proxy Window.

#### target
Specifies the target domain controller. The attack target is always the domain controller in standard windows domains.

A target can be specified in the following formats:
- **ID**: ID of the target domain controller from the Targets Window.

---

### Advanced Parameters

#### maxruntime
Specifies the maximum runtime for the attack.
#### resultsfile
Specifies a file for saving the attack results.

The file will be saved in OctoPwn’s `/browserefs/volatile` directory.

#### showerrors
Determines whether errors encountered during the attack should be displayed.

#### timeout
Sets the timeout (in seconds) for each target.

#### workercount
Specifies the number of parallel workers for the attack.
#### wsnetreuse
Internal parameter. Do not modify.
