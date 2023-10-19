# SMB Client plugin
This section describes the features and functionalities of the SMB client plugin

## Features
- SMB file browser
- SMB operations
- DCE/RPC operations

### SMB File browser
After sucsessfully logging in to the target server, the SMB file browser will automatically list the host in the File Browser Window
The file browser supports basic file operations as you'd expect from a file browser like downloading and uploading files, removing and creating directories.

## Commands
As usual, all functionalities will be discussed in command groups which logically group commands of similar nature.

### Connection
#### Login
Performs an SMB login to the target server
#### Logout
Terminates the connection after logging out gracefully
#### Nodce
This is a pre-login command which disables all DCE operations for restricted systems which do not even allow listing of shares. (Because for some reason SMB doesn't support lisiting of shares without using an extra complex protocol...)

### File Operations
The file operation commands are independent of the operations performed in the File Browser Window.
#### shares
Lists available shares on the target server
#### use
Mounts the share so further file operations can be perfomed on it.
#### cd
Changes current directory on the mounted share
#### get
Download a file or multiple files from the mounted share's current directory
#### put
Uploads a file to the mounted share's current directory
#### del
Removes a file from the mounted share's current directory
#### mkdir
Creates a new folder under the mounted share's current directory
#### getdirsd
Fetches the Security Descriptor of a directory in the the mounted share's current directory
#### getfilesd
Fetches the Security Descriptor of a file in the the mounted share's current directory
#### ls
Lists the contents of the mounted share's current directory
#### dir
See `ls`
#### refreshcurdir
As the directory listing of the current directory is cached, this command is used to refresh the listing

### USER/GROUP MANAGEMENT

#### domains
Lists all available domains the server is a member of
#### domaingroups
Lists all groups of a given domain
#### groupmembers
Lists all accounts in a given domain for a given group
#### users
Lists all users of a given domain
#### localgroups
Lists all local groups on the target (using `Builtin` domain)
#### localgroupmembers
Lists all accounts which are member of the given loal group
#### session
Enumerates all active sessions
#### enumall
Do not use this.

### SERVICE OPERATIONS
#### services
Lists all services on the target machine
#### serviceen
Enables a service given it's name on the remote machine
#### servicedeploy
Deploys a binary file from the local system as a service on the remote system
#### servicecreate
Creates a service and starts it. This only operates on the remote system, no file upload and alike

### REGISTRY OPERATIONS
#### reglistusers
Lists users who have logged in at some point to the remote system via querying the registry.
#### regsave
Dumps registry hive on the remote system.

### TASK OPERATIONS
#### tasks
List tasks on the remote system
#### taskregister
Registers a new scheduled task on the remote system
#### taskdel
Deletes a scheduled task on the remote system

### PRINTER OPERATIONS
#### printerenumdrivers
Enumerates printer drivers on the remote system

### CERTIFICATE OPERATIONS
#### certreq
#### certreqonbehalf

### NTLM COERCION
#### printerbug

### COMMAND EXECUTION
#### servicecmdexec
#### taskcmdexec

### SECRETS DUMPING
#### regdump
#### backupkeys
#### dcsync
#### lsassdump

### SECRETS HUNTING
#### cpasswd

### VULNERABILITIES
#### printnightmare
#### parprintnightmare