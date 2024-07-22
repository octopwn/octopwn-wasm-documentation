# Installing/deploying OctoPwn

Octopwn is a versatile tool with multiple startup options, the best way to start it depends on your starting environment, the target networks and the type of license you obtained.  

## Pro license, self hosting

You must download the `offline bundle` zip file from the [website](https://octopwn.com). This bundle contains three files

* `octopwn.zip` This file contains the entire [live website](https://live.octopwn.com), it is always the latest version. This also contains the `license.zip` and `plugins.zip` which are created for your user. The license you get from downloading this bundle works for one week, after which you must download the `offline bundle` again to continue using this product.  
* `wsnet.exe` This executable is a precompiled version of the [WSNET proxy](https://github.com/octopwn/wsnet-dotnet). This can be used to allow OctoPwn to perform network communication.  
* `zipserver.exe` A simple webserver that is capable to serve files directly from a zip file. Compiled version of [this project](https://github.com/octopwn/zipserver) It is used to "host" the `octopwn.zip` file.

As you see, the `offline bundle` is geared towards Windows usage. This is because on other operating systems we recommend using the Python3 version of `zipserver` and `wsnet`. These can be easily precompiled to the target OS using `pyinstaller`.

### Deploying the self-hosted version - Windows
Deployment of the self-hosted version is relatively simple.

1. Start the `zipserver` which will host your own OctoPwn website. Command: `zipserver.exe octopwn.zip`
2. Start the `WSNET proxy` which will host the Websockets->TCP proxy. *Note: Command will change in the future* Command: `wsnet.exe` 
3. Visit your own OctoPwn instance on `http://localhost:8000`

### Deploying the self-hosted version - Other OS
When using the self-hosted version on operating systems such as Linux or Mac, you will need to decide wether you wish to install `python3` or not (or maybe it's already installed).  
In case you have `python3` and can use `pip`, you can easily install the `wsnet` and `zipserver` utilities by typing  

* `python3 -m pip install wsnet pyzipserver`  


In case you do not have `python3` installed or you do not wish to use the pre-build packages, you will have to create your own binaries from the [`zipserver`](https://github.com/octopwn/pyzipserver) and [`wsnet`](https://github.com/octopwn/wsnet) packages yourself.  



## Online version - All license types (community included)
1. Execute any version of the `wsnet` proxy on the system you have direct connection to. This is usually your own computer, but it can be any other system as long as you can directly connect to the `wsnet` proxy's listening port to. You have the option to change this port (and listen address) of the proxy during startup.
2. Visit the [https://live.octopwn.com](https://live.octopwn.com) website, and log in with your credentials.  
3. When prompted, enter the address (hostname:port) of the `wsnet` proxy you started earlier. Depending on your setup you might need to connect to the proxy via TLS, in this case prepend `wss://` to the address, if you started the `wsnet` proxy without TLS, you will need to use `ws://`. 

!!! warning
	IMPORTANT: *If you loaded the live version of OctoPwn via ***https***, you can only connect to wsnet proxy over secure TLS connection, unless it's listening on localhost. But even in the latter case you MUST use ws://localhost:port not the IP*

## Offline version - All license types (community included)
If you do not wish to use any network related functions of OctoPwn, you only need to visit the [https://live.octopwn.com](https://live.octopwn.com) website and select `No networking` option.  

## Remote version
Remote version allows the OctoPwn webUI to connect to a remote OctoPwn server. This version is currently not public