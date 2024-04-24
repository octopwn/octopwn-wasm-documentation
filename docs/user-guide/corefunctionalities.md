## Core functionalities of OctoPwn

Welcome to the core functionalities of Octopwn, where the magic of modern penetration testing unfolds with sophistication and a touch of wizardry. Octopwn isn't just another tool; it's a symphony of well-coordinated functionalities that transform the chaos of traditional pentesting into a streamlined, powerful process.

---

### Clients

In the top right of the Octopwn UI, you'll find the 'Clients' section, a command center that lists all open client windows. Each client is a gateway to a suite of plugins—ranging from SMB plugins and file browsers to Kerberos plugins—tailored to your specific pentesting needs. Start by selecting your desired credentials and target, then create a new client by choosing the authentication protocol and client type. This seamless integration creates a client with the selected credentials and target, ready for interaction. Say goodbye to the tedious credential switching of yesteryear; with Octopwn, it’s all about efficiency. More on client plugins.

### Credentials

At the heart of Octopwn lies the 'Credentials' hub, a vault where all types of keys to the kingdom are stored. Whether you're dealing with passwords, NT Hashes, AES Keys, or any form of certificate-based keys like P12/PFX, they're all here. Add credentials once, and use them across all plugins. When Octopwn discovers new credentials during a scan or attack, they're automatically integrated into this central manager, ready for immediate use.

### Targets

Identifying your battlefield is crucial, and the 'Targets' section allows for precise settings. Add hosts and define their context. Adding the correct hostname and domain controller are essential for using Kerberos authentication. Selecting a target is your first step in deploying a client tailored to that environment.

### Scanners

With the 'Scanners' feature, Octopwn transcends regular capabilities, allowing you to deploy a variety of scanner plugins. From SMB file scanners to checking for administrative privileges on systems. This is where Octopwn’s power in network reconnaissance comes to life. Learn about scanner plugins.

### Proxies

Finally, the 'Proxies' function redefines network pivoting. Traditional tools make managing multiple proxies a cumbersome task, often requiring complex Command and Control (C2) frameworks. Octopwn simplifies this with integrated support for SOCKS5 and reverse socks proxies like Chisel. Chain multiple proxies and navigate through network layers as if they were mere stepping stones. Octopwn makes advanced network pivoting as simple as setting up a game of dominoes.

---

By harnessing these core functionalities, Octopwn equips penetration testers with a robust, intuitive platform that not only simplifies complex tasks but also enhances the effectiveness and scope of their testing efforts. This is not just a tool; it's your partner in the art of digital investigation and security assessment.

