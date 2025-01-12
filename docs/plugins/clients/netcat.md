# Netcat Client

The Netcat Client within the "OctoPwn" framework facilitates interaction with remote systems using Netcat-like functionalities. This client is designed for establishing connections, sending data, and customizing communication encodings.

## Features

- Establish and manage connections to remote systems.
- Send data in various formats, including plain text, hexadecimal, and files.
- Configure communication encodings and line terminations.
- Visualize binary data in printable formats.

---

## Commands

### Connection

#### connect

Establishes a connection to the specified target. This can also be used to test if a port is open instead of a port scanner. 

#### disconnect

Terminates the connection gracefully.

---

### Send

#### send

Sends plain text data to the target.

##### Parameters

- **data**: The string data to send.

#### sendhex

Sends hexadecimal data to the target.

##### Parameters

- **data**: The hexadecimal string data to send.

#### sendfile

Sends a file to the target in blocks of specified size.

##### Parameters

- **filepath**: The path to the file to send. 
- **blocksize**: The size of each data block (optional, defaults to standard block size).

!!! info 
	Before using this command, the file must first be uploaded into OctoPwn. Use the file browser to upload the file into the `/browserfs/volatile` directory. Once uploaded, reference the file path from that directory.

---

### Encodings {==How to use==}

#### encoding

{==Sets the encoding for data transmission.==}

#### lineterm

{==Configures the line termination sequence used in the communication.==}

#### binprint

{==Visualizes binary data in a human-readable, printable format.==}