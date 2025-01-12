# Credentials

Credentials can be added via the credentials menu on the left. Depending on which communication and authentication protocol you are using you need to store the appropriate credentials. A list of each supported credential type and authentication protocol associated with each communication protocol can be found below.

!!! warning
	If you want to use Kerberos, you must have a hostname, DCIP set either on the target or in global settings, and a realm (FQDN) set in the target or global settings.

	To set globally, go to Global Settings -->
	
	- **Set DC IP** > Enter the IP address of the domain controller
	- **Set realm** > Enter the fully qualified domain name (FQDN) of the domain (e.g. sevenkingdoms.local)

	Note that this can be overriden by setting a DC and realm in the target.

| **Communication Protocol** | **Authentication Protocol and Supported Credentials**                                                                                                                                                                                     |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **SMB**                    | - **NTLM**: password, nt, lm, rc4  <br>- **KERBEROS**: password, nt, rc4, aes256, aes128, pfxb64, kirbi, kirbib64, keytab, keytabb64, ccache, ccacheb64                                                                                   |
| **LDAP**                   | - **NTLM**: password, nt, lm, rc4  <br>- **KERBEROS**: password, nt, rc4, aes256, aes128, pfxb64, kirbi, kirbib64, keytab, keytabb64, ccache, ccacheb64                                                                                   |
| **LDAPS**                  | - **NTLM**: password, nt, lm, rc4  <br>- **KERBEROS**: password, nt, rc4, aes256, aes128, pfxb64, kirbi, kirbib64, keytab, keytabb64, ccache, ccacheb64                                                                                   |
| **RDP**                    | - **NTLM**: password, nt, lm, rc4  <br>- **KERBEROS**: password, nt, rc4, aes256, aes128, pfxb64, kirbi, kirbib64, keytab, keytabb64, ccache, ccacheb64  <br>- PLAIN: password, none                                                      |
| **SSH**                    | - **PLAIN**: password  <br>- **SSHPRIVKEY**: sshprivkey, sshprivkeyb64                                                                                                                                                                    |
| **VNC**                    | - **NONE**: none  <br>- **PLAIN**: password                                                                                                                                                                                               |
| **WINRM**                  | - **NTLM** (also for CREDSSP_NTLM, SPNEGO_NTLM): password, nt, lm, rc4  <br>- **KERBEROS** (also for CREDSSP_KERBEROS, SPNEGO_KERBEROS): password, nt, rc4, aes256, aes128, pfxb64, kirbi, kirbib64, keytab, keytabb64, ccache, ccacheb64 |
| **KERBEROS**               | - **KERBEROS**: password, nt, rc4, aes256, aes128, pfxb64, kirbi, kirbib64, keytab, keytabb64, ccache, ccacheb64                                                                                                                          |
| **DNS**                    | - **NONE**                                                                                                                                                                                                                                |
| **SNMP**                   | - **PLAIN**: password  <br>- **NONE**                                                                                                                                                                                                     |
| **NTP**                    | - **NONE**                                                                                                                                                                                                                                |
| **NETCAT**                 | - **NONE**                                                                                                                                                                                                                                |
| **NFS**                    | - **SYS**: password<br>- **NONE**                                                                                                                                                                                                         |
| **DCEDRSUAPI**             | - **NTLM**: password, nt, lm, rc4  <br>- **KERBEROS**: password, nt, rc4, aes256, aes128, pfxb64, kirbi, kirbib64, keytab, keytabb64, ccache, ccacheb64                                                                                   |
