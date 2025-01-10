# IDE Utility

The **IDE Utility** in OctoPwn serves as an **Integrated Development Environment** for extending and automating OctoPwn functionalities. It provides a streamlined way to develop custom plugins and scripts tailored to your needs, with built-in support for code stubs, autocompletion, and language server integration.

## Getting Started

### Function Stubs
Predefined function stubs for plugin development are available on the official GitHub repository:  
!!! info "OctoPwn Function Stubs"
	[OctoPwn IDE Language Server](https://github.com/octopwn/octopwn-ide-language-server)

Use these stubs to start developing custom plugins that integrate seamlessly into OctoPwn.

---

## Enabling the OctoPwn Language Server

The **OctoPwn Language Server** provides autocompletion and enhanced development support. To enable it:

1. Navigate to **Global Settings > Change IDE Language Server**.
2. Enter the following URL:  
   `wss://symbols.octopwn.com`
3. Save the settings to activate the language server.

!!! warning
	Enabling the OctoPwn Language Server sends your code to OctoPwn's servers for processing. Ensure you are comfortable with this before proceeding, especially when handling sensitive or proprietary code.

