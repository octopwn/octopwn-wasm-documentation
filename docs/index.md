## Welcome!

Here you can find all information about all editions of Octopwn:

* [Getting started with Octopwn](https://docs.octopwn.com/user-guide/gettingstarted.html)
* [How to install Octopwn](https://docs.octopwn.com/setup/install.html)
* [Overview of clients](https://docs.octopwn.com/plugins/overview.html)
* [Overview of scanners](https://docs.octopwn.com/plugins/scanners/index.html)
* [Overview of utilities](https://docs.octopwn.com/plugins/utils/index.html)

If you need further help, please [write us here](https://octopwn.com/support) or use the support channel on our [Discord](https://discord.gg/7amw5mD37Y).  
    
**Current Octopwn version:** v1.0  
**Current public Beta version:** none  
**Currently in development:** New UI, Attacks, improved file uploader, bug fixes

## Release notes for v1.1:

## Release notes for v1.0:  

**GUI Enhancements:**  
* File Integration: Load targets directly from files, enhancing ease of use.  
* Improved Navigation: Enjoy paginated target views.  
* Batch Processing: Targets are now sent in batches from the Python core.  
* Enhanced Interaction: Copy IP and hostname details individually from the targets table.  
* Credential Management: Merge hashes and create new plaintext credentials via file upload.  
* Error Handling: Clear notifications for missing parameters, avoiding unnecessary exceptions.  
* Session Setup: Enhanced display of selected targets and credentials in the client creation modal.  
* Demo Lab Access: Triggered exclusively via wsnet URL during setup.  

**Client Improvements:**  
LDAP & SMB Enhancements:  
* LDAP target enumeration is now faster with batch processing.  
* SMB notifications for session status are more reliable.  
* Cross-forest dcsyncing is possible with extended target specification options in SMB dcsync.  
* New regdump2 command in SMB for safer registry secrets dumping.  
* Beta feature for DPAPI secrets dumping and parsing in SMB, enhancing data security.  

**Scanner Enhancements:**
* User Experience: Direct file downloads from the SMBFILE scanner results.  
* LDAPSIG Scanner: Fixed display issues in results table.  

**Utility Tools Updates:**  
* pypykatz’s 'ofscan' Tool: Enhanced decryption capability with updated regex and 'latin-1' encoding.  

**Core System Updates:**  
* Session Management: Improved file versioning and accurate storage of target port and group details.  


