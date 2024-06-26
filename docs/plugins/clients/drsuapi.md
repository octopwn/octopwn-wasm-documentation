# DCEDRSUAPI Client 
DRSUAPI allows you to perform a DCSync, without the use of SMB.  
This has the benefit of not touching port 445 on the domain controller, but the tradeoff is that you won't get any automatization. This means you will need to know the domain and username to use for a dcsync attack.

## Features
- DRSUAPI operations

## Commands
As usual, all functionalities will be discussed in command groups which logically group commands of similar nature.

### CONNECTION
#### login
Logs in to the server. Required before dcsync.

#### logout
Logs out of the server

### OPERATIONS
#### dcsync
Performs a DCSync against a given user. Using this client it is only possible to sync specific users

##### Parameter

- **username**: The username you want to dcsync in the format `username@domain`. 

{==no response on dcsync==}
