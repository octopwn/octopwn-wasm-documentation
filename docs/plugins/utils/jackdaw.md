This is subset of the features of the [Jackdaw](https://github.com/skelsec/jackdaw) domain graphing and password cracking tool. More information is found on it's github page. 
## Domain graphing
The SQLite database file contains all information which is needed to create one or multiple relationship graphs of domain objects.  
To achieve this, the first step is to use the `dbload` or `bhimport` commands. This graph cache file will then be interpreted by a graph library which can be `networkx` or `igraph`. By default we ship OctoPwn with `networkx` for licensing reasons, but `igraph` is much more performant. After the graph has been created in memory it is ready to be used by the 


## Commands
JackDaw tool has two components: scanner and util. This documentation discusses the util part.  
The JackDaw tool supports the following activities:
 - Domain graphing -similar to BloodHound
 - Performing password cracking excercise

Jackdaw relies on a SQLite database file which is produced by the scanner part of the tool.  

### DATABASE

#### dbload
The `dbload` will load the SQLite database file and generate a temporary graph cache file. 

#### bhimport
This commands convers a Bloodhound ingestor file (.zip) and converts it to Jackdaw database.

#### adids
Lists available active directory IDs from the database

#### graphids
Lists available graph IDs from the database

#### currentad
Shows the currently active AD ID

### GRAPH
#### graphload

#### graphsetowned

#### graphclearowned

#### grapthsethvt

#### graphclearhvt

### PATH

#### pathdcsync
#### pathkerberoastda
#### pathasrepda
#### pathhvtda
#### pathownedda
#### pathfromowned
#### pathgettaggednodes
#### pathownedhvt
#### pathkerberoastany
#### pathtoda
#### path

### AD
#### currentad
#### changead
#### trusts
#### kerberoast
#### shares
#### dns

## PWCRACK
#### dcsyncaiosmb
#### dcsyncimpacket
#### potfile
#### pwuncracked
#### pwcracked
#### pwsharing
#### pwstats
#### pwreport
