# Getting Started with OctoPwn


![](img/octopwn-schematics.png)

OctoPwn consists of three components. 

1. The Octopwn Live website [available at live.octopwn.com](https://live.octopwn.com). This will load the octopwn application into your browser. Login with your your OctoPwn credentials or choose the free Community version. 
2. Your browser. After loading the application all interaction and pentesting tools run locally in your browser. Octopwn will only communicate locally via the WSNet Proxy and all data entered is only stored in your browser. 
3. A WebSocket-to-TCP translation proxy ([wsnet](https://github.com/octopwn/wsnet)) which will run on a host in the attack target's network. For getting started it is assumed that both will run on the same computer. The proxy is used to forward traffic into the target network only, all logic regarding attacks is implemented in the browser. You can download the client for your system as needed. 
## Getting Started

1. Go to [live.octopwn.com](https://live.octopwn.com) and log in with you OctoPwn credentials. You can sign up at [octopwn.com](https://octopwn.com). 

	??? info "For Mac Users"
		Safari is currently not supported and will result in connection errors. 
		
		You might need enable local network access for the browser you are using. Go to `System Settings > Privacy & Security > Local Network` and enable your browser here. You might need local administrative privileges to enable this.

2. Download and execute the [wsnet](https://github.com/octopwn/wsnet) client. This will by default open the local port 8700 for communication via websockets with your host machine. If you wish, you can also host the wsnet client on a different device. 

	=== "Python (source)"
	    ```zsh
		 git clone https://github.com/octopwn/wsnet
	     cd wsnet
	     python -m venv venv
		 source venv/bin/activate
	     pip install .
	     wsnet-wssserver
		```
	=== "Python (executable)"
		 Download and execute the wsserver executable for your platform from: 
		 
	     [https://github.com/octopwn/wsnet/releases/latest](https://github.com/octopwn/wsnet/releases/latest)
	
	=== "PIP"
		```bash
		python3 -m venv venv
		source venv/bin/activate
		pip install wsnet
		wsnet-wssserver
		```

	=== "Go"
	    ```
	    https://github.com/octopwn/wsnet-go/releases/latest
		```
	=== ".NET"
	    
	    ```
	    https://github.com/octopwn/wsnet-dotnet/releases/latest
	    ```

	??? info "For Mac Users"
		In order to run `pip3 install wsnet` you need to install XCode Developer Tools. macOS will prompt you to install them automatically when running `pip3 install wsnet`. 

		You will have to add python user binary (`Users/<user>/Library/Python/3.9/bin`) files to your current path in the `~/.zshrc` file and start a new terminal session. 

3. Go back to your browser and enter the address of your local wsnet client in the Networking section `ws://127.0.0.1:8700/` and _Launch OctoPwn_.  

	!!! info 
		If you wish to test OctoPwn features you can use our provided test network by connecting to `wss://goad.octopwn.com/demo`. 


---
### Navigating the Interface

- A detailed guide on how to navigate through OctoPwn's user interface will be provided at a later time. For getting started, add a credential and a target (e.g. the DC), then add a client, such as an SMB client. 

---
### Core Functionalities

You can find comprehensive information on core functionalities and usage here:

* [Overview of clients](../plugins/clients/overview.html): Clients allow you to interact on a protocol-level with various single services such SMB, LDAP and Kerberos. 
* [Overview of scanners](../plugins/scanners/index.html): Scanners allow you to scan multiple hosts based on previously defined target groups. You can for example scan for admin priviliges with a specified user, scan for sensitive files across multiple hosts. 
* [Overview of servers](../plugins/servers/overview.html): Servers allow you to execute attacks that require a server component, such as NTLM Relaying and LLMNR/NBTNS Poisoning. This might require you to open a port on the firewall to receive the connections
* [Overview of utilities](../plugins/utils/index.html): Utilities allow you to run additional functionality that partly run only in the browser, such as pypykatz for lsass analysis, access a local IDE or run roadtools for cloud pentesting. 
* [Overview of attacks](../plugins/attacks/overview.html): Attacks allows an easy one-click experience for common attacks, such as Kerberoasting, DCSync, SAM Dump, ...
* Overview of proxies and proxy chains are coming soon: For now, if you want to tunnel your traffic over a proxy, e.g. when using a C2 or want to tunnel your connection over RDP (e.g. with https://github.com/airbus-seclab/soxy), simply add the proxy with ip address and port and choose your proxy id (shown in the Proxies section in the right popout menu) when connecting a client or a scanner. 

---
### User Management

#### Types of Users:

- **Unregistered, Community Users:** Explore basic operations with our community edition at [live.octopwn.com](https://live.octopwn.com) without the need to register.

- **Paid Users:** Access the full suite of tools and plugins for an extensive experience. You can choose from Starter, Pro or Enterprise licenses. For a detailed feature comparison, see our website [here](https://octopwn.com/features-and-pricing).

If you have purchased multiple licenses, you can assign one unassigned license to a user by inviting them from your account page on our [website](https://octopwn.com/account/login).

4. Click on the chosen license on the "Assign license user" button you want to assign.
5. Enter the email address of the invited person.
6. The invited person will get an email shortly where they can set up an account and the license will get assigned and can be used immediately.

Please note: 

- License validity starts for the date of purchase and not the date of assignment.
- License owners can be changed in the same way every 30 days in case a colleague leaves or do not with to use the license anymore.

---

### Support and Help

If you cannot find the answer you are looking for in this documentation site, please feel free to:

7. Write us an email to support at octopwn dot com.
8. Contact us through the website at [https://octopwn.com/support](https://octopwn.com/support).
9. Ask your question on our [Discord support channel](https://discord.gg/7amw5mD37Y).

---

### Troubleshooting and FAQs

- Coming soon.
