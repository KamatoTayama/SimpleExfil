import http.server
import socketserver
import os
import cgi
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
        html = '''
        <html>
        <head>
        <title>Upload File</title>
        </head>
        <body>
        <form enctype="multipart/form-data" method="post">
        <input name="file" type="file"/>
        <input type="submit" value="Upload"/>
        </form>
        </body>
        </html>
        '''
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

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

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"Uploaded {filename}\n".encode('utf-8'))

with socketserver.TCPServer(("", port), ServerHandler) as httpd:
    print(f"serving at port {port}")
    httpd.serve_forever()
