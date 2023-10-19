# Scanners
OctoPwn comes with various scanner plugins, these can be operated with the same unified interface both via the UI or via the command line.  


# Parameters
The actual parameters depend on the plugin type, but the most common parameters are `credential`, `targets` and `proxy`.  Some scanner plugins do not need credential, in which case you will not see that parameter listed during setup.

## Credential
The `credential` parameter takes an integer corresponding to the `credentialId` parameter form the credentials displayed in the `Credentials Window`.  
Any credential you wish to use for scanning MUST be first stored in the `Credentials Window`

## Targets
The `targets` parameter controls which hosts the scan job will be executad against.  
This parameter is quite special as it can take different input values. 

### Using stored targets
In case you wish to specify a target which is stored in the `Targets Window` you can do so by entering the `targetId` of the corresponding target. If succsessful, the `targetId` will be resolved to the correspondint target's IP or Hostname.  
There is one shortcut which is the control word `all` which will add all targets stored in the `Targets Window` to the list of targets in the scanner options table. 

### Using IP addresses
If you wish to scan one IP address or a range of IP addresses, you can enter it directly to the target field, there is no need to create separate targets in the `Targets Window`. For IP ranges, this parameter accepts CDIR notation. 

### Using target list files
If you wish to scan a list of targets from a text file, you can simply enter the targets file name, but be careful the file must be located in the `work directory` of OctoPwn which is by default the `/volatile` mount point. 

## Proxy
The `proxy` parameter takes an integer corresponding to the `proxyId` parameter form the credentials displayed in the `Proxy Window`.  
Any credential you wish to use for scanning MUST be first stored in the `Proxy Window`.  
IMPORTANT: If you are using the webassembly based OctoPwn version (eg. from the browser) there must always be either one proxy with the id of `0` set OR a proxy chain created from the `Proxy Window` but all of the chains must start with the proxyID of `0`!


# Operating via UI
After loading any scanner plugin you will see a Parameter Table that lets you control all aspects of the scan job.  
You can modify the parameters by left-clicking on the value field and edit the current value then either hit enter button or click on the small `save` button below the parameter value editor.  
Once all parameters set up you will see a button `SCAN` which will start the scan job.  
Hitting the `STOP` button will terminate the scan job.

# Operating via terminal
In case you are a fan of terminals, OctoPwn has you covered! All aspects of the scan job can be controlled from the terminal, in a fashion which closely resembles a certain well known tool starting with `meta`.  
To list the scan parameters, you can use the `options` command. All available parameters will be printed out in a neat table.  
To set a given scan parameter, you can use the `set` command.
To start the scan job you can use the `scan` command.