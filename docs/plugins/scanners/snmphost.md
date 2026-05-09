# SNMP Host Scanner (snmphost)

The **SNMP Host Scanner** queries SNMP agents (UDP port 161) on each target and retrieves a single OID value. By default it asks for the **system description** (`sysDescr`, OID `1.3.6.1.2.1.1.1.0`), which is the cheapest way to confirm a community string is valid and to grab a useful identification string in one round trip.

Each result row contains the target IP and the returned OID value. The default `sysDescr` string typically reveals the exact OS name and version (Linux distribution + kernel, Windows version, IOS image) and on network and embedded gear the device type and firmware revision (router, switch, printer, UPS, BMC, …). Confirming that the configured community string works on a target also opens the door for deeper SNMP enumeration (interfaces, routes, ARP table, processes, …) using the SNMP client.

!!! info "Credential = community string"
    For SNMPv1/v2c the "credential" used by this scanner is the SNMP community string stored in the Credentials Window. SNMPv3 uses a credential that holds the full v3 authentication parameters.

!!! tip "Pull a different OID"
    Set `hostnameoid` to any OID you care about — for example `1.3.6.1.2.1.1.5.0` (`sysName`) for a short hostname, `1.3.6.1.2.1.1.6.0` (`sysLocation`) for the configured location string, or `1.3.6.1.4.1.9.2.1.73.0` for Cisco running-config retrieval (when permitted).

!!! tip "Authentication"
    The `authtype` field below defaults to `NTLM` purely for framework symmetry — SNMP
    does not use NTLM or Kerberos. The actual SNMP authentication mechanism (v1/v2c
    community string vs. SNMPv3 user with auth/priv keys) is selected by the credential
    type stored in the Credentials Window. The
    [SNMP client authentication](../clients/snmp.md#authentication) section has the full
    matrix.

---

## Parameters

### Normal Parameters

#### credential
Specifies the ID of the credential to use for authentication. For SNMPv1/v2c this is the community string credential.

Enter the ID of the credential stored in the Credentials Window.

#### hostnameoid
The OID to fetch on each target. Defaults to `1.3.6.1.2.1.1.1.0` (`sysDescr`).

#### targets
Specifies the targets to scan.

A list of targets can be specified in the following formats:

- **ID**: ID of the target server from the targets window.
- **IP**: Single IP address (e.g., `192.168.1.1`).
- **CIDR**: IP range in CIDR notation (e.g., `192.168.1.0/24`).
- **Hostname**: Resolvable hostname.
- **File**: Path to a file containing targets (must be in OctoPwn’s `/browserefs/volatile` directory). File lists need to be uploaded into OctoPwn and separated by newlines.
- **Control word**: Use `all` to scan all stored targets.
- **Single Group**: `g:<groupname>` (e.g., `g:test1`).
- **Multiple Groups**: `g:<groupname1>,g:<groupname2>` (e.g., `g:test1,g:test2`).
- **Port Group**: `p:<port>` (e.g., `p:161`).
- **Port Group with Protocol**: `p:<port>/<protocol>` (e.g., `p:161/udp`).

---

### Advanced Parameters

#### authtype
Specifies the authentication protocol. Defaults to `NTLM` for symmetry with the rest of the
framework — the actual SNMP authentication mechanism (v1/v2c community vs. SNMPv3 user) is
determined by the credential type. See
[SNMP client authentication](../clients/snmp.md#authentication) for the full breakdown.

#### krbetypes
Specifies the Kerberos encryption types to use during the scan.

Provide a comma-separated list of encryption types (e.g., `23,17,18`).

#### krbrealm
Specifies the Kerberos realm to use.

#### maxruntime
Specifies the maximum runtime per host (in seconds). Set to `-1` to disable.

#### protocol
Specifies the protocol. Fixed to `SNMP` for this scanner.

#### proxy
Specifies the proxy ID to use for the scan.

Enter the ID of the proxy to route the scan through. Proxies must be configured in the Proxy Window.

#### resultsfile
Specifies a file for saving the scan results.

The file will be saved in OctoPwn’s `/browserefs/volatile` directory.

#### showerrors
Determines whether errors encountered during the scan should be displayed.

#### timeout
Sets the timeout (in seconds) for each SNMP request.

#### triggerports
Ports which trigger an automated `snmphost` scan when discovered by other scanners. Pre-populated with `161/UDP`.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter. Do not modify.
