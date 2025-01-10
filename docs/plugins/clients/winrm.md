# WinRM Client 

The WinRM Client  within the "OctoPwn" framework allows interaction with Windows systems using the Windows Remote Management (WinRM) protocol. This client provides command execution capabilities and supports secure authentication methods. You can use the WinRM Client for lateral movement in a network. 

---
## Features

- **WinRM Operations**: Execute shell commands on remote Windows systems using the WinRM protocol.

---
## Supported Authentication Types

| Authentication Protocol | Secret Type | Description                                            | Example                               |
| ----------------------- | ----------- | ------------------------------------------------------ | ------------------------------------- |
| **NTLM**                | Password    | Authenticate using a username and password.            | `username:password`                   |
| **Kerberos**            | Ticket      | Authenticate using a Kerberos ticket in CCACHE format. | `/browserfs/volatile/krb5cc_0.ccache` |
| **Kerberos**            | Keytab      | Authenticate using a Kerberos keytab file.             | `/browserfs/volatile/admin.keytab`    |

## Commands

### CONNECTION

#### login
Establishes a WinRM connection to the target Windows system.
#### logout

Terminates the WinRM connection.
### CMD

#### cmdexec

Executes a single shell command on the remote Windows system and prints the result.

##### Parameters

- **command**: The command to execute.