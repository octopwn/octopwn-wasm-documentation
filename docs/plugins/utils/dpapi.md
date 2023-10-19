
This plugin Performs DPAPI related functions.  

## Deep-dive

```
In order to decrpyt a file/blob/data of any kind you must obtain a masterkey.
Masterkey can be obtained either from the LSASS process, or by decrypting a masterkeyfile. LSASS is straightforward, succsessfully dumping it will give you all the plaintext masterkeys with the appropriate GUID.
 But if you can't use LSASS, you have to obtain the masterkey file, and decrypt it with an appropriate key. (too many keys, I know...)
 Masterkey files can be located in '%APPDATA%\Microsoft\Protect\%SID%' for each user or '%SYSTEMDIR%\Microsoft\Protect' for the SYSTEM user. But how to decrypt them?
 A masterkeyfile can contain multiple different keys, a masterkey is one of them. The masterkey is stored encrypted in the masterkeyfile, and is encrypted with a key that can be either a key stored in registry (LSA secrets) or not. In case the LSA DPAPI keys are not valid, you will need to use the NT hash of the user's password or the user's plaintext password itself. BUT! deriving the key from the password and the SID will yield 3 different keys, and so far noone could tell what key is the correct one to be used.
 Solution for decrypting a masterkey in the mastereky file: harvest as many key candidates as possible and try to decrypt the masterkey. Much to our luck, verifying the signature data after decryption can tell us if the decrpytion was sucsessfull, so we can tell if the masterkey decrypted correctly or not.

But you may ask: I see a lot of different masterkey files, how can I tell which one is used for my <credential file/vault files/blob>. The answer: a masterkeyfile stores GUID of the keys it stores (eg. the masterkey), and so does your <secret> data sructure for the appropriate key. Therefore it's easy to tell which file to decrypt for a given <secret>

BUT WAIT! THERE IS MORE!

DPAPI is also used to decrypt stroed secrets in Windows Vault and Credential files.
Credential files:
	1. standalone file, inside it there is a DPAPI_BLOB.
	2. DPAPI_BLOB can be decrypted with the corresponding masterkey
	3. After decryption you'll find a CREDENTIAL_BLOB strucutre.
	4. CREDENTIAL_BLOB strucutre has the plaintext secrets, but it's not possible to tell in which filed they are stored. You'll need to check them by hand :)
	
Vault files (VCRD and VPOL):
	VCRD file holds the secrets encrypted. The decrpytion key is stored in the VPOL file, but also encryted. The VPOL file's decryption key is a masterkey. The masterkey is stored in a Masterkeyfile...
	1. Need to find the masterkey to decrypt the VPOL file
	2. VPOL file will give two keys after sucsessful decryption
	3. There is no way to tell (atm) which key will be the correct one to decrypt the VCRD file
	4. The VCRD file has a lot of stored secrets, called attributes. Each attribute is encrypted with one of the keys from the VPOL file
	5. For each attribute: for each key: decrypt attribute.
	6. Check manually if one of them sucseeded because there are no integrity checks, so no way to tell programatically which key worked.
	
Path to decrypt stuff:
	Sub-sections are options of how to get the keys
	
	1. pre_masterkey:
		a, from user password and SID
		b, from user NT hash and SID
		c, from live registry SYSTEM cached DPAPI key or SAM cache NT hash and SID
		d, from offline registry hives
		
	2. masterkey:
		a, from masterkeyfile + pre_masterkey
		b, from live LSASS dump
		c, from offline LSASS dump
		
	3. credential file:
		a, masterkey + credential_file
		
	3. VPOL file:
		a, masterkey + VPOL file
		
	3. VCRED file:
		a, VPOL file + VCRED file
		
	3. DPAPI_BLOB:
		a, masterkey
```

## Tips
All `pre-key` and `masterkey` data will be automatically cached in the session to help you in the secrets extraction phase.  

To perform any meaningful decryption, first you will need to generate `pre-keys`, except if you have already decrypted masterkey secrets in the form of LSASS dump or you are a wizard Harry and from some unknown source you managed to get the keys (pls let me know how).  
You can get `pre-keys` by either using user SID and password or NT hash. Chanses are that you have some `pre-key` material already stored in the `Credentials Window` int his case just smash the `loadcreds` button. In case you have some not stored creds, use the commands in the `PREKEY` command group.  
Now that you have `pre-keys` you can grab a `Masterkey file` and try to decrypt the `masterkey` using the `masterkeys` or `masterkey` command. The former will automatically search all masterkey files and try to decrypt if with all the `pre-keys` cached from before. In case you have successfully decrypted a masterkey the key will be cached.  
If you have masterkeys cached, then you can try to decrypt some actual secrets with the other command groups.  Those commands do not need any masterkey specification because the blobs they are decrypting already contain the masterkey's ID which will be looked up in the hidden cache.

## Commands
As usual, all functionalities will be discussed in command groups which logically group commands of similar nature.

### LOADCREDS
#### loadcreds
Loads all useble credentials from the `Credentials Window`.  

#### minidump
Parses an LSASS minidump file to extract masterkeys.

#### masterkeys
Searches the given path for Masterkey files (filenames with GUID format) and tries to decrypt them all with previously loaded `pre-keys`

### PREKEY
#### clearprekeys
Clears the `pre-key` cache

#### prekey_nt
Generates pre-keys from user's SID and NT hash

#### prekey_password
Generates pre-keys from user SID and plaintext password

#### prekey_registry
Fetches pre-keys from registry hives

### MASTERKEY
#### clearmasterkeys
Clears the `masterkey` cache
#### masterkey
Tries to decrypt a Maskterkey file using all cached pre-keys

### BLOB
#### blob
Decrypts a DPAPI blob (in hex please) using the exisiting masterkey cache
#### describe
Shows metadata of the DPAPI Blob data without performing decryption

### BROWSER
#### chrome
Decrypts credentials stored by Google Chrome using the exisiting masterkey cache.

### WIFI
#### wifi
Decrypts Windows stored WiFi passwords using the exisiting masterkey cache

### VPOL/VCRED/CREDENTIAL
#### vpol
Decrypts .vpol files using the exisiting masterkey cache
#### vcred
Decrypts .vcred files using the exisiting masterkey cache
#### credential
Decrypts .cred files using the exisiting masterkey cache

### CLOUDAP
#### cloudapkd
Decrypts CloudAP PRT secret using the exisiting masterkey cache

### SECURESTRING
#### securestring
Decrypts Powershell SecureString blob using the exisiting masterkey cache