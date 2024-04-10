# SimpleExfil

This server accepts and stores files sent through HTTP POST requests, ideal for operations requiring file uploads from compromised machines or remote systems. It's lightweight, easy to deploy, and listens on a customizable port.

## Requirements

- Python 3.x

## Usage

Start the server by specifying the desired port as an argument. If no port is specified, it defaults to 8000.

```
python SimpleExfil.py 8000

```

To upload a file, use `curl` from the command line, PowerShell, or any suitable HTTP client. Example for uploading `example.txt`:

```
curl -F "file=@example.txt" http://localhost:8000

```

Server can also be accessed on the browser for a classic upload UI.
