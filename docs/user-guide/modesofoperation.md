#
# Modes of operation

# Without Networking (Offline)
No network connections will be made to other hosts. Nothing extra to configure.



# With Networking (Online)
In this mode the wasm code running in the browser relies on a custom websocket to tcp proxy for communicating over the network. This is needed as browsers do not allow raw TCP/UDP sockets to be created which are needed for the common protocols you'd use on a pentest.  

For detailed setup instructions, please visit [our installation guide](https://docs.octopwn.com/setup/install.html).

# Remote
This mode turns the OctoPwn webpage into a UI for a remote server. Currently in closed beta.
