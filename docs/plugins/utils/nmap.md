
This plugin parses NMAP XML files and supports some basic processing on the results, as well as capable of adding the hosts to the `Targets Window`

## Commands
As usual, all functionalities will be discussed in command groups which logically group commands of similar nature.

### GENERIC
#### load
Loads an NMAP XML file.
#### hosts
Lists all host entries from the Nmap XMl file.
#### ips
Lists all ip addresses from the Nmap XMl file.
#### ports
Lists all ip:port touples from the Nmap XMl file.
#### services
Generates a table of all services with IP:port touples.

#### addtargets
Adds all hosts from the NMAP file with at least one open ports to the `Targets Window`