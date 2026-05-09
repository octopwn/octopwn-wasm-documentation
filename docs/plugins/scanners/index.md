# Scanners

Scanners in OctoPwn automate network reconnaissance, vulnerability detection and service enumeration across many targets at once. Unlike **clients**, which provide direct, interactive access to a single protocol (SMB, LDAP, RDP, …), scanners perform bulk operations to identify misconfigurations, exposed services, vulnerabilities and credential opportunities at scale. Discovered information (open ports, valid credentials, vulnerable hosts, …) is automatically registered in the project so it can feed straight into other scanners, clients and attacks.

## Getting started

1. **Configure targets** — enter target IDs, single IPs, CIDR ranges, hostnames, target groups (`g:<name>`), port groups (`p:<port>`) or use `all` to run against everything in the project.
2. **Set credentials** — store any required credentials (passwords, hashes, certificates, community strings) in the Credentials Window and reference them by ID in the `credential` parameter.
3. **Set proxy** (optional) — the default proxy has ID `0`. Chain through other proxies if you need to scan into segregated network segments.
4. **Launch the scanner** — pick a scanner, set `targets` and any scanner-specific parameters, hit run.
5. **Analyse results** — credentials are added to the project automatically. Output appears in the scanner window and, when `resultsfile` is set, in `/browserfs/volatile`. **Export anything you care about before reloading or exiting OctoPwn — volatile storage is wiped by the browser.**

## Tiers and platform support

Each scanner is tagged with a **tier** and a **WASM** flag:

- **Tier** (`community` / `pro` / `enterprise`) — indicates which OctoPwn licence tier is required to run the scanner.
- **WASM** — indicates whether the scanner runs in the browser-based build of OctoPwn. Scanners that shell out to local binaries (Nmap, Nuclei, Chrome) or otherwise need a real OS will be marked as **no**.

## Scanner catalogue

### Discovery & inventory

| Shortname | Tier | Auth | WASM | Description |
|-----------|------|------|------|-------------|
| [portscan](portscan.md) | community | – | yes | TCP connect scanner; auto-registers open ports as target-port entries |
| [nmap](nmap.md) | enterprise | – | no | Nmap wrapper with XML import; SYN scan, version detection, NSE |
| [baseline](baseline.md) | enterprise | yes | yes | All-in-one assessment combining 12 checks per target |

### SMB protocol & fingerprinting

| Shortname | Tier | Auth | WASM | Description |
|-----------|------|------|------|-------------|
| [smbfinger](smbfinger.md) | community | – | yes | OS / domain info from unauthenticated SMB NTLM handshake |
| [smbsig](smbsig.md) | pro | – | yes | Fast SMB-signing yes/no check; finds relay-attack targets |
| [smbproto](smbproto.md) | pro | – | yes | Per-dialect SMB version + signing enumeration |
| [smbiface](smbiface.md) | community | yes | yes | Network interface / IP enumeration via SMB |

### SMB share, file and session enumeration

| Shortname | Tier | Auth | WASM | Description |
|-----------|------|------|------|-------------|
| [smbshare](smbshare.md) | pro | yes | yes | Enumerates SMB shares, tests for read/write access |
| [smbfile](smbfile.md) | community | yes | yes | Recursive share / directory / file enumeration |
| [snaffler](snaffler.md) | pro | yes | yes | Rule-based file triage to find sensitive data on shares |
| [smbsession](smbsession.md) | pro | yes | yes | Lists active user sessions on SMB targets |
| [smbregsession](smbregsession.md) | community | yes | yes | Enumerates local user SIDs from the remote registry |

### Web reconnaissance

| Shortname | Tier | Auth | WASM | Description |
|-----------|------|------|------|-------------|
| [httpheader](httpheader.md) | pro | – | yes | HTTP headers, status codes and page titles |
| [httpfinger](httpfinger.md) | community | – | yes | Web technology / service fingerprinting |
| [webscreenshot](webscreenshot.md) | enterprise | – | no | Headless-Chrome screenshots for visual triage |
| [nuclei](nuclei.md) | enterprise | – | no | Template-based web vulnerability scanner |

### SSH reconnaissance

| Shortname | Tier | Auth | WASM | Description |
|-----------|------|------|------|-------------|
| [sshbanner](sshbanner.md) | pro | – | yes | Retrieves SSH server banner |
| [sshinfo](sshinfo.md) | pro | – | yes | Enumerates KEX algorithms, ciphers, MACs |
| [sshauth](sshauth.md) | pro | yes | yes | Enumerates accepted SSH authentication methods |

### Authentication / credential validation

| Shortname | Tier | Auth | WASM | Description |
|-----------|------|------|------|-------------|
| [krb5user](krb5user.md) | pro | yes | yes | AD username enumeration via Kerberos pre-auth |
| [smbadmin](smbadmin.md) | pro | yes | yes | Tests admin access via C$ / SCM / Remote Registry |
| [smblaps](smblaps.md) | community | yes | yes | Validates LAPS passwords against target hosts |
| [smbbrute](smbbrute.md) | community | yes | yes | Username/password brute force with smart throttling |
| [mssqllogin](mssqllogin.md) | pro | yes | yes | MSSQL credential validation |
| [mssqladmin](mssqladmin.md) | pro | yes | yes | Checks `sysadmin` membership on MSSQL servers |
| [sshlogin](sshlogin.md) | pro | yes | yes | SSH credential validation |
| [ftplogin](ftplogin.md) | pro | yes | yes | FTP credential validation |
| [ftpanon](ftpanon.md) | community | – | yes | Tests FTP servers for anonymous login |
| [rdplogin](rdplogin.md) | pro | yes | yes | RDP credential validation |

### RDP

| Shortname | Tier | Auth | WASM | Description |
|-----------|------|------|------|-------------|
| [rdpcap](rdpcap.md) | pro | yes | yes | Enumerates RDP security capabilities (Restricted Admin, RCG, …) |
| [rdpscreen](rdpscreen.md) | pro | yes | yes | Captures RDP session screenshots |

### MSSQL data hunting

| Shortname | Tier | Auth | WASM | Description |
|-----------|------|------|------|-------------|
| [mssqlfinger](mssqlfinger.md) | pro | – | yes | Unauthenticated OS / domain info from MSSQL NTLM handshake |
| [mssqlpipe](mssqlpipe.md) | pro | yes | yes | Discover MSSQL instances behind SMB named pipes |
| [mssqldbinfo](mssqldbinfo.md) | community | yes | yes | Maps databases / schemas / tables / columns |
| [mssqlsensdata](mssqlsensdata.md) | community | yes | yes | Finds sensitive data (PII, financial, secrets) by keyword + sampling |
| [mssqlquery](mssqlquery.md) | pro | yes | yes | Runs an arbitrary SQL query across many servers |

### WMI

| Shortname | Tier | Auth | WASM | Description |
|-----------|------|------|------|-------------|
| [wmiadmin](wmiadmin.md) | community | yes | yes | Tests admin-level WMI access |
| [wmiquery](wmiquery.md) | community | yes | yes | Runs a custom WQL query across many hosts |

### LDAP & NFS

| Shortname | Tier | Auth | WASM | Description |
|-----------|------|------|------|-------------|
| [ldapsig](ldapsig.md) | pro | yes | yes | Tests LDAP signing / channel-binding enforcement on DCs |
| [nfs3file](nfs3file.md) | pro | yes | yes | Recursive enumeration of NFS v3 shares |

### SNMP & IPMI

| Shortname | Tier | Auth | WASM | Description |
|-----------|------|------|------|-------------|
| [snmphost](snmphost.md) | pro | yes | yes | Reads `sysDescr` (or any OID) from SNMP agents |
| [ipmicaps](ipmicaps.md) | pro | – | yes | Discovers IPMI BMCs and their auth capabilities |
| [ipmicipherzero](ipmicipherzero.md) | pro | – | yes | Tests IPMI BMCs for unauthenticated cipher-zero access |

### Vulnerability & relay-path checks

| Shortname | Tier | Auth | WASM | Description |
|-----------|------|------|------|-------------|
| [smbprintnightmare](smbprintnightmare.md) | community | yes | yes | Tests for PrintNightmare (CVE-2021-1675 / 34527) |
| [smbspooler](smbspooler.md) | community | – | yes | Print Spooler reachable? (PrinterBug / coercion) |
| [smbwebdav](smbwebdav.md) | community | yes | yes | WebClient (WebDAV) active? (NTLM relay sink) |
| [ntlmreflection](ntlmreflection.md) | community | yes | yes | Vulnerable to NTLM relay-back-to-self? |
| [ntlmv1](ntlmv1.md) | community | yes | yes | NTLMv1 still permitted? (`LmCompatibilityLevel`) |
| [CVE_2017_12542](CVE_2017_12542.md) | pro | – | yes | HP iLO 4 authentication bypass |

### Post-exploitation secret hunting

| Shortname | Tier | Auth | WASM | Description |
|-----------|------|------|------|-------------|
| [smbpshistory](smbpshistory.md) | community | yes | yes | Downloads PSReadline command history files |
| [event6secrets](event6secrets.md) | community | yes | yes | Mines Windows Event Logs for embedded secrets |
