At its heart, the **Clients** section serves as the command center for communication with different protocols. These clients are not standalone tools but rather modular components that work together seamlessly to execute complex tasks during a pentest. They can be used in conjuction with the scanners, attacks and servers to achieve the goals of the pentest.
### Getting Started

1. Add **credentials** (e.g., passwords, hashes, certificates) to the Credentials Hub.
2. Define **targets** (IP/hostname) in the Targets section.
3. Launch a client (e.g., SMB, LDAP) with the selected credentials and target.


To use OctoPwn's clients effectively, you must first add credentials and define targets within the framework. Credentials can include passwords, NT Hashes, AES Keys, or certificate-based keys like P12/PFX, which are stored in a centralized hub for easy access across OctoPwn. Targets represent the systems or networks you intend to attack, and they require precise configuration, such as hostnames and domain controllers, especially when using authentication protocols like Kerberos.

The clients themselves are designed to interact with these credentials and targets to perform specific tasks. For example:

- **Authentication Plugins**: Clients can be configured to use different authentication methods (e.g., SMB or Kerberos) based on the target environment.
- **File Browsers**: Some clients expose a file browser in the files menu for easy navigation on remote file systems to search for sensitive data. 

You can use multiple clients together to achieve your pentesting goals. For instance, you might start by using a client with LDAP connected to the DC to enumerate ADCS, then switch to the SMB client connected to the ADCS server to abuse the identified vulnerability. You can also deploy a [scanner](../scanners/index.html) to search for vulnerabilities across multiple systems.

OctoPwn simplifies complex tasks like credential management and pivoting through its integrated support for proxies, such as SOCKS5 and reverse SOCKS proxies. This allows pentesters to chain multiple proxies and navigate through network layers with ease, effectively redefining network pivoting in a way that feels almost seamless.