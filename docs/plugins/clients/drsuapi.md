# DRSUAPI Client plugin
DRSUAPI allows you to perform DCSync, without the use of SMB.  
This has the benefit of not touching port 445 on the DC, but the tradeoff is that you won't get any automatization eg. you will need to know the domain and username to use for a dcsync attack.

## Features
- DRSUAPI operations

## Commands
As usual, all functionalities will be discussed in command groups which logically group commands of similar nature.

### CONNECTION
#### login
#### logout

### OPERATIONS
#### dcsync
Performs DCSync agains a given user.


