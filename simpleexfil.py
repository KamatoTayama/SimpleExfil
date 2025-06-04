import http.server
import socketserver
import os
import sys
import logging
from cgi import FieldStorage

DEFAULT_PORT = 8000

port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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
        form = FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )

        if 'file' not in form:
            self.send_error(400, 'Invalid upload')
            return

        item = form['file']
        filename = item.filename
        file_data = item.file.read()

        if not filename or file_data is None:
            logging.error('Failed to read uploaded file from %s', self.client_address[0])
            self.send_error(400, 'Invalid upload')
            return

        logging.info('Upload attempt from %s for %s', self.client_address[0], filename)

        base_name = os.path.basename(filename)
        name_root, name_ext = os.path.splitext(base_name)
        unique_name = base_name
        counter = 1
        while os.path.exists(os.path.join(upload_dir, unique_name)):
            unique_name = f'{name_root}_{counter}{name_ext}'
            counter += 1

        target_path = os.path.join(upload_dir, unique_name)
        try:
            with open(target_path, 'wb') as f:
                f.write(file_data)
        except Exception as e:
            logging.error('Failed to save %s: %s', target_path, e)
            self.send_error(500, 'Failed to save file')
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f'Uploaded {unique_name}\n'.encode('utf-8'))

with socketserver.TCPServer(("", port), ServerHandler) as httpd:
    print(f"serving at port {port}")
    httpd.serve_forever()
