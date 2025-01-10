# Timeroast Attack

The **Timeroast Attack** leverages the **Kerberos NTP response hashing mechanism** to retrieve hashes of computer accounts in an Active Directory (AD) domain. It performs NTP Roasting by requesting NTP responses with specific RIDs. The attack is notable for being **unauthenticated**, allowing attackers to extract hashes without requiring domain credentials. 

When domain controllers (DCs) send NTP responses, they include a **message authentication code (MAC)** to prevent tampering. This MAC is calculated using the NTLM hash of the computer account's password combined with the NTP response as a salt:

```
MAC = MD5(MD4(computer-password) || NTP-response)
```

These hashes can then be cracked offline using tools like **Hashcat** to recover the plaintext password of computer accounts, potentially leading to lateral movement or privilege escalation.

### How Computer Accounts Get Weak Passwords
- **Legacy Tools and Settings**: Older tools (e.g., `net computer`) and GUI settings may assign default passwords that match the first 14 characters of the computer name. Pre-Windows 2000 Accounts are all vulnerable.
- **Manual Misconfigurations**: Administrators may unintentionally assign weak passwords during manual setups or resets.
- **Disabled Password Resets**: Default settings for Windows rotate passwords every 30 days, but disabling this feature can leave weak passwords unchanged indefinitely.

!!! info
    For a detailed explanation of Timeroasting and how to secure against it, see: [Secura Whitepaper on Timeroasting](https://www.secura.com/uploads/whitepapers/Secura-WP-Timeroasting-v3.pdf).

OctoPwn's Timeroast can either target a specific RID Range (the RID is the last part of the SID, e.g. S-1-5-21-2604966440-2990042199-2902315216-**1117**), or brute force all RIDs, but this will be very slow. 

---

## Parameters

### Normal Parameters

#### endrid
Specifies the RID to target if a specific range is not brute-forced.
#### oldhashes
Indicates whether to retrieve previous hashes during the enumeration process.
#### startrid
Specifies the starting RID for enumeration. Use `-1` to brute-force all available RIDs.

#### target
Specifies the ID of the target NTP server. This is usually the domain controller.

A list of targets can be specified in the following formats:

- **ID**: ID of the target server from the Targets Window.
- **IP**: Single IP address (e.g., `192.168.1.1`).
- **CIDR**: IP range in CIDR notation (e.g., `192.168.1.0/24`).
- **Hostname**: Resolvable hostname.
- **File**: Path to a file containing targets (must be in OctoPwn’s `/browserefs/volatile` directory). File lists need to be uploaded into OctoPwn and separated by newlines.
- **Control word**: Use `all` to scan all stored targets.

---

### Advanced Parameters

#### bindport
Specifies the port to bind the NTP client to.

#### maxruntime
Specifies the maximum runtime for the attack.
#### proxy
Specifies the proxy ID to use for the attack.

#### rate
Defines the rate of NTP packets sent per second.

#### resultsfile
Specifies a file for saving the attack results.
#### showerrors
Determines whether errors encountered during the attack should be displayed.

#### timeout
Sets the timeout in seconds for each target.

#### workercount
Specifies the number of parallel workers for the attack.
