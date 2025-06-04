import http.server
import socketserver
import os
from email import message_from_binary_file
from email.policy import default
from io import BytesIO
import sys

DEFAULT_PORT = 8000

port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT

# Determine directory for uploaded files
upload_dir = os.environ.get("UPLOAD_DIR", ".")
if len(sys.argv) > 2:
    upload_dir = sys.argv[2]

# Ensure the directory exists
os.makedirs(upload_dir, exist_ok=True)

class ServerHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.path = '/static/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )
        filename = form['file'].filename
        file_data = form['file'].file.read()
        target_path = os.path.join(upload_dir, filename)
        with open(target_path, 'wb') as f:
            f.write(file_data)
            
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        ct = self.headers.get('Content-Type', '')

        msg_bytes = b'Content-Type: ' + ct.encode() + b"\r\n\r\n" + body
        msg = message_from_binary_file(BytesIO(msg_bytes), policy=default)

        filename = None
        file_data = None
        for part in msg.walk():
            if part.get_content_disposition() == 'form-data':
                if part.get_param('name', header='Content-Disposition') == 'file':
                    filename = part.get_filename()
                    file_data = part.get_payload(decode=True)
                    break

        if filename and file_data is not None:
            with open(filename, 'wb') as f:
                f.write(file_data)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"Uploaded {filename}\n".encode('utf-8'))

with socketserver.TCPServer(("", port), ServerHandler) as httpd:
    print(f"serving at port {port}")
    httpd.serve_forever()
