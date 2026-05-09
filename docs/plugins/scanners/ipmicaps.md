# IPMI Capabilities Scanner

The **Intelligent Platform Management Interface (IPMI)** Capabilities Scanner in OctoPwn scans for open IPMI services and lists their authentication capabilities. IPMI is a protocol that allows for remote management of servers,. Compromising IPMI allows complete control over the hardware with a low-level access to the motherboard, similar to physical access to the machine.  

!!! info
	More information can be found here: [https://www.rapid7.com/blog/post/2013/07/02/a-penetration-testers-guide-to-ipmi/](https://www.rapid7.com/blog/post/2013/07/02/a-penetration-testers-guide-to-ipmi/)

---

## Parameters

### Normal Parameters

#### targets
List of targets to scan. IP/CDIR/file/hostname or enter "all" to scan all stored targets. You can also enter the id of your target to fill in the hostname automatically. 
##### Description
A list of targets can be specified in the following formats:

- **ID**: ID of the target server from the targets window.
- **IP**: Single IP address (e.g., `192.168.1.1`).
- **CIDR**: IP range in CIDR notation (e.g., `192.168.1.0/24`).
- **Hostname**: Resolvable hostname.
- **File**: Path to a file containing targets (must be in OctoPwn’s `/browserefs/volatile` directory). File lists need to be uploaded into OctoPwn and separated by newlines.
- **Control word**: Use `all` to scan all stored targets.
- **Single Group**: `g:<groupname>` (e.g., `g:test1`).
- **Multiple Groups**: `g:<groupname1>,g:<groupname2>` (e.g., `g:test1,g:test2`).
- **Port Group**: `p:<port>` (e.g., `p:445`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:445/tcp`).

---
### Advanced Parameters

#### maxruntime

Specifies the maximum runtime for the scan.
#### proxy

Specifies the proxy ID to use for the scan. Enter the ID of the proxy to route the scan through. Proxies must be configured in the Proxy Window. By default proxy 0 is used. 

#### resultsfile

Specifies a  csv filename for saving scan results. Results will be written to `/browserefs/volatile/`. 
#### showerrors

Determines whether errors encountered during the scan should be displayed.
#### timeout

Sets the timeout in seconds for each target.

#### workercount

Specifies the number of parallel workers for the scan.
#### wsnetreuse

Internal parameter, do not modify.
