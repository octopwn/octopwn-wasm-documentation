## Credentials


| Authentication Protocol | Client Type | Supported Credentials |
| --- | --- | --- |
| NTLM | SMB, LDAP | Password, NT Hash, AES |
| Kerberos | SMB, LDAP | Password, NT Hash, AES, P12/PFX, CCACHE, KEYTAB, KIRBI |
| SSL | LDAP | P12/PFX, PEM |
| SIMPLE | LDAP | Password |
| SICILY | LDAP | Password, NT Hash, AES |

### Additional Information on Each Authentication Protocol

*   **NTLM (NT LAN Manager)**: A challenge-response authentication protocol used to authenticate a client to a network server on a Windows domain. It's commonly used for SMB and LDAP in environments where Kerberos might not be feasible.
    
*   **Kerberos**: A network authentication protocol designed to provide strong authentication for client/server applications by using secret-key cryptography. It's highly recommended for environments that require robust security, especially in Active Directory setups.
    
*   **SSL (Secure Sockets Layer)**: Provides encryption for data transfers, creating a secure channel over potentially insecure networks. Primarily used in LDAP configurations when data security and privacy are of paramount importance.
    
*   **SIMPLE**: The most basic form of authentication that transmits credentials in plain text. It is generally not recommended for secure environments unless additional security measures, like encryption, are already in place.
    
*   **SICILY (Security Integrated Channel over LDAP Integrated Cryptographic Login)**: Microsoft's proprietary authentication protocol that supports multiple authentication methods including NTLM and sometimes Kerberos. It provides a more integrated authentication approach, particularly useful in Microsoft-centric environments.

### Credential File Management

Uploading credential files into OctoPwn enables the use of various types of credentials, such as ccache, keytab, kirbi, SSH files, and P12/PFX files. There are two primary methods to upload and use these files in OctoPwn:

#### Method 1: Base64 Encoding and Secret Input

1.  **Base64 Encode the Credential File:**
    
    *   First, convert your credential file into a Base64-encoded string. This can be done using a tool or command line utility (e.g., using the `base64` command in Linux or third-party tools online).
    *   Example command in Linux: `base64 /path/to/your/file > encoded.txt`

2.  **Input the Encoded String as a Secret:**
    
    *   Copy the Base64-encoded string from your file.
    *   In OctoPwn, navigate to the section where you can add or edit secrets.
    *   Paste the Base64-encoded string into the secret input field.

#### Method 2: File Upload to Browser and Use the File Path

1.  **Upload the File:**
    
    *   Open OctoPwn in your browser.
    *   Drag and drop your credential file into the browser window. This uploads the file to the volatile browser storage of OctoPwn.
    *   Files uploaded this way are stored temporarily in `/browserfs/volatile`, accessible via the FILE Browser in the clients section on the top right.

2.  **Use the Uploaded File Path as a Secret:**
    
    *   You can navigate to the file browser within OctoPwn to confirm the path of the uploaded file. Typically, it will be something like `/browserfs/volatile/yourfilename`.
    *   When creating a credential that needs credential files as a secret, enter the file name from the file browser into the secret input field where credentials are required. Just enter only the file name `mysecret.pfx`, without the `/browserfs/volatiles/` part. 

!!! warning
	Remember that files uploaded to the volatile browser storage are **temporary**. They will need to be re-uploaded if the browser or OctoPwn session is restarted.




Creating empty credentials:
- Add empty fields with type NONE