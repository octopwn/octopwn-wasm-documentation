# KRB5User Enumeration Scanner

The **KRB5User Scanner** in OctoPwn performs user enumeration against Kerberos authentication server. This scanner operates similarly to the [kerbrute](https://github.com/ropnop/kerbrute) tool and leverages the Kerberos protocol to enumerate valid usernames within a target domain (realm). By attempting authentication with known or guessed usernames, it identifies accounts that exist in the target environment. 

Use the `usernamefiles` or `usernames` parameters to identify valid accounts within a Kerberos environment. Valid accounts can be used for further attacks, such as password spraying.

---

## Parameters

### Normal Parameters

#### realm
Specifies the target Kerberos realm (domain name).

#### target
Specifies the TID (Target ID) of the Kerberos server.
Enter the ID of the Kerberos server from the Targets Window.

#### usernamefiles
Specifies a file containing a list of usernames for enumeration.

Upload the file with usernames into OctoPwn’s `/browserefs/volatile` directory. The file must contain one username per line.

#### usernames
Allows manual input of a list of usernames for enumeration.

Provide usernames as a comma-separated list (e.g., `user1,user2,user3`).

---
### Advanced Parameters

#### maxruntime
Specifies the maximum runtime for the scanner.

#### proxy
Specifies the proxy ID to use for the scan.

Enter the ID of the proxy to route the scan through. Proxies must be configured in the Proxy Window.

#### resultsfile
Specifies a file for saving the scan results.

The file will be saved in OctoPwn’s `/browserefs/volatile` directory.

#### showerrors
Determines whether errors encountered during the scan should be displayed.

#### timeout
Sets the timeout (in seconds) for each authentication attempt.

#### workercount
Specifies the number of parallel workers for the scan.

#### wsnetreuse
Internal parameter, do not modify.

