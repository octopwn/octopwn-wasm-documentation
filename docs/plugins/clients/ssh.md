# SSH Client plugin
This section describes the features and functionalities of the SSH client plugin

## Features
- SFTP file browser
- SSH operations


### SFTP File browser
After sucsessfully logging in to the target server, the SFTP file browser will automatically list the host in the File Browser Window
The file browser supports basic file operations as you'd expect from a file browser like downloading and uploading files, removing and creating directories.

## Supported Authentication Types

| Authentication Protocol | Secret Type | Description                                                                                                        | Example                      |
| ----------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------ | ---------------------------- |
| **Plain**               | Password    | Authenticates with a username and password.                                                                        | `username:password`          |
| **SSH Private Key**     | Private Key | Authenticates using an SSH private key. The private key must be uploaded to OctoPwn’s volatile storage beforehand. | `/browserfs/volatile/id_rsa` |

## Commands
As usual, all functionalities will be discussed in command groups which logically group commands of similar nature.

### CONNECTION
#### login
Establishes an SSH connection to the target server.
#### logout
Terminates the SSH connection.

### SHELL
#### ptyshell
Spawns an interactive shell on the target system. Set this to True if you want an interactive shell.
