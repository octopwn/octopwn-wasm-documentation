## Welcome!

Here you can find all information about all editions of Octopwn:

* [Getting started with Octopwn](https://docs.octopwn.com/user-guide/gettingstarted.html)
* [How to install Octopwn](https://docs.octopwn.com/setup/install.html)
* [Overview of clients](https://docs.octopwn.com/plugins/clients/overview)
* [Overview of scanners](https://docs.octopwn.com/plugins/scanners/index.html)
* [Overview of utilities](https://docs.octopwn.com/plugins/utils/index.html)
* [Overview of attacks](https://docs.octopwn.com/plugins/attacks/overview)
* [Overview of credentials](https://docs.octopwn.com/user-guide/credentials)
* [Overview of servers](https://docs.octopwn.com/plugins/servers/overview)
* [Overview of targets](https://docs.octopwn.com/user-guide/target)


If you need further help, please [write us here](https://octopwn.com/support) or use the support channel on our [Discord](https://discord.gg/7amw5mD37Y).  
    
**Current Octopwn version:** v2.1  (6-April 2025)  
**Current closed beta:** Octopwn Binary v0.1 (6-April 2025)  
**Currently in development:** Improved automations, tutorials, more attacks and scanners
  
## Release notes for v2.1:
  
**New scanners:**  
- SSHLOGIN: Checks if user can login  
- MSSQLLOGIN: Checks if user can login  
- FTPLOGIN: Checks if user can login  
- MSSQLFINGER: Gets basic NTLM information  
- MSSQLPIPE: It's actually an SMB scanner that checks if servers expose MSSQL pipes  
- MSSQLQUERY: Performs MSSQL query on multiple targets  
- HTTPHEADER: Fetches HTTP(S) headers from targets  
  
**New clients:**  
- MSSQL  
- FTP  
  
**Added new snaffler utility:**  
- besides the core snaffler feature this module can use LLMs via ollama to automatically parse and create new credentials found during a snaffling run  
  
**Added Octopwn core callbacks:**
- target creation callback  
- credential creation callback  
- port creation callbacks  
- session creation callbacks  
These callbacks can be used to automate octopwn via already existing or user-defined modules.
  
**Added autoscan utility:**  
- automatically use built-in (or custom) scanner modules against newlty created targets and/or newly discovered ports which match the pre-set triggerport of any scanner.  
  
**Target ports are now merged when an existing target is added with ports which have not seen before**  
  
**Improved remote control modules**
  
**Changing session file password now automatically performs a save immediately to actualize the password change on disk.**  
  
**Improved plugin system:**  
- The plugin system received some improvements, and we're providing "header" files for octopwn which can be used in vscode/visual studio to help plugin developement.  
  
**Bug fixes:**  
- UI bug fixed: the starter modal's start button could be pressed mutiple times which caused multiple octopwn instances to start in paralel. Now it's been fixed.  
  
**Pyodide upgrade:**  
- We moved from Pyodide version 0.24 to 0.27. This change means considerable speed improrovements and fixes many stability issues.  
  
## Release notes for v2.0:
**Documentation Improvements**

 - Comprehensive updates for better clarity and usability.

**First attacks are implemented**

 - New attack plugins include IPMI, Kerberoast, Timeroast, DPAPI, and more.

**New Scanners Added**

 - SMB Signing Check

 - SMB Share Enumeration with Write-Test

 - PMI Scanners

 - NFS File Scanner

**Target Enhancements**

 - Port/Protocol Pairs: Targets now store port and protocol information.

 - Flexible import: Load targets from Nmap, Nessus, Masscan, or plaintext files, including port details.

 - Prefix Support: Add prefixes when loading targets from list files.

 - Group Assignments: Assign targets to groups during import and creation.

 - One-Click Remote Name Resolution: Simplify single-target creation with remote name resolution.

**Scanner Target Specification**

 - Add group and port-based target filtering for more precise scanning.

**Reworked Product Core**

  - Faster Session Reloads: Experience significantly reduced loading times.

  - Improved Scan Parameters: Enhanced descriptions for better clarity.

  - Overall Performance Boost: Enjoy a much faster and more responsive product.

**Integrated Python Code Execution**

  - Run Python scripts directly from a VSCode-like editor in your browser.

  - Automate various aspects of Octopwn seamlessly.

**Switch protocols directly within the scanners**

  - Create client sessions using different protocols than the scanners themselves.

**UI Improvements**

- Improved and more consistent UI screens

**Improved Creator Logic**

  - Client/Target/Credential/Proxy Creators: Complete in-place configuration without the need to close and reopen them.

**Proxy Improvements**

  - Protocol Support: Python, .NET, and Golang proxies now support UDP.

  - Authentication Proxy: Available in the Golang version.

  - Tailscale Integration: Golang proxies can act as nodes on your Tailscale VPN.

  - Name Resolution: All proxies support name resolution without predefined DNS assignments.

**Neo4j Integration**

  - Optional utility for Bloodhound database integration.

**Session File Enhancements**

  - JSON Serialization: Faster saving and loading times compared to TOML.

  - Important: Older session files are no longer supported. If you have data in older formats, please use the previous version of the session viewer available on [GitHub].

 - Scan History: Now stored in session files for easy access.

**Enhanced User Profile**

 - Displays up-to-date information on the current release.

 - Enables direct proxy code downloads.

**QR Code Login for live.octopwn.com**

 - Seamlessly log in without entering credentials on the machine running Octopwn.

## Release notes for v1.1:

**DNS client**  
 - can resolve already stored targets (both IP and hostname)  
 - can resolve addresses from files  
 - some fixes on the underlying client  

**NFS3 client improvements**  
 - file browsing and downloads/deletion etc. is now supported from the file browser window  
 - some fixes applied to the client code itself  
 
**[NEW] NFS3 file scanner**  
 - same as SMB file scanner, but on NFS3  

**[NEW] HTTP client (beta)**  
 - can render single pages via the proxy  
 - can perform GET and POST queries  

**[NEW] NEO4J client (beta)**  
 - attach to neo4j database  
 - store octopwn data as nodes (targets,credentials, proxies) and edges (sessions)  
 - can interpret existing bloodhound data  
 - perform bloodhound queries  
 - extend existing bloodhound data with octopwn data, and perform combined queries  

**[NEW] Python IDE (beta)**  
 - uses Monaco IDE, same as VSCode  
 - can run python scripts from the browser (pyodide limitations apply)  
 - can automate octopwn  
 - has languageserver support for [python](https://github.com/octopwn/octopwn-ide-language-server)  

**[NEW] Octopwn API interface via languageserver**  
 - supports the new IDE  
 - must be run separately  
 - available on our github  

**Bug fixes**  
 - image editor (beta) fixed  
 - share enumerator statistics fixed  
 
**User Interface improvements**  
 - you can close windows now. Finally :)  
 - window title text improvement  
 - scanner mandatory parameters indicated  
 - frontend-only utilities can be launched from the utils menu  

## Release notes for v1.0:  

**GUI Enhancements:**  
- File Integration: Load targets directly from files, enhancing ease of use.  
- Improved Navigation: Enjoy paginated target views.  
- Batch Processing: Targets are now sent in batches from the Python core.  
- Enhanced Interaction: Copy IP and hostname details individually from the targets table.  
- Credential Management: Merge hashes and create new plaintext credentials via file upload.  
- Error Handling: Clear notifications for missing parameters, avoiding unnecessary exceptions.  
- Session Setup: Enhanced display of selected targets and credentials in the client creation modal.  
- Demo Lab Access: Triggered exclusively via wsnet URL during setup.  
  
**Client Improvements:**  
*LDAP & SMB Enhancements:*    
- LDAP target enumeration is now faster with batch processing.  
- SMB notifications for session status are more reliable.  
- Cross-forest dcsyncing is possible with extended target specification options in SMB dcsync.  
- New regdump2 command in SMB for safer registry secrets dumping.  
- Beta feature for DPAPI secrets dumping and parsing in SMB, enhancing data security.  
  
**Scanner Enhancements:**  
- User Experience: Direct file downloads from the SMBFILE scanner results.  
- LDAPSIG Scanner: Fixed display issues in results table.  
  
**Utility Tools Updates:**  
- pypykatz’s 'ofscan' Tool: Enhanced decryption capability with updated regex and 'latin-1' encoding.  
  
**Core System Updates:**  
- Session Management: Improved file versioning and accurate storage of target port and group details.  
  

