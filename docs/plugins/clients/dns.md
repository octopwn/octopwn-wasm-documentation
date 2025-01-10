# DNS Client 
Simple DNS client based on [unidns](https://github.com/skelsec/unidns). Only TCP is supported currently! The DNS client is integrated into other functionalities within OctoPwn. In order to set a custom DNS resolver (other than the default provided by wsnet), you need to create a DNS session and set it as a default resolver for all future targets.
# Getting started

- To create the DNS client, add the DNS server as target and create the client with the DNS server selected as target. You don't need to provide any credentials. 
- In order to use the custom DNS client to automatically resolve IP addresses within OctoPwn you need to go to Global Settings > Set Resolver and enter the session id of your DNS client there. 

# BASIC
## query
Sends a single DNS query to the server, prints result to the console.
##### Parameters
- **name**: The DNS name you wish to resolve.
- **qtype**: The query type. Supported query types are A/AAAA/PTR.
- **search**: search for a string {==what does this search?==}

# Commands
## TARGETS
#### resolvtargets {==?==}

##### Parameters
- **targetspec**: 
- **search**: 

#### resolvfile

##### Parameters
- **filename**: 
- **store**: 