# IPMI Hash Attack (ipmihash)

A significant flaw in the **IPMI 2.0 specification** allows the server (Baseboard Management Controller or BMC) to send a salted SHA1 or MD5 hash of a user's password during the authentication process. This means that for any valid user account, the attacker can request and retrieve the password hash without completing authentication. The extracted hashes can then be subjected to offline brute force or dictionary attacks to recover the plaintext password.

The **ipmihash** attack automates this process, identifying user accounts, retrieving password hashes. Recovered hashes can be exported in formats compatible with tools like **Hashcat**. {==what is the output format, hashcat or john?==}

### Hash Extraction Process

1. **Retrieve Hashes**:
   - The BMC responds to a client's request by sending a salted SHA1 or MD5 hash of the requested user's password.
   - This hash is extracted without the need for successful authentication.

2. **Crack Passwords**:
   - The retrieved hashes can be cracked offline using tools like **Hashcat**.
   - Example
     - **Hashcat**: Use mode `7300` to crack IPMI RAKP hashes.
       ```bash
       ./hashcat-cli64.bin --username -m 7300 out.hashcat -a 3 ?a?a?a?a
       ```


---

## Parameters

### Normal Parameters

#### targets
Specifies the targets for the attack.

A list of targets can be specified in the following formats:

- **ID**: ID of the target server from the Targets Window.
- **IP**: Single IP address (e.g., `192.168.1.1`).
- **CIDR**: IP range in CIDR notation (e.g., `192.168.1.0/24`).
- **Hostname**: Resolvable hostname.
- **File**: Path to a file containing targets (must be in OctoPwn’s `/browserefs/volatile` directory). File lists need to be uploaded into OctoPwn and separated by newlines.
- **Control word**: Use `all` to attack all stored targets.

---

### Advanced Parameters

#### maxruntime
Specifies the maximum runtime for the attack.

#### proxy
Specifies the proxy ID to use for the attack.

Enter the ID of the proxy to route the attack through. Proxies must be configured in the Proxy Window.
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
