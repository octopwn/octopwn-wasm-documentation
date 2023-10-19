#
# Mode of operation

# Offline
No network connections will be made to other hosts. Nothing extra to configure

# Remote
This mode turns the OctoPwn webpage into a UI for a remote server. Currently in closed beta.

# Standalone
Standalone is the default mode of operation. In this mode the wasm code running in the browser relies on a custom websocket to tcp proxy for communicating over the network. This is needed as browsers do not allow raw TCP/UDP sockets to be created which are needed for the common protocols you'd use on a pentest.  
The setup can be a bit tricky so please read this part carefully.  
You'd need to use an implementation of the WSNET protocol, which is officially available in Python and C#. This manual will show the setup of the Python implementation, as it is the most up-to-date.  

## Install wsnet
You'd need to have Python3.8 or above installed.  
You can install wsnet via the PIP package manager
```
pip install wsnet
```

After installing, you'd need to start the server binary `wsnet-wssserver`.

### OctoPwn loaded via HTTP
In case the frameowrk is loaded via HTTP, the following command will start the proxy on HTTP mode
```wsnet-wsserver --plaintext```

### Octopwn loaded via HTTPS
As browsers do no allow connecting to a plaintext websocket server from a page loaded via HTTPS, the server binary must use a TLS certificate which is trusted by your browser. There are two options: either supply your own certificate and private key `--ssl-cert` and `--ssl-key` respectively. Be sure that the certificate is trusted by your browser.  
If you start the proxy without any parameters, it will look for certificate and private key under the name of `octopwn_ceritficate.pem` and `octopwn_ca_key.pem`. If these files exist they will be used to set up the server. if not, the code will automatically generate a new CA and a certificate/key combo that will be loaded automatically during startup. The CA certificate will need to be manually loaded in the browser's trusted CA store.

