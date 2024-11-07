## Welcome!

Here you can find all information about all editions of Octopwn:

* [Getting started with Octopwn](https://docs.octopwn.com/user-guide/gettingstarted.html)
* [How to install Octopwn](https://docs.octopwn.com/setup/install.html)
* [Overview of clients](https://docs.octopwn.com/plugins/overview.html)
* [Overview of scanners](https://docs.octopwn.com/plugins/scanners/index.html)
* [Overview of utilities](https://docs.octopwn.com/plugins/utils/index.html)

If you need further help, please [write us here](https://octopwn.com/support) or use the support channel on our [Discord](https://discord.gg/7amw5mD37Y).  
    
**Current Octopwn version:** v1.1  (6-November 2024)  
**Currently in development:** New UI, Attacks, improved file uploader, bug fixes, documentation updates

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
  

