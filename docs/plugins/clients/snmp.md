# SNMP Client

The SNMP Client within the "OctoPwn" framework allows interaction with SNMP-enabled devices to query data from their Management Information Base (MIB). This is particularly useful for network enumeration and gathering information about devices and their configurations.  

---  
## Features  
- **OID Querying**: Retrieve specific information from devices using Object Identifiers (OIDs). 
- **Bulk Enumeration**: Perform bulk queries for broader data extraction. 
- **File Output**: Save bulk query results directly to a file for analysis.  

--- 
## Commands  
### CMD  
#### get 
Fetches the value of a specific OID from the target SNMP-enabled device.  

**Common OIDs of interest:** 

- **1.3.6.1.2.1.25.1.6.0**: System Processes 
- **1.3.6.1.2.1.25.4.2.1.2**: Running Programs 
- **1.3.6.1.4.1.77.1.2.25**: User Accounts 
- **1.3.6.1.2.1.6.13.1.3**: TCP Local Ports 
- **1.3.6.1.2.1.25.6.3.1.2**: Installed Software
##### Parameters 
- **command**: The OID to query.  **Example:** `1.3.6.1.2.1.25.1.6.0`

---
#### bulkwalk

Performs a bulk walk of the MIB starting from a specific OID. A bulk walk can provide insights into:

- Open TCP ports 
- Running processes 
- Active user sessions 
- Device configurations
##### Parameters
- **startoid**: The starting OID for the bulk walk. (Example: `1.3.6.1.2.1`)

---
#### bulkwalkfile

Performs a bulk walk starting from a specific OID and saves the output to a file.
##### Parameters

- **startoid**: The starting OID for the bulk walk.
- **fname**: The filename to save the output. It will be saved to the octopwn volatile browser storage.
