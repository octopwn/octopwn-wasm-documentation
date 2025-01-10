# Target Menu Documentation

The **Target Menu** in OctoPwn allows you to define and manage targets for scanning and attacks. Targets can be added, grouped, and configured to suit various use cases. Below are the details of the functionality and configuration options available in the Target Menu.

---

## Adding Targets

You can add targets via the target menu on the left side. There are multiple ways of importing targets.

!!! warning
	If you want to use Kerberos, you must have a hostname, DCIP set either on the target or in global settings, and a realm (FQDN) set in the target or global settings.

	To set globally, go to Global Settings -->
	
	- **Set DC IP** > Enter the IP address of the domain controller
	- **Set realm** > Enter the fully qualified domain name (FQDN) of the domain (e.g. sevenkingdoms.local)

	Note that this can be overriden by setting a DC and realm in the target.

### Single Target
- Add a single target by specifying an **IP address** or **hostname**.
- Automatically resolves hostnames if only an IP address is provided.
- You can set either the IP address, the hostname, or both.  
	- If both are set, no hostname resolution will be performed.
### Multiple Targets
- Add multiple targets by entering one target per line.

### Import from Tools
- **Nmap**: Import targets from an Nmap XML file.
- **Masscan**: Import targets from a Masscan XML file.
- **Nessus**: Import targets from a Nessus scan file.

### Import from Flat File
- Import a list of targets from a plain text file.  
- Each line should contain one **hostname** or **IP address**.

---
### Stored target data
Each target stores the following data:

- **IP Address**: The IP address of the target.  
- **Hostname**: The hostname of the target (optional).  
- **Ports**: A list of discovered ports in the format `port/protocol` (e.g., `445/tcp`) (not shown in the GUI yet).  
- **DCIP**: The Domain Controller IP address for Kerberos operations. If set on a target, it overrides the global DCIP setting.  
- **Realm**: The Kerberos realm. If set on a target, it overrides the global realm setting.  


---

## Target Grouping

Groups make managing and selecting targets easier. For example:

- Assign targets to specific groups (e.g., `test1`, `test2`).  
- Use the group name in scanners to automatically select all targets in that group.
### Creating Groups
- Targets can be assigned to one or more groups.  
- Specify groups as a comma-separated list (e.g., `test1,test2`) when adding a target.  
- Group names are case-insensitive.
- Group names must:
  - Use ASCII characters (letters, digits).  
  - Contain no spaces.  

### Using Groups in Scanners
- In scanners, you can reference groups in the **Target Field** using the following format:
  - **Single Group**: `g:<groupname>` (e.g., `g:test1`).  
  - **Multiple Groups**: `g:<groupname1>,g:<groupname2>` (e.g., `g:test1,g:test2`).  
- Note: **Negation of groups is not supported**.

### Port-Based Groups
- Ports are automatically grouped when the target is imported via xml file.  
- You can reference these groups in scanners using the **Target Field**:
  - **Single Port**: `p:<port>` (e.g., `p:445`).  
  - **Port with Protocol**: `p:<port>/<protocol>` (e.g., `p:445/tcp`).  
- This will select all targets where the specified port that have been discovered or imported.

---

## Notes on GUI
- Groups and port-based groups are currently **not shown in the GUI** (feature coming soon).  
- Ports associated with targets are also **not shown in the GUI yet**.


