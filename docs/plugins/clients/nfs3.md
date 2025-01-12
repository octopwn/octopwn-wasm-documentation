# NFS3 Client

The NFS3 Client within the "OctoPwn" framework facilitates interaction with remote systems using the NFSv3 protocol. This client supports managing NFS mounts, traversing directories, performing file operations, and retrieving filesystem information. It can be a powerful tool in penetration testing, particularly for enumerating NFS shares and leveraging them for privilege escalation or sensitive information retrieval.

---

## Features

- NFS3 file browser
- Provides operations on NFS3, Mount, RPC protocols

---
## Supported Authentication Types

The **NFS3 Client** supports the following authentication protocols and credential types:
{==TODO - what is supported?==}

| Authentication Protocol | Credential Type | Description | Example |
| ----------------------- | --------------- | ----------- | ------- |
| **SYS**                 | Password        |             |         |
| **NONE**                |                 |             |         |

---
## Commands

### Connection

#### login
Logs into the NFS server with the provided credentials. 

#### logout
Logs out from the NFS server, ending the session gracefully.

---

### Services

#### services
Lists available NFS services on the target server. This command can help identify exposed shares and services, providing an entry point for further enumeration.

---

### Mount

#### mount
Mounts a specific NFS share to access its contents.

##### Parameters
- **mountpoint**: The path where the NFS share will be mounted.
#### mounts
{==Lists all currently mounted NFS shares. This can help you keep track of active mounts during testing.==}
#### mountinfo
{==what does it display==}


---

### Traversal

#### ls
Lists the contents of the current directory on the mounted NFS share. Use this to explore files and directories.

#### cd
Changes the current directory to the specified path.

##### Parameters
- **dirname**: The name of the directory to navigate to.

#### refreshcurrentdir
Refreshes the cached directory listing of the current directory.

---

### File Operations

#### get
Downloads a file from the mounted NFS share.

##### Parameters
- **filename**: The name of the file to download.
#### mkdir
Creates a new directory in the current location on the NFS share.
##### Parameters
- **dirname**: The name of the directory to create.

#### rmdir
Removes a directory from the NFS share.
##### Parameters
- **dirname**: The name of the directory to remove.

#### rm
Removes a file from the NFS share.
##### Parameters
- **filename**: The name of the file to remove.

#### touch
Creates an empty file in the current directory on the NFS share.

##### Parameters
- **filename**: The name of the file to create.

#### symlink
Creates a symbolic link to a file or directory.

##### Parameters
- **filename**: The name of the target file or directory.  
- **linkname**: The name of the symbolic link to create.

#### readlink
Reads the target of a symbolic link.

##### Parameters
- **filename**: The name of the symbolic link to read.

---

### Filesystem

#### fsinfo
Retrieves information about the file system where the specified file resides.

##### Parameters
- **filename**: The path to the file or directory.

#### fsstat
Retrieves detailed statistics about the file system.

##### Parameters
- **filename**: The path to the file or directory.

---