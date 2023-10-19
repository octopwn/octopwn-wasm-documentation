
This plugin implements the file parsing and secrets extraction part of pypykatz.  

## Commands
As usual, all functionalities will be discussed in command groups which logically group commands of similar nature.

### LSASS
#### lsass
Parses an LSASS minidump file to extract secrets.

#### registry
Parses registry hive files and extracts the secrets. At least the system hive file must be provided.

### NTDS
#### ntds
Parses an NTDS.dit file extracted from a domain controller. You must also supply the SYSTEM registry hive as it contains the decryption keys for the secrets to be extracted. The outfile specifies the location of the results file which will hold the extracted secrets.  
The NTDS.dit file and the SYSTEM hive must first be 'uploaded' to the `/volatile` mountpoint of the browser.

### DECRYPTORS
#### gppassword
Decrypts encrypted passwords found in Group Policy Preferences xml/ini files.  

#### ofscan
Decryptes passwords found in TrendMicro's OfficeScan ofcscan.ini files.

### HASHING
#### lm
Generates the LM hash of a given plaintext password
#### nt
Generates the NT hash of a given plaintext password.
#### msdcc
Generates the old Domain Cached Credentials hash of a given password
#### msdcc2
Generates the new (current) Domain Cached Credentials hash of a given username and password
#### kerberos
Generates the kerberos keys for a given passowrd. Be careful, the AES key is generated from using the username and domain as a salt, and this salt might not always be static.  

#### hashes
Generates all the hashes mentioned above in one go.