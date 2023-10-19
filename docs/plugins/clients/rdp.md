# RDP Client plugin
This section describes the features and functionalities of the RDP client plugin

## Tips
If you enable recording please remember that the resulting file will be stored in your browser's memory.  
Copy-pase of text data works, but depending on the browser and hosting location of the framework you might bw prompted to allow clipboard access to OctoPwn's webpage.

## Features
- RDP operations

## Commands

### CONNECTION
#### login
You can set the resolution up front, as screen resizing is not implemented yet.  
The `record` option allows you to record the entire RDP session to an mp4 file.

#### logout

### CLIPBOARD OPERATIONS
#### paste
Sets the remote clipboard to a given text.
#### pastefile
Sets the remote clipboard to a local text file's content.

### RUBBERDUCKY
#### duckyexec
Performs a single rubberducky command on the remote host's virtual keyboard
#### duckyfile
Performs a sequence of rubberducky commands on the remote host's virtual keyboard

### SCREEN
#### screenshot
Takes a screenshot