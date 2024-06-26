# DNS Client 
Simple DNS client based on [unidns](https://github.com/skelsec/unidns). Only TCP is supported currently! The DNS client is integrated into other functionalities within OctoPwn. In order to resolve queries for IPs automatically, you need to create a DNS session and set it as a default resolver for all future targets.
# Getting started

- To create the DNS client, add the DNS server as target and create the client with the DNS server selected as target. You don't need to provide any credentials. 
- Recommended: In order to use the DNS client to automatically resolve IP addresses withing OctoPwn you need to go to Global Settings > Resolver and enter the session id of your DNS client there. This is necessary if you want to add targets by DNS name or want to use Kerberos.

# BASIC
## query
Sends a single DNS query to the server, prints result to the console.
##### Parameters
- **name**: The DNS name you wish to resolve.
- **qtype**: The query type. Supported query types are A/AAAA/PTR.

