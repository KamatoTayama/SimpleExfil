import http.server
import socketserver
import os
import sys
import json
import logging
import argparse
import secrets
import urllib.parse

SESSION_TOKEN = secrets.token_hex(32)


def parse_args():
    parser = argparse.ArgumentParser(
        description="SimpleExfil - lightweight file exfiltration server"
    )
    parser.add_argument(
        "-p", "--port", type=int, default=8000, help="Port to listen on (default: 8000)"
    )
    parser.add_argument(
        "-pw", "--password", type=str, default=None,
        help="Password required to access the server"
    )
    parser.add_argument(
        "-d", "--directory", type=str, default=None,
        help="Upload directory (default: ./vault)"
    )
    return parser.parse_args()


args = parse_args()
port = args.port
password = args.password
upload_dir = args.directory or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "vault"
)

os.makedirs(upload_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def parse_multipart_upload(rfile, content_type, content_length):
    """Extract filename and bytes for the 'file' field from multipart form data."""
    body = rfile.read(content_length)

    if "boundary=" not in content_type:
        return None, None

    boundary = content_type.split("boundary=")[-1].strip()
    if boundary.startswith('"') and boundary.endswith('"'):
        boundary = boundary[1:-1]

    boundary_bytes = ("--" + boundary).encode()
    parts = body.split(boundary_bytes)

    for part in parts:
        if not part or part.strip() in (b"", b"--", b"--\r\n"):
            continue

        if part.startswith(b"\r\n"):
            part = part[2:]

        sep = part.find(b"\r\n\r\n")
        if sep == -1:
            continue

        headers_raw = part[:sep].decode("utf-8", errors="replace")
        body_data = part[sep + 4:]

        if body_data.endswith(b"\r\n"):
            body_data = body_data[:-2]

        if 'name="file"' not in headers_raw:
            continue

        filename = None
        for header_line in headers_raw.split("\r\n"):
            if 'filename="' in header_line:
                start = header_line.index('filename="') + 10
                end = header_line.index('"', start)
                filename = header_line[start:end]
                break

        return filename, body_data

    return None, None


def format_size(size_bytes):
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


class ServerHandler(http.server.SimpleHTTPRequestHandler):

    def check_auth(self):
        if not password:
            return True
        if self.headers.get("X-Password") == password:
            return True
        cookies = self.headers.get("Cookie", "")
        for cookie in cookies.split(";"):
            cookie = cookie.strip()
            if cookie.startswith("session="):
                if cookie[len("session="):] == SESSION_TOKEN:
                    return True
        return False

    def send_json(self, code, data, extra_headers=None):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.path = "/static/index.html"
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        if self.path == "/api/check-auth":
            if not password:
                self.send_json(200, {"authenticated": True, "required": False})
            elif self.check_auth():
                self.send_json(200, {"authenticated": True, "required": True})
            else:
                self.send_json(200, {"authenticated": False, "required": True})
            return

        if self.path == "/api/files":
            if not self.check_auth():
                self.send_json(401, {"error": "Unauthorized"})
                return
            files = []
            for f in os.listdir(upload_dir):
                fpath = os.path.join(upload_dir, f)
                if os.path.isfile(fpath):
                    stat = os.stat(fpath)
                    files.append({
                        "name": f,
                        "size": stat.st_size,
                        "size_human": format_size(stat.st_size),
                        "modified": stat.st_mtime,
                    })
            files.sort(key=lambda x: x["modified"], reverse=True)
            self.send_json(200, files)
            return

        if self.path.startswith("/download/"):
            if not self.check_auth():
                self.send_json(401, {"error": "Unauthorized"})
                return
            raw_name = urllib.parse.unquote(self.path[len("/download/"):])
            safe_name = os.path.basename(raw_name)
            filepath = os.path.join(upload_dir, safe_name)
            if not os.path.isfile(filepath):
                self.send_error(404, "File not found")
                return
            fsize = os.path.getsize(filepath)
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header(
                "Content-Disposition", f'attachment; filename="{safe_name}"'
            )
            self.send_header("Content-Length", str(fsize))
            self.end_headers()
            with open(filepath, "rb") as f:
                while chunk := f.read(65536):
                    self.wfile.write(chunk)
            return

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/api/auth":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8", errors="replace")
            try:
                data = json.loads(body)
                pw = data.get("password", "")
            except (json.JSONDecodeError, AttributeError):
                pw = ""

            if pw == password:
                logging.info("Successful login from %s", self.client_address[0])
                self.send_json(200, {"success": True}, extra_headers={
                    "Set-Cookie": f"session={SESSION_TOKEN}; Path=/; HttpOnly; SameSite=Strict"
                })
            else:
                logging.warning("Failed login attempt from %s", self.client_address[0])
                self.send_json(401, {"success": False, "error": "Invalid password"})
            return

        if not self.check_auth():
            self.send_json(401, {"error": "Unauthorized"})
            return

        content_type = self.headers.get("Content-Type", "")
        content_length = int(self.headers.get("Content-Length", 0))

        filename, file_data = parse_multipart_upload(
            self.rfile, content_type, content_length
        )

        if not filename or file_data is None:
            logging.error(
                "Failed to read uploaded file from %s", self.client_address[0]
            )
            self.send_error(400, "Invalid upload")
            return

        logging.info(
            "Upload from %s: %s (%s)",
            self.client_address[0], filename, format_size(len(file_data)),
        )

        base_name = os.path.basename(filename)
        name_root, name_ext = os.path.splitext(base_name)
        unique_name = base_name
        counter = 1
        while os.path.exists(os.path.join(upload_dir, unique_name)):
            unique_name = f"{name_root}_{counter}{name_ext}"
            counter += 1

        target_path = os.path.join(upload_dir, unique_name)
        try:
            with open(target_path, "wb") as f:
                f.write(file_data)
        except Exception as e:
            logging.error("Failed to save %s: %s", target_path, e)
            self.send_error(500, "Failed to save file")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(f"Uploaded {unique_name}\n".encode("utf-8"))

    def log_message(self, format, *log_args):
        pass


with socketserver.TCPServer(("", port), ServerHandler) as httpd:
    banner = f"SimpleExfil listening on port {port} | vault: {upload_dir}"
    if password:
        banner += " | password protected"
    print(banner)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
