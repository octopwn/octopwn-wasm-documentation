# Scanners
Scanners in OctoPwn automate network reconnaissance, vulnerability detection, and service enumeration across multiple targets. Unlike **clients**, which enable direct interaction with protocols (e.g., SMB, LDAP) for manual exploitation, scanners perform bulk operations to identify misconfigurations, exposed services, and vulnerabilities at scale.

### Getting started

1. **Configure Targets**: Enter the ID of your target or use any of the format described in the plugin details. 
2. **Set Credentials**: Store credentials (passwords, hashes, certificates) in the [Credentials Hub](https://chat.deepseek.com/a/chat/credentials.md). You need to enter the id of the credential
3. **Set Proxy**: The default proxy has the id `0`. Alternatively you can chain through to another proxy if you want to scan in a network that is not available to your host. 
4. **Launch Scanner**: Select a scanner, specify `targets` (e.g., `g:domain_controllers`), and set parameters (e.g., scan depth).
5. **Analyze Results**: Credentials will be added to octopwn automatically. Results will be shown either directly in the scanner window or will be available as a file in the file browser under `/browserfs/volatile`. Be sure to export any file before reloading/exiting ocotopwn, as the volatile storage will be deleted by the browser.
