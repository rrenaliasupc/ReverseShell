# ReverseShell

*Made by Ricard Renalias as the final project
for Wireless Network Security, a course for the
ML and Cybersecurity for Internet-Connected Devices MSc.*

## Overview

This repository contains an implementation of a ReverseShell viewed in class but with some improvements:
- Return system information of the client on connection
- Allow to work in different bash types in case in windows (cmd, powershell and wsl) it they are installed
- Allow multiple clients connected to the server. A new UI based in tabs allows to manage it
- Minnnor UI improvements

## Repository distribution

The files are structured as follows:
- In `src` you will find the source code for the client and server part.

## Run the demo

Install dependencies:

```sh
python3 -m pip install -r requirements.txt
```

### Try it!

Run `src/client.py`to execute the client

Run `src/server.py`to execute the server

## More information

For more information, please refer to the project report. You can find
a build of it, if not already in that directory, on the
[GitHub release page](https://github.com/rrenaliasupc/ReverseShell/releases).

## Contributing

This project is licensed under the MIT License. This is a close project that
does not accept contributions per se, but we're more than happy for you to use
this tool to build something more meaningful.
