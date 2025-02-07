OctoPwn's **servers** allow hosting services on the local system enabling man-in-the-middle (MitM) attacks and credential harvesting by exploiting network protocols like LLMNR, mDNS, NTLM, and more. These servers can enable you to do poisoning, spoofing, and relaying attacks to capture credentials or escalate privileges in Active Directory environments.

Please note that you will need to open the ports required for these protocols to operate.

### Getting Started

#### **1. Configure Prerequisites**

- **Targets**: Add victim IPs/hostnames to the [Targets Window](https://chat.deepseek.com/a/chat/target.md).
- **Credentials**: Ensure credentials for spoofing/relaying are stored in the [Credentials Hub](https://chat.deepseek.com/a/chat/credentials.md).
- **Firewall**: Open ports (e.g., UDP 5355 for LLMNR, TCP 80/443 for Relay).
#### **2. Start a Server**

- **LLMNR/mDNS Server**:
    
    - Set `spoof=1` to enable response spoofing.
        
    - Use `localip` to define the attacker’s IP.
        
    - Captured hashes are saved to `/browserfs/volatile/results.txt`.
        
- **Relay Server**:
    
    - Specify `ldaptargets` or `httptargets` for relay destinations.
        
    - Use `adcstemplate` to request certificates during ADCS relaying.
        

#### **3. Trigger Authentication**

- **Coercion Techniques**:
    
    - Use `printerbug` (via SMB Client) or host malicious WebDAV shares.
        
    - Combine relay with LLMNR/mDNS poisoning to redirect victims.
        

#### **4. Analyze Results**

- **Hashes**: Crack captured Net-NTLMv2 hashes with tools like Hashcat.
    
- **Certificates**: Use obtained certificates for Kerberos authentication.
