# IPMI CipherZero Scanner

The **IPMI CipherZero Scanner** in OctoPwn identifies systems vulnerable to the **Cipher 0** authentication bypass in the IPMI 2.0 protocol. Cipher 0 is a significant vulnerability in IPMI 2.0 implementations that allows clear-text authentication, effectively granting access with any password when a valid username is provided. This flaw has been identified in implementations from major vendors like HP, Dell, and Supermicro. 

The **Intelligent Platform Management Interface (IPMI)** is a protocol for remote management of servers and workstations, providing out-of-band access to hardware for monitoring, configuration, and power cycling. It is commonly used in enterprise environments and embedded in Baseboard Management Controllers (BMCs) like HP iLO, Dell DRAC, and Supermicro IPMI.

!!! info
	More information can be found here: [A Penetration Tester's Guide to IPMI](https://www.rapid7.com/blog/post/2013/07/02/a-penetration-testers-guide-to-ipmi/)

---

## Parameters

### Normal Parameters

#### targets
List of targets to scan. IP/CDIR/file/hostname or enter "all" to scan all stored targets. You can also enter the ID of your target to fill in the hostname automatically.

A list of targets can be specified in the following formats:

- **ID**: ID of the target server from the targets window.
- **IP**: Single IP address (e.g., `192.168.1.1`).
- **CIDR**: IP range in CIDR notation (e.g., `192.168.1.0/24`).
- **Hostname**: Resolvable hostname.
- **File**: Path to a file containing targets (must be in OctoPwn’s `/browserefs/volatile` directory). File lists need to be uploaded into OctoPwn and separated by newlines.
- **Control word**: Use `all` to scan all stored targets.

---
### Advanced Parameters

#### maxruntime
Specifies the maximum runtime for the scan.

#### proxy
Specifies the proxy ID to use for the scan. Enter the ID of the proxy to route the scan through. Proxies must be configured in the Proxy Window.

#### resultsfile
Specifies a CSV filename for saving scan results. Results will be written to `/browserefs/volatile/`.
#### showerrors
Determines whether errors encountered during the scan should be displayed.

#### timeout
Sets the timeout in seconds for each target.

#### workercount
Specifies the number of parallel workers for the scan.
#### wsnetreuse
Internal parameter, do not modify.
