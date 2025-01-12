# RDP Client plugin
This section describes the features and functionalities of the RDP client plugin. 


## Tips
If you enable recording please remember that the resulting file will be stored in your browser's memory.  
Copy-pase of text data works, but depending on the browser and hosting location of the framework you might be prompted to allow clipboard access to OctoPwn's webpage.

## Features
- RDP operations
- Recording RDP sessions

### Supported Authentication Types {==what are supported?==}
| Authentication Protocol | Secret Type | Description | Example |
| ----- | ----- | ------| ----- |
| NTLM | Password | Plaintext Password | MyPassw0rd | 
| NTLM | NT | NT Hash - Login only possible if RestrictedAdminMode is enabled | 8846F7EAEE8FB117AD06BDD830B7586C |
| NTLM | RC4 | RC4 NT Hash - same as NT - Login only possible if RestrictedAdminMode is enabled| 8846F7EAEE8FB117AD06BDD830B7586C |
| NTLM | AES | AES Key (contains a salt such as TEST.LOCALusername) - can be used in stead of the NT Hash - Login only possible if RestrictedAdminMode is enabled | d74ff0ee8da3b9806b18c877dbf29bbde50b5bd8e4dad7a3a725000feb82e8f1 |
| NTLM | NONE | Null authentication |  |
| Kerberos | NT | NT Hash - Login only possible if RestrictedAdminMode is enabled| 8846F7EAEE8FB117AD06BDD830B7586C |
| Kerberos | RC4 | RC4 NT Hash - Login only possible if RestrictedAdminMode is enabled | 8846F7EAEE8FB117AD06BDD830B7586C |
| Kerberos | AES | AES Key (contains a salt such as TEST.LOCALusername) - can be used instead of the NT Hash | d74ff0ee8da3b9806b18c877dbf29bbde50b5bd8e4dad7a3a725000feb82e8f1 |
| Kerberos | P12/PFX | Certificate - upload the certificate to volatile storage and then enter certfile path relative from `/browserefs/volatile`. If the certfile has a password, enter it as a secret | Administrator.pfx |
| Kerberos | CCACHE | Kerberos credentials in binary CCACHE file format  | Administrator.ccache |
| Kerberos | KEYTAB | Kerberos credentials in binary KEYTAB file format | Administrator.keytab |
| Kerberos | KIRBI | Kerberos credentials in binary KIRBI file format | Administrator.kirbi |
| Kerberos | KIRBI | Kerberos credentials in base64 KIRBI file format | doIF9DCCBfCg ...(snip)... ZXVzLmdob3N0cGFjay5sb2NhbA== |
| Kerberos | NONE | Null authentication |  |
| SSL | P12/PFX, PEM |  | |

## Commands

### CONNECTION
#### login
You can set the resolution up front, as screen resizing is not implemented yet.  
The `record` option allows you to record the entire RDP session to an mp4 file. After logging in switch to the screen tab to view the screen. 

#### logout
Ends the RDP session. This does not log out the user, but disconnects the session

{==these following are missing in the GUI, I'll just leave the text here as it is for now==}

### CLIPBOARD OPERATIONS
#### paste
Sets the remote clipboard to a given text.
#### pastefile
Sets the remote clipboard to a local text file's content.

### RUBBERDUCKY
#### duckyexec
Performs a single rubberducky command on the remote host's virtual keyboard
#### duckyfile
Performs a sequence of rubberducky commands on the remote host's virtual keyboard

### SCREEN
#### screenshot
Takes a screenshot